"""
[app/services/llm_service.py]
LiteLLM 라이브러리를 사용하여 여러 AI 모델(API 기반)을 통일된 방식으로 호출합니다.
스트리밍 NDJSON 포맷으로 응답을 반환합니다.
"""

import os
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, List, Dict
from litellm import completion

from app.services.rag_service import rag_service
from app.services.search_service import search_service

logger = logging.getLogger("llm_service")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('🔍 [%(name)s] %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def _chunk(delta: str = "", done: bool = False, **kwargs) -> str:
    return json.dumps({"delta": delta, "done": done, **kwargs}, ensure_ascii=False) + "\n"

def _map_model(model_name: str) -> str:
    if "gemini-3.1-lite" in model_name or "gemini-2.0-flash-lite" in model_name:
        return "gemini/gemini-3.1-flash-lite-preview"
    if "gemini-2.5-flash" in model_name:
        return "gemini/gemini-2.5-flash"
    return model_name

class LLMService:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            logger.warning("⚠️ GOOGLE_API_KEY가 설정되지 않았습니다.")

    async def _build_messages(self, messages: List[Dict], enable_web_search: bool) -> List[Dict]:
        """RAG/웹 검색 컨텍스트를 포함한 최종 메시지 목록을 구성합니다."""
        user_query = messages[-1]["content"] if messages else ""

        internal_context = rag_service.query_internal(user_query)
        web_context = ""
        if enable_web_search:
            web_context = await search_service.search_web(user_query)

        context_str = ""
        if internal_context:
            context_str += f"\n[내부 데이터 참고]:\n{internal_context}\n"
        if web_context:
            context_str += f"\n[웹 검색 결과 참고]:\n{web_context}\n"

        enriched = list(messages)
        if context_str:
            enriched[-1] = {
                **enriched[-1],
                "content": f"다음 정보를 참고해서 답변해줘.\n{context_str}\n\n사용자 질문: {user_query}"
            }
        return enriched

    def _system_message(self) -> Dict:
        now = datetime.now()
        days_ko = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        day_name = days_ko[now.weekday()]
        now_str = now.strftime(f'%Y년 %m월 %d일 {day_name} %H시 %M분 %S초')
        return {
            "role": "system",
            "content": (
                f"당신은 친절하고 능동적인 AI 조언자이며, 현재 시각은 [{now_str}] 임을 알고 있습니다.\n"
                f"- 현재 시각은 답변의 맥락을 이해하는 용도로만 참고하세요.\n"
                f"- 사용자가 시간을 직접 묻지 않는 한, 현재 시각을 문자 그대로 답변에 포함하지 마세요.\n"
                f"- 분위기에 맞춰 '좋은 오후네요!', '늦은 밤까지 고생 많으세요' 화법을 사용하고, 대화를 이어갈 수 있는 제안을 덧붙여 주세요."
            )
        }

    async def stream_chat_response(
        self,
        messages: List[Dict],
        model_name: str,
        user_id: str = None,
        enable_web_search: bool = False
    ) -> AsyncGenerator[str, None]:
        """LiteLLM 스트리밍 응답을 NDJSON 포맷으로 yield합니다."""
        mapped_model = _map_model(model_name)
        logger.info(f"🤖 [LLM] Streaming {mapped_model} (user={user_id}, web_search={enable_web_search})")

        enriched = await self._build_messages(
            [m if isinstance(m, dict) else m.model_dump() for m in messages],
            enable_web_search
        )
        final_messages = [self._system_message(), *enriched]

        try:
            response = completion(
                model=mapped_model,
                messages=final_messages,
                api_key=self.google_api_key,
                stream=True
            )

            prompt_tokens = 0
            completion_tokens = 0

            for chunk in response:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    yield _chunk(delta=delta)

                # 마지막 청크에서 usage 수집 (provider마다 다를 수 있음)
                if hasattr(chunk, "usage") and chunk.usage:
                    prompt_tokens = chunk.usage.prompt_tokens or 0
                    completion_tokens = chunk.usage.completion_tokens or 0

            yield _chunk(
                done=True,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                },
                model_used=mapped_model
            )
            logger.info(f"✨ [LLM] Stream complete — tokens: {prompt_tokens}+{completion_tokens}")

        except Exception as e:
            logger.error(f"❌ LiteLLM 스트리밍 오류: {e}")
            yield _chunk(delta=f"오류가 발생했습니다: {str(e)}", done=True)

llm_service = LLMService()

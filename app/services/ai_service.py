"""
[app/services/ai_service.py]
MLX LM 라이브러리를 사용하여 실제 AI 답변 생성을 담당하는 서비스 모듈입니다.
모델 로딩, 텍스트 생성 및 스트리밍 로직을 캡슐화하여 제공합니다.
"""

import json
import logging
from typing import AsyncGenerator, Dict, List
from mlx_lm import stream_generate
from mlx_lm.sample_utils import make_sampler, make_logits_processors

from app.services.rag_service import rag_service
from app.services.search_service import search_service

def _chunk(delta: str = "", done: bool = False, **kwargs) -> str:
    return json.dumps({"delta": delta, "done": done, **kwargs}, ensure_ascii=False) + "\n"

logger = logging.getLogger("ai_service")

# 애플리케이션 상태를 저장하는 전역 변수 (모델 및 토크나이저)
state = {
    "model": None,
    "tokenizer": None
}

class AIService:
    @staticmethod
    async def generate_chunks(
        messages: List[Dict[str, str]],
        max_tokens: int,
        temp: float,
        top_p: float,
        repetition_penalty: float,
        enable_web_search: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        AI 모델을 통해 답변을 생성하고 스트림 형태로 반환합니다.
        마지막에 토큰 사용량 메타데이터를 포함합니다.
        """
        if not state["model"] or not state["tokenizer"]:
            yield _chunk(delta="❌ 모델이 로드되지 않았습니다.", done=True)
            return

        tokenizer = state["tokenizer"]
        model = state["model"]

        # RAG 및 웹 검색을 통한 컨텍스트 강화
        user_query = messages[-1]["content"] if messages else ""
        internal_context = rag_service.query_internal(user_query)
        web_context = ""
        
        if enable_web_search:
            web_context = await search_service.search_web(user_query)

        # 컨텍스트가 있으면 시스템 메시지나 대화 내용에 삽입
        enriched_messages = messages.copy()
        context_str = ""
        if internal_context:
            context_str += f"\n[내부 데이터 참고]:\n{internal_context}\n"
        if web_context:
            context_str += f"\n[웹 검색 결과 참고]:\n{web_context}\n"
        
        if context_str:
            # 마지막 사용자 메시지 앞에 컨텍스트 정보를 추가하여 AI가 참고하게 함
            enriched_messages[-1]["content"] = f"정보 참고: {context_str}\n\n질문: {user_query}"

        # 채팅 템플릿 적용
        prompt = tokenizer.apply_chat_template(enriched_messages, tokenize=False, add_generation_prompt=True)
        
        # 보정 파라미터 적용을 위한 유틸리티 생성
        sampler = make_sampler(temp, top_p)
        logits_processors = make_logits_processors(repetition_penalty=repetition_penalty)

        last_chunk = None
        
        # MLX LM 스트리밍 생성 시작
        # stop_tokens 인자가 지원되지 않을 경우를 대비해 수동으로 제어합니다.
        for response in stream_generate(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            sampler=sampler,
            logits_processors=logits_processors
        ):
            last_chunk = response
            text = response.text
            
            # 정지 토큰이 감지되면 생성 중단
            stop_signals = ["<|eot_id|>", "<|end_of_text|>", "<|im_end|>"]
            should_stop = False
            for signal in stop_signals:
                if signal in text:
                    text = text.replace(signal, "")
                    should_stop = True
            
            if text:
                yield _chunk(delta=text)

            if should_stop:
                break

        # 스트림 종료 후 usage 포함 마지막 청크 전송
        if last_chunk:
            yield _chunk(
                done=True,
                usage={
                    "prompt_tokens": last_chunk.prompt_tokens,
                    "completion_tokens": last_chunk.generation_tokens,
                    "total_tokens": last_chunk.prompt_tokens + last_chunk.generation_tokens
                },
                model_used="local"
            )

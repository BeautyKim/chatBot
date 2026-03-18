"""
[app/services/llm_service.py]
LiteLLM 라이브러리를 사용하여 여러 AI 모델(API 기반)을 통일된 방식으로 호출합니다.
Gemini 2.5 Flash(1.5 Flash 최신 버전 포함) 및 OpenAI 등 확장이 용이합니다.
"""

import os
import logging
from datetime import datetime
from litellm import completion
from app.schemas.chat_v2 import Usage
from app.services.rag_service import rag_service
from app.services.search_service import search_service

logger = logging.getLogger("llm_service")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('🔍 [%(name)s] %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class LLMService:
    def __init__(self):
        # 환경 변수 로딩 재확인 (v2 용)
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            logger.warning("⚠️ GOOGLE_API_KEY가 설정되지 않았습니다. Gemini 호출이 실패할 수 있습니다.")

    async def get_chat_response(self, user_id: str, message: str, model_name: str, enable_web_search: bool = False) -> dict:
        """
        RAG 및 웹 검색 결과와 함께 AI 답변을 생성합니다.
        """
        logger.info(f"🤖 [LLM] Calling model {model_name} for user {user_id} (Web Search: {enable_web_search})")
        
        # 1. RAG(문서) 및 웹 검색 컨텍스트 가져오기
        internal_context = rag_service.query_internal(message)
        web_context = ""
        if enable_web_search:
            web_context = await search_service.search_web(message)
            
        # 2. 컨텍스트를 포함한 최종 프롬프트 구성
        context_str = ""
        if internal_context:
            context_str += f"\n[내부 데이터 참고]:\n{internal_context}\n"
        if web_context:
            context_str += f"\n[웹 검색 결과 참고]:\n{web_context}\n"
            
        final_message = message
        if context_str:
            final_message = f"다음 정보를 참고해서 답변해줘.\n{context_str}\n\n사용자 질문: {message}"
            
        # 모델명 매핑 보정 (최신 2.5 / 3.1 대응)
        mapped_model = model_name
        if "gemini-3.1-lite" in model_name or "gemini-2.0-flash-lite" in model_name:
            # 2.0 지원 종료에 따라 3.1 프리뷰로 연결
            mapped_model = "gemini/gemini-3.1-flash-lite-preview"
        elif "gemini-2.5-flash" in model_name:
            mapped_model = "gemini/gemini-2.5-flash"
     
        
        # 3. 시스템 프롬프트 및 시간 정보 구성
        # 요일 정보를 포함하여 AI가 날짜를 더 정확하게 인지하도록 함
        now = datetime.now()
        days_ko = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        day_name = days_ko[now.weekday()]
        now_str = now.strftime(f'%Y년 %m월 %d일 {day_name} %H시 %M분 %S초')
        system_instruction = (
     f"당신은 친절하고 능동적인 AI 조언자이며, 현재 시각은 [{now_str}] 임을 알고 있습니다.\n"
            f"- 현재 시각은 답변의 맥락(밤 인지, 점심 시간인지 등)을 이해하는 용도로만 참고하세요.\n"
            f"- 사용자가 시간을 직접 묻지 않는 한, 매번 현재 시각을 문자 그대로 답변에 포함하지 마세요.\n"
            f"- 대신 분위기에 맞춰 '좋은 오후네요!', '늦은 밤까지 고생 많으세요' 화법을 사용하고, 대화를 이어갈 수 있는 제안을 덧붙여 주세요."
        )

        try:
            # LiteLLM 호출 (시스템 프롬프트 추가)
            response = completion(
                model=mapped_model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": final_message}
                ],
                api_key=self.google_api_key
            )
            logger.info(f"✨ [LLM] Response received from {mapped_model}")
            logger.info(f"📊 [Usage] Tokens: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}, Total={response.usage.total_tokens}")
            # 전체 응답 구조가 궁금할 경우를 위해 한 줄로 남겨둠
            logger.debug(f"📦 [Full Response] {response}")
            
            answer = response.choices[0].message.content
            usage_info = response.usage
            
            return {
                "answer": answer,
                "usage": Usage(
                    prompt_tokens=usage_info.prompt_tokens,
                    completion_tokens=usage_info.completion_tokens,
                    total_tokens=usage_info.total_tokens
                ),
                "model_used": mapped_model
            }
            
        except Exception as e:
            logger.error(f"❌ LiteLLM 호출 중 오류 발생: {e}")
            raise Exception(f"AI 모델({mapped_model}) 응답 생성 실패: {str(e)}")

llm_service = LLMService()

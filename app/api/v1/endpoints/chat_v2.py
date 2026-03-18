"""
[app/api/v1/endpoints/chat_v2.py]
확장형 /chat 엔드포인트를 정의합니다.
LiteLLM 연동, 크레딧 차감(Billing), 대화 내역 저장(Cache)을 포함합니다.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.chat_v2 import ChatRequestV2, ChatResponseV2
from app.services.llm_service import llm_service
from app.services.billing import billing_service
from app.services.cache import cache_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponseV2)
async def chat_v2_endpoint(request: ChatRequestV2):
    """
    유저 식별 및 모델 선택이 가능한 고급 챗 엔드포인트입니다.
    """
    try:
        # Step 1: 대화 저장소(Redis)에서 히스토리 가져오기 (미구현)
        # history = cache_service.get_conversation_history(request.user_id)
        
        # Step 2: AI 모델 호출 (Gemini 등 LiteLLM 연동)
        result = await llm_service.get_chat_response(
            user_id=request.user_id,
            message=request.message,
            model_name=request.model_name,
            enable_web_search=request.enable_web_search
        )
        
        # Step 3: 과금(Billing) 로직 연결 (미구현)
        # 차감할 크레딧 산출 (사용량 기반 가능)
        billing_service.deduct_credit(request.user_id, cost=result["usage"].total_tokens * 0.001)
        
        # Step 4: 결과 반환
        return ChatResponseV2(
            answer=result["answer"],
            usage=result["usage"],
            model_used=result["model_used"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
[app/api/v1/endpoints/cloud_chat.py]
클라우드 LLM(LiteLLM) 기반 채팅 엔드포인트입니다.
NDJSON 스트리밍 포맷으로 응답을 반환합니다.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services.llm_service import llm_service
from app.services.billing import billing_service

router = APIRouter()

@router.post("/cloud")
async def cloud_chat_endpoint(request: ChatRequest):
    async def generate():
        total_tokens = 0
        async for chunk in llm_service.stream_chat_response(
            messages=[msg.model_dump() for msg in request.messages],
            model_name=request.model_name,
            user_id=request.user_id,
            enable_web_search=request.enable_web_search
        ):
            yield chunk

            # done 청크에서 usage 추출해 과금 처리
            import json
            try:
                data = json.loads(chunk)
                if data.get("done") and data.get("usage"):
                    total_tokens = data["usage"].get("total_tokens", 0)
            except Exception:
                pass

        if request.user_id and total_tokens:
            billing_service.deduct_credit(request.user_id, cost=total_tokens * 0.001)

    return StreamingResponse(generate(), media_type="application/x-ndjson")

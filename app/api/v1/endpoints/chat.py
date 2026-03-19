"""
[app/api/v1/endpoints/chat.py]
로컬 MLX LM 모델을 사용하는 채팅 엔드포인트입니다.
NDJSON 스트리밍 포맷으로 응답을 반환합니다.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/local")
async def local_chat_endpoint(request: ChatRequest):
    generator = AIService.generate_chunks(
        messages=[msg.model_dump() for msg in request.messages],
        max_tokens=request.max_tokens,
        temp=request.temp,
        top_p=request.top_p,
        repetition_penalty=request.repetition_penalty,
        enable_web_search=request.enable_web_search
    )
    return StreamingResponse(generator, media_type="application/x-ndjson")

"""
[app/api/v1/endpoints/chat.py]
채팅 관련 API 엔드포인트를 정의하는 파일입니다.
클라이언트의 요청을 받아 AIService를 통해 답변을 생성하고 스트리밍 응답을 반환합니다.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/completions")
async def chat_endpoint(request: ChatRequest):
    """
    사용자의 메시지를 받아 스트리밍 방식으로 답변을 생성합니다.
    """
    # AIService의 제너레이터를 사용하여 스트리밍 응답 생성
    generator = AIService.generate_chunks(
        messages=[msg.model_dump() for msg in request.messages],
        max_tokens=request.max_tokens,
        temp=request.temp,
        top_p=request.top_p,
        repetition_penalty=request.repetition_penalty
    )
    
    return StreamingResponse(generator, media_type="text/plain")

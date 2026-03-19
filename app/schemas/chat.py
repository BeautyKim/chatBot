"""
[app/schemas/chat.py]
채팅 API 요청 및 응답에 사용되는 공통 스키마입니다.
로컬/클라우드 엔드포인트 모두 동일한 스키마를 사용합니다.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model_name: str = Field("local", description="'local' 또는 LiteLLM 모델명 (예: gemini/gemini-2.5-flash)")
    user_id: Optional[str] = Field(None, description="사용자 식별 ID (과금용, 클라우드 모델 시 사용)")
    max_tokens: Optional[int] = 256
    temp: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    repetition_penalty: Optional[float] = 1.1
    enable_web_search: bool = False

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatStreamChunk(BaseModel):
    delta: str
    done: bool
    usage: Optional[Usage] = None       # done=True일 때만 포함
    model_used: Optional[str] = None    # done=True일 때만 포함

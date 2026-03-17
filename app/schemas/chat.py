"""
[app/schemas/chat.py]
API 요청 및 응답에 사용되는 데이터 구조(Pydantic 모델)를 정의합니다.
데이터 유효성 검사를 자동으로 수행합니다.
"""

from pydantic import BaseModel
from typing import List, Dict, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 256
    temp: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    repetition_penalty: Optional[float] = 1.1

"""
[app/schemas/chat_v2.py]
확장형 챗봇 API를 위한 새로운 스키마 정의입니다.
사용자 식별(userId) 및 AI 토큰 사용량(usage) 정보를 포함합니다.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict

class ChatRequestV2(BaseModel):
    user_id: str = Field(..., description="사용자를 식별하는 Unique ID")
    message: str = Field(..., description="사용자가 입력한 질문 메시지")
    model_name: Optional[str] = Field("gemini/gemini-1.5-flash", description="사용할 AI 모델의 이름 (LiteLLM 형식)")
    enable_web_search: bool = Field(False, description="웹 검색(Tavily) 활성화 여부")

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponseV2(BaseModel):
    answer: str
    usage: Usage
    model_used: str
    metadata: Optional[Dict] = None

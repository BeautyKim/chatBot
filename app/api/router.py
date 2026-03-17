"""
[app/api/router.py]
API 버전별 라우터를 통합하는 메인 라우터 설정 파일입니다.
v1, v2 등 API 버전 확장이 용이하도록 구성합니다.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import chat

api_router = APIRouter()

# v1 엔드포인트를 등록 (프리픽스 /v1 추가)
api_router.include_router(chat.router, prefix="/v1/chat", tags=["chat"])

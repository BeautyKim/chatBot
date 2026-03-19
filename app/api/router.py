"""
[app/api/router.py]
API 라우터를 통합하는 메인 라우터 설정 파일입니다.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import chat
from app.api.v1.endpoints import files
from app.api.v1.endpoints import cloud_chat

api_router = APIRouter()

# 로컬 모델 스트리밍 엔드포인트
api_router.include_router(chat.router, prefix="/v1/chat", tags=["chat"])
api_router.include_router(cloud_chat.router, prefix="/v1/chat", tags=["chat"])
api_router.include_router(files.router, prefix="/v1/files", tags=["files"])

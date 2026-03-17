"""
[app/main.py]
애플리케이션의 메인 엔트리 포인트입니다.
FastAPI 앱을 인스턴스화하고, 라우터, 미들웨어, 정적 파일 서빙 등을 설정합니다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.router import api_router
from app.core.config import settings
from app.core.lifespan import lifespan
import os

# FastAPI 인스턴스 생성 및 라이프사이클 관리 연결
app = FastAPI(title=settings.API_TITLE, lifespan=lifespan)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 연결
app.include_router(api_router)

# 정적 파일 서빙 설정 (static 폴더)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 루트 경로 접속 시 프론트엔드 메인 페이지 노출
@app.get("/")
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "index.html not found in static directory"}

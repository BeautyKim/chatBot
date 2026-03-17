"""
[app/core/lifespan.py]
FastAPI 애플리케이션의 시작(startup)과 종료(shutdown) 이벤트를 처리합니다.
서버 시작 시 AI 모델을 메모리에 로드하고, 종료 시 자원을 정리합니다.
"""

import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from mlx_lm import load
from app.core.config import settings
from app.services.ai_service import state

logger = logging.getLogger("lifespan")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 모델 로드
    logger.info(f"🧠 모델 로딩 중... (경로: {settings.MODEL_PATH})")
    try:
        # mlx_lm.load 라이브러리를 통해 모델과 토크나이저를 가져옵니다.
        result = load(settings.MODEL_PATH)
        if len(result) == 3:
            state["model"], state["tokenizer"], _ = result
        else:
            state["model"], state["tokenizer"] = result
        logger.info("✅ 모델 로딩 성공!")
    except Exception as e:
        logger.error(f"❌ 모델 로딩 실패: {e}")
        # 로딩 실패 시 서버 실행을 중단할 수 있습니다.
        raise e
    
    yield
    
    # 종료 시 자원 정리
    state.clear()
    logger.info("♻️ 자원 정리 완료.")

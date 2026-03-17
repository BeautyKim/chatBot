"""
[app/core/config.py]
이 파일은 애플리케이션의 전역 설정을 관리합니다. 
모델 경로, API 제목 등 구성 요소들을 한곳에서 정의하여 유지보수를 용이하게 합니다.
"""

from pydantic import BaseModel
import os

class Settings(BaseModel):
    # AI 모델이 저장된 로컬 경로
    MODEL_PATH: str = "./my-custom-bllossom"
    
    # API 서버의 제목 및 설명
    API_TITLE: str = "AI Chat API"
    
    # 서버 실행 포트 및 호스트
    HOST: str = "0.0.0.0"
    PORT: int = 8080

settings = Settings()

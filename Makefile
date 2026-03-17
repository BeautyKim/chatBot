# Chat API - Makefile

.PHONY: run dev install

# 기본 실행 (서버 구동)
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8080

# 개발용 실행 (Hot Reload 적용)
dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# 모델 학습 (파인튜닝) 시작
train:
	bash scripts/run_train.sh

# 의존성 설치
install:
	pip install -r requirements.txt

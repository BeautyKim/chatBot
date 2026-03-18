# Chat API - Makefile

.PHONY: run dev install

# 기본 실행 (서버 구동)
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8080

# 개발용 실행 (가용 포트 자동 검색 및 Hot Reload 적용)
dev:
	@if [ -f .venv/bin/python ]; then \
		.venv/bin/python scripts/dev.py; \
	else \
		python3 scripts/dev.py; \
	fi

# 모델 학습 (파인튜닝) 시작
train:
	bash scripts/run_train.sh

# 의존성 설치
install:
	pip install -r requirements.txt

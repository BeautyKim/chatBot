# 🤖 AI Chatbot

이 프로젝트는 MLX LM 기반의 로컬 초거대 언어 모델(LLM)을 활용한 맞춤형 채팅 대시보드 애플리케이션입니다.  
`Bllossom` 모델을 기반으로 하며, 사용자의 자체 데이터를 학습(Fine-tuning)시켜 특화된 답변을 제공할 수 있습니다.

## 🚀 시작하기

이 프로젝트를 클론 받은 후, 아래 단계에 따라 서버를 구동할 수 있습니다.

### 1. 환경 설정 및 의존성 설치

Python 3.10 이상의 환경을 권장합니다.

```bash
# 가상 환경 생성 및 활성화 (선택 사항)
python -m venv .venv
source .venv/bin/activate  # Mac/Linux 기준

# 의존성 패키지 설치
pip install -r requirements.txt
```

### 2. AI 모델 준비 (중요)

이 프로젝트는 대용량 모델 파일을 포함하지 않습니다. 아래 모델을 다운로드하여 프로젝트 루트 디렉토리에 위치시켜야 합니다.

* **기본 모델 명칭**: `Bllossom-3B`
* **다운로드 방법**: HuggingFace 등을 통해 다운로드하거나, 제공된 `scripts/download_model.py`를 활용하세요.

### 3. 서버 실행

`Makefile`을 사용하여 아주 간편하게 서버를 구동할 수 있습니다.

```bash
# 개발용 서버 (Hot-Reload 적용)
make dev

# 일반 실행
make run
```

서버가 실행되면 [http://localhost:8080](http://localhost:8080)에 접속하여 채팅 UI를 확인하세요.

---

## 📊 맞춤형 데이터 학습 (Fine-tuning)

본인의 데이터를 모델에 학습시켜 특정 분야의 전문가로 만들 수 있습니다.

1. `qa_data.csv` 파일에 질문(question)과 답변(answer) 쌍을 추가합니다.
2. 아래 명령어를 실행하여 학습을 시작합니다:

    ```bash
    make train
    ```

    *이 과정은 데이터 믹싱 -> LoRA 학습 -> 모델 병합(Fuse) 과정을 자동으로 수행합니다.*

---

## 📂 프로젝트 구조

* `app/`: FastAPI 기반 백엔드 (API 로직, AI 서비스)
* `static/`: 프론트엔드 정적 파일 (채팅 UI)
* `scripts/`: 데이터 전처리 및 모델 학습용 스크립트
* `Makefile`: 서버 실행 및 관리를 위한 단축 명령어 모음

---

## 🛠 주요 기능

* **Streaming Response**: AI의 답변을 실시간 타자로 치는 듯한 효과로 제공
* **Markdown Rendering**: 코드 블록 및 기술 문서 형식 완벽 지원
* **Inference Dashboard**: Temperature, Top-P 등 AI 설정을 실시간 튜닝
* **Usage Tracker**: 실제 토큰 사용량 및 예상 비용 실시간 계산

---

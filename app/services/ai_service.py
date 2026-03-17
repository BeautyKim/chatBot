"""
[app/services/ai_service.py]
MLX LM 라이브러리를 사용하여 실제 AI 답변 생성을 담당하는 서비스 모듈입니다.
모델 로딩, 텍스트 생성 및 스트리밍 로직을 캡슐화하여 제공합니다.
"""

import json
import logging
from typing import AsyncGenerator, Dict, List
from mlx_lm import stream_generate
from mlx_lm.sample_utils import make_sampler, make_logits_processors

logger = logging.getLogger("ai_service")

# 애플리케이션 상태를 저장하는 전역 변수 (모델 및 토크나이저)
state = {
    "model": None,
    "tokenizer": None
}

class AIService:
    @staticmethod
    async def generate_chunks(
        messages: List[Dict[str, str]],
        max_tokens: int,
        temp: float,
        top_p: float,
        repetition_penalty: float
    ) -> AsyncGenerator[str, None]:
        """
        AI 모델을 통해 답변을 생성하고 스트림 형태로 반환합니다.
        마지막에 토큰 사용량 메타데이터를 포함합니다.
        """
        if not state["model"] or not state["tokenizer"]:
            yield "❌ 모델이 로드되지 않았습니다."
            return

        tokenizer = state["tokenizer"]
        model = state["model"]

        # 채팅 템플릿 적용
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        # 보정 파라미터 적용을 위한 유틸리티 생성
        sampler = make_sampler(temp, top_p)
        logits_processors = make_logits_processors(repetition_penalty=repetition_penalty)

        last_chunk = None
        
        # MLX LM 스트리밍 생성 시작
        # stop_tokens 인자가 지원되지 않을 경우를 대비해 수동으로 제어합니다.
        for response in stream_generate(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            sampler=sampler,
            logits_processors=logits_processors
        ):
            last_chunk = response
            text = response.text
            
            # 정지 토큰이 감지되면 생성 중단
            stop_signals = ["<|eot_id|>", "<|end_of_text|>", "<|im_end|>"]
            should_stop = False
            for signal in stop_signals:
                if signal in text:
                    text = text.replace(signal, "")
                    should_stop = True
            
            if text:
                yield text
            
            if should_stop:
                break

        # 스트림 종료 후 토큰 사용량 메타데이터 전송
        if last_chunk:
            usage_metadata = {
                "prompt_tokens": last_chunk.prompt_tokens,
                "generation_tokens": last_chunk.generation_tokens,
                "total_tokens": last_chunk.prompt_tokens + last_chunk.generation_tokens
            }
            # 프론트엔드에서 구분할 수 있도록 특수 태그 사용
            yield f"[METADATA]{json.dumps(usage_metadata)}"

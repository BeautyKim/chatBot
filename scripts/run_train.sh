#!/bin/bash

# 에러 발생 시 즉시 중단 (어느 단계든 실패하면 뒤로 넘어가지 않음)
set -e

echo "========================================"
echo "📊 0단계: 데이터 준비 및 믹싱을 시작합니다..."
echo "========================================"

# 사내 CSV 데이터와 코알파카 데이터를 섞어 train.jsonl을 새로 굽습니다.
python scripts/mix_data.py

echo ""
echo "========================================"
echo "🚀 1단계: MLX 파인튜닝(학습)을 시작합니다..."
echo "========================================"

# [Tip] 만약 이어서 학습하고 싶다면 rm -rf 명령어를 주석 처리하고,
# 아래 mlx_lm.lora 명령어에 --resume-adapter-file ./adapters/adapters.safetensors 옵션을 추가하세요.

rm -rf ./adapters
mkdir -p ./adapters

mlx_lm.lora \
    --model ./Bllossom-3B \
    --train \
    --data ./data \
    --iters 1000 \
    --batch-size 1 \
    --num-layers 4
    # --resume-adapter-file ./adapters/adapters.safetensors

echo "✅ 1단계 완료! adapters 폴더가 생성되었습니다."
echo ""
echo "========================================"
echo "📦 2단계: 모델 병합(Fuse)을 시작합니다..."
echo "========================================"

mlx_lm.fuse \
    --model ./Bllossom-3B \
    --adapter-path ./adapters \
    --save-path ./my-custom-bllossom

echo "========================================"
echo "🎉 데이터 전처리부터 빌드까지 모든 과정이 완료되었습니다!"
echo "이제 'my-custom-bllossom' 폴더를 서버에 배포할 수 있습니다."
echo "========================================"
import csv
import json
import random
import os
import shutil
import logging
from typing import List, Dict
from datasets import load_dataset

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_koalpaca_data(sample_size: int = 500) -> List[Dict]:
    """KoAlpaca 데이터셋을 로드하고 변환합니다."""
    logger.info(f"📥 KoAlpaca 데이터셋을 다운로드 중... (샘플 크기: {sample_size})")
    try:
        dataset = load_dataset("beomi/KoAlpaca-v1.1a", split="train")
        sampled = dataset.shuffle(seed=42).select(range(min(sample_size, len(dataset))))
        
        return [
            {
                "messages": [
                    {"role": "user", "content": item['instruction']},
                    {"role": "assistant", "content": item['output']}
                ]
            }
            for item in sampled
        ]
    except Exception as e:
        logger.error(f"KoAlpaca 로드 실패: {e}")
        return []

def load_local_csv(file_path: str, oversample: int = 20) -> List[Dict]:
    """로컬 CSV 파일을 로드하고 오버샘플링합니다."""
    if not os.path.exists(file_path):
        logger.warning(f"⚠️ {file_path} 파일이 존재하지 않습니다. 건너뜁니다.")
        return []

    logger.info(f"🏢 사내 데이터({file_path})를 병합 중... (오버샘플링: {oversample}배)")
    combined = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                conversation = {
                    "messages": [
                        {"role": "user", "content": row['question']},
                        {"role": "assistant", "content": row['answer']}
                    ]
                }
                for _ in range(oversample):
                    combined.append(conversation)
        return combined
    except Exception as e:
        logger.error(f"CSV 로드 실패: {e}")
        return []

def save_jsonl(data: List[Dict], output_path: str):
    """데이터를 JSONL 형식으로 저장합니다."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, mode='w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        logger.info(f"💾 {output_path} 저장 완료.")
    except Exception as e:
        logger.error(f"파일 저장 실패: {e}")

def main():
    # 설정
    KOALPACA_SAMPLE_SIZE = 500
    LOCAL_DATA_PATH = 'qa_data.csv'
    TRAIN_OUTPUT = 'data/train.jsonl'
    VALID_OUTPUT = 'data/valid.jsonl'

    # 1. 데이터 로드
    koalpaca_data = load_koalpaca_data(KOALPACA_SAMPLE_SIZE)
    local_data = load_local_csv(LOCAL_DATA_PATH)

    # 2. 병합 및 믹싱
    combined_data = koalpaca_data + local_data
    random.shuffle(combined_data)

    if not combined_data:
        logger.error("❌ 생성할 데이터가 없습니다.")
        return

    # 3. 저장
    save_jsonl(combined_data, TRAIN_OUTPUT)
    
    # 검증용 파일 생성 (필요 시 로직 분리 가능)
    shutil.copyfile(TRAIN_OUTPUT, VALID_OUTPUT)
    
    logger.info(f"✅ 모든 작업 완료! 총 {len(combined_data)}개의 데이터가 준비되었습니다.")

if __name__ == "__main__":
    main()
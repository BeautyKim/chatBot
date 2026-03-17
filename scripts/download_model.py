from huggingface_hub import snapshot_download

print("모델 다운로드를 시작합니다...")
snapshot_download(
    repo_id="Bllossom/llama-3.2-Korean-Bllossom-3B",
    local_dir="./Bllossom-3B"
)
print("다운로드 완료!")
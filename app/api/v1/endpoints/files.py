"""
[app/api/v1/endpoints/files.py]
RAG용 파일을 업로드하고 관리하는 엔드포인트입니다.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import shutil
from app.services.rag_service import rag_service

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    여러 파일을 업로드하고 RAG 인덱스에 순차적으로 추가합니다.
    """
    results = []
    for file in files:
        if not file.filename:
            continue
            
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            # 파일 저장
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # RAG 인덱싱 추가
            success = rag_service.add_file_to_index(file_path)
            results.append({"filename": file.filename, "status": "success" if success else "failed"})
        except Exception as e:
            results.append({"filename": file.filename, "status": f"error: {str(e)}"})

    return {"message": "Processing complete", "details": results}

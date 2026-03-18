"""
[app/services/rag_service.py]
프로젝트 내부 데이터(qa_data.csv)를 기반으로 벡터 검색(RAG)을 수행합니다.
FAISS 라이브러리와 Sentence-Transformers를 활용하여 고성능 검색 기능을 제공합니다.
"""

import os
import pandas as pd
import logging
import warnings
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Python 3.14+ 및 LangChain 지원을 위한 경고 무시
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_core")

logger = logging.getLogger("rag_service")

class RAGService:
    def __init__(self):
        # 최신 패키지인 langchain-huggingface 사용
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.vector_store = None

    def add_file_to_index(self, file_path: str):
        """
        다양한 형식의 파일을 읽어 벡터 인덱스에 추가합니다.
        """
        try:
            ext = os.path.splitext(file_path)[-1].lower()
            if ext == ".pdf":
                loader = PyPDFLoader(file_path)
            elif ext == ".csv":
                loader = CSVLoader(file_path)
            elif ext == ".txt":
                loader = TextLoader(file_path)
            else:
                logger.warning(f"⚠️ 지원하지 않는 파일 형식입니다: {ext}")
                return False

            docs = loader.load()
            splits = self.text_splitter.split_documents(docs)
            
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(splits, self.embeddings)
            else:
                self.vector_store.add_documents(splits)
            
            logger.info(f"✅ 파일 인덱싱 완료: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 파일 인덱싱 중 오류 발생: {e}")
            return False

    def query_internal(self, query: str, k: int = 3) -> str:
        """
        내부 데이터에서 질문과 가장 관련 있는 내용을 검색합니다.
        """
        if not self.vector_store:
            return ""

        try:
            # 유사도 검색 수행
            docs = self.vector_store.similarity_search(query, k=k)
            context = "\n---\n".join([doc.page_content for doc in docs])
            return context
        except Exception as e:
            logger.error(f"❌ RAG 검색 중 오류 발생: {e}")
            return ""

# 싱글톤으로 인스턴스 제공
rag_service = RAGService()

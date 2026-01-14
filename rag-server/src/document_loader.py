import os
from pathlib import Path
from typing import List
from langchain.schema import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredExcelLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import Config

class DocumentProcessor:
    """범용 문서 로더 및 청킹 프로세서"""
    
    # 지원 파일 형식 매핑
    LOADERS = {
        '.pdf': PyPDFLoader,
        '.docx': Docx2txtLoader,
        '.doc': Docx2txtLoader,
        '.txt': TextLoader,
        '.xlsx': UnstructuredExcelLoader,
        '.xls': UnstructuredExcelLoader,
    }
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", ".", " ", ""],  # 한국어 우선 구분자
            length_function=len,
        )
    
    def load_document(self, file_path: str) -> List[Document]:
        """단일 문서 로딩"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext not in self.LOADERS:
            raise ValueError(f"지원하지 않는 파일 형식: {ext}")
        
        loader_class = self.LOADERS[ext]
        loader = loader_class(file_path)
        
        print(f"[파일] 로딩 중: {path.name}")
        documents = loader.load()
        
        # 메타데이터 추가
        for doc in documents:
            doc.metadata.update({
                'source_file': path.name,
                'file_type': ext,
                'file_path': str(path.absolute())
            })
        
        return documents
    
    def load_directory(self, directory: str) -> List[Document]:
        """디렉토리 내 모든 지원 문서 로딩"""
        all_documents = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            print(f"[경고] 디렉토리가 존재하지 않습니다: {directory}")
            return all_documents
        
        for file_path in dir_path.rglob('*'):
            if file_path.suffix.lower() in self.LOADERS:
                try:
                    docs = self.load_document(str(file_path))
                    all_documents.extend(docs)
                except Exception as e:
                    print(f"[오류] 파일 로딩 실패 ({file_path.name}): {e}")
        
        print(f"[완료] 총 {len(all_documents)}개 문서 로딩 완료")
        return all_documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """문서를 청크로 분할"""
        print(f"[처리] 문서 청킹 중 (chunk_size={Config.CHUNK_SIZE}, overlap={Config.CHUNK_OVERLAP})")
        chunks = self.text_splitter.split_documents(documents)
        print(f"[완료] {len(chunks)}개 청크 생성 완료")
        return chunks

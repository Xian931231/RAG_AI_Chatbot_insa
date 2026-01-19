from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from src.config import Config
from src.embeddings import EmbeddingService

class VectorStoreManager:
    """ChromaDB 벡터 스토어 관리자"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store: Optional[Chroma] = None
        self._initialize_store()
    
    def _initialize_store(self):
        """벡터 스토어 초기화 (기존 DB 로드 또는 신규 생성)"""
        print(f"[DB] ChromaDB 초기화 중: {Config.CHROMA_DB_PATH}")
        self.vector_store = Chroma(
            collection_name=Config.COLLECTION_NAME,
            embedding_function=self.embedding_service.get_embeddings(),
            persist_directory=Config.CHROMA_DB_PATH
        )
        
        # 기존 문서 수 확인
        try:
            count = self.vector_store._collection.count()
            print(f"[완료] ChromaDB 로딩 완료 (저장된 문서: {count}개)")
        except:
            print("[완료] ChromaDB 초기화 완료 (신규)")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """문서를 벡터 스토어에 추가"""
        if not documents:
            print("[경고] 추가할 문서가 없습니다.")
            return []
        
        print(f"[저장] {len(documents)}개 문서를 벡터 스토어에 저장 중...")
        ids = self.vector_store.add_documents(documents)
        print(f"[완료] 저장 완료 (IDs: {len(ids)}개)")
        return ids
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """유사도 검색"""
        k = k or Config.TOP_K_RESULTS
        results = self.vector_store.similarity_search(query, k=k)
        print(f"[검색] 검색 완료: {len(results)}개 관련 문서 발견")
        return results
    
    def clear_database(self):
        """벡터 스토어 초기화 (모든 문서 삭제)"""
        print("[초기화] 벡터 스토어 초기화 중...")
        self.vector_store.delete_collection()
        self._initialize_store()
        print("[완료] 초기화 완료")
    
    def get_stats(self) -> dict:
        """벡터 스토어 통계"""
        try:
            count = self.vector_store._collection.count()
            return {
                "total_documents": count,
                "collection_name": Config.COLLECTION_NAME,
                "embedding_model": Config.EMBEDDING_MODEL
            }
        except Exception as e:
            return {"error": str(e)}

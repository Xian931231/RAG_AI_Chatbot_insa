"""문서 수집 및 벡터 DB 저장 스크립트"""

import sys
from pathlib import Path
from src.document_loader import DocumentProcessor
from src.vector_store import VectorStoreManager
from src.config import Config

def ingest_documents(directory: str = "./documents", clear_existing: bool = False):
    """문서를 로딩하고 벡터 스토어에 저장"""
    
    print("=" * 60)
    print("[수집] 문서 수집 시작")
    print("=" * 60)
    
    # 초기화
    processor = DocumentProcessor()
    vector_store = VectorStoreManager()
    
    # 기존 DB 초기화 (옵션)
    if clear_existing:
        vector_store.clear_database()
    
    # 문서 로딩
    documents = processor.load_directory(directory)
    
    if not documents:
        print("[오류] 로딩된 문서가 없습니다.")
        print(f"[안내] {directory} 폴더에 PDF, DOCX, TXT 파일을 추가하세요.")
        return
    
    # 문서 청킹
    chunks = processor.split_documents(documents)
    
    # 벡터 스토어에 저장
    vector_store.add_documents(chunks)
    
    # 통계 출력
    stats = vector_store.get_stats()
    print("\n" + "=" * 60)
    print("[통계] 수집 완료 통계:")
    print(f"   - 총 문서 수: {stats.get('total_documents', 0)}개")
    print(f"   - 컬렉션: {stats.get('collection_name', 'N/A')}")
    print(f"   - 임베딩 모델: {stats.get('embedding_model', 'N/A')}")
    print("=" * 60)

if __name__ == "__main__":
    # 명령줄 인자 처리
    doc_dir = sys.argv[1] if len(sys.argv) > 1 else "./documents"
    clear = "--clear" in sys.argv
    
    Config.validate()
    ingest_documents(doc_dir, clear_existing=clear)

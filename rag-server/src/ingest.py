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
    
    try:
        # 초기화
        print("[1/4] 프로세서 초기화 중...")
        processor = DocumentProcessor()
        
        print("[2/4] 벡터 스토어 초기화 중...")
        vector_store = VectorStoreManager()
        
        # 기존 DB 초기화 (옵션)
        if clear_existing:
            vector_store.clear_database()
        
        # 문서 로딩
        print(f"[3/4] 문서 로딩 중 (경로: {directory})...")
        documents = processor.load_directory(directory)
        
        if not documents:
            print("[오류] 로딩된 문서가 없습니다.")
            print(f"[안내] {directory} 폴더에 PDF, DOCX, TXT 파일을 추가하세요.")
            return
        
        print(f"[성공] {len(documents)}개 문서 로딩 완료")
        
        # 문서 청킹
        print("[4/4] 문서 청킹 중...")
        chunks = processor.split_documents(documents)
        print(f"[성공] {len(chunks)}개 청크 생성 완료")
        
        # 벡터 스토어에 저장
        print("[저장] 벡터 스토어에 저장 중...")
        vector_store.add_documents(chunks)
        
        # 통계 출력
        stats = vector_store.get_stats()
        print("\n" + "=" * 60)
        print("[통계] 수집 완료 통계:")
        print(f"   - 총 문서 수: {stats.get('total_documents', 0)}개")
        print(f"   - 컬렉션: {stats.get('collection_name', 'N/A')}")
        print(f"   - 임베딩 모델: {stats.get('embedding_model', 'N/A')}")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n[오류] 수집 중 오류 발생:")
        print(f"   오류 타입: {type(e).__name__}")
        print(f"   오류 메시지: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 명령줄 인자 처리
    doc_dir = sys.argv[1] if len(sys.argv) > 1 else "./documents"
    clear = "--clear" in sys.argv
    
    Config.validate()
    ingest_documents(doc_dir, clear_existing=clear)

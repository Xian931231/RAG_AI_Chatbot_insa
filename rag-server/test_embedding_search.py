"""임베딩 기반 검색 테스트"""
from src.embeddings import EmbeddingService
from langchain_community.vectorstores import Chroma

# 임베딩 서비스 초기화
embedding_service = EmbeddingService()

# ChromaDB 로드
vector_store = Chroma(
    collection_name="company_documents",
    embedding_function=embedding_service.get_embeddings(),
    persist_directory="./chroma_db"
)

# 다양한 쿼리로 검색 테스트
test_queries = [
    "출근율",
    "출근율 계산",
    "출근율 산식",
    "출근율 공식",
    "1년간 출근일수",
    "소정근로일수",
    "연차유급휴가 출근율"
]

print("=" * 80)
print("임베딩 검색 테스트")
print("=" * 80)

for query in test_queries:
    print(f"\n\n[질의] '{query}'")
    print("-" * 80)
    
    # 상위 3개 결과 검색
    results = vector_store.similarity_search_with_score(query, k=3)
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n[결과 {i}] 유사도 점수: {score:.4f}")
        print(f"파일: {doc.metadata.get('source_file', 'Unknown')}")
        
        # 내용 미리보기 (첫 150자)
        content_preview = doc.page_content[:150].replace('\n', ' ')
        print(f"내용: {content_preview}...")
        
        # 출근율 산식이 포함되어 있는지 확인
        if "출근율" in doc.page_content and "산식" in doc.page_content:
            print("[★] 이 청크에 출근율 산식이 포함되어 있습니다!")

"""ChromaDB에 저장된 문서 청크를 분석하는 스크립트"""

from src.vector_store import VectorStoreManager
from src.config import Config

Config.validate()

# 벡터 스토어 로드
vector_store = VectorStoreManager()

# 출근율 관련 검색
test_queries = [
    "출근율",
    "출근율 계산",
    "출근율 산식",
    "1년간 출근일수"
]

print("=" * 80)
print("출근율 관련 검색 테스트")
print("=" * 80)

for query in test_queries:
    print(f"\n[질의] {query}")
    print("-" * 80)
    results = vector_store.similarity_search(query, k=5)
    
    for i, doc in enumerate(results, 1):
        print(f"\n[결과 {i}]")
        print(f"파일: {doc.metadata.get('source_file', 'Unknown')}")
        print(f"내용: {doc.page_content[:300]}...")
        print()

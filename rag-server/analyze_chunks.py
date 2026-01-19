"""ChromaDB에 저장된 청크 직접 분석"""
import chromadb
import os
from dotenv import load_dotenv

# 루트 .env 파일 로드
load_dotenv('../.env')

# ChromaDB 클라이언트 생성
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="company_documents")

# 모든 문서 가져오기
results = collection.get(include=['documents', 'metadatas'])

print(f"총 청크 수: {len(results['documents'])}")
print("=" * 80)

# 출근율 키워드가 포함된 청크 찾기
search_keywords = ["출근율", "산식", "소정근로일수"]

for keyword in search_keywords:
    print(f"\n키워드 '{keyword}' 포함 청크:")
    print("-" * 80)
    found = 0
    for i, doc in enumerate(results['documents']):
        if keyword in doc:
            found += 1
            print(f"\n[청크 {i+1}]")
            print(f"파일: {results['metadatas'][i].get('source_file', 'Unknown')}")
            print(f"길이: {len(doc)} 글자")
            print(f"내용:\n{doc}")
            print("-" * 80)
    
    print(f"'{keyword}' 발견 개수: {found}")

"""ChromaDB 상태 확인"""
import chromadb

# ChromaDB 클라이언트 생성
client = chromadb.PersistentClient(path="./chroma_db")

# 모든 컬렉션 나열
collections = client.list_collections()
print(f"총 컬렉션 수: {len(collections)}")

if collections:
    for coll in collections:
        print(f"\n컬렉션 이름: {coll.name}")
        print(f"문서 수: {coll.count()}")
else:
    print("컬렉션이 존재하지 않습니다.")
    print("\n[조치] 문서를 다시 수집해야 합니다:")
    print("python -m src.ingest")

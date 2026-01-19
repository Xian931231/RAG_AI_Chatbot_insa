"""빠른 문서 수집 스크립트"""
import sys
sys.path.append('.')

from pathlib import Path
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

print("[1/5] 설정 로딩...")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "jhgan/ko-sroberta-multitask"
DB_PATH = "./chroma_db"
COLLECTION_NAME = "company_documents"

print("[2/5] 문서 로딩...")
doc_path = "./documents/20220214_취업규칙_딜라이브.docx"
loader = Docx2txtLoader(doc_path)
documents = loader.load()
print(f"   로딩된 문서: {len(documents)}개")

print("[3/5] 청킹...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", "。", ".", " ", ""]
)
chunks = text_splitter.split_documents(documents)
print(f"   생성된 청크: {len(chunks)}개")

# 각 청크에 메타데이터 추가
for chunk in chunks:
    chunk.metadata['source_file'] = Path(doc_path).name

print("[4/5] 임베딩 모델 로딩...")
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

print("[5/5] ChromaDB 저장...")
# 배치 단위로 저장
BATCH_SIZE = 10
total_saved = 0

# 첫 번째 배치로 벡터 스토어 생성
first_batch = chunks[:BATCH_SIZE]
vector_store = Chroma.from_documents(
    documents=first_batch,
    embedding=embeddings,
    persist_directory=DB_PATH,
    collection_name=COLLECTION_NAME
)
total_saved += len(first_batch)
print(f"   진행: {total_saved}/{len(chunks)} 청크...")

# 나머지 배치 추가
for i in range(BATCH_SIZE, len(chunks), BATCH_SIZE):
    batch = chunks[i:i+BATCH_SIZE]
    vector_store.add_documents(batch)
    total_saved += len(batch)
    print(f"   진행: {total_saved}/{len(chunks)} 청크...")

print(f"\n[완료] {len(chunks)}개 청크가 ChromaDB에 저장되었습니다.")
print(f"   컬렉션: {COLLECTION_NAME}")
print(f"   경로: {DB_PATH}")

# 검증
collection = vector_store._collection
count = collection.count()
print(f"\n[검증] 저장된 문서 수: {count}개")

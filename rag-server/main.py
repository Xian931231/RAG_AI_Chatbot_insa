from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

from src.config import Config
from src.rag_service import RAGService
from src.document_loader import DocumentProcessor
from src.vector_store import VectorStoreManager

# FastAPI 앱 초기화
app = FastAPI(
    title="RAG Server",
    description="회사 문서 기반 RAG 시스템",
    version="1.0.0"
)

# CORS 설정 (Node.js 서버에서 호출 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 서비스 인스턴스
rag_service: Optional[RAGService] = None

# Request/Response 모델
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict]

class IngestRequest(BaseModel):
    directory: str = "./documents"
    clear_existing: bool = False

class StatusResponse(BaseModel):
    status: str
    total_documents: int
    embedding_model: str
    llm_model: str

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 RAG 서비스 초기화"""
    global rag_service
    try:
        Config.validate()
        print("\n[시작] RAG 서버 시작 중...")
        rag_service = RAGService()
        print("[완료] RAG 서비스 초기화 완료\n")
    except Exception as e:
        print(f"[오류] 초기화 실패: {e}")
        raise

@app.get("/", response_model=StatusResponse)
async def root():
    """서버 상태 확인"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG 서비스가 초기화되지 않았습니다.")
    
    stats = rag_service.vector_store.get_stats()
    return {
        "status": "ok",
        "total_documents": stats.get("total_documents", 0),
        "embedding_model": Config.EMBEDDING_MODEL,
        "llm_model": Config.OPENAI_MODEL
    }

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """RAG 질의 처리"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG 서비스가 초기화되지 않았습니다.")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="질문이 비어있습니다.")
    
    try:
        result = rag_service.query(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG 처리 중 오류: {str(e)}")

@app.post("/ingest")
async def ingest_documents(request: IngestRequest):
    """문서 수집 및 벡터 DB 저장"""
    try:
        processor = DocumentProcessor()
        vector_store = VectorStoreManager()
        
        if request.clear_existing:
            vector_store.clear_database()
        
        documents = processor.load_directory(request.directory)
        if not documents:
            raise HTTPException(
                status_code=404, 
                detail=f"{request.directory}에서 문서를 찾을 수 없습니다."
            )
        
        chunks = processor.split_documents(documents)
        vector_store.add_documents(chunks)
        
        stats = vector_store.get_stats()
        return {
            "status": "success",
            "message": f"{len(chunks)}개 청크를 벡터 DB에 저장했습니다.",
            "total_documents": stats.get("total_documents", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 수집 실패: {str(e)}")

@app.get("/stats")
async def get_stats():
    """벡터 스토어 통계"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG 서비스가 초기화되지 않았습니다.")
    
    return rag_service.vector_store.get_stats()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=Config.PORT,
        reload=True
    )

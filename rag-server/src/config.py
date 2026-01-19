import os
from pathlib import Path
from dotenv import load_dotenv

# 루트 디렉토리의 .env 파일 로드
root_dir = Path(__file__).parent.parent.parent
env_path = root_dir / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # OpenAI 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # 임베딩 모델 (한국어 최적화)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "jhgan/ko-sroberta-multitask")
    
    # ChromaDB 설정
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    COLLECTION_NAME = "company_documents"
    
    # 문서 처리 설정
    CHUNK_SIZE = 500  # 한국어는 토큰 밀도가 높아서 작게
    CHUNK_OVERLAP = 50
    
    # 검색 설정
    TOP_K_RESULTS = 5  # 3 → 5로 증가
    
    # 서버 설정
    PORT = int(os.getenv("RAG_PORT", os.getenv("PORT", 8000)))
    
    @staticmethod
    def validate():
        if not Config.OPENAI_API_KEY:
            raise ValueError("[경고] OPENAI_API_KEY가 설정되지 않았습니다.")

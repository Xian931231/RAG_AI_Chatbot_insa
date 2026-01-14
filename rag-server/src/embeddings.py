from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config import Config

class EmbeddingService:
    """한국어 문서용 임베딩 서비스"""
    
    def __init__(self):
        print(f"[로딩] 임베딩 모델 로딩 중: {Config.EMBEDDING_MODEL}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("[완료] 임베딩 모델 로딩 완료")
    
    def get_embeddings(self):
        return self.embeddings

from typing import List, Dict
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.config import Config
from src.vector_store import VectorStoreManager

class RAGService:
    """RAG 검색 및 응답 생성 서비스"""
    
    PROMPT_TEMPLATE = """당신은 회사 문서를 기반으로 답변하는 AI 어시스턴트입니다.
아래 제공된 문서 내용을 참고하여 사용자의 질문에 답변하세요.

**중요 지침:**
- 제공된 문서에 있는 정보만 사용하여 답변하세요.
- 문서에 없는 내용은 "제공된 문서에서 관련 정보를 찾을 수 없습니다"라고 답변하세요.
- 답변은 간결하고 명확하게 작성하세요.
- 가능하면 출처 문서명을 언급하세요.

**참고 문서:**
{context}

**질문:** {question}

**답변:**"""
    
    def __init__(self):
        Config.validate()
        self.vector_store = VectorStoreManager()
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=0.3,
            api_key=Config.OPENAI_API_KEY
        )
        self.prompt = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)
        print(f"[RAG] RAG 서비스 초기화 완료 (모델: {Config.OPENAI_MODEL})")
    
    def _format_documents(self, docs: List[Document]) -> str:
        """검색된 문서를 프롬프트용 텍스트로 포맷팅"""
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source_file', 'Unknown')
            content = doc.page_content.strip()
            formatted.append(f"[문서 {i}: {source}]\n{content}\n")
        return "\n".join(formatted)
    
    def retrieve(self, query: str, k: int = None) -> List[Document]:
        """질문과 관련된 문서 검색"""
        return self.vector_store.similarity_search(query, k)
    
    def generate_answer(self, query: str, context_docs: List[Document]) -> Dict:
        """검색된 문서를 기반으로 답변 생성"""
        context = self._format_documents(context_docs)
        
        # 프롬프트 생성 및 LLM 호출
        messages = self.prompt.format_messages(
            context=context,
            question=query
        )
        
        print(f"[GPT] GPT 호출 중... (질문: {query[:50]}...)")
        response = self.llm.invoke(messages)
        
        return {
            "answer": response.content,
            "sources": [
                {
                    "file": doc.metadata.get('source_file', 'Unknown'),
                    "content": doc.page_content[:200] + "..."
                }
                for doc in context_docs
            ]
        }
    
    def query(self, question: str) -> Dict:
        """RAG 전체 플로우 실행: 검색 + 답변 생성"""
        print(f"\n[질의] RAG 질의 시작: {question}")
        
        # 1. 관련 문서 검색
        relevant_docs = self.retrieve(question)
        
        if not relevant_docs:
            return {
                "answer": "죄송합니다. 질문과 관련된 문서를 찾을 수 없습니다.",
                "sources": []
            }
        
        # 2. 답변 생성
        result = self.generate_answer(question, relevant_docs)
        print("[완료] RAG 답변 생성 완료\n")
        
        return result

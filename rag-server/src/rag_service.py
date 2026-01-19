from typing import List, Dict
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
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
        """질문과 관련된 문서 검색 (하이브리드: 키워드 + 임베딩)"""
        if k is None:
            k = Config.TOP_K_RESULTS
        
        # 임베딩 기반 검색
        semantic_results = self.vector_store.similarity_search(query, k)
        
        # 키워드 기반 재순위화
        # 질문에 포함된 주요 키워드가 많이 포함된 문서를 우선
        keywords = self._extract_keywords(query)
        print(f"[키워드] 추출된 키워드: {keywords}")
        
        # 각 문서에 키워드 매칭 점수 부여
        scored_docs = []
        for i, doc in enumerate(semantic_results, 1):
            keyword_score = sum(1 for kw in keywords if kw in doc.page_content)
            scored_docs.append((doc, keyword_score))
            
            # 검색된 청크 내용 출력
            print(f"\n[검색 {i}] 키워드 매칭: {keyword_score}개")
            print(f"   파일: {doc.metadata.get('source_file', 'Unknown')}")
            print(f"   내용 미리보기: {doc.page_content[:150]}...")
        
        # 키워드 매칭 점수가 높은 순으로 재정렬
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n[재정렬] 키워드 매칭 점수 기준으로 재정렬 완료")
        
        return [doc for doc, score in scored_docs]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """질문에서 주요 키워드 추출"""
        # 불용어 제거 및 의미있는 키워드만 추출
        stop_words = {'은', '는', '이', '가', '을', '를', '의', '에', '에서', '로', '으로', 
                      '와', '과', '하고', '하는', '어떻게', '어떤', '무엇', '뭐', '알려줘', '알려주세요'}
        words = query.split()
        keywords = [w for w in words if len(w) > 1 and w not in stop_words]
        return keywords
    
    def generate_answer(self, query: str, context_docs: List[Document], history: List[Dict] = None) -> Dict:
        """검색된 문서를 기반으로 답변 생성"""
        context = self._format_documents(context_docs)
        
        # 대화 히스토리가 있는 경우 메시지 직접 구성
        if history and len(history) > 0:
            messages = []
            # 시스템 프롬프트
            messages.append({
                "role": "system",
                "content": "당신은 회사 문서를 기반으로 답변하는 AI 어시스턴트입니다. 제공된 문서 내용을 참고하여 사용자의 질문에 답변하세요."
            })
            
            # 이전 대화 히스토리 추가 (마지막 메시지 제외)
            for msg in history[:-1]:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # 현재 질문과 문서 컨텍스트
            current_prompt = f"""**참고 문서:**
{context}

**질문:** {query}

**답변:**"""
            messages.append({
                "role": "user",
                "content": current_prompt
            })
            
            print(f"[GPT] GPT 호출 중... (질문: {query[:50]}..., 히스토리: {len(history)}개, 총 메시지: {len(messages)}개)")
        else:
            # 히스토리 없는 경우 기존 방식
            messages = self.prompt.format_messages(
                context=context,
                question=query
            )
            print(f"[GPT] GPT 호출 중... (질문: {query[:50]}...)")
        
        response = self.llm.invoke(messages)
        
        # 고유한 파일명만 추출 (중복 제거)
        unique_sources = {}
        for doc in context_docs:
            file_name = doc.metadata.get('source_file', 'Unknown')
            if file_name not in unique_sources:
                unique_sources[file_name] = doc.page_content[:200] + "..."
        
        return {
            "answer": response.content,
            "sources": [
                {"file": file_name, "content": content}
                for file_name, content in unique_sources.items()
            ]
        }
    
    def query(self, question: str, history: List[Dict] = None) -> Dict:
        """RAG 전체 플로우 실행: 검색 + 답변 생성"""
        print(f"\n{'='*80}")
        print(f"[질의] RAG 질의 시작: {question}")
        if history:
            print(f"[히스토리] 이전 대화: {len(history)}개")
        print(f"{'='*80}")
        
        # 1. 관련 문서 검색
        relevant_docs = self.retrieve(question)
        
        if not relevant_docs:
            return {
                "answer": "죄송합니다. 질문과 관련된 문서를 찾을 수 없습니다.",
                "sources": []
            }
        
        # 검색된 최종 문서들 출력
        print(f"\n{'='*80}")
        print(f"[최종 선택] GPT에 전달될 청크 {len(relevant_docs)}개:")
        print(f"{'='*80}")
        for i, doc in enumerate(relevant_docs, 1):
            print(f"\n[청크 {i}]")
            print(f"파일: {doc.metadata.get('source_file', 'Unknown')}")
            print(f"내용:\n{doc.page_content[:300]}...")
            print(f"{'-'*80}")
        
        # 2. 답변 생성 (대화 히스토리 포함)
        result = self.generate_answer(question, relevant_docs, history)
        print(f"\n[완료] RAG 답변 생성 완료\n")
        
        return result

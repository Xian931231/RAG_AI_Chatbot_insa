# RAG Server - 회사 문서 기반 질의응답 시스템

## 개요
한국어 회사 문서를 기반으로 질문에 답변하는 RAG (Retrieval-Augmented Generation) 서버입니다.

## 기술 스택
- **LLM**: OpenAI GPT-4o-mini
- **임베딩**: jhgan/ko-sroberta-multitask (한국어 최적화)
- **벡터 DB**: ChromaDB
- **프레임워크**: LangChain + FastAPI

## 설치

### 1. Python 가상환경 생성
```bash
cd rag-server
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env.example`을 `.env`로 복사하고 OpenAI API 키 입력:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

## 사용 방법

### 1단계: 문서 수집
`documents/` 폴더에 PDF, DOCX, TXT 파일을 추가한 후:

```bash
# 방법 1: 스크립트로 수집
python -m src.ingest

# 방법 2: API 서버 실행 후 POST 요청
python main.py
# 다른 터미널에서:
curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d '{"directory": "./documents"}'
```

### 2단계: RAG 서버 실행
```bash
python main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 3단계: 질의하기

#### API로 테스트
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "회사의 복지 제도는 무엇인가요?"}'
```

#### Node.js 서버에서 호출 (통합 후)
```javascript
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: userMessage })
});
const result = await response.json();
console.log(result.answer, result.sources);
```

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 서버 상태 확인 |
| POST | `/query` | RAG 질의 |
| POST | `/ingest` | 문서 수집 |
| GET | `/stats` | 벡터 DB 통계 |

## 지원 파일 형식
- PDF (`.pdf`)
- Word (`.docx`, `.doc`)
- Text (`.txt`)
- Excel (`.xlsx`, `.xls`)

## 디렉토리 구조
```
rag-server/
├── main.py                 # FastAPI 서버
├── requirements.txt        # 의존성
├── .env                    # 환경 변수 (생성 필요)
├── documents/              # 원본 문서 폴더 (생성 필요)
├── chroma_db/              # 벡터 DB (자동 생성)
└── src/
    ├── config.py           # 설정
    ├── embeddings.py       # 임베딩 서비스
    ├── document_loader.py  # 문서 로더
    ├── vector_store.py     # ChromaDB 관리
    ├── rag_service.py      # RAG 로직
    └── ingest.py           # 문서 수집 스크립트
```

## 설정 커스터마이징 (config.py)
- `CHUNK_SIZE`: 문서 청크 크기 (기본: 500)
- `TOP_K_RESULTS`: 검색할 문서 개수 (기본: 3)
- `OPENAI_MODEL`: 사용할 GPT 모델 (기본: gpt-4o-mini)
- `EMBEDDING_MODEL`: 임베딩 모델 (기본: jhgan/ko-sroberta-multitask)

## 문제 해결

### 임베딩 모델 로딩 느림
첫 실행 시 Hugging Face에서 모델 다운로드 (1-2분 소요). 이후 캐시 사용.

### ChromaDB 오류
```bash
rm -rf chroma_db  # DB 초기화
python -m src.ingest --clear  # 재수집
```

### OpenAI API 오류
`.env` 파일에 유효한 API 키가 있는지 확인.

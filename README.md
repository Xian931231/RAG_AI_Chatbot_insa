# DliveInsaBot - RAG 기반 인사규정 챗봇

React + Socket.io + FastAPI + OpenAI GPT-4o-mini를 이용한 실시간 RAG 채팅 시스템입니다.  
**RAG (Retrieval-Augmented Generation)** 기능으로 회사 인사규정 문서를 기반으로 정확한 답변을 제공합니다.

## 주요 기능

**핵심 기능**
- 실시간 AI 챗봇 (GPT-4o-mini)
- RAG 기반 문서 검색 및 답변 생성
- **멀티턴 대화 지원** - 이전 대화 맥락 이해
- **하이브리드 검색** - 임베딩 + 키워드 매칭
- 한국어 최적화 (임베딩: jhgan/ko-sroberta-multitask)
- 다양한 문서 형식 지원 (PDF, DOCX, TXT, Excel)
- 답변 출처 문서 표시

## 시스템 아키텍처

```
┌─────────────┐     WebSocket      ┌──────────────┐     HTTP/REST     ┌─────────────┐
│  Frontend   │ ←─────────────────→ │  Node.js     │ ←────────────────→ │  RAG Server │
│  (React)    │    Socket.IO       │  Gateway     │   POST /query     │  (FastAPI)  │
│  Port 5173  │                    │  Port 4000   │                   │  Port 8000  │
└─────────────┘                    └──────────────┘                   └──────┬──────┘
                                          │                                   │
                                          │ 대화 히스토리 관리                 │
                                          │ (conversationStore)              │
                                          │                          ┌───────┴────────┐
                                          │                          │   ChromaDB +   │
                                          └─────────────────────────→│   GPT-4o-mini  │
                                                                     └────────────────┘
```

## 기술 스택

| 계층 | 기술 | 버전 |
|------|------|------|
| Frontend | React + Vite + Socket.IO Client | 18.3.1 / 5.4.8 / 4.7.5 |
| Gateway | Node.js + Express + Socket.IO | 18+ / 4.19.2 / 4.7.5 |
| RAG Server | Python + FastAPI + LangChain | 3.13 / - / 1.2.6 |
| Vector DB | ChromaDB | 1.4.1 |
| Embedding | jhgan/ko-sroberta-multitask | 443MB |
| LLM | OpenAI GPT-4o-mini | - |

## 사전 준비

- Node.js 18 이상
- Python 3.8 이상
- OpenAI API 키

## 설치

### 1. Node.js 의존성 설치
```bash
# 서버
cd server
npm install

# 프론트엔드
cd ../frontend
npm install
```

### 2. Python 환경 설정 (RAG 서버)
```bash
cd rag-server

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 변수 설정

루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```bash
# OpenAI API 키 (필수)
OPENAI_API_KEY=sk-your_api_key_here

# Node.js 서버 설정
NODE_PORT=4000
USE_RAG=true                           # RAG 모드 활성화
RAG_SERVER_URL=http://localhost:8000

# Python RAG 서버 설정
RAG_PORT=8000
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=jhgan/ko-sroberta-multitask
CHROMA_DB_PATH=./chroma_db
```

## 실행 방법

### 전체 시스템 실행 (3개 서버 필요)

**1단계: 문서 추가 및 수집**
```bash
# 1. 문서 파일을 rag-server/documents/ 폴더에 추가
# 2. 문서를 벡터 DB에 저장
cd rag-server
python -m src.ingest
```

**2단계: 서버 실행 (3개 터미널)**
```bash
# 터미널 1 - RAG 서버 (Python)
cd rag-server
python main.py

# 터미널 2 - Node.js Gateway
cd server
npm run dev

# 터미널 3 - Frontend (React)
cd frontend
npm run dev
```

**3단계: 브라우저 접속**
- http://localhost:5173 열기
- "DliveInsaBot"과 대화 시작!

### 테스트 질문 예시

```
질문 1: "출산전후휴가가 어떻게 되는지 알려줘"
→ 봇이 문서를 검색하여 답변

질문 2: "더 자세하게 알려줘"
→ 이전 대화 맥락을 이해하고 답변 (멀티턴 대화)

질문 3: "육아휴직은 어떻게 되나요?"
→ 새로운 주제로 질문
```

## 프로젝트 구조

```
rag_ai_chatbot_insa/
├── .env                           # 환경 변수 (공통, git ignore)
├── .github/
│   └── copilot-instructions.md    # AI 코딩 가이드
├── frontend/                      # React 프론트엔드 (포트 5173)
│   ├── src/
│   │   ├── App.jsx               # 메인 UI (DliveInsaBot)
│   │   └── hooks/
│   │       └── useChat.js        # Socket.IO 통신 로직
│   └── vite.config.js
├── server/                        # Node.js Gateway (포트 4000)
│   └── src/
│       └── index.js              # Socket.IO 서버 + 대화 히스토리 관리
└── rag-server/                    # Python RAG 서버 (포트 8000)
    ├── main.py                   # FastAPI 서버
    ├── requiremen및 통계
  ```json
  {
    "status": "ok",
    "total_documents": 288,
    "embedding_model": "jhgan/ko-sroberta-multitask",
    "llm_model": "gpt-4o-mini"
  }
  ```
- `POST /query` - RAG 질의 (멀티턴 대화 지원)
  ```json
  {
    "question": "출산전후휴가가 어떻게 되는지 알려줘",
    "history": [
      {"role": "user", "content": "이전 질문"},
      {"role": "assistant", "content": "이전 답변"}
    ]
  }
  ```
- `POST /ingest` - 문서 수집
- `GET /stats` - 벡터 DB 상세 통계

### Node.js Gateway (http://localhost:4000)
- Socket.IO 이벤트:
  - `userMessage` - 사용자 메시지 전송
  - `assistantMessage` - 봇 답변 수신
  - `conversationInit` - 대화 초기화
  - `serverError` - 오류 처리

## 문제 해결

### 1. RAG 서버 오류
```bash
# Python 가상환경 확인
cd rag-server
python --version  # 3.8 이상 확인

# 의존성 재설치
pip install -r requirements.txt --upgrade
```

### 2. 문서가 검색되지 않음
```bash
# ChromaDB 초기화 후 재수집
cd rag-server
python -m src.ingest --clear

# 저장된 청크 수 확인
# 브라우저에서 http://localhost:8000/ 접속하여 total_documents 확인
```

### 3. 멀티턴 대화가 작동하지 않음
- Node.js 서버와 RAG 서버가 모두 최신 코드로 실행 중인지 확인
- `.env` 파일에 `USE_RAG=true` 설정 확인
- Node.js 터미널과 RAG 서버 터미널에서 로그 확인

### 4. 포트 충돌
`.env` 파일에서 포트 변경:
```bash
NODE_PORT=4001
RAG_PORT=8001
```

### 5. 임베딩 모델 로딩 느림
- 첫 실행 시 443MB 모델 다운로드 (약 1-2분)
- 이후 실행은 캐시 사용으로 빠름

## 개발자 가이드

### 새로운 문서 형식 추가
`rag-server/src/document_loader.py`의 `load_directory()` 메서드에 로더 추가

### 청킹 전략 변경
`rag-server/src/config.py`에서 `CHUNK_SIZE`, `CHUNK_OVERLAP` 조정

### 검색 개수 조정
`rag-server/src/config.py`에서 `TOP_K_RESULTS` 변경

### 프롬프트 수정
`rag-server/src/rag_service.py`의 `PROMPT_TEMPLATE` 또는 `generate_answer()` 메서드 수정


## 멀티턴 대화 처리 방식

1. **Frontend**: 사용자 메시지 전송 (Socket.IO)
2. **Node.js Gateway**: 
   - 소켓별 대화 히스토리 저장 (`conversationStore`)
   - RAG 서버에 질문 + 히스토리 전달
3. **RAG Server**:
   - 문서 검색 (하이브리드: 임베딩 + 키워드)
   - GPT에 프롬프트 구성:
     ```
     시스템 프롬프트
     + 이전 user 메시지
     + 이전 assistant 메시지
     + 현재 참고 문서 + 질문
     ```
4. **응답 반환**: 전체 경로 역순으로 답변 전달

## API 엔드포인트

### RAG 서버 (http://localhost:8000)
- `GET /` - 서버 상태 확인
- `POST /query` - RAG 질의
- `POST /ingest` - 문서 수집
- `GET /stats` - 벡터 DB 통계

## 문제 해결

### RAG 서버 오류
- Python 가상환경이 활성화되어 있는지 확인
- `.env` 파일에 `OPENAI_API_KEY`가 설정되어 있는지 확인

### 문서가 검색되지 않음
```bash
# ChromaDB 초기화 후 재수집
cd rag-server
python -m src.ingest --clear
```

### 포트 충돌
`.env` 파일에서 `NODE_PORT`, `RAG_PORT` 값 변경


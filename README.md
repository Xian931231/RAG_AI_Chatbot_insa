## RAG AI 챗봇 (INSA)

React + Socket.io + OpenAI GPT-4o-mini를 이용한 실시간 채팅 앱입니다.  
**RAG (Retrieval-Augmented Generation)** 기능을 통해 회사 문서 기반 질의응답이 가능합니다.

## 주요 기능

- 실시간 AI 채팅 (GPT-4o-mini)
- RAG 기반 문서 검색 및 답변 생성
- 한국어 최적화 (임베딩 모델: jhgan/ko-sroberta-multitask)
- 다양한 문서 형식 지원 (PDF, DOCX, TXT, Excel)
- RAG 모드 On/Off 전환 가능

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
# OpenAI API 키
OPENAI_API_KEY=your_openai_api_key_here

# Node.js 서버 설정
NODE_PORT=4000
USE_RAG=false
RAG_SERVER_URL=http://localhost:8000

# Python RAG 서버 설정
RAG_PORT=8000
EMBEDDING_MODEL=jhgan/ko-sroberta-multitask
CHROMA_DB_PATH=./rag-server/chroma_db
```

## 실행

### 기본 모드 (RAG 없이 GPT만 사용)

```bash
# 터미널 1 - Node.js 서버
cd server
npm run dev

# 터미널 2 - 프론트엔드
cd frontend
npm run dev
```

브라우저에서 `http://localhost:5173` 접속

### RAG 모드 (문서 기반 질의응답)

#### 1단계: 문서 추가
`rag-server/documents/` 폴더에 PDF, DOCX, TXT, Excel 파일을 추가합니다.

#### 2단계: 문서 수집 (벡터 DB에 저장)
```bash
cd rag-server
python -m src.ingest
```

#### 3단계: RAG 서버 실행
```bash
# 터미널 1 - RAG 서버
cd rag-server
python main.py

# 터미널 2 - Node.js 서버
cd server
npm run dev

# 터미널 3 - 프론트엔드
cd frontend
npm run dev
```

#### 4단계: RAG 모드 활성화
`.env` 파일에서 `USE_RAG=true`로 변경 후 Node.js 서버 재시작

## 프로젝트 구조

```
rag_ai_chatbot_insa/
├── .env                    # 환경 변수 (공통)
├── frontend/               # React 프론트엔드 (포트 5173)
├── server/                 # Node.js 서버 (포트 4000)
└── rag-server/             # Python RAG 서버 (포트 8000)
    ├── main.py
    ├── requirements.txt
    ├── documents/          # 원본 문서 폴더
    ├── chroma_db/          # 벡터 DB (자동 생성)
    └── src/
```

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


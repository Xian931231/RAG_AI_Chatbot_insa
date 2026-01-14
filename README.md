## 로컬 ChatGPT 양방향 데모

React + Socket.io + OpenAI GPT-4o-mini를 이용한 멀티턴 채팅 예제입니다.

### 사전 준비
- Node.js 18 이상
- OpenAI API 키

### 설치
```bash
cd server
npm install

cd ../frontend
npm install
```

### 환경 변수
`server/env.example`를 `server/.env`로 복사한 뒤 `OPENAI_API_KEY` 값을 입력하세요.

### 실행
```bash
# 터미널 1
cd server
npm run dev

# 터미널 2
cd frontend
npm run dev
```

브라우저에서 `http://localhost:5173`에 접속하면 양방향 채팅을 테스트할 수 있습니다.


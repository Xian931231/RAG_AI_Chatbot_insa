import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { Server } from 'socket.io';
import OpenAI from 'openai';
import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// 루트 디렉토리의 .env 파일 로드
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
config({ path: join(__dirname, '../../.env') });

const PORT = process.env.NODE_PORT || process.env.PORT || 4000;
const openaiApiKey = process.env.OPENAI_API_KEY;

if (!openaiApiKey) {
  console.warn('[경고] OPENAI_API_KEY가 설정되지 않았습니다. 요청 시 오류가 발생합니다.');
}

const openai = new OpenAI({ apiKey: openaiApiKey });
const systemPrompt =
  '너는 친절한 한국어 AI 어시스턴트야. 답변은 간결하고 실용적으로 작성하고, 필요한 경우 bullet을 사용해. 사용자가 명확히 요청하지 않는 이상 영어를 사용하지 마.';

// RAG 서버 설정
const RAG_SERVER_URL = process.env.RAG_SERVER_URL || 'http://localhost:8000';
const USE_RAG = process.env.USE_RAG === 'true'; // RAG 사용 여부

const app = express();
app.use(cors());
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', serverTime: new Date().toISOString() });
});

const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: '*'
  }
});

const conversationStore = new Map();

io.on('connection', (socket) => {
  const baseHistory = [
    { role: 'system', content: systemPrompt, timestamp: Date.now() },
    { role: 'assistant', content: '안녕하세요! 무엇을 도와드릴까요?', timestamp: Date.now() }
  ];
  conversationStore.set(socket.id, baseHistory);

  socket.emit('conversationInit', { history: baseHistory.slice(1) });

  socket.on('userMessage', async (message) => {
    const history = conversationStore.get(socket.id) ?? [{ role: 'system', content: systemPrompt }];
    const normalizedMessage = {
      role: 'user',
      content: message.content,
      timestamp: message.timestamp || Date.now()
    };
    history.push(normalizedMessage);
    conversationStore.set(socket.id, history);

    try {
      let responseContent;

      // RAG 사용 여부에 따라 분기
      if (USE_RAG) {
        console.log('[RAG] RAG 서버로 질의 전송:', message.content);
        
        // 대화 히스토리를 RAG 서버로 전달 (시스템 프롬프트 제외)
        const conversationHistory = history
          .filter(msg => msg.role !== 'system')
          .map(msg => ({ role: msg.role, content: msg.content }));
        
        // RAG 서버에 질의
        const ragResponse = await fetch(`${RAG_SERVER_URL}/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            question: message.content,
            history: conversationHistory
          })
        });

        if (!ragResponse.ok) {
          const errorText = await ragResponse.text();
          console.error(`[오류] RAG 서버 응답: ${ragResponse.status}`, errorText);
          throw new Error(`RAG 서버 오류: ${ragResponse.status} - ${errorText}`);
        }

        const ragResult = await ragResponse.json();
        responseContent = ragResult.answer;

        // 출처 정보가 있으면 추가
        if (ragResult.sources && ragResult.sources.length > 0) {
          const sourceNames = ragResult.sources.map(s => s.file).join(', ');
          responseContent += `\n\n[출처] 참고 문서: ${sourceNames}`;
        }
      } else {
        // 기존 방식: OpenAI 직접 호출
        const completion = await openai.chat.completions.create({
          model: 'gpt-4o-mini',
          messages: history.map(({ role, content }) => ({ role, content })),
          temperature: 0.2
        });

        responseContent = completion.choices[0]?.message?.content ?? '죄송해요, 지금은 답변할 수 없어요.';
      }

      const assistantMessage = {
        role: 'assistant',
        content: responseContent,
        timestamp: Date.now()
      };

      conversationStore.set(socket.id, [...history, assistantMessage]);
      socket.emit('assistantMessage', assistantMessage);
    } catch (error) {
      console.error('AI 처리 오류:', error);
      socket.emit('serverError', {
        message: error?.message || 'AI 호출 중 오류가 발생했어요.'
      });
    }
  });

  socket.on('disconnect', () => {
    conversationStore.delete(socket.id);
  });
});

httpServer.listen(PORT, () => {
  console.log(`[서버] 서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
});


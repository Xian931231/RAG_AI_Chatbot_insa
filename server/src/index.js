import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { Server } from 'socket.io';
import OpenAI from 'openai';

const PORT = process.env.PORT || 4000;
const openaiApiKey = process.env.OPENAI_API_KEY;

if (!openaiApiKey) {
  console.warn('⚠️  OPENAI_API_KEY가 설정되지 않았습니다. 요청 시 오류가 발생합니다.');
}

const openai = new OpenAI({ apiKey: openaiApiKey });
const systemPrompt =
  '너는 친절한 한국어 AI 어시스턴트야. 답변은 간결하고 실용적으로 작성하고, 필요한 경우 bullet을 사용해. 사용자가 명확히 요청하지 않는 이상 영어를 사용하지 마.';

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
      const completion = await openai.chat.completions.create({
        model: 'gpt-4o-mini',
        messages: history.map(({ role, content }) => ({ role, content })),
        temperature: 0.2
      });

      const responseContent = completion.choices[0]?.message?.content ?? '죄송해요, 지금은 답변할 수 없어요.';
      const assistantMessage = {
        role: 'assistant',
        content: responseContent,
        timestamp: Date.now()
      };

      conversationStore.set(socket.id, [...history, assistantMessage]);
      socket.emit('assistantMessage', assistantMessage);
    } catch (error) {
      console.error('OpenAI error:', error);
      socket.emit('serverError', {
        message: error?.response?.data?.error?.message || 'AI 호출 중 오류가 발생했어요.'
      });
    }
  });

  socket.on('disconnect', () => {
    conversationStore.delete(socket.id);
  });
});

httpServer.listen(PORT, () => {
  console.log(`🚀 서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
});


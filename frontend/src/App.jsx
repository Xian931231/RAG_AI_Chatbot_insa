import { useEffect, useRef, useState } from 'react';
import { useChat } from './hooks/useChat.js';

const formatTime = (timestamp) =>
  new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(timestamp || Date.now());

export default function App() {
  const { messages, sendMessage, status } = useChat();
  const [input, setInput] = useState('');
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (event) => {
    event.preventDefault();
    sendMessage(input);
    setInput('');
  };

  return (
    <div className="app">
      <header className="app__header">
        <h1>DliveInsaBot - 인사 규정 챗봇</h1>
        <span className="status">{status}</span>
      </header>

      <main className="chat-window">
        {messages.map((message, idx) => (
          <article key={`${message.timestamp || idx}-${message.role}`} className={`bubble ${message.role}`}>
            <div className="meta">
              <strong>{message.role === 'user' ? '나' : '딜라이브_인사봇'}</strong>
              <time>{formatTime(message.timestamp)}</time>
            </div>
            <p>{message.content}</p>
          </article>
        ))}
        <div ref={endRef} />
      </main>

      <form className="input-bar" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="메시지를 입력하세요..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit" disabled={!input.trim()}>
          전송
        </button>
      </form>
    </div>
  );
}


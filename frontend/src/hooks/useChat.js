import { useEffect, useRef, useState } from 'react';
import { io } from 'socket.io-client';

const SOCKET_URL = 'http://localhost:4000';

export const useChat = () => {
  const socketRef = useRef(null);
  const initializedRef = useRef(false);
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState('연결되지 않음');

  useEffect(() => {
    if (initializedRef.current) return undefined;
    initializedRef.current = true;

    const socket = io(SOCKET_URL, { autoConnect: true });
    socketRef.current = socket;

    socket.on('connect', () => setStatus('연결됨'));
    socket.on('disconnect', () => setStatus('연결 끊김'));

    socket.on('assistantMessage', (payload) => {
      setMessages((prev) => [...prev, payload]);
    });

    socket.on('conversationInit', (payload) => {
      setMessages(payload.history || []);
    });

    socket.on('serverError', (payload) => {
      setMessages((prev) => [
        ...prev,
        { role: 'system', content: payload.message || '알 수 없는 오류가 발생했습니다.' }
      ]);
    });

    return () => {
      initializedRef.current = false;
      socket.disconnect();
    };
  }, []);

  const sendMessage = (text) => {
    if (!text.trim()) return;
    const newMessage = { role: 'user', content: text, timestamp: Date.now() };
    setMessages((prev) => [...prev, newMessage]);
    socketRef.current?.emit('userMessage', newMessage);
  };

  return { messages, sendMessage, status };
};


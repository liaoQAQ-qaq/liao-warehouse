import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import UploadManager from './components/UploadManager';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);

  // 加载会话列表
  const loadSessions = () => {
    fetch('/api/sessions')
      .then(res => res.json())
      .then(data => setSessions(data));
  };

  useEffect(() => {
    loadSessions();
  }, []);

  // 切换会话
  const switchSession = async (id) => {
    setCurrentSessionId(id);
    setActiveTab('chat');
    if (!id) {
        setMessages([]);
        return;
    }
    try {
        const res = await fetch(`/api/sessions/${id}/messages`);
        const msgs = await res.json();
        setMessages(msgs);
    } catch (e) {
        console.error(e);
    }
  };

  // 🚀 删除会话
  const handleDeleteSession = async (id) => {
    if (!confirm('确定要删除这条历史记录吗？')) return;

    try {
        const res = await fetch(`/api/sessions/${id}`, { method: 'DELETE' });
        if (res.ok) {
            // 如果删除的是当前正在查看的会话，重置到新会话状态
            if (currentSessionId === id) {
                setCurrentSessionId(null);
                setMessages([]);
            }
            // 刷新列表
            loadSessions();
        }
    } catch (e) {
        alert('删除失败');
    }
  };

  // 处理发送消息
  const handleSendMessage = async (text, currentMsgs) => {
    // ... (保持不变)
    setMessages([...currentMsgs, { role: 'assistant', content: '' }]);
    
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: text, session_id: currentSessionId })
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let aiResponse = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        aiResponse += chunk;
        setMessages(prev => {
          const newArr = [...prev];
          newArr[newArr.length - 1] = { role: 'assistant', content: aiResponse };
          return newArr;
        });
      }

      if (!currentSessionId) {
         loadSessions(); // 刷新会话列表
      }
    } catch (e) {
      console.error("Chat error:", e);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSessionSelect={switchSession}
        onNewSession={() => switchSession(null)}
        onDeleteSession={handleDeleteSession} // 传递删除函数
      />
      
      {activeTab === 'chat' ? (
        <ChatArea 
          messages={messages} 
          setMessages={setMessages}
          sessionId={currentSessionId}
          onSendMessage={handleSendMessage}
        />
      ) : (
        <UploadManager />
      )}
    </div>
  );
}
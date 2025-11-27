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

  // 删除会话
  const handleDeleteSession = async (id) => {
    if (!confirm('确定要删除这条历史记录吗？')) return;
    try {
        const res = await fetch(`/api/sessions/${id}`, { method: 'DELETE' });
        if (res.ok) {
            if (currentSessionId === id) {
                setCurrentSessionId(null);
                setMessages([]);
            }
            loadSessions();
        }
    } catch (e) {
        alert('删除失败');
    }
  };

  // 🚀【核心修改】处理发送消息 + 支持打断 + 自动捕获SessionID
  const handleSendMessage = async (text, currentMsgs, controller) => {
    setMessages([...currentMsgs, { role: 'assistant', content: '', sources: null }]);
    
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: text, session_id: currentSessionId }),
        signal: controller.signal
      });

      // 🚀 关键修复：从响应头中获取 Session ID 并锁定状态
      // 防止连续对话产生碎片
      const newSessionId = res.headers.get('X-Session-Id');
      if (newSessionId && newSessionId !== currentSessionId) {
          setCurrentSessionId(newSessionId);
          loadSessions(); // 刷新侧边栏
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullBuffer = ''; 
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        fullBuffer += chunk;
        
        let displayContent = fullBuffer;
        let parsedSources = null;

        if (fullBuffer.includes('__SOURCES__')) {
            const parts = fullBuffer.split('__SOURCES__');
            displayContent = parts[0];
            try {
                parsedSources = JSON.parse(parts[1]);
            } catch (e) {
                // JSON 传输中
            }
        }

        setMessages(prev => {
          const newArr = [...prev];
          newArr[newArr.length - 1] = { 
              role: 'assistant', 
              content: displayContent,
              sources: parsedSources
          };
          return newArr;
        });
      }
    } catch (e) {
      if (e.name === 'AbortError') {
        console.log('生成已手动停止');
      } else {
        console.error("Chat error:", e);
      }
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
        onDeleteSession={handleDeleteSession}
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
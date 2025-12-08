import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import UploadManager from './components/UploadManager';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [sessions, setSessions] = useState([]);
  // ✅ 定义的是 currentSessionId
  const [currentSessionId, setCurrentSessionId] = useState(null); 
  const [messages, setMessages] = useState([]);
  const [isChatUploading, setIsChatUploading] = useState(false);

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
    setIsChatUploading(false);
    if (!id) {
        setMessages([]);
        return;
    }
    try {
        const res = await fetch(`/api/sessions/${id}/messages`);
        const msgs = await res.json();
        // 切换历史记录时，也需要处理一下 <think> 标签，防止历史记录显示空白
        const processedMsgs = msgs.map(msg => ({
            ...msg,
            content: msg.content
                .replace(/<think>/g, '> **🧠 深度思考中...**\n> ')
                .replace(/<\/think>/g, '\n\n')
        }));
        setMessages(processedMsgs);
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

  // 聊天框上传
  const handleChatUpload = async (file) => {
    if (!currentSessionId) {
        alert("请先发送一条消息开启会话，然后再上传视频进行分析。");
        return;
    }

    setIsChatUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', currentSessionId);

    try {
        const res = await fetch('/api/chat/upload', {
            method: 'POST',
            body: formData
        });
        
        if (res.ok) {
            const data = await res.json();
            const reportMsg = {
                role: 'assistant',
                content: `🎥 **${data.message}**\n\n> ${data.report_preview || "分析报告已生成，请直接提问。"}`,
                sources: null
            };
            setMessages(prev => [...prev, reportMsg]);
        } else {
            const err = await res.json();
            alert(`上传失败: ${err.detail || '未知错误'}`);
        }
    } catch (e) {
        console.error(e);
        alert("网络请求失败");
    } finally {
        setIsChatUploading(false);
    }
  };

  // 🚀 核心修复：发送消息与流式处理 + 思考标签解析
  // 🚀 核心升级：支持多模态文件上传
  const handleSendMessage = async (text, history, controller, file = null) => {
    // 乐观更新：先在界面上显示用户消息 (ChatArea 已经做了，这里只需要处理请求)
    // 注意：history 已经是更新后的了
    
    try {
      let response;
      
      if (file) {
        // --- 🅰️ 多模态联合模式 (视频 + 文字) ---
        console.log("🚀 启动多模态联合分析...");
        const formData = new FormData();
        formData.append('file', file);
        formData.append('input', text || "请分析这个视频"); 
        // ❌ 修复点1：原代码是 sessionId，改为 currentSessionId
        formData.append('session_id', currentSessionId || "");

        response = await fetch('/api/chat/multimodal', {
          method: 'POST',
          body: formData,
          signal: controller.signal
        });
      } else {
        // --- 🅱️ 普通对话模式 (仅文字) ---
        response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          // ❌ 修复点2：原代码是 sessionId，改为 currentSessionId
          body: JSON.stringify({ input: text, session_id: currentSessionId }),
          signal: controller.signal
        });
      }

      // --- 下面是通用的流式读取逻辑 ---
      if (!response.ok) throw new Error("网络请求失败");
      
      // 更新 Session ID (如果是新会话)
      const newSessionId = response.headers.get("X-Session-Id");
      
      // ❌ 修复点3：变量名 sessionId 改为 currentSessionId
      if (newSessionId && newSessionId !== currentSessionId) {
        // ❌ 修复点4：函数名 setSessionId 改为 setCurrentSessionId
        setCurrentSessionId(newSessionId);
        // 刷新侧边栏会话列表（建议取消注释，这样左侧列表会自动更新）
        loadSessions(); 
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMsg = { role: 'assistant', content: '' };
      
      // 先添加一个空的 assistant 消息占位
      setMessages(prev => [...prev, assistantMsg]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        assistantMsg.content += chunk;
        
        // 实时更新最后一条消息
        setMessages(prev => {
          const newMsgs = [...prev];
          newMsgs[newMsgs.length - 1] = { ...assistantMsg };
          return newMsgs;
        });
      }

    } catch (e) {
      if (e.name === 'AbortError') {
        console.log("请求已中断");
      } else {
        console.error(e);
        setMessages(prev => [...prev, { role: 'assistant', content: `⚠️ 出错: ${e.message}` }]);
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
          onUploadFile={handleChatUpload}
          isUploading={isChatUploading}
        />
      ) : (
        <UploadManager />
      )}
    </div>
  );
}
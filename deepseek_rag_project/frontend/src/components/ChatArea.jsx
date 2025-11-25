import React, { useState, useRef, useLayoutEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Sparkles, Bot, User } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ChatArea({ messages, setMessages, sessionId, onSendMessage }) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useLayoutEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'auto', block: 'end' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const text = input;
    setInput('');
    setLoading(true);
    const newMessages = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);
    await onSendMessage(text, newMessages);
    setLoading(false);
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative', background: '#f8fafc' }}>
      
      {/* 聊天滚动区域 */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '40px 20px 120px 20px' }}>
        {messages.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="h-full flex flex-col items-center justify-center text-center"
            style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}
          >
            <div className="w-20 h-20 bg-white rounded-3xl flex items-center justify-center shadow-xl mb-6">
              <Sparkles size={40} className="text-indigo-500" style={{color: '#6366f1'}} />
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">欢迎使用企业知识库</h2>
            <p className="text-slate-500 max-w-md mb-8">我可以帮您分析文档、回答技术问题或查询公司政策。</p>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', maxWidth: '600px', width: '100%' }}>
              {['Docker CP 命令怎么用？', '查询我的简历信息', '公司的考勤制度是？', '如何部署 Python 应用？'].map((q, i) => (
                <motion.button
                  key={i}
                  whileHover={{ scale: 1.02, backgroundColor: '#fff' }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => { setInput(q); }}
                  style={{
                    padding: '16px',
                    background: 'rgba(255,255,255,0.6)',
                    border: '1px solid rgba(255,255,255,0.5)',
                    borderRadius: '16px',
                    textAlign: 'left',
                    color: '#475569',
                    cursor: 'pointer',
                    fontSize: '14px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.01)'
                  }}
                >
                  {q}
                </motion.button>
              ))}
            </div>
          </motion.div>
        ) : (
          <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.3 }}
                style={{
                  display: 'flex',
                  gap: '16px',
                  flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                }}
              >
                <div style={{
                  width: '40px', height: '40px',
                  borderRadius: '12px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: msg.role === 'user' ? 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)' : 'white',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                  color: msg.role === 'user' ? 'white' : '#6366f1',
                  flexShrink: 0
                }}>
                  {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>
                
                <div style={{
                  background: msg.role === 'user' ? '#6366f1' : 'white',
                  color: msg.role === 'user' ? 'white' : '#1e293b',
                  padding: '16px 24px',
                  borderRadius: msg.role === 'user' ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
                  boxShadow: msg.role === 'user' ? '0 10px 20px -5px rgba(99, 102, 241, 0.4)' : '0 4px 15px rgba(0,0,0,0.05)',
                  maxWidth: '80%',
                  lineHeight: '1.6',
                  fontSize: '15px'
                }}>
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown 
                      components={{
                        // 自定义 Markdown 样式
                        p: ({node, ...props}) => <p style={{marginBottom: '0.5em'}} {...props} />,
                        strong: ({node, ...props}) => <span style={{color: '#4f46e5', fontWeight: 600}} {...props} />
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  ) : (
                    <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                  )}
                </div>
              </motion.div>
            ))}
            {loading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4">
                <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm">
                  <Bot size={20} className="text-indigo-500 animate-pulse" />
                </div>
                <div className="bg-white px-6 py-4 rounded-[20px] rounded-bl-sm shadow-sm flex items-center gap-2">
                  <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></span>
                  <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                  <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                </div>
              </motion.div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* 输入框悬浮层 */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        padding: '20px 40px 40px 40px',
        background: 'linear-gradient(to top, #f8fafc 0%, rgba(248,250,252,0) 100%)',
        display: 'flex',
        justifyContent: 'center'
      }}>
        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          style={{
            width: '100%',
            maxWidth: '800px',
            position: 'relative',
            background: 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(12px)',
            borderRadius: '24px',
            padding: '8px',
            boxShadow: '0 20px 40px -10px rgba(0,0,0,0.1)',
            border: '1px solid rgba(255,255,255,0.8)',
            display: 'flex',
            alignItems: 'flex-end',
            gap: '8px'
          }}
        >
          <textarea
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
            placeholder="✨ 问点什么..."
            disabled={loading}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              padding: '16px 20px',
              fontSize: '16px',
              outline: 'none',
              resize: 'none',
              maxHeight: '120px',
              minHeight: '56px',
              color: '#334155'
            }}
          />
          <motion.button 
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={handleSend}
            disabled={loading || !input.trim()}
            style={{
              background: input.trim() ? '#6366f1' : '#e2e8f0',
              color: 'white',
              border: 'none',
              width: '48px',
              height: '48px',
              borderRadius: '18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: input.trim() ? 'pointer' : 'not-allowed',
              marginBottom: '4px',
              transition: 'background 0.2s'
            }}
          >
            <Send size={22} />
          </motion.button>
        </motion.div>
      </div>
    </div>
  );
}
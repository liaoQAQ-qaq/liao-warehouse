import React, { useState, useRef, useLayoutEffect } from 'react';
import ReactMarkdown from 'react-markdown';
// 🚀 引入 Paperclip 和 X (关闭) 图标
import { Send, Sparkles, Bot, User, BookOpen, ChevronDown, ChevronUp, FileText, ArrowDown, Square, Paperclip, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// 来源卡片组件 (保持不变)
const SourceCard = ({ sources }) => {
  const [isOpen, setIsOpen] = useState(false);
  if (!sources || sources.length === 0) return null;
  return (
    <div style={{ marginTop: '12px' }}>
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        style={{
          display: 'flex', alignItems: 'center', gap: '8px',
          padding: '6px 12px', background: 'rgba(255,255,255,0.8)',
          border: '1px solid #e0e7ff', borderRadius: '12px',
          fontSize: '12px', color: '#6366f1', fontWeight: '600',
          cursor: 'pointer', boxShadow: '0 2px 4px rgba(99, 102, 241, 0.05)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '-4px' }}>
           <div style={{width:18, height:18, borderRadius:'50%', background:'#e0e7ff', display:'flex', alignItems:'center', justifyContent:'center', border:'2px solid white'}}>
             <BookOpen size={10} />
           </div>
        </div>
        <span>引用了 {sources.length} 篇资料</span>
        {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            style={{ overflow: 'hidden', marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '6px' }}
          >
            {sources.map((src, i) => (
              <motion.div
                key={i}
                initial={{ x: -10, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: i * 0.05 }}
                style={{
                  padding: '10px', background: 'white', borderRadius: '10px',
                  border: '1px solid #f1f5f9', fontSize: '12px',
                  display: 'flex', alignItems: 'center', gap: '10px', color: '#475569',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
                }}
              >
                <span style={{ background: '#f1f5f9', color: '#64748b', minWidth: '20px', height: '20px', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '11px' }}>{src.id}</span>
                <FileText size={14} className="text-indigo-400" style={{flexShrink: 0}} />
                <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{src.name}</span>
                <span style={{ color: '#10b981', fontSize: '11px', background: '#ecfdf5', padding: '2px 6px', borderRadius: '4px' }}>{(src.score * 100).toFixed(0)}%</span>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default function ChatArea({ messages, setMessages, sessionId, onSendMessage }) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);
  // 🚀 新增：选中文件状态
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  
  const scrollContainerRef = useRef(null);
  const bottomRef = useRef(null);
  const shouldAutoScroll = useRef(true);
  const abortControllerRef = useRef(null);

  const scrollToBottom = (behavior = 'auto') => {
    if (bottomRef.current) {
        bottomRef.current.scrollIntoView({ behavior, block: 'end' });
    }
    shouldAutoScroll.current = true;
    setShowScrollButton(false);
  };

  useLayoutEffect(() => {
    if (shouldAutoScroll.current) {
      scrollToBottom('auto');
    }
  }, [messages]);

  const handleScroll = () => {
    const container = scrollContainerRef.current;
    if (!container) return;
    const { scrollTop, scrollHeight, clientHeight } = container;
    const distanceToBottom = scrollHeight - scrollTop - clientHeight;
    shouldAutoScroll.current = distanceToBottom <= 150;
    setShowScrollButton(distanceToBottom > 200);
  };

  // 🚀 处理文件选择
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // 简单校验一下是不是视频
      if (!file.type.startsWith('video/')) {
        alert("目前仅支持视频文件的联合分析");
        return;
      }
      setSelectedFile(file);
    }
  };

  // 🚀 发送逻辑 (升级版)
  const handleSend = async () => {
    if ((!input.trim() && !selectedFile) || loading) return;
    
    const text = input;
    const fileToSend = selectedFile;
    
    // 清空状态
    setInput('');
    setSelectedFile(null);
    setLoading(true);
    shouldAutoScroll.current = true;
    
    const controller = new AbortController();
    abortControllerRef.current = controller;
    
    // 乐观更新 UI
    const displayContent = fileToSend 
        ? `[上传视频] ${fileToSend.name}\n${text}` 
        : text;
        
    const newMessages = [...messages, { role: 'user', content: displayContent }];
    setMessages(newMessages);
    setTimeout(() => scrollToBottom('smooth'), 0);

    // 🚀 将文件传给父组件处理
    await onSendMessage(text, newMessages, controller, fileToSend);
    
    setLoading(false);
    abortControllerRef.current = null;
    // 重置文件输入框，允许重复选择同一文件
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setLoading(false);
    }
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative', background: '#f8fafc' }}>
      
      <div 
        ref={scrollContainerRef}
        onScroll={handleScroll}
        style={{ flex: 1, overflowY: 'auto', padding: '40px 20px 80px 20px' }}
        className="custom-scroll"
      >
        {messages.length === 0 ? (
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-14 h-14 bg-white rounded-2xl flex items-center justify-center shadow-lg mb-5">
              <Sparkles size={28} className="text-indigo-500" style={{color: '#6366f1'}} />
            </div>
            <h2 className="text-lg font-bold text-slate-800 mb-2">DeepSeek RAG Enterprise</h2>
            <p className="text-slate-500 max-w-md mb-6 text-xs">上传视频并提问，我会同时看视频并回答您的问题。</p>
          </motion.div>
        ) : (
          <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {messages.map((msg, idx) => (
              <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} style={{ display: 'flex', gap: '10px', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row', alignItems: 'flex-start' }}>
                <div style={{ width: '28px', height: '28px', borderRadius: '8px', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: msg.role === 'user' ? 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)' : 'white', boxShadow: '0 2px 6px rgba(0,0,0,0.05)', color: msg.role === 'user' ? 'white' : '#6366f1' }}>{msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}</div>
                <div style={{ display: 'flex', flexDirection: 'column', maxWidth: '85%', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                    <div style={{ background: msg.role === 'user' ? '#6366f1' : 'white', color: msg.role === 'user' ? 'white' : '#1e293b', padding: '10px 16px', borderRadius: msg.role === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px', boxShadow: msg.role === 'user' ? '0 4px 12px -2px rgba(99, 102, 241, 0.3)' : '0 2px 8px rgba(0,0,0,0.03)', lineHeight: '1.5', fontSize: '14px' }}>
                      {msg.role === 'assistant' ? (
                        <ReactMarkdown components={{
                            p: ({node, ...props}) => <p style={{marginBottom: '0.4em'}} {...props} />,
                            code: ({node, inline, children, ...props}) => (inline ? <code style={{background: 'rgba(0,0,0,0.05)', padding:'2px 4px', borderRadius:4}} {...props}>{children}</code> : <code style={{display:'block', background:'#f8fafc', padding:10, borderRadius:8, margin:'0.5em 0', overflowX:'auto'}} {...props}>{children}</code>)
                        }}>{msg.content}</ReactMarkdown>
                      ) : (<div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>)}
                    </div>
                    {msg.role === 'assistant' && msg.sources && (<SourceCard sources={msg.sources} />)}
                </div>
              </motion.div>
            ))}
            {loading && <div style={{marginLeft:40, fontSize:12, color:'#94a3b8'}}>Qwen 正在思考...</div>}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <AnimatePresence>
        {showScrollButton && (
          <motion.button initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} onClick={() => scrollToBottom('smooth')} style={{ position: 'absolute', bottom: '100px', left: '50%', transform: 'translateX(-50%)', background: 'white', border: '1px solid #e2e8f0', borderRadius: '20px', padding: '8px 16px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center', gap: '6px', color: '#6366f1', fontWeight: '600', fontSize: '12px', zIndex: 30, cursor: 'pointer' }}>
            <ArrowDown size={14} /> 查看最新消息
          </motion.button>
        )}
      </AnimatePresence>

      <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '10px 30px 16px 30px', background: 'linear-gradient(to top, #f8fafc 30%, rgba(248,250,252,0) 100%)', display: 'flex', flexDirection: 'column', alignItems: 'center', zIndex: 20 }}>
        
        {/* 🚀 文件预览卡片 (ChatGPT 风格) */}
        <AnimatePresence>
            {selectedFile && (
                <motion.div 
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    style={{ width: '100%', maxWidth: '800px', marginBottom: '8px', display:'flex', justifyContent:'flex-start' }}
                >
                    <div style={{ background: 'white', padding: '8px 12px', borderRadius: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)', display: 'flex', alignItems: 'center', gap: '8px', border: '1px solid #e2e8f0' }}>
                        <div style={{ width: 32, height: 32, background: '#f1f5f9', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6366f1' }}>
                            <FileText size={16} />
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span style={{ fontSize: '13px', fontWeight: '500', color: '#334155', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{selectedFile.name}</span>
                            <span style={{ fontSize: '11px', color: '#94a3b8' }}>{(selectedFile.size / 1024 / 1024).toFixed(1)} MB</span>
                        </div>
                        <button onClick={() => setSelectedFile(null)} style={{ border: 'none', background: 'transparent', cursor: 'pointer', padding: 4, color: '#94a3b8' }}>
                            <X size={14} />
                        </button>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>

        <motion.div initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} style={{ width: '100%', maxWidth: '800px', position: 'relative', background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(12px)', borderRadius: '16px', padding: '4px', boxShadow: '0 4px 20px -4px rgba(0,0,0,0.06)', border: '1px solid rgba(255,255,255,0.9)', display: 'flex', alignItems: 'flex-end', gap: '6px' }}>
          
          {/* 🚀 隐藏的文件输入框 */}
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileSelect} 
            accept="video/*" 
            style={{ display: 'none' }} 
          />
          
          {/* 🚀 回形针按钮 */}
          <motion.button
            whileHover={{ scale: 1.1, backgroundColor: '#f1f5f9' }}
            whileTap={{ scale: 0.9 }}
            onClick={() => fileInputRef.current.click()}
            style={{ 
                padding: '10px', borderRadius: '12px', border: 'none', background: 'transparent', 
                color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' 
            }}
            title="上传视频进行联合分析"
          >
            <Paperclip size={20} />
          </motion.button>

          <textarea rows={1} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())} placeholder="✨ 输入问题（可配合上传视频）..." disabled={loading} style={{ flex: 1, background: 'transparent', border: 'none', padding: '10px 4px', fontSize: '14px', outline: 'none', resize: 'none', maxHeight: '100px', minHeight: '24px', color: '#334155', lineHeight: '1.4' }} />
          
          {loading ? (
            <motion.button 
                key="stop"
                whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} 
                onClick={handleStop}
                style={{ background: '#ef4444', color: 'white', border: 'none', width: '34px', height: '34px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', marginBottom: '3px' }}
            >
                <Square size={14} fill="white" />
            </motion.button>
          ) : (
            <motion.button 
                key="send"
                whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} 
                onClick={handleSend} 
                disabled={!input.trim() && !selectedFile}
                style={{
                  background: (input.trim() || selectedFile) ? 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)' : '#f1f5f9',
                  color: (input.trim() || selectedFile) ? 'white' : '#cbd5e1', border: 'none', width: '34px', height: '34px', borderRadius: '12px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: (input.trim() || selectedFile) ? 'pointer' : 'not-allowed', marginBottom: '3px', transition: 'all 0.2s'
                }}
            >
                <Send size={16} strokeWidth={2.5} />
            </motion.button>
          )}
        </motion.div>
      </div>
    </div>
  );
}
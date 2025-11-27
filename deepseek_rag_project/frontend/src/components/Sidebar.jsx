import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, FolderUp, Plus, Trash2, Bot, History } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, sessions, currentSessionId, onSessionSelect, onNewSession, onDeleteSession }) {
  return (
    <aside 
      className="sidebar-container"
      style={{
        width: '280px',
        height: '100%',
        background: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(20px)',
        borderRight: '1px solid rgba(255, 255, 255, 0.5)',
        display: 'flex',
        flexDirection: 'column',
        padding: '20px',
        // paddingBottom: '0', // 移除底部的 padding，交给内部容器控制
        boxShadow: '4px 0 24px rgba(0,0,0,0.02)',
        position: 'relative',
        zIndex: 10
      }}
    >
      {/* 1. 品牌 Logo */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px', paddingLeft: '4px' }}
      >
        <div style={{
          width: '36px', height: '36px',
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
          borderRadius: '10px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)'
        }}>
          <Bot size={20} color="white" />
        </div>
        <span style={{ fontSize: '18px', fontWeight: '700', color: '#1e293b', letterSpacing: '-0.5px' }}>
          DeepSeek RAG
        </span>
      </motion.div>

      {/* 2. 新建按钮 */}
      <motion.button
        whileHover={{ scale: 1.02, translateY: -1 }}
        whileTap={{ scale: 0.98 }}
        onClick={onNewSession}
        style={{
          width: '100%',
          padding: '12px',
          background: 'linear-gradient(to right, #6366f1, #4f46e5)',
          borderRadius: '14px',
          border: 'none',
          color: 'white',
          fontSize: '14px',
          fontWeight: '600',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(99, 102, 241, 0.25)',
          marginBottom: '32px',
          transition: 'all 0.2s',
          flexShrink: 0 // 防止被压缩
        }}
      >
        <Plus size={18} strokeWidth={3} /> 
        <span>开启新对话</span>
      </motion.button>

      {/* 3. 导航菜单 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '32px', flexShrink: 0 }}>
        {[
          { id: 'chat', icon: MessageSquare, label: '智能对话' },
          { id: 'upload', icon: FolderUp, label: '知识库管理' }
        ].map((item) => {
          const isActive = activeTab === item.id;
          return (
            <div
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                position: 'relative',
                padding: '12px 16px',
                borderRadius: '12px',
                cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: '12px',
                color: isActive ? '#4f46e5' : '#64748b',
                fontWeight: isActive ? '600' : '500',
                background: isActive ? 'rgba(99, 102, 241, 0.08)' : 'transparent',
                transition: 'all 0.2s'
              }}
            >
              <item.icon size={18} style={{ opacity: isActive ? 1 : 0.7 }} />
              <span>{item.label}</span>
              {isActive && (
                <motion.div
                  layoutId="active-pill"
                  style={{
                    position: 'absolute', left: 0, width: '3px', height: '16px',
                    background: '#4f46e5', borderRadius: '0 4px 4px 0'
                  }}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* 4. 历史记录 (修复截断问题) */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minHeight: 0 }}>
        <div style={{ 
          display: 'flex', alignItems: 'center', gap: '6px', 
          paddingLeft: '4px', marginBottom: '12px', 
          color: '#94a3b8', fontSize: '12px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px',
          flexShrink: 0
        }}>
          <History size={12} /> 最近记录
        </div>
        
        <div 
          className="custom-scroll"
          style={{ 
            flex: 1, 
            overflowY: 'auto', 
            paddingRight: '4px', 
            display: 'flex', 
            flexDirection: 'column', 
            gap: '4px',
            // 🚀【核心修复】增加底部内边距，让最后一个元素能完整显示出来
            paddingBottom: '20px' 
          }}
        >
          <AnimatePresence>
            {sessions.map((session, i) => (
              <motion.div
                key={session.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.03 }}
                onClick={() => onSessionSelect(session.id)}
                className="group"
                style={{
                  padding: '10px 12px',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  fontSize: '13px',
                  color: currentSessionId === session.id ? '#1e293b' : '#64748b',
                  background: currentSessionId === session.id ? 'white' : 'transparent',
                  boxShadow: currentSessionId === session.id ? '0 2px 8px rgba(0,0,0,0.04)' : 'none',
                  border: currentSessionId === session.id ? '1px solid rgba(0,0,0,0.02)' : '1px solid transparent',
                  transition: 'all 0.2s',
                  flexShrink: 0 // 防止 flex 挤压列表项
                }}
              >
                <span style={{ 
                  whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', flex: 1,
                  fontWeight: currentSessionId === session.id ? '500' : '400'
                }}>
                  {session.title || '无标题会话'}
                </span>
                
                {/* 删除按钮 */}
                <motion.button
                  whileHover={{ scale: 1.1, color: '#ef4444', background: 'rgba(239, 68, 68, 0.1)' }}
                  onClick={(e) => { e.stopPropagation(); onDeleteSession(session.id); }}
                  style={{
                    border: 'none', background: 'transparent', cursor: 'pointer',
                    padding: '4px', borderRadius: '6px',
                    color: '#cbd5e1',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    opacity: currentSessionId === session.id ? 1 : 0
                  }}
                  className="delete-btn-hover"
                >
                  <Trash2 size={14} />
                </motion.button>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </aside>
  );
}
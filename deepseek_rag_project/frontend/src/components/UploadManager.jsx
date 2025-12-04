import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Trash2, CheckCircle, AlertCircle, HardDrive, File as FileIcon, Video } from 'lucide-react';

export default function UploadManager() {
  const [fileList, setFileList] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const res = await fetch('/api/files');
      const data = await res.json();
      setFileList(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setProgress(0);
    setStatus(null);

    const formData = new FormData();
    formData.append('file', file);
    const xhr = new XMLHttpRequest();
    
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        setProgress(Math.round((event.loaded / event.total) * 100));
      }
    };
    xhr.onload = () => {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        // 🚀 针对视频上传显示特殊提示
        const msg = file.type.startsWith('video/') 
            ? '视频上传成功，后台正在进行多模态分析（耗时较长）...' 
            : '上传成功，后台正在索引...';
            
        setStatus({ type: 'success', msg: msg });
        loadFiles();
      } else {
        setStatus({ type: 'error', msg: '上传失败' });
      }
      setUploading(false);
    };
    xhr.open('POST', '/api/upload', true);
    xhr.send(formData);
  };

  const handleDelete = async (filename) => {
    if (!confirm(`确定删除 ${filename} 吗?`)) return;
    try {
      const res = await fetch(`/api/files/${filename}`, { method: 'DELETE' });
      if (res.ok) loadFiles();
    } catch (e) { alert("网络错误"); }
  };

  const isVideo = (filename) => {
    return /\.(mp4|avi|mov|mkv|flv)$/i.test(filename);
  };

  return (
    <div style={{ flex: 1, padding: '40px', overflowY: 'auto', background: '#f8fafc' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ fontSize: '28px', fontWeight: '800', color: '#1e293b', marginBottom: '32px', display: 'flex', alignItems: 'center', gap: '12px' }}
        >
          <HardDrive size={32} className="text-indigo-500" /> 知识库管理
        </motion.h1>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
          {/* 上传卡片 */}
          <motion.div 
            whileHover={{ y: -4 }}
            style={{
              background: 'white', padding: '32px', borderRadius: '24px',
              boxShadow: '0 4px 20px rgba(0,0,0,0.02)', border: '1px solid rgba(255,255,255,0.6)',
              textAlign: 'center'
            }}
          >
            <div style={{ width: '64px', height: '64px', background: '#e0e7ff', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <Upload size={32} className="text-indigo-600" />
            </div>
            <h3 style={{ fontWeight: '600', fontSize: '18px', marginBottom: '8px' }}>上传文件</h3>
            {/* 🚀 更新支持格式提示 */}
            <p style={{ color: '#64748b', fontSize: '14px', marginBottom: '24px' }}>
              支持 PDF, DOCX, TXT <br/>
              <span style={{color: '#6366f1', fontWeight: 'bold'}}>及 MP4, AVI 视频 (自动分析)</span>
            </p>
            
            <label style={{
              display: 'inline-block', padding: '12px 32px',
              background: uploading ? '#e2e8f0' : '#6366f1',
              color: uploading ? '#94a3b8' : 'white',
              borderRadius: '12px', fontWeight: '600', cursor: uploading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s'
            }}>
              {uploading ? '上传中...' : '选择文件'}
              {/* 🚀 增加 accept 属性 */}
              <input type="file" onChange={handleUpload} disabled={uploading} style={{ display: 'none' }} accept=".pdf,.docx,.doc,.txt,.md,.jpg,.png,.mp4,.avi,.mov,.mkv" />
            </label>

            {uploading && (
              <div style={{ marginTop: '20px', background: '#f1f5f9', borderRadius: '8px', height: '8px', overflow: 'hidden' }}>
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  style={{ height: '100%', background: '#6366f1' }}
                />
              </div>
            )}
            {status && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ marginTop: '16px', fontSize: '14px', color: status.type === 'success' ? '#16a34a' : '#ef4444', fontWeight: '500' }}
              >
                {status.msg}
              </motion.div>
            )}
          </motion.div>

          {/* 统计卡片 */}
          <motion.div 
            whileHover={{ y: -4 }}
            style={{
              background: 'linear-gradient(135deg, #4f46e5 0%, #8b5cf6 100%)',
              padding: '32px', borderRadius: '24px', color: 'white',
              display: 'flex', flexDirection: 'column', justifyContent: 'center'
            }}
          >
            <h3 style={{ opacity: 0.8, fontSize: '16px', fontWeight: '500' }}>当前存储状态</h3>
            <div style={{ fontSize: '48px', fontWeight: '800', margin: '16px 0' }}>{fileList.length} <span style={{ fontSize: '20px', fontWeight: '500', opacity: 0.8 }}>个文件</span></div>
            <p style={{ opacity: 0.7, fontSize: '14px' }}>视频文件将自动提取语音与画面信息。</p>
          </motion.div>
        </div>

        {/* 文件列表 */}
        <h4 style={{ fontSize: '18px', fontWeight: '700', color: '#334155', marginBottom: '20px' }}>文件列表</h4>
        <div style={{ background: 'white', borderRadius: '20px', padding: '8px', boxShadow: '0 4px 20px rgba(0,0,0,0.02)' }}>
          <AnimatePresence>
            {fileList.length === 0 ? (
              <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>暂无文件</div>
            ) : (
              fileList.map((file, i) => (
                <motion.div
                  key={file.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ delay: i * 0.05 }}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '16px 24px', borderBottom: i === fileList.length - 1 ? 'none' : '1px solid #f1f5f9',
                    transition: 'background 0.2s'
                  }}
                  className="hover:bg-slate-50"
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{ width: '40px', height: '40px', background: '#f1f5f9', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: isVideo(file.name) ? '#8b5cf6' : '#64748b' }}>
                      {/* 🚀 动态图标 */}
                      {isVideo(file.name) ? <Video size={20} /> : <FileIcon size={20} />}
                    </div>
                    <div>
                      <div style={{ fontWeight: '600', color: '#1e293b' }}>{file.name}</div>
                      <div style={{ fontSize: '13px', color: '#94a3b8' }}>{file.size}</div>
                    </div>
                  </div>
                  <button 
                    onClick={() => handleDelete(file.name)}
                    style={{ padding: '8px', color: '#94a3b8', background: 'transparent', border: 'none', cursor: 'pointer', transition: 'color 0.2s' }}
                    className="hover:text-red-500"
                  >
                    <Trash2 size={18} />
                  </button>
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
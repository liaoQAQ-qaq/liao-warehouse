import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // 🚀 核心优化：防止开发环境下大视频上传/分析时连接中断
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        timeout: 600000, // 设置 10 分钟超时
        proxyTimeout: 600000
      }
    }
  }
})
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// /api/* 요청을 백엔드로 넘긴다. Docker 안에서는 VITE_PROXY_TARGET=http://backend:8000
const target = process.env.VITE_PROXY_TARGET ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { target, changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, '') },
    },
    // macOS 바인드 마운트에서 파일 변경 감지가 안 되면 true로
    watch: { usePolling: process.env.VITE_USE_POLLING === 'true' },
  },
})

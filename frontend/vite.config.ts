import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 서버(dev 서버) 전용 설정. VITE_ 접두사 변수는 브라우저 번들에 들어가므로 여기에 쓰지 않는다.
// /api/* 요청을 백엔드로 넘긴다. Docker 안에서는 PROXY_TARGET=http://backend:8000
const target = process.env.PROXY_TARGET ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { target, changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, '') },
    },
    // macOS 바인드 마운트에서 파일 변경 감지가 안 되면 true로
    watch: { usePolling: process.env.USE_POLLING === 'true' },
  },
})

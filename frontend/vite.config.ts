import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // 默认 :8000；本机 8000 被占用时可用 LIMS_API_PROXY 覆盖，如 LIMS_API_PROXY=http://localhost:8010
    proxy: { '/api': process.env.LIMS_API_PROXY || 'http://localhost:8000' },
  },
})

import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 9000,
    strictPort: true,
    proxy: {
      '/api': { target: 'http://127.0.0.1:9100', rewrite: (path) => path.replace(/^\/api/, '') },
    },
  },
})

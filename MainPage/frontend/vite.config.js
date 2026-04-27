// Example Vite config — adjust for your environment
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 8000,
    host: '0.0.0.0',
    proxy: {
      '/api/v1': {
        target: 'http://localhost:3333',
        changeOrigin: true
      }
    }
  }
});

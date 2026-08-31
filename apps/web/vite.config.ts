import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@webtest/shared': path.resolve(__dirname, '../../packages/shared/src/index.ts')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:4000',
        changeOrigin: true
      },
      '/artifacts': {
        target: 'http://localhost:4000',
        changeOrigin: true
      }
    }
  }
});

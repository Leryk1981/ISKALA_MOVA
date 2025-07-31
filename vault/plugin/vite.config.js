import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@core': path.resolve(__dirname, './src/core'),
      '@ui': path.resolve(__dirname, './src/ui'),
      '@cloud': path.resolve(__dirname, './src/cloud'),
      '@utils': path.resolve(__dirname, './src/utils'),
    },
  },
  publicDir: 'public',
});

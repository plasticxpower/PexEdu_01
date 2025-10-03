import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  base: '/PexEdu_01/',
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});

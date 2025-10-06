import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const base =
    env.VITE_BASE_PATH && env.VITE_BASE_PATH.trim().length > 0
      ? env.VITE_BASE_PATH
      : mode === 'production'
        ? './'
        : '/';
  return {
    base,
    plugins: [react()],
    build: {
      outDir: 'dist',
      sourcemap: true,
    },
  };
});

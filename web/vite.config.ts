import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  root: '.', // Root is web/ directory
  publicDir: 'public',
  css: {
    postcss: './postcss.config.js',
  },
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist/client',
    emptyOutDir: true,
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'),
      },
      output: {
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            // React and React Router must be in the same chunk
            if (id.includes('react')) {
              return 'react-vendor';
            }
            if (id.includes('axios')) {
              return 'http-utils';
            }
            if (id.includes('date-fns')) {
              return 'date-utils';
            }
          }
        },
      },
    },
  },
})
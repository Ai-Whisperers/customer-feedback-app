import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
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
    chunkSizeWarningLimit: 1000, // Increase warning limit to 1000 kB
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        about: resolve(__dirname, 'about.html'),
        analyzer: resolve(__dirname, 'analyzer.html'),
      },
      output: {
        manualChunks: {
          // Separate Plotly into its own chunk (shared across pages)
          'plotly-core': ['plotly.js'],
          'react-plotly': ['react-plotly.js'],
          // Vendor chunks for common dependencies
          'vendor-react': ['react', 'react-dom'],
          'vendor-utils': ['axios', 'date-fns', 'clsx'],
        },
        // Ensure proper chunk naming
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId;
          if (facadeModuleId && facadeModuleId.includes('plotly')) {
            return 'assets/charts-[hash].js';
          }
          return 'assets/[name]-[hash].js';
        },
        entryFileNames: 'assets/[name]-[hash].js',
      },
    },
  },
})
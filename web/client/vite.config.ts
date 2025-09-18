import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { resolve } from 'path'
import { nodeResolve } from '@rollup/plugin-node-resolve'
import commonjs from '@rollup/plugin-commonjs'

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
      // Add polyfills for Node.js modules
      buffer: 'buffer',
      process: 'process/browser',
      stream: 'stream-browserify',
      util: 'util'
    },
  },
  define: {
    // Define global for libraries that expect it
    global: 'globalThis',
    'process.env': {},
  },
  optimizeDeps: {
    // Include these dependencies for optimization
    include: ['buffer', 'process'],
    esbuildOptions: {
      // Define global for esbuild
      define: {
        global: 'globalThis'
      }
    }
  },
  build: {
    chunkSizeWarningLimit: 1500, // Increase warning limit to 1500 kB
    // Disable modulePreload to prevent plotly from loading on all pages
    modulePreload: false,
    rollupOptions: {
      plugins: [
        nodeResolve({
          browser: true,
          preferBuiltins: false
        }),
        commonjs()
      ],
      input: {
        main: resolve(__dirname, 'index.html'),
        about: resolve(__dirname, 'about.html'),
        analyzer: resolve(__dirname, 'analyzer.html'),
      },
      output: {
        manualChunks: (id) => {
          // Better chunking strategy
          if (id.includes('plotly.js')) {
            return 'plotly-core';
          }
          if (id.includes('react-plotly')) {
            return 'react-plotly';
          }
          if (id.includes('node_modules/react') || id.includes('node_modules/react-dom')) {
            return 'vendor-react';
          }
          if (id.includes('node_modules') && (id.includes('axios') || id.includes('date-fns') || id.includes('clsx'))) {
            return 'vendor-utils';
          }
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
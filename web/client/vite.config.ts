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
      // Redirect plotly.js imports to plotly.js-dist-min
      'plotly.js/dist/plotly': path.resolve(__dirname, 'node_modules/plotly.js-dist-min/plotly.min.js'),
      'plotly.js': path.resolve(__dirname, 'node_modules/plotly.js-dist-min/plotly.min.js'),
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
    // Use terser for better control over minification
    minify: 'terser',
    terserOptions: {
      keep_fnames: true,
      keep_classnames: true,
      compress: {
        passes: 2,
        hoist_funs: false, // Prevent function hoisting that can cause TDZ
        hoist_vars: false, // Prevent variable hoisting that can cause TDZ
        reduce_funcs: false, // Prevent function inlining that might cause issues
        drop_console: false, // Keep console logs for debugging
        drop_debugger: true,
      },
      mangle: {
        // Keep function names for better debugging
        keep_fnames: true,
      },
    },
    target: 'es2018', // Target ES2018 for better compatibility
    rollupOptions: {
      // Mark Plotly as external since we're loading from CDN
      external: (id) => {
        return id.includes('plotly.js') || id.includes('plotly.js-dist-min');
      },
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
          // Advanced chunking strategy for better isolation

          // Plotly chunks - completely isolated
          if (id.includes('plotly.js-dist-min')) {
            return 'plotly-vendor';  // Pre-minified plotly
          }
          if (id.includes('react-plotly.js')) {
            return 'plotly-react';   // React wrapper
          }

          // React ecosystem - core libraries
          if (id.includes('node_modules/react-dom')) {
            return 'react-dom';
          }
          if (id.includes('node_modules/react')) {
            return 'react-vendor';
          }
          if (id.includes('react-router')) {
            return 'react-router';
          }

          // Utility libraries - grouped by function
          if (id.includes('date-fns')) {
            return 'date-utils';
          }
          if (id.includes('axios')) {
            return 'http-utils';
          }
          if (id.includes('clsx') || id.includes('tailwind-merge')) {
            return 'ui-utils';
          }

          // File handling
          if (id.includes('react-dropzone') || id.includes('xlsx')) {
            return 'file-utils';
          }

          // Form/validation
          if (id.includes('zod')) {
            return 'validation';
          }

          // Chart components (will be dynamically imported)
          if (id.includes('components/results') &&
              (id.includes('Chart') || id.includes('chart'))) {
            return 'charts-components';
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
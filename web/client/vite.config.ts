import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
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
      output: {
        manualChunks: {
          // Separate Plotly into its own chunk
          'plotly-core': ['plotly.js'],
          'react-plotly': ['react-plotly.js'],
          // Vendor chunks for common dependencies
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-utils': ['axios', 'date-fns', 'clsx'],
        },
        // Ensure proper chunk naming
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop() : '';
          if (facadeModuleId.includes('plotly')) {
            return 'assets/charts-[hash].js';
          }
          return 'assets/[name]-[hash].js';
        },
      },
    },
    // Optimize dependencies
    optimizeDeps: {
      include: ['react-plotly.js', 'plotly.js'],
    },
  },
})

import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ command, mode }) => {
  // Load environment variables based on the current mode (development/production)
  const env = loadEnv(mode, process.cwd(), '');
  
  // Determine if we're in development mode
  const isDevelopment = mode === 'development';
  
  // Get the API server URL from environment or use default
  const apiServerUrl = env.VITE_API_SERVER_URL || 'http://localhost:8000';
  
  // In development, we'll use the proxy. In production, we'll use the full URL
  const proxyConfig = isDevelopment ? {
    // In development, use the proxy to avoid CORS issues
    '/api': {
      target: apiServerUrl,
      changeOrigin: true,
      secure: false,
    },
  } : undefined;

  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: true, // Listen on all network interfaces
      proxy: proxyConfig,
    },
    // In production, use relative paths for assets
    base: isDevelopment ? '/' : './',
    // Define global constants
    define: {
      __APP_ENV__: JSON.stringify(mode),
    },
  };
});

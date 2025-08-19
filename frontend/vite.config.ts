import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "@tailwindcss/vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "/app/",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: process.env.FRONTEND_HOST || "localhost",
    port: parseInt(process.env.FRONTEND_PORT || "5173"),
    strictPort: false, // Allow Vite to try other ports if the specified one is taken
    proxy: {
      // Proxy API requests to the backend server
      "/api": {
        target: process.env.VITE_API_TARGET || "http://localhost:2024",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // Remove /api prefix for backend
        configure: (proxy, options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (_proxyReq, req, _res) => {
            console.log('Proxying request:', req.method, req.url, '→', options.target + (req.url || '').replace('/api', ''));
          });
        }
      },
    },
  },
});

import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vite";

// Portas injetadas pelo dev.sh via variáveis de ambiente.
// Em produção, o proxy não é necessário — o frontend é servido
// como arquivos estáticos pelo mesmo servidor que a API.
const API_PORT = process.env.API_PORT ?? "8000";
const WEB_PORT = parseInt(process.env.WEB_PORT ?? "5173", 10);

export default defineConfig({
  plugins: [TanStackRouterVite(), react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    port: WEB_PORT,
    strictPort: false, // se a porta estiver ocupada, tenta a próxima
    proxy: {
      "/api": {
        target: `http://localhost:${API_PORT}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});

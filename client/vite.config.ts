import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  base: "/sample/ai-crm/",
  resolve: {
    alias: {
      "@src": path.resolve(__dirname, "src"),
    },
  },
  server: {
    port: 5196,
    proxy: {
      "/sample/ai-crm/api": {
        target: "http://127.0.0.1:3096",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});

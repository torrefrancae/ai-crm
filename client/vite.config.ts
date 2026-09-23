import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, rootDir, "");
  const base = env.VITE_BASE || "/sample/ai-crm/";
  const apiBase = (env.VITE_API_BASE || "/api/ai-crm").replace(/\/+$/, "");
  const sampleApi = `${base.replace(/\/+$/, "")}/api`;

  return {
    plugins: [react()],
    base,
    resolve: {
      alias: {
        "@src": path.resolve(rootDir, "src"),
      },
    },
    server: {
      port: 5196,
      proxy: {
        [apiBase]: {
          target: "http://127.0.0.1:3096",
          changeOrigin: true,
        },
        [sampleApi]: {
          target: "http://127.0.0.1:3096",
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: "dist",
      emptyOutDir: true,
    },
  };
});

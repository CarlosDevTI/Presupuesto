import path from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const rootDir = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      components: path.resolve(rootDir, "src/components"),
      pages: path.resolve(rootDir, "src/pages"),
      services: path.resolve(rootDir, "src/services"),
      store: path.resolve(rootDir, "src/store"),
      types: path.resolve(rootDir, "src/types"),
      utils: path.resolve(rootDir, "src/utils"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
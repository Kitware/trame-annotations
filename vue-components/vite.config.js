import { fileURLToPath, URL } from "node:url";

import vue from "@vitejs/plugin-vue";

export default {
  base: "./",
  build: {
    lib: {
      entry: "./src/main.js",
      name: "trame_annotations",
      formats: ["umd"],
      fileName: "trame_annotations",
    },
    rollupOptions: {
      external: ["vue"],
      output: {
        globals: {
          vue: "Vue",
        },
      },
    },
    outDir: "../src/trame_annotations/module/serve",
    assetsDir: ".",
  },
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
};

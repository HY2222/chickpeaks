import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// base "./" para que el build funcione abierto desde cualquier carpeta o subruta.
export default defineConfig({
  base: "./",
  plugins: [react(), tailwindcss()],
});

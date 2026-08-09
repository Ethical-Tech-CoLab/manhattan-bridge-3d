import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The viewer is intentionally standalone: it reads everything it needs from /public at runtime, so
// the same build can serve any source-governed GLB by swapping model.config.json.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
});

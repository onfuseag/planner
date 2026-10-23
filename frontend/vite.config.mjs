import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { fileURLToPath } from 'url'
import frappeui from 'frappe-ui/vite'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    // planner.html and the build output are managed by this app, so frappe-ui's build and boot-data plugins stay off
    frappeui({ buildConfig: false, jinjaBootData: false }),
    vue(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: `../${path.basename(path.resolve(__dirname, '..'))}/public/frontend`,
    emptyOutDir: true,
    target: 'es2015',
  },
  optimizeDeps: {
    // frappe-ui ships source with ~icons/* imports that only its vite plugin can resolve,
    // so it is served as-is and only its CommonJS dependencies are pre-bundled
    include: [
      'feather-icons',
      'prosemirror-state',
      'prosemirror-view',
      'prosemirror-gapcursor',
      'prosemirror-tables',
      'lowlight',
      'interactjs',
      'engine.io-client',
      'socket.io-client',
    ],
    exclude: ['frappe-ui'],
  },
})

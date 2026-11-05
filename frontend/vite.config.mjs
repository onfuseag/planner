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
    // Frappe UI's extensionless package imports are resolved by Vite rather
    // than esbuild's dependency scanner.
    exclude: ['frappe-ui', 'frappe-ui/editor'],
  },
})

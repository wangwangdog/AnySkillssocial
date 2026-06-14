import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { VantResolver } from 'unplugin-vue-components/resolvers'
import AutoImport from 'unplugin-auto-import/vite'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({ imports: ['vue', 'vue-router'] }),
    Components({ resolvers: [VantResolver()] }),
  ],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  base: '/skillgate/c2c/',
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:9902',
        changeOrigin: true,
      },
    },
  },
})

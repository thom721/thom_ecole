import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue' 
import path from 'path'// ou react

// export default defineConfig({
//   plugins: [
//     vue(),
//     tailwindcss(),
//   ],
// })


 // 1. Importe le module path de Node

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // 2. Définit @ comme raccourci vers le dossier 'src'
      '@': path.resolve(__dirname, './src'),
    },
  },
})
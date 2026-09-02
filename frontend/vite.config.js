import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    emptyOutDir: true,
    rollupOptions: {
      input: {
        index: 'src/pages/index.html',
        about: 'src/pages/about.html',
        contact: 'src/pages/contact.html',
        donate: 'src/pages/donate.html',
        login: 'src/pages/login.html',
        projects: 'src/pages/projects.html',
        signup: 'src/pages/signup.html',
        stories: 'src/pages/stories.html',
        support: 'src/pages/support.html'
      }
    }
  }
})

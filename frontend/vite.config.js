import { defineConfig } from 'vite'

const pageNames = ['about', 'contact', 'donate', 'login', 'projects', 'signup', 'stories', 'support']

export default defineConfig({
  plugins: [{
    name: 'clean-page-routes',
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const pathname = request.url.split('?')[0]
        const pageName = pathname === '/' ? 'index' : pathname.slice(1).replace(/\.html$/, '')

        if (pageName === 'index' || pageNames.includes(pageName)) {
          request.url = `/src/pages/${pageName}.html`
        }

        next()
      })
    }
  }],
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
  },
  test: {
    environment: 'jsdom',
  }
})

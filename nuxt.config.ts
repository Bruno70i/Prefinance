// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  nitro: {
    routeRules: {
      '/api/**': { proxy: 'http://localhost:8000/api/**' }
    }
  },
  vite: {
    server: {
      allowedHosts: true
    }
  },
  app: {
    head: {
      title: 'PreFinance - Gestão de Entidades',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' }
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap' }
      ]
    }
  },
  css: ['~/assets/css/main.css']
})

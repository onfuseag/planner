import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

import { Button, setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'

let app = createApp(App)

// Configure Frappe request with proper CSRF token handling
setConfig('resourceFetcher', frappeRequest)

// Ensure CSRF token is fetched on app load
async function initializeApp() {
  // Fetch CSRF token if not present
  if (!window.csrf_token) {
    try {
      const response = await fetch('/api/method/frappe.auth.get_logged_user', {
        credentials: 'include'
      })
      const data = await response.json()
      if (data.message) {
        // CSRF token should now be set in window.csrf_token by Frappe
      }
    } catch (error) {
      console.error('Failed to initialize CSRF token:', error)
    }
  }

  app.use(router)
  app.use(resourcesPlugin)

  app.component('Button', Button)
  app.mount('#app')
}

initializeApp()

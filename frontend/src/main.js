import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import ganttastic from '@infectoone/vue-ganttastic'

import { Button, setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)
app.use(ganttastic)

app.component('Button', Button)
app.mount('#app')

import './index.css'
import { createApp } from 'vue'
import router from "./router";
import axios from 'axios'
import VueAxios from 'vue-axios'
import App from './app.vue'

import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createPinia } from 'pinia'
import { setConfig, frappeRequest, resourcesPlugin, 
    Button, 
    Breadcrumbs,
    Avatar,  
    FormControl,
    FeatherIcon,
    Select,
    Dropdown,
    Dialog,
    Autocomplete,
} from 'frappe-ui'

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const app = createApp(App);
setConfig('resourceFetcher', frappeRequest)
app.use(router)
app.use(resourcesPlugin)
app.use(pinia)
app.use(VueAxios, axios)
app.provide('axios', app.config.globalProperties.axios)
app.component('Button', Button)
app.component('Breadcrumbs', Breadcrumbs)
app.component('Avatar', Avatar)
app.component('FormControl', FormControl)
app.component('FeatherIcon', FeatherIcon)
app.component('Select', Select)
app.component('Dropdown', Dropdown)
app.component('Dialog', Dialog)
app.component('Autocomplete', Autocomplete)
app.mount("#app");
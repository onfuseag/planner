import './index.css'
import { createApp } from 'vue'
import router from "./router";
import App from './App.vue'

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
    ErrorMessage,
    TextInput
} from 'frappe-ui'
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

const app = createApp(App);
setConfig('resourceFetcher', frappeRequest)
app.use(router)
app.use(resourcesPlugin)
app.component('Button', Button)
app.component('Breadcrumbs', Breadcrumbs)
app.component('Avatar', Avatar)
app.component('FormControl', FormControl)
app.component('FeatherIcon', FeatherIcon)
app.component('Select', Select)
app.component('Dropdown', Dropdown)
app.component('Dialog', Dialog)
app.component('Autocomplete', Autocomplete)
app.component('ErrorMessage', ErrorMessage)
app.component('TextInput', TextInput)
app.component('VueDatePicker', VueDatePicker);
app.mount("#app");
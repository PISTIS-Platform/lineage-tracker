import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import keycloakService from './services/keycloakService';


import VueAxios from 'vue-axios'
import axios from 'axios'

import App from './App.vue'
import router from './router'

import AuthStorePlugin from './plugins/authStore';

import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.css'
import bootstrap from 'bootstrap/dist/js/bootstrap'

import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faArrowRightArrowLeft,
  faDatabase,
  faHouse,
  faStore,
  faClipboardList,
  faChartLine,
  faBell,
  faBars
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import './assets/scss/custom-variables.scss'



library.add(faHouse, faDatabase, faArrowRightArrowLeft, faStore, faClipboardList, faChartLine, faBell, faBars)


// Create Pinia instance
const pinia = createPinia();

// Use persisted state with Pinia so our store data will persist even after page refresh
pinia.use(piniaPluginPersistedstate);

const renderApp = () => {
  const app = createApp(App);
  app.use(AuthStorePlugin, { pinia });
  app.use(pinia);
  app.use(router, bootstrap);
  app.use(VueAxios, axios)
  axios.defaults.withCredentials = true
  app.component('font-awesome-icon', FontAwesomeIcon).mount('#app')
}

// renderApp();
keycloakService.CallInit(renderApp)

// app.use(createPinia())


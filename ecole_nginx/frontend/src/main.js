import axios from 'axios'
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
// import 'animate.css'; 
// import './assets/main.css'


// npm install @fortawesome/fontawesome-free remixicon

 
// import '@fortawesome/fontawesome-free/css/all.min.css'
import 'remixicon/fonts/remixicon.css'
import './assets/main.css'
import './assets/public.css'

axios.defaults.baseURL = import.meta.env.VITE_APP_BASE_URL;
// axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

// // Si tu as déjà un token dans le localStorage
const token = localStorage.getItem('auth-token');
if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

axios.interceptors.request.use((config) => {
  // On récupère le token (vérifie bien le nom : 'auth-token' ou 'token')
  const token = localStorage.getItem('auth-token'); 
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  config.headers['Accept'] = 'application/json';
  return config;
}, (error) => {
  return Promise.reject(error);
});

// 3. (Optionnel) Rediriger vers login si on reçoit une 401 n'importe où
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('auth-token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// main.js ou axios.js
axios.interceptors.response.use(
  response => response,
  error => {
    // Laisser passer sans log supplémentaire
    return Promise.reject(error);
  }
);

// import ToastPlugin from '@/plugins/toast';
// app.use(ToastPlugin);
{/* <AppToast :show="toast.show" :message="toast.message" :ok="toast.ok" /> */}

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

import axios from 'axios'
import { ViteSSG } from 'vite-ssg'
import { createPinia } from 'pinia'

import App from './App.vue'
import { routes, setupRouterGuards } from './router'

import 'remixicon/fonts/remixicon.css'
import './assets/main.css'
import './assets/public.css'

axios.defaults.baseURL = import.meta.env.VITE_APP_BASE_URL;

// Le token n'existe que côté client (localStorage) — au chargement initial
// du module pendant le pré-rendu (vite-ssg, environnement Node), il n'y a
// ni window ni localStorage.
if (typeof window !== 'undefined') {
  const token = localStorage.getItem('auth-token');
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }
}

axios.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
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
    if (error.response && error.response.status === 401 && typeof window !== 'undefined') {
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

// ViteSSG crée le router lui-même (createWebHistory côté client,
// createMemoryHistory côté Node pour le pré-rendu) à partir du même
// tableau `routes` — voir router/index.js, qui n'exporte plus un router
// déjà construit pour cette raison.
export const createApp = ViteSSG(
  App,
  {
    routes,
    scrollBehavior(to, _from, savedPosition) {
      if (savedPosition) return savedPosition
      if (to.hash) return { el: to.hash, behavior: 'smooth' }
      return { top: 0, behavior: 'smooth' }
    },
  },
  ({ app, router, isClient }) => {
    app.use(createPinia())
    setupRouterGuards(router)
  },
)

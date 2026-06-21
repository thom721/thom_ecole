import { createApp, ref } from 'vue';
import AppToast from '@/components/AppToast.vue';

// Store global partagé
const globalToast = ref({ show: false, message: '', ok: true });

export const useToast = (duration = 3000) => {
  const notify  = (message, ok = true) => {
    globalToast.value = { show: true, message, ok };
    setTimeout(() => (globalToast.value.show = false), duration);
  };
  return {
    toast:   globalToast,
    notify,
    success: (msg) => notify(msg, true),
    error:   (msg) => notify(msg, false),
  };
};

// Plugin Vue
export default {
  install(app) {
    app.component('AppToast', AppToast);
    app.config.globalProperties.$toast = useToast();
  },
};
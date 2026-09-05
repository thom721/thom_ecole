import { ref } from 'vue';

export function useToast(duration = 3000) {
  const toast = ref({ show: false, message: '', ok: true });

  const notify = (message, ok = true) => {
    toast.value = { show: true, message, ok };
    setTimeout(() => (toast.value.show = false), duration);
  };

  const success = (message) => notify(message, true);
  const error   = (message) => notify(message, false);

  return { toast, notify, success, error };
}
import { reactive, toRefs } from 'vue'

const state = reactive({
  open: false,
  app:  null,
  form: { nom: '', email: '', entreprise: '', message: '' }
})

export function useDemoStore() {
  function openDemo(app) {
    state.app  = app
    state.open = true
  }
  function closeDemo() {
    state.open = false
    state.form = { nom: '', email: '', entreprise: '', message: '' }
  }
  return { ...toRefs(state), openDemo, closeDemo }
}

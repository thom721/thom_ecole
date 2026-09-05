import { ref, onMounted, onUnmounted } from 'vue'

const IDLE_MINUTES = 10
const IDLE_MS      = IDLE_MINUTES * 60 * 1000
const WARN_MS      = IDLE_MS - 60_000   // avertissement 1 min avant

// Événements considérés comme activité
const ACTIVITY_EVENTS = ['mousemove', 'keydown', 'mousedown', 'touchstart', 'scroll', 'click']

export function useIdleTimer(onLogout) {
  const showWarning  = ref(false)
  const secondsLeft  = ref(60)

  let idleTimer  = null
  let warnTimer  = null
  let countTimer = null

  const clearAllTimers = () => {
    clearTimeout(idleTimer)
    clearTimeout(warnTimer)
    clearInterval(countTimer)
  }

  const resetTimers = () => {
    clearAllTimers()
    showWarning.value = false
    secondsLeft.value = 60

    // Avertissement 1 min avant expiration
    warnTimer = setTimeout(() => {
      showWarning.value = true
      secondsLeft.value = 60
      countTimer = setInterval(() => {
        secondsLeft.value--
        if (secondsLeft.value <= 0) clearInterval(countTimer)
      }, 1000)
    }, WARN_MS)

    // Déconnexion après IDLE_MS
    idleTimer = setTimeout(() => {
      clearAllTimers()
      showWarning.value = false
      onLogout()
    }, IDLE_MS)
  }

  const handleActivity = () => {
    if (showWarning.value) return   // ne pas reset pendant le warning
    resetTimers()
  }

  const stayConnected = () => {
    resetTimers()
  }

  onMounted(() => {
    ACTIVITY_EVENTS.forEach(e => window.addEventListener(e, handleActivity, { passive: true }))
    resetTimers()
  })

  onUnmounted(() => {
    ACTIVITY_EVENTS.forEach(e => window.removeEventListener(e, handleActivity))
    clearAllTimers()
  })

  return { showWarning, secondsLeft, stayConnected }
}

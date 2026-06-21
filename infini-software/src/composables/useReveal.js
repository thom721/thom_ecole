import { onMounted, onUnmounted } from 'vue'

export function useReveal() {
  let observer = null

  function init() {
    const els = document.querySelectorAll('.reveal-hidden')
    observer = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.remove('reveal-hidden')
          observer.unobserve(e.target)
        }
      })
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' })
    els.forEach(el => observer.observe(el))
  }

  onMounted(() => setTimeout(init, 100))
  onUnmounted(() => observer?.disconnect())

  return { init }
}

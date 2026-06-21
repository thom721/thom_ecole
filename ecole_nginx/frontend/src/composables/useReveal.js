// ─────────────────────────────────────────────
//  src/composables/useReveal.js
//  Composable réutilisable pour le scroll-reveal
//  Usage : appelé dans onMounted() de chaque vue
// ─────────────────────────────────────────────
import { nextTick } from 'vue'

let observer = null

export function initReveal() {
  nextTick(() => {
    if (observer) observer.disconnect()

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) e.target.classList.add('visible')
        })
      },
      { threshold: 0.08 }
    )

    document
      .querySelectorAll('.reveal, .reveal-l, .reveal-r, .reveal-s')
      .forEach((el) => observer.observe(el))
  })
}

export function useReveal() {
  return { initReveal }
}

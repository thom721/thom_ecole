<template>
  <div
    class="cascade relative select-none"
    tabindex="0"
    role="region"
    aria-roledescription="carrousel"
    aria-label="Galerie photo"
    @mouseenter="paused = true"
    @mouseleave="paused = false"
    @keydown.left.prevent="prev"
    @keydown.right.prevent="next"
    @touchstart.passive="onTouchStart"
    @touchend.passive="onTouchEnd"
  >
    <!-- Cartes empilées en cascade : la photo active au centre, les voisines
         décalées, réduites et assombries derrière elle. -->
    <div class="cascade-stage">
      <button
        v-for="s in visible"
        :key="s.i"
        type="button"
        class="cascade-card"
        :style="cardStyle(s.d)"
        :aria-label="s.d === 0 ? `Agrandir la photo ${s.i + 1}` : `Afficher la photo ${s.i + 1}`"
        :tabindex="s.d === 0 ? 0 : -1"
        @click="s.d === 0 ? (lightbox = true) : go(s.i)"
      >
        <img
          :src="Math.abs(s.d) <= 2 ? photos[s.i].src : photos[s.i].thumb"
          :alt="`Photo ${s.i + 1} — vie universitaire à l'IUSTH`"
          class="w-full h-full object-cover block pointer-events-none"
          draggable="false"
          decoding="async"
        />
      </button>
    </div>

    <!-- Contrôles -->
    <div class="flex items-center justify-center gap-5 mt-2">
      <button type="button" class="cascade-btn" aria-label="Photo précédente" @click="prev">‹</button>
      <span class="text-sm font-semibold tabular-nums" style="color:#0B1F3A">{{ current + 1 }} / {{ photos.length }}</span>
      <button type="button" class="cascade-btn" aria-label="Photo suivante" @click="next">›</button>
    </div>
    <div class="cascade-progress mx-auto mt-4">
      <div class="cascade-progress-bar" :style="{ width: `${((current + 1) / photos.length) * 100}%` }"></div>
    </div>

    <!-- Visionneuse plein écran -->
    <Teleport to="body">
      <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                  leave-active-class="transition duration-150" leave-to-class="opacity-0">
        <div
          v-if="lightbox"
          class="fixed inset-0 z-[100] flex items-center justify-center"
          style="background:rgba(8,16,30,.94)"
          role="dialog"
          aria-modal="true"
          aria-label="Visionneuse de photos"
          @click.self="lightbox = false"
          @touchstart.passive="onTouchStart"
          @touchend.passive="onTouchEnd"
        >
          <img
            :key="photos[current].src"
            :src="photos[current].src"
            :alt="`Photo ${current + 1} sur ${photos.length}`"
            class="max-w-[92vw] max-h-[86vh] object-contain rounded-lg shadow-2xl"
          />
          <button type="button" class="lb-btn top-4 right-4" aria-label="Fermer" @click="lightbox = false">✕</button>
          <!-- Mobile : flèches en bas, à côté du compteur, pour ne pas couvrir la photo. -->
          <button type="button" class="lb-btn left-3 bottom-3 sm:bottom-auto sm:top-1/2 sm:-translate-y-1/2" aria-label="Photo précédente" @click="prev">‹</button>
          <button type="button" class="lb-btn right-3 bottom-3 sm:bottom-auto sm:top-1/2 sm:-translate-y-1/2" aria-label="Photo suivante" @click="next">›</button>
          <div class="absolute bottom-4 left-1/2 -translate-x-1/2 text-sm" style="color:rgba(255,255,255,.7)">
            {{ current + 1 }} / {{ photos.length }}
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  photos: { type: Array, required: true },
  interval: { type: Number, default: 4500 },
})

// Nombre de cartes visibles de chaque côté de la photo active.
const SIDE = 3

const current = ref(0)
const paused = ref(false)
const lightbox = ref(false)

const n = computed(() => props.photos.length)
const go = (i) => { current.value = (i + n.value) % n.value }
const next = () => go(current.value + 1)
const prev = () => go(current.value - 1)

// Écart circulaire le plus court entre une photo et la photo active.
const offset = (i) => {
  let d = i - current.value
  if (d > n.value / 2) d -= n.value
  if (d < -n.value / 2) d += n.value
  return d
}

// Rendu limité aux cartes proches (±SIDE + 1 pour l'entrée en fondu).
const visible = computed(() => {
  const out = []
  for (let d = -(SIDE + 1); d <= SIDE + 1; d++) {
    const i = ((current.value + d) % n.value + n.value) % n.value
    if (!out.some(s => s.i === i)) out.push({ i, d: offset(i) })
  }
  return out
})

function cardStyle(d) {
  const a = Math.abs(d)
  return {
    transform: `translateX(calc(-50% + ${d * 58}%)) scale(${1 - a * 0.14}) rotateY(${d * -8}deg)`,
    zIndex: 20 - a,
    opacity: a > SIDE ? 0 : 1,
    filter: a ? `brightness(${1 - a * 0.18})` : 'none',
    pointerEvents: a > SIDE ? 'none' : 'auto',
  }
}

// Défilement automatique, suspendu au survol et pendant la visionneuse.
let timer = null
onMounted(() => { timer = setInterval(() => { if (!paused.value && !lightbox.value) next() }, props.interval) })

function onKey(e) {
  if (!lightbox.value) return
  if (e.key === 'Escape') lightbox.value = false
  else if (e.key === 'ArrowRight') next()
  else if (e.key === 'ArrowLeft') prev()
}
onMounted(() => window.addEventListener('keydown', onKey))
watch(lightbox, (v) => { document.body.style.overflow = v ? 'hidden' : '' })
onBeforeUnmount(() => {
  clearInterval(timer)
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})

// Balayage horizontal sur mobile.
let touchX = 0
const onTouchStart = (e) => { touchX = e.changedTouches[0].clientX }
const onTouchEnd = (e) => {
  const dx = e.changedTouches[0].clientX - touchX
  if (Math.abs(dx) > 50) (dx < 0 ? next : prev)()
}
</script>

<style scoped>
.cascade {
  outline: none;
}
.cascade-stage {
  position: relative;
  height: clamp(380px, 56vw, 560px);
  perspective: 1400px;
  overflow: hidden;
}
.cascade-card {
  position: absolute;
  /* Marge haut/bas : l'ombre et les coins arrondis ne sont pas rognés
     par l'overflow:hidden de la scène. */
  top: 20px;
  left: 50%;
  width: clamp(230px, 34vw, 360px);
  height: calc(100% - 60px);
  padding: 0;
  border: 0;
  border-radius: 18px;
  overflow: hidden;
  cursor: pointer;
  background: #0B1F3A;
  box-shadow: 0 18px 40px rgba(11, 31, 58, .28);
  transform-origin: center center;
  transition: transform .6s cubic-bezier(.22, .8, .3, 1), opacity .6s ease, filter .6s ease;
}
.cascade-card:focus-visible {
  outline: 3px solid #D4A853;
  outline-offset: 3px;
}
.cascade-btn {
  width: 44px;
  height: 44px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  line-height: 1;
  color: #0B1F3A;
  border: 1.5px solid rgba(11, 31, 58, .18);
  background: #fff;
  transition: background .2s, color .2s, border-color .2s;
}
.cascade-btn:hover {
  background: #D4A853;
  border-color: #D4A853;
  color: #fff;
}
.cascade-progress {
  width: min(240px, 60%);
  height: 3px;
  border-radius: 9999px;
  background: rgba(11, 31, 58, .1);
  overflow: hidden;
}
.cascade-progress-bar {
  height: 100%;
  background: #D4A853;
  transition: width .6s ease;
}
.lb-btn {
  position: absolute;
  width: 44px;
  height: 44px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  line-height: 1;
  color: #fff;
  background: rgba(255, 255, 255, .12);
  transition: background .2s;
}
.lb-btn:hover {
  background: rgba(212, 168, 83, .55);
}
</style>

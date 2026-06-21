<template>
  <main class="pt-28 pb-24">
    <div class="max-w-7xl mx-auto px-6">

      <div class="text-center mb-14 reveal reveal-hidden">
        <div class="section-label justify-center mb-4">Nos Produits</div>
        <h1 class="font-syne text-5xl font-extrabold tracking-tight mb-4">Store Infini Software</h1>
        <p class="text-[#64748b] max-w-xl mx-auto">Découvrez nos applications, téléchargez-les ou demandez une démonstration personnalisée.</p>
      </div>

      <!-- Filters -->
      <div class="flex flex-wrap gap-2 justify-center mb-12 reveal reveal-hidden">
        <div ref="filterBar" class="relative flex flex-wrap gap-2 justify-center">
          <!-- Sliding pill -->
          <div class="absolute rounded-full bg-[#06b6d4] transition-all duration-300 ease-out"
            :style="pillStyle"/>
          <button v-for="(cat, i) in categories" :key="cat"
            :ref="el => { if (el) btnRefs[i] = el }"
            class="relative z-10 px-4 py-2 rounded-full text-sm font-semibold transition-colors duration-200"
            :class="selected === cat
              ? 'text-[#080c10] font-bold'
              : 'bg-[#111820] text-[#64748b] border border-[#1e2a38] hover:border-[#253040] hover:text-white'"
            @click="selectCat(cat, i)">
            {{ cat }}
          </button>
        </div>
      </div>

      <!-- Grid -->
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="(app,i) in filtered" :key="app.slug"
          class="card overflow-hidden reveal reveal-hidden" :style="`transition-delay:${i*.06}s`">
          <div class="h-44 flex items-center justify-center relative"
            :style="`background:linear-gradient(135deg,${app.bg1},${app.bg2})`">
            <span class="text-6xl">{{ app.icon }}</span>
            <div class="absolute top-3 right-3">
              <span :class="app.badgeClass" class="inline-flex items-center gap-1">
                <span v-if="app.badge === 'Nouveau'" class="relative flex h-1.5 w-1.5">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#06b6d4] opacity-75"/>
                  <span class="relative inline-flex h-1.5 w-1.5 rounded-full bg-[#06b6d4]"/>
                </span>
                {{ app.badge }}
              </span>
            </div>
          </div>
          <div class="p-6">
            <div class="flex items-start justify-between mb-2">
              <div>
                <h3 class="font-syne font-bold text-lg">{{ app.name }}</h3>
                <span class="text-xs text-[#64748b]">{{ app.category }}</span>
              </div>
              <span class="font-mono text-xs text-[#06b6d4]">v{{ app.version }}</span>
            </div>
            <p class="text-sm text-[#94a3b8] leading-relaxed mb-4">{{ app.desc }}</p>
            <div class="space-y-1.5 mb-4">
              <div v-for="f in app.features" :key="f" class="flex items-center gap-2 text-xs text-[#64748b]">
                <span class="text-[#10b981]">✓</span> {{ f }}
              </div>
            </div>
            <div class="flex flex-wrap gap-1.5 mb-5">
              <span v-for="t in app.tags" :key="t" class="tech-tag">{{ t }}</span>
            </div>
            <div class="flex gap-2">
              <div class="group relative flex-1">
                <button disabled class="btn-primary w-full justify-center text-xs py-2.5 !opacity-40 !cursor-not-allowed pointer-events-none">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                  </svg>
                  Télécharger
                </button>
                <div class="absolute -top-9 left-1/2 -translate-x-1/2 whitespace-nowrap text-[10px] bg-[#0d1219] border border-[#253040] text-[#94a3b8] px-2.5 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                  Bientôt disponible
                </div>
              </div>
              <div class="group relative">
                <button disabled class="btn-gold text-xs py-2.5 px-5 !opacity-40 !cursor-not-allowed pointer-events-none">Démo</button>
                <div class="absolute -top-9 left-1/2 -translate-x-1/2 whitespace-nowrap text-[10px] bg-[#0d1219] border border-[#253040] text-[#94a3b8] px-2.5 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                  Bientôt disponible
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </main>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useReveal }    from '@/composables/useReveal.js'
import { useDemoStore } from '@/stores/demo.js'
import { apps, categories } from '@/stores/apps.js'

const { init } = useReveal()
const demoStore = useDemoStore()
const selected  = ref('Tous')
const filtered  = computed(() =>
  selected.value === 'Tous' ? apps : apps.filter(a => a.category === selected.value)
)

watch(selected, () => nextTick(init))

const filterBar = ref(null)
const btnRefs   = ref([])
const pillStyle = ref({ opacity: '0', position: 'absolute', borderRadius: '9999px' })

function selectCat(cat, idx) {
  selected.value = cat
  nextTick(() => {
    const btn = btnRefs.value[idx]
    if (!btn) return
    pillStyle.value = {
      position: 'absolute',
      left:   btn.offsetLeft + 'px',
      top:    btn.offsetTop  + 'px',
      width:  btn.offsetWidth  + 'px',
      height: btn.offsetHeight + 'px',
      opacity: '1',
    }
  })
}

onMounted(() => nextTick(() => selectCat('Tous', 0)))
</script>

<template>
  <div class="animate-[fadeUp_0.3s_ease_both] space-y-6">

    <!-- ── Filtre année ── -->
    <div class="flex items-center justify-between gap-4 flex-wrap">
      <div>
        <h1 class="text-[17px] font-semibold text-[#e8eaf0] tracking-tight">Vue d'ensemble</h1>
        <p class="text-[12.5px] text-[#7c83a0] mt-0.5">Répartition des étudiants par année, niveau et classe</p>
      </div>
      <div class="flex items-center gap-2">
        <select
          v-model="selectedAnneeId"
          @change="chargerStats"
          class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition"
        >
          <option value="">Toutes les années</option>
          <option v-for="a in annee" :key="a.id" :value="a.id">
            {{ a.libelle ?? a.nom }}
          </option>
        </select>
        <button
          @click="chargerStats"
          class="p-2 rounded-lg border border-white/[0.1] text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.05] transition"
          title="Rafraîchir"
        >
          <svg :class="['w-4 h-4 transition-transform duration-500', loading ? 'animate-spin' : '']"
               fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- ── Skeleton loading ── -->
    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i"
           class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5 animate-pulse">
        <div class="h-4 w-32 bg-white/[0.06] rounded mb-4"></div>
        <div class="grid grid-cols-4 gap-3">
          <div v-for="j in 4" :key="j" class="h-20 bg-white/[0.04] rounded-lg"></div>
        </div>
      </div>
    </div>

    <!-- ── Contenu ── -->
    <template v-else-if="stats.length > 0">
      <div v-for="anneeData in stats" :key="anneeData.annee.id" class="space-y-4">

        <!-- Header année avec KPIs globaux -->
        <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">

          <!-- Titre année -->
          <div class="px-5 py-3.5 border-b border-white/[0.07] flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-1.5 h-5 rounded-full" :style="{ background: 'var(--accent)' }"></div>
              <h2 class="text-[14px] font-semibold text-[#e8eaf0]">
                Année {{ anneeData.annee.libelle }}
              </h2>
            </div>
            <span class="font-mono text-[12px] text-[#7c83a0]">
              {{ anneeData.total }} étudiants au total
            </span>
          </div>

          <!-- KPIs année -->
          <div class="grid grid-cols-2 sm:grid-cols-4 divide-x divide-y sm:divide-y-0 divide-white/[0.05]">
            <div class="px-5 py-4">
              <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-1.5">Total</p>
              <p class="text-[26px] font-bold font-mono text-[#e8eaf0] leading-none">{{ anneeData.total }}</p>
            </div>
            <div class="px-5 py-4">
              <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-1.5">Garçons</p>
              <p class="text-[26px] font-bold font-mono leading-none" :style="{ color: 'var(--accent)' }">
                {{ anneeData.garcons }}
              </p>
              <p class="text-[11px] text-[#7c83a0] mt-1">
                {{ pct(anneeData.garcons, anneeData.total) }}%
              </p>
            </div>
            <div class="px-5 py-4">
              <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-1.5">Filles</p>
              <p class="text-[26px] font-bold font-mono text-pink-400 leading-none">{{ anneeData.filles }}</p>
              <p class="text-[11px] text-[#7c83a0] mt-1">
                {{ pct(anneeData.filles, anneeData.total) }}%
              </p>
            </div>
            <div class="px-5 py-4">
              <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-1.5">Niveaux</p>
              <p class="text-[26px] font-bold font-mono text-[#e8eaf0] leading-none">
                {{ anneeData.niveaux.length }}
              </p>
            </div>
          </div>

          <!-- Barre de genre globale -->
          <div class="px-5 pb-4">
            <div class="flex items-center gap-2 mb-1.5">
              <span class="text-[11px] text-[#7c83a0]">Garçons</span>
              <div class="flex-1 h-2 bg-white/[0.06] rounded-full overflow-hidden flex">
                <div
                  class="h-full rounded-l-full transition-all duration-700"
                  :style="{
                    width: pct(anneeData.garcons, anneeData.total) + '%',
                    background: 'var(--accent)'
                  }"
                ></div>
                <div
                  class="h-full rounded-r-full bg-pink-500/70 transition-all duration-700"
                  :style="{ width: pct(anneeData.filles, anneeData.total) + '%' }"
                ></div>
              </div>
              <span class="text-[11px] text-[#7c83a0]">Filles</span>
            </div>
          </div>
        </div>

        <!-- Niveaux -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div
            v-for="niveauData in anneeData.niveaux"
            :key="niveauData.niveau.id"
            class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden"
          >
            <!-- Header niveau -->
            <div class="px-4 py-3 border-b border-white/[0.07] flex items-center justify-between bg-[#13161f]">
              <div class="flex items-center gap-2">
                <span class="text-[12px] font-semibold text-[#e8eaf0]">{{ niveauData.niveau.nom }}</span>
                <span class="font-mono text-[11px] px-1.5 py-0.5 rounded bg-white/[0.06] text-[#7c83a0]">
                  {{ niveauData.total }} élèves
                </span>
              </div>
              <div class="flex items-center gap-3 text-[11px]">
                <span :style="{ color: 'var(--accent)' }">♂ {{ niveauData.garcons }}</span>
                <span class="text-pink-400">♀ {{ niveauData.filles }}</span>
              </div>
            </div>

            <!-- Tableau classes du niveau -->
            <div class="divide-y divide-white/[0.04]">
              <div
                v-for="classeData in niveauData.classes"
                :key="classeData.classe.id"
                class="px-4 py-3 hover:bg-white/[0.02] transition-colors"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="text-[13px] font-medium text-[#e8eaf0]">{{ classeData.classe.nom }}</span>
                  <div class="flex items-center gap-3 text-[12px] font-mono">
                    <span :style="{ color: 'var(--accent)' }">{{ classeData.garcons }}G</span>
                    <span class="text-pink-400">{{ classeData.filles }}F</span>
                    <span class="text-[#7c83a0] font-semibold">= {{ classeData.total }}</span>
                  </div>
                </div>

                <!-- Barre stacked garçons / filles -->
                <div class="h-1.5 bg-white/[0.05] rounded-full overflow-hidden flex">
                  <div
                    class="h-full transition-all duration-700 rounded-l-full"
                    :style="{
                      width: pct(classeData.garcons, classeData.total) + '%',
                      background: 'var(--accent)',
                      opacity: '0.85'
                    }"
                  ></div>
                  <div
                    class="h-full bg-pink-500/60 transition-all duration-700"
                    :style="{ width: pct(classeData.filles, classeData.total) + '%' }"
                  ></div>
                </div>

                <!-- Mini légende pourcentages -->
                <div class="flex justify-between mt-1">
                  <span class="text-[10.5px] font-mono text-[#7c83a0]/60">
                    {{ pct(classeData.garcons, classeData.total) }}%
                  </span>
                  <span class="text-[10.5px] font-mono text-[#7c83a0]/60">
                    {{ pct(classeData.filles, classeData.total) }}%
                  </span>
                </div>
              </div>
            </div>

            <!-- Mini chart canvas par niveau -->
            <div class="px-4 pb-4 pt-2 border-t border-white/[0.05]">
              <canvas
                :id="`chart-${anneeData.annee.id}-${niveauData.niveau.id}`"
                height="120"
              ></canvas>
            </div>
          </div>
        </div>

      </div>
    </template>

    <!-- ── Vide ── -->
    <div v-else class="bg-[#171b26] border border-white/[0.07] rounded-xl p-16 text-center">
      <svg class="w-10 h-10 text-[#7c83a0]/20 mx-auto mb-3" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z"/>
      </svg>
      <p class="text-[13px] text-[#7c83a0]">Aucune donnée disponible</p>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSchoolStore } from '@/stores/schoolStore'
import axios from 'axios'

// ── Store ──────────────────────────────────────────────────────────────────
const schoolStore = useSchoolStore()
const { annee } = storeToRefs(schoolStore)

// ── State ──────────────────────────────────────────────────────────────────
const selectedAnneeId = ref('')
const loading         = ref(false)
const stats           = reactive([])

// Garder les instances Chart pour les détruire avant de recréer
const chartInstances = {}

// ── Charger les stats depuis FastAPI ──────────────────────────────────────
async function chargerStats() {
  loading.value = true

  // Détruire les anciens charts
  Object.values(chartInstances).forEach(c => c?.destroy())
  Object.keys(chartInstances).forEach(k => delete chartInstances[k])

  stats.splice(0)

  try {
    const params = {}
    if (selectedAnneeId.value) params.annee_id = selectedAnneeId.value

    const { data } = await axios.get('/stats/etudiants', { params })
    const liste = Array.isArray(data) ? data : []
    liste.forEach(d => stats.push(d))

    // Attendre le rendu DOM puis dessiner les charts
    await nextTick()
    stats.forEach(anneeData => {
      anneeData.niveaux.forEach(niveauData => {
        dessinerChart(anneeData.annee.id, niveauData)
      })
    })

  } catch (err) {
    console.error('[Dashboard] chargerStats :', err)
  } finally {
    loading.value = false
  }
}

// ── Dessiner un bar chart horizontal par niveau ────────────────────────────
async function dessinerChart(anneeId, niveauData) {
  const canvasId = `chart-${anneeId}-${niveauData.niveau.id}`
  const canvas   = document.getElementById(canvasId)
  if (!canvas) return

  // Charger Chart.js dynamiquement (si pas déjà chargé)
  if (!window.Chart) {
    await loadChartJs()
  }

  const labels  = niveauData.classes.map(c => c.classe.nom)
  const garcons = niveauData.classes.map(c => c.garcons)
  const filles  = niveauData.classes.map(c => c.filles)

  // Lire la couleur accent depuis CSS vars
  const accentColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--accent').trim() || '#4f8ef7'

  const key = canvasId
  if (chartInstances[key]) chartInstances[key].destroy()

  chartInstances[key] = new window.Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Garçons',
          data: garcons,
          backgroundColor: accentColor + 'CC',
          borderColor: accentColor,
          borderWidth: 1,
          borderRadius: 4,
          borderSkipped: false,
        },
        {
          label: 'Filles',
          data: filles,
          backgroundColor: 'rgba(244,114,182,0.75)',
          borderColor: 'rgb(244,114,182)',
          borderWidth: 1,
          borderRadius: 4,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',   // barres horizontales
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#7c83a0',
            font: { size: 11 },
            boxWidth: 10,
            boxHeight: 10,
            padding: 12,
          },
        },
        tooltip: {
          backgroundColor: '#1e2335',
          borderColor: 'rgba(255,255,255,0.08)',
          borderWidth: 1,
          titleColor: '#e8eaf0',
          bodyColor: '#a0a8c0',
          padding: 10,
          callbacks: {
            afterBody: (items) => {
              const total = items.reduce((s, i) => s + i.raw, 0)
              return [`Total : ${total}`]
            }
          }
        },
      },
      scales: {
        x: {
          stacked: false,
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#7c83a0', font: { size: 10 } },
        },
        y: {
          stacked: false,
          grid: { display: false },
          ticks: { color: '#a0a8c0', font: { size: 11 } },
        },
      },
    },
  })
}

// ── Charger Chart.js depuis CDN ────────────────────────────────────────────
function loadChartJs() {
  return new Promise((resolve, reject) => {
    if (window.Chart) { resolve(); return }
    const script   = document.createElement('script')
    script.src     = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js'
    script.onload  = resolve
    script.onerror = reject
    document.head.appendChild(script)
  })
}

// ── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => chargerStats())

onUnmounted(() => {
  Object.values(chartInstances).forEach(c => c?.destroy())
})

// ── Helper ─────────────────────────────────────────────────────────────────
const pct = (val, total) =>
  total > 0 ? Math.round((val / total) * 100) : 0
</script>

<style scoped>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px) }
  to   { opacity: 1; transform: translateY(0)   }
}
</style>

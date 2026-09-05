<template>
  <div class="animate-[fadeUp_0.3s_ease_both] space-y-5">

    <!-- ── Header + filtre ── -->
    <div class="flex items-center justify-between gap-4 flex-wrap">
      <!-- <div>
        <h1 class="text-[17px] font-semibold text-[#e8eaf0] tracking-tight">Vue d'ensemble</h1>
        <p class="text-[12.5px] text-[#7c83a0] mt-0.5">
          
        </p>
      </div> -->

        <div class="px-4 mt-2 flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center border transition-colors border-blue-500/20 bg-blue-500/10 shrink-0">
            <i class="text-[16px] ri-group-line text-blue-400"></i>
          </div>
          <div>
            <h1 class="text-[17px] font-semibold text-[#e8eaf0] tracking-tight">Vue d'ensemble</h1>
            <p class="text-[12px] text-[#7c83a0]">Répartition des étudiants par année, niveau et classe</p>
          </div>
        </div>


      <div class="flex items-center gap-2">
        <select
          v-model="selectedAnneeId"
          @change="chargerStats"
          class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition"
        >
          <option value="">Toutes les années</option>
          <option v-for="a in annee_global" :key="a.id" :value="a.id">
            {{ a.libelle ?? a.annee_academique }}
          </option>
        </select>
        <button
          @click="chargerStats"
          class="p-2 rounded-lg border border-white/[0.1] text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.05] transition"
        >
          <svg :class="['w-4 h-4', loading ? 'animate-spin' : '']"
               fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- ── Skeleton ── -->
    <div v-if="loading" class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5 animate-pulse">
      <div class="h-4 w-48 bg-white/[0.06] rounded mb-6"></div>
      <div class="h-72 bg-white/[0.03] rounded-lg"></div>
    </div>

    <template v-else-if="stats.length">

      <!-- ── KPIs globaux (toutes années ou année filtrée) ── -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
          <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-2">Total élèves</p>
          <p class="text-[28px] font-bold font-mono text-[#e8eaf0] leading-none">{{ kpis.total }}</p>
        </div>
        <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
          <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-2">Garçons</p>
          <p class="text-[28px] font-bold font-mono leading-none" :style="{ color: 'var(--accent)' }">
            {{ kpis.garcons }}
          </p>
          <p class="text-[11px] text-[#7c83a0] mt-1">{{ pct(kpis.garcons, kpis.total) }}%</p>
        </div>
        <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
          <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-2">Filles</p>
          <p class="text-[28px] font-bold font-mono text-pink-400 leading-none">{{ kpis.filles }}</p>
          <p class="text-[11px] text-[#7c83a0] mt-1">{{ pct(kpis.filles, kpis.total) }}%</p>
        </div>
        <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
          <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-2">Années</p>
          <p class="text-[28px] font-bold font-mono text-[#e8eaf0] leading-none">{{ stats.length }}</p>
          <p class="text-[11px] text-[#7c83a0] mt-1">{{ kpis.niveaux }} niveaux</p>
        </div>
      </div>

      <!-- ── Charte principale + Breadcrumb + Drill-down ── -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">

        <!-- Toolbar -->
        <div class="px-5 py-3.5 border-b border-white/[0.07] flex items-center justify-between gap-3 flex-wrap">

          <!-- Breadcrumb de navigation -->
          <div class="flex items-center gap-1.5 text-[12.5px] min-w-0">
            <button
              @click="resetDrill"
              :class="['font-medium transition-colors', drillLevel === 0
                ? 'text-[var(--accent)]'
                : 'text-[#7c83a0] hover:text-[#e8eaf0]']"
            >Années</button>

            <template v-if="drillLevel >= 1">
              <svg class="w-3 h-3 text-[#7c83a0]/40 shrink-0" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
              </svg>
              <button
                @click="goToNiveaux"
                :class="['font-medium truncate max-w-[120px] transition-colors', drillLevel === 1
                  ? 'text-[var(--accent)]'
                  : 'text-[#7c83a0] hover:text-[#e8eaf0]']"
              >{{ drillAnneeLabel }}</button>
            </template>

            <template v-if="drillLevel >= 2">
              <svg class="w-3 h-3 text-[#7c83a0]/40 shrink-0" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
              </svg>
              <span class="text-[var(--accent)] font-medium truncate max-w-[120px]">
                {{ drillNiveauLabel }}
              </span>
            </template>
          </div>

          <!-- Légende + hint -->
          <div class="flex items-center gap-4 shrink-0">
            <div class="flex items-center gap-3 text-[11.5px]">
              <span class="flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-sm" :style="{ background: 'var(--accent)' }"></span>
                <span class="text-[#7c83a0]">Garçons</span>
              </span>
              <span class="flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-sm bg-pink-500/80"></span>
                <span class="text-[#7c83a0]">Filles</span>
              </span>
            </div>
            <span v-if="drillLevel < 2"
                  class="text-[11px] text-[#7c83a0]/60 hidden sm:block">
              Cliquez sur une barre pour explorer →
            </span>
          </div>
        </div>

        <!-- Canvas Chart.js -->
        <div class="p-5">
          <div style="position:relative" :style="{ height: chartHeight + 'px' }">
            <canvas id="chart-main"></canvas>
          </div>
        </div>

        <!-- Panel détail inline (apparaît sous la charte après clic) -->
        <Transition
          enter-active-class="transition-all duration-300 ease-out overflow-hidden"
          enter-from-class="opacity-0 max-h-0"
          enter-to-class="opacity-100 max-h-[500px]"
          leave-active-class="transition-all duration-200 ease-in overflow-hidden"
          leave-from-class="opacity-100 max-h-[500px]"
          leave-to-class="opacity-0 max-h-0"
        >
          <div v-if="detailVisible" class="border-t border-white/[0.07]">

            <!-- Header du panel -->
            <div class="px-5 py-3 bg-[#13161f] flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-1 h-4 rounded-full" :style="{ background: 'var(--accent)' }"></div>
                <span class="text-[13px] font-semibold text-[#e8eaf0]">{{ detailTitle }}</span>
                <span class="font-mono text-[11px] px-1.5 py-0.5 rounded bg-white/[0.06] text-[#7c83a0]">
                  {{ detailTotal }} élèves
                </span>
              </div>
              <div class="flex items-center gap-3 text-[11.5px]">
                <span :style="{ color: 'var(--accent)' }">♂ {{ detailGarcons }} ({{ pct(detailGarcons, detailTotal) }}%)</span>
                <span class="text-pink-400">♀ {{ detailFilles }} ({{ pct(detailFilles, detailTotal) }}%)</span>
              </div>
            </div>

            <!-- Rows détail -->
            <div class="divide-y divide-white/[0.04] max-h-64 overflow-y-auto">
              <div
                v-for="row in detailRows" :key="row.id"
                class="flex items-center gap-4 px-5 py-3 hover:bg-white/[0.02] transition-colors"
              >
                <span class="text-[13px] font-medium text-[#e8eaf0] w-36 shrink-0 truncate">
                  {{ row.nom }}
                </span>
                <div class="flex-1 flex items-center gap-2">
                  <!-- Barre stacked -->
                  <div class="flex-1 h-2 bg-white/[0.05] rounded-full overflow-hidden flex">
                    <div
                      class="h-full rounded-l-full transition-all duration-500"
                      :style="{
                        width: pct(row.garcons, row.total) + '%',
                        background: 'var(--accent)',
                        opacity: '0.85'
                      }"
                    ></div>
                    <div
                      class="h-full bg-pink-500/60 transition-all duration-500"
                      :style="{ width: pct(row.filles, row.total) + '%' }"
                    ></div>
                  </div>
                </div>
                <div class="flex items-center gap-2.5 text-[12px] font-mono shrink-0">
                  <span :style="{ color: 'var(--accent)' }">{{ row.garcons }}G</span>
                  <span class="text-pink-400">{{ row.filles }}F</span>
                  <span class="text-[#7c83a0] font-semibold w-8 text-right">{{ row.total }}</span>
                </div>
              </div>
            </div>

            <!-- Barre genre globale du détail -->
            <div class="px-5 py-3 bg-[#13161f]/60 border-t border-white/[0.04]">
              <div class="flex items-center gap-2">
                <span class="text-[10.5px] text-[#7c83a0] w-12 text-right">♂</span>
                <div class="flex-1 h-2 bg-white/[0.05] rounded-full overflow-hidden flex">
                  <div
                    class="h-full rounded-l-full transition-all duration-700"
                    :style="{ width: pct(detailGarcons, detailTotal) + '%', background: 'var(--accent)' }"
                  ></div>
                  <div
                    class="h-full bg-pink-500/60 transition-all duration-700"
                    :style="{ width: pct(detailFilles, detailTotal) + '%' }"
                  ></div>
                </div>
                <span class="text-[10.5px] text-[#7c83a0] w-12">♀</span>
              </div>
            </div>
          </div>
        </Transition>

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
import { ref, reactive, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSchoolStore,useSchoolStoreInfo } from '@/stores/schoolStore'
import axios from 'axios' 
const {annee_global} =useSchoolStoreInfo()
// ── Store ──────────────────────────────────────────────────────────────────
const schoolStore = useSchoolStore()
const { annee } = storeToRefs(schoolStore)

// ── State ──────────────────────────────────────────────────────────────────
const selectedAnneeId = ref('')
const loading         = ref(false)
const stats           = reactive([])   // données brutes de l'API

// Drill-down
// level 0 = années, level 1 = niveaux d'une année, level 2 = classes d'un niveau
const drillLevel      = ref(0)
const drillAnneeId    = ref(null)
const drillNiveauId   = ref(null)
const drillAnneeLabel = ref('')
const drillNiveauLabel= ref('')

// Détail panel
const detailVisible = ref(false)
const detailTitle   = ref('')
const detailRows    = ref([])   // [{ id, nom, garcons, filles, total }]

let chartInstance = null

// ── KPIs globaux ───────────────────────────────────────────────────────────
const kpis = computed(() => {
  let total = 0, garcons = 0, filles = 0, niveaux = 0
  stats.forEach(a => {
    total   += a.total
    garcons += a.garcons
    filles  += a.filles
    niveaux += a.niveaux.length
  })
  return { total, garcons, filles, niveaux }
})

// Détail panel agrégats
const detailTotal   = computed(() => detailRows.value.reduce((s, r) => s + r.total,   0))
const detailGarcons = computed(() => detailRows.value.reduce((s, r) => s + r.garcons, 0))
const detailFilles  = computed(() => detailRows.value.reduce((s, r) => s + r.filles,  0))

// Hauteur adaptative de la charte
const chartHeight = computed(() => {
  if (drillLevel.value === 0) return Math.max(260, stats.length * 60)
  if (drillLevel.value === 1) {
    const a = stats.find(a => a.annee.id === drillAnneeId.value)
    return Math.max(220, (a?.niveaux.length ?? 4) * 60)
  }
  const a = stats.find(a => a.annee.id === drillAnneeId.value)
  const n = a?.niveaux.find(n => n.niveau.id === drillNiveauId.value)
  return Math.max(200, (n?.classes.length ?? 4) * 55)
})

// ── Charger les données API ────────────────────────────────────────────────
async function chargerStats() {
  loading.value = true
  destroyChart()
  stats.splice(0)
  resetDrill(false)

  try {
    const params = {}
    if (selectedAnneeId.value) params.annee_id = selectedAnneeId.value

    const { data } = await axios.get('/stats/etudiants', { params })
    ;(Array.isArray(data) ? data : []).forEach(d => stats.push(d))

    // Désactiver le skeleton AVANT de dessiner pour que le canvas soit dans le DOM
    loading.value = false
    await nextTick()
    await nextTick()
    dessinerChartAnnees()

  } catch (err) {
    console.error('[Dashboard] chargerStats :', err)
  } finally {
    loading.value = false
  }
}

// ══════════════════════════════════════════════════════════════════════════
//  NAVIGATION DRILL-DOWN
// ══════════════════════════════════════════════════════════════════════════

// Clic sur une barre → descendre d'un niveau
function onBarClick(index) {
  if (drillLevel.value === 0) {
    // Années → Niveaux
    const anneeData = stats[index]
    if (!anneeData) return
    drillAnneeId.value    = anneeData.annee.id
    drillAnneeLabel.value = anneeData.annee.libelle
    drillLevel.value      = 1
    detailVisible.value   = false

    // Panel : niveaux de cette année
    detailTitle.value = `Niveaux — ${anneeData.annee.libelle}`
    detailRows.value  = anneeData.niveaux.map(n => ({
      id:      n.niveau.id,
      nom:     n.niveau.nom,
      garcons: n.garcons,
      filles:  n.filles,
      total:   n.total,
    }))
    detailVisible.value = true

    nextTick(() => dessinerChartNiveaux(anneeData))

  } else if (drillLevel.value === 1) {
    // Niveaux → Classes
    const anneeData  = stats.find(a => a.annee.id === drillAnneeId.value)
    const niveauData = anneeData?.niveaux[index]
    if (!niveauData) return
    drillNiveauId.value    = niveauData.niveau.id
    drillNiveauLabel.value = niveauData.niveau.nom
    drillLevel.value       = 2

    // Panel : classes de ce niveau
    detailTitle.value = `Classes — ${niveauData.niveau.nom}`
    detailRows.value  = niveauData.classes.map(c => ({
      id:      c.classe.id,
      nom:     c.classe.nom,
      garcons: c.garcons,
      filles:  c.filles,
      total:   c.total,
    }))
    detailVisible.value = true

    nextTick(() => dessinerChartClasses(niveauData))
  }
  // level 2 = feuille, plus de drill
}

function resetDrill(redraw = true) {
  drillLevel.value      = 0
  drillAnneeId.value    = null
  drillNiveauId.value   = null
  drillAnneeLabel.value = ''
  drillNiveauLabel.value= ''
  detailVisible.value   = false
  detailRows.value      = []
  if (redraw && stats.length) nextTick(() => dessinerChartAnnees())
}

function goToNiveaux() {
  if (drillLevel.value < 1) return
  drillNiveauId.value    = null
  drillNiveauLabel.value = ''
  drillLevel.value       = 1

  const anneeData = stats.find(a => a.annee.id === drillAnneeId.value)
  if (!anneeData) return

  detailTitle.value = `Niveaux — ${anneeData.annee.libelle}`
  detailRows.value  = anneeData.niveaux.map(n => ({
    id: n.niveau.id, nom: n.niveau.nom,
    garcons: n.garcons, filles: n.filles, total: n.total,
  }))
  detailVisible.value = true
  nextTick(() => dessinerChartNiveaux(anneeData))
}

// ══════════════════════════════════════════════════════════════════════════
//  RENDU DES CHARTES
// ══════════════════════════════════════════════════════════════════════════

async function dessinerChartAnnees() {
  await ensureChartJs()
  const labels  = stats.map(a => a.annee.libelle)
  const garcons = stats.map(a => a.garcons)
  const filles  = stats.map(a => a.filles)
  dessiner(labels, garcons, filles, 'Années — cliquez pour explorer')
}

async function dessinerChartNiveaux(anneeData) {
  await ensureChartJs()
  const labels  = anneeData.niveaux.map(n => n.niveau.nom)
  const garcons = anneeData.niveaux.map(n => n.garcons)
  const filles  = anneeData.niveaux.map(n => n.filles)
  dessiner(labels, garcons, filles, `${anneeData.annee.libelle} — Niveaux`)
}

async function dessinerChartClasses(niveauData) {
  await ensureChartJs()
  const labels  = niveauData.classes.map(c => c.classe.nom)
  const garcons = niveauData.classes.map(c => c.garcons)
  const filles  = niveauData.classes.map(c => c.filles)
  dessiner(labels, garcons, filles, `${niveauData.niveau.nom} — Classes`, false)
}

// Fonction centrale de rendu Chart.js
function dessiner(labels, garcons, filles, subtitle, clickable = true) {
  destroyChart()
  const canvas = document.getElementById('chart-main')
  if (!canvas) return

  const accent = getAccent()

  chartInstance = new window.Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label:            'Garçons',
          data:             garcons,
          backgroundColor:  accent + 'BB',
          borderColor:      accent,
          borderWidth:      1,
          borderRadius:     5,
          borderSkipped:    false,
          hoverBackgroundColor: accent + 'EE',
        },
        {
          label:            'Filles',
          data:             filles,
          backgroundColor:  'rgba(244,114,182,0.70)',
          borderColor:      'rgba(244,114,182,0.9)',
          borderWidth:      1,
          borderRadius:     5,
          borderSkipped:    false,
          hoverBackgroundColor: 'rgba(244,114,182,0.9)',
        },
      ],
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      indexAxis:           'y',
      interaction:         { mode: 'index', intersect: false },

      onClick: clickable
        ? (evt, elements) => {
            if (elements.length > 0) onBarClick(elements[0].index)
          }
        : undefined,

      onHover: (evt, elements) => {
        evt.native.target.style.cursor =
          clickable && elements.length > 0 ? 'pointer' : 'default'
      },

      plugins: {
        legend: {
          display: false,    // légende gérée manuellement dans le toolbar
        },
        tooltip: {
          backgroundColor: '#1e2335',
          borderColor:     'rgba(255,255,255,0.08)',
          borderWidth:     1,
          titleColor:      '#e8eaf0',
          bodyColor:       '#a0a8c0',
          padding:         12,
          callbacks: {
            afterBody: (items) => {
              const total = items.reduce((s, i) => s + i.raw, 0)
              const g = items.find(i => i.dataset.label === 'Garçons')?.raw ?? 0
              const f = items.find(i => i.dataset.label === 'Filles')?.raw  ?? 0
              return [
                `Total : ${total}`,
                `${pct(g, total)}% garçons / ${pct(f, total)}% filles`,
                clickable ? '→ Cliquez pour voir le détail' : '',
              ].filter(Boolean)
            }
          }
        },
        subtitle: {
          display: true,
          text:    subtitle,
          color:   '#7c83a0',
          font:    { size: 11 },
          padding: { bottom: 8 },
        },
      },

      scales: {
        x: {
          stacked: false,
          grid:    { color: 'rgba(255,255,255,0.04)' },
          ticks:   { color: '#7c83a0', font: { size: 10 } },
        },
        y: {
          stacked: false,
          grid:    { display: false },
          ticks:   { color: '#a0a8c0', font: { size: 11 } },
        },
      },

      animation: {
        duration: 450,
        easing:   'easeOutQuart',
      },
    },
  })
}

// ── Helpers ────────────────────────────────────────────────────────────────
const pct = (val, total) => total > 0 ? Math.round((val / total) * 100) : 0

const getAccent = () =>
  getComputedStyle(document.documentElement)
    .getPropertyValue('--accent').trim() || '#4f8ef7'

function destroyChart() {
  if (chartInstance) { chartInstance.destroy(); chartInstance = null }
}

function ensureChartJs() {
  return new Promise((resolve, reject) => {
    if (window.Chart) { resolve(); return }
    const s = document.createElement('script')
    s.src   = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js'
    s.onload  = resolve
    s.onerror = reject
    document.head.appendChild(s)
  })
}

// ── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => chargerStats())
onUnmounted(() => destroyChart())
</script>

<style scoped>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px) }
  to   { opacity: 1; transform: translateY(0)   }
}
</style>

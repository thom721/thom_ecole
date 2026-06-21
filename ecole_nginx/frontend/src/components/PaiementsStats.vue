<template>
  <div class="animate-[fadeUp_0.3s_ease_both] space-y-5">

    <!-- ── Header + filtres ── -->
    <div class="flex items-center justify-between gap-4 flex-wrap">
    <div class="px-4 mt-4 flex items-center gap-3">
  <div class="w-9 h-9 rounded-xl flex items-center justify-center border transition-colors border-emerald-500/20 bg-emerald-500/10 shrink-0">
    <i class="text-[16px] ri-bank-card-line text-emerald-400"></i>
  </div>
  <div>
    <h1 class="text-[17px] font-semibold text-[#e8eaf0] tracking-tight">Paiements</h1>
    <p class="text-[12px] text-[#7c83a0]">Suivi des encaissements par année et par mois</p>
  </div>
</div>
      <!-- {{ statsAnnee.mois }} -->
      <div class="flex items-center gap-2 mt-2">
        <!-- Sélecteur année académique -->
        <select
          v-model="selectedAnnee"
          @change="chargerStats"
          class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition min-w-[130px]"
        >
          <option value="">-- Année --</option>
          <option v-for="a in anneesDisponibles" :key="a" :value="a">{{ a }}</option>
        </select>

        <select v-if="statsAnnee"
          v-model="selectedMois"
          @change.stop="chargerJournalier"
          class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition min-w-[130px]"
        >
          <option value="">Mois</option>
          <option v-for="a in statsAnnee?.mois" :key="a.mois_key" :value="a.mois_key">{{ a.mois }}</option>
        </select>


        <button
          @click="chargerStats"
          :disabled="loading"
          class="p-2 rounded-lg border border-white/[0.1] text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.05] transition disabled:opacity-40"
        >
          <svg :class="['w-4 h-4', loading ? 'animate-spin' : '']"
               fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
        </button>
      </div>
    </div>

    <div v-if="statsAnnee3 != null" class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
        <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-2">Total annuel</p>
        <p class="text-[22px] font-bold font-mono leading-none" :style="{ color: 'var(--accent)' }">
          {{ fmt(statsAnnee.total_annuel) }}
        </p>
        <p class="text-[11.5px] text-[#7c83a0] mt-1.5">{{ statsAnnee.devise }}</p>
      </div>
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
        <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-2">Mois actifs</p>
        <p class="text-[22px] font-bold font-mono text-[#e8eaf0] leading-none">{{ statsAnnee.nb_mois }}</p>
        <p class="text-[11.5px] text-[#7c83a0] mt-1.5">mois avec versements</p>
      </div>
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
        <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-2">Versements</p>
        <p class="text-[22px] font-bold font-mono text-[#e8eaf0] leading-none">
          {{ statsAnnee.mois.reduce((s, m) => s + m.nb_versements, 0) }}
        </p>
        <p class="text-[11.5px] text-[#7c83a0] mt-1.5">transactions totales</p>
      </div>
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
        <p class="text-[11px] uppercase tracking-wider text-[#7c83a0] font-semibold mb-2">Moy. / mois</p>
        <p class="text-[22px] font-bold font-mono text-emerald-400 leading-none">
          {{ fmt(statsAnnee.nb_mois > 0 ? statsAnnee.total_annuel / statsAnnee.nb_mois : 0) }}
        </p>
        <p class="text-[11.5px] text-[#7c83a0] mt-1.5">{{ statsAnnee.devise }}</p>
      </div>
    </div>

    <!-- ── Skeleton ── -->
    <div v-if="loading" class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5 animate-pulse">
      <div class="h-4 w-40 bg-white/[0.06] rounded mb-6"></div>
      <div class="h-52 bg-white/[0.03] rounded-lg"></div>
    </div>

    <!-- ── Chart principal : masqué (canvas vide) ── -->

    <!-- ── Tableau des mois ── -->
    <div v-if="statsAnnee2 != null" class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
      <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between cursor-pointer select-none"
           @click="showDetailMois = !showDetailMois">
        <span class="text-[13.5px] font-medium text-[#e8eaf0]">Détail par mois</span>
        <svg :class="['w-4 h-4 text-[#7c83a0] transition-transform duration-200', showDetailMois ? 'rotate-180' : '']"
             fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
      </div>
      <table v-if="showDetailMois" class="w-full">
        <thead>
          <tr class="bg-[#13161f]">
            <th v-for="h in ['Mois','Versements','Total','% du total','']" :key="h"
                class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">
              {{ h }}
            </th>
          </tr>
        </thead>
        <tbody>
          <template v-for="m in statsAnnee.mois" :key="m.mois_key">
            <!-- Ligne mois -->
            <tr
              @click="toggleMois(m.mois_key)"
              class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors cursor-pointer"
              :class="moisOuvert === m.mois_key ? 'bg-white/[0.03]' : ''"
            >
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <svg :class="['w-3 h-3 text-[#7c83a0] transition-transform duration-200',
                    moisOuvert === m.mois_key ? 'rotate-90' : '']"
                    fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
                  </svg>
                  <span class="text-[13.5px] font-medium text-[#e8eaf0]">{{ m.mois }}</span>
                </div>
              </td>
              <td class="px-4 py-3 font-mono text-[13px] text-[#7c83a0]">{{ m.nb_versements }}</td>
              <td class="px-4 py-3 font-mono text-[13.5px] font-semibold" :style="{ color: 'var(--accent)' }">
                {{ fmt(m.total) }} <span class="text-[11px] font-normal text-[#7c83a0]">{{ m.devise }}</span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-20 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-700"
                         :style="{
                           width: pct(m.total, statsAnnee.total_annuel) + '%',
                           background: 'var(--accent)'
                         }"></div>
                  </div>
                  <span class="text-[12px] font-mono text-[#7c83a0]">
                    {{ pct(m.total, statsAnnee.total_annuel) }}%
                  </span>
                </div>
              </td>
              <td class="px-4 py-3">
                <button
                  @click.stop="chargerJournalier(m.mois_key)"
                  class="text-[11.5px] px-2.5 py-1 rounded-lg border border-white/[0.1] text-[#7c83a0] hover:text-[#e8eaf0] hover:border-white/[0.2] transition-colors"
                >
                  Détail jour 
                </button>
              </td>
            </tr>

            <!-- Ligne expandée : versements du mois -->
            <Transition
              enter-active-class="transition-all duration-200 ease-out"
              enter-from-class="opacity-0"
              enter-to-class="opacity-100"
              leave-active-class="transition-all duration-150"
              leave-to-class="opacity-0"
            >
              <tr v-if="moisOuvert === m.mois_key" class="bg-[#0f1117]">
                <td colspan="5" class="px-6 py-3">
                  <div class="space-y-1.5 max-h-48 overflow-y-auto">
                    <div
                      v-for="d in m.details" :key="d.date"
                      class="flex items-center justify-between py-1.5 border-b border-white/[0.04] last:border-0"
                    >
                      <div class="flex items-center gap-3">
                        <span class="font-mono text-[11px] text-[#7c83a0] w-36">{{ d.date }}</span>
                        <span class="text-[12.5px] text-[#a0a8c0]">{{ d.employer }}</span>
                        <span v-if="d.aide" class="text-[11px] px-1.5 py-0.5 rounded bg-white/[0.05] text-[#7c83a0]">
                          {{ d.aide }}
                        </span>
                      </div>
                      <span class="font-mono text-[13px] font-semibold" :style="{ color: 'var(--accent)' }">
                        + {{ fmt(d.depot) }} {{ d.devise }}
                      </span>
                    </div>
                  </div>
                </td>
              </tr>
            </Transition>
          </template>
        </tbody>
      </table>
    </div>

    <!-- ── Drill-down journalier (modal/panel) ── -->
    <Transition
      enter-active-class="transition-all duration-250 ease-out"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200"
      leave-to-class="opacity-0 translate-y-4"
    >
      <div v-if="statsJour" class="bg-[#171b26] border border-[var(--accent)]/30 rounded-xl overflow-hidden">
        <div class="px-5 py-3.5 border-b border-white/[0.07] flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-1.5 h-4 rounded-full bg-emerald-500"></div>
            <span class="text-[13.5px] font-medium text-[#e8eaf0]">
              Détail journalier — {{ moisJourLabel }}
            </span>
            <span class="font-mono text-[12px] px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400">
              {{ fmt(statsJour.total) }} {{ statsAnnee?.devise }}
            </span>
          </div>
          <button @click="statsJour = null"
                  class="w-6 h-6 flex items-center justify-center rounded text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] transition">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Chart journalier -->
        <div class="p-5">
          <div style="position:relative; height:200px">
            <canvas id="chart-journalier"></canvas>
          </div>
        </div>

        <!-- Tableau jours -->
        <div class="border-t border-white/[0.07]">
          <div class="px-5 py-2.5 flex items-center justify-between cursor-pointer select-none hover:bg-white/[0.02] transition-colors"
               @click="showTableJournalier = !showTableJournalier">
            <span class="text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">Détail journalier</span>
            <svg :class="['w-3.5 h-3.5 text-[#7c83a0] transition-transform duration-200', showTableJournalier ? 'rotate-180' : '']"
                 fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
            </svg>
          </div>
          <table v-if="showTableJournalier" class="w-full">
            <thead>
              <tr class="bg-[#13161f]">
                <th v-for="h in ['Date','Versements','Total']" :key="h"
                    class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">{{ h }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="j in statsJour.jours" :key="j.date"
                  class="border-t border-white/[0.05] hover:bg-white/[0.02] transition-colors">
                <td class="px-4 py-3 font-mono text-[13px] text-[#a0a8c0]">{{ j.date }}</td>
                <td class="px-4 py-3 font-mono text-[13px] text-[#7c83a0]">{{ j.nb_versements }}</td>
                <td class="px-4 py-3 font-mono text-[13.5px] font-semibold text-emerald-400">
                  {{ fmt(j.total) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </Transition>
    
    <!-- ── Vide ── -->
    <div v-if="!loading && !statsJour"
         class="bg-[#171b26] border border-white/[0.07] rounded-xl p-16 text-center">
      <svg class="w-10 h-10 text-[#7c83a0]/20 mx-auto mb-3" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75"/>
      </svg>
      <p class="text-[13px] text-[#7c83a0]">Sélectionnez une année académique</p>
    </div> 
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const props= defineProps({
  annee:{
    type:Object
  }
})
const statsAnnee1 =ref(null)
const statsAnnee2 =ref(null)
const statsAnnee3 =ref(null)

const showDetailMois      = ref(false)
const showTableJournalier = ref(false)

import { useSchoolStoreInfo } from '@/stores/schoolStore';
const {annee_global} =useSchoolStoreInfo()
const now = new Date()
const dMois = ref(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`)

// ── State ──────────────────────────────────────────────────────────────────
const selectedAnnee      = ref('')
const selectedMois      = ref(dMois.value)
const anneesDisponibles  = ref(annee_global)
const loading            = ref(false)
const statsAnnee         = ref(null)
const statsJour          = ref(null)
const moisOuvert         = ref(null)
const moisJourLabel      = ref('')

let chartAnnuel     = null
let chartJournalier = null

// ── Charger la liste des années disponibles depuis l'API ───────────────────
async function chargerAnnees() {
  try {
    const { data } = await axios.get('/paiements/stats/annees')
    anneesDisponibles.value = data
    if (data.length > 0) {
      selectedAnnee.value = data[0]   // sélectionner la plus récente
      await chargerStats()
    }
  } catch (err) {
    console.error('[Paiements] chargerAnnees :', err)
  }
}

// ── Charger les stats annuelles ────────────────────────────────────────────
async function chargerStats() {
  if (!selectedAnnee.value) return

  loading.value   = true
  statsAnnee.value  = null
  statsAnnee1.value = null
  statsAnnee2.value = null
  statsAnnee3.value = null
  statsJour.value   = null
  moisOuvert.value  = null

  destroyCharts()

  try {
    const { data } = await axios.get('/paiements/stats/annuel', {
      params: { annee_academique: selectedAnnee.value }
    })
    statsAnnee.value  = data
    statsAnnee1.value = data
    statsAnnee2.value = data
    statsAnnee3.value = data

    // Désactiver le skeleton AVANT de dessiner pour que le canvas soit dans le DOM
    loading.value = false
    await nextTick()
    await nextTick()
    dessinerChartAnnuel(data)

    // Charger automatiquement le mois courant
    await chargerJournalier()

  } catch (err) {
    console.error('[Paiements] chargerStats :', err)
  } finally {
    loading.value = false
  }
}

// ── Toggle détail mois dans le tableau ────────────────────────────────────
function toggleMois(moisKey) {
  moisOuvert.value = moisOuvert.value === moisKey ? null : moisKey
}

// ── Charger le drill-down journalier ──────────────────────────────────────
async function chargerJournalier() {
  statsJour.value   = null
  moisJourLabel.value = ''

  if (chartJournalier) { chartJournalier.destroy(); chartJournalier = null }

  try {
    const { data } = await axios.get('/paiements/stats/journalier', {
      params: {
        annee_academique: selectedAnnee.value,
        mois:             selectedMois.value,
      }
    })
    statsJour.value = data

    // Label lisible
    const moisObj = statsAnnee.value?.mois?.find(m => m.mois_key === selectedMois.value)
    moisJourLabel.value = moisObj?.mois ?? selectedMois.value

    await nextTick()
    dessinerChartJournalier(data)

  } catch (err) {
    console.error('[Paiements] chargerJournalier :', err)
  }
}

// ── Chart annuel (barres par mois) ────────────────────────────────────────
async function dessinerChartAnnuel(data) {
  if (!data?.mois?.length) return
  await ensureChartJs()

  const canvas = document.getElementById('chart-annuel')
  if (!canvas) return
  if (chartAnnuel) { chartAnnuel.destroy(); chartAnnuel = null }

  const accent = getAccent()
  const labels = data.mois.map(m => m.mois)
  const totaux = data.mois.map(m => m.total)
  const max    = Math.max(...totaux)

  chartAnnuel = new window.Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label:           'Encaissements',
        data:            totaux,
        backgroundColor: totaux.map(v =>
          v === max
            ? accent + 'FF'
            : accent + '80'
        ),
        borderColor:     accent,
        borderWidth:     1,
        borderRadius:    6,
        borderSkipped:   false,
        hoverBackgroundColor: accent + 'DD',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onClick: (evt, elements) => {
        if (elements.length > 0) {
          const idx = elements[0].index
          chargerJournalier(data.mois[idx].mois_key)
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1e2335',
          borderColor:     'rgba(255,255,255,0.08)',
          borderWidth:     1,
          titleColor:      '#e8eaf0',
          bodyColor:       '#a0a8c0',
          padding:         12,
          callbacks: {
            label: (ctx) => ` ${fmt(ctx.raw)} ${data.devise}`,
            afterLabel: (ctx) => {
              const m = data.mois[ctx.dataIndex]
              return ` ${m.nb_versements} versement(s) — ${pct(m.total, data.total_annuel)}% du total`
            }
          }
        },
      },
      scales: {
        x: {
          grid:  { display: false },
          ticks: { color: '#7c83a0', font: { size: 11 } },
        },
        y: {
          grid:  { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            color: '#7c83a0',
            font:  { size: 10 },
            callback: v => fmtK(v),
          },
        },
      },
      animation: {
        duration: 600,
        easing:   'easeOutQuart',
      },
    }
  })
}

// ── Chart journalier (ligne par jour) ─────────────────────────────────────
async function dessinerChartJournalier(data) {
  if (!data?.jours?.length) return
  await ensureChartJs()

  const canvas = document.getElementById('chart-journalier')
  if (!canvas) return
  if (chartJournalier) { chartJournalier.destroy(); chartJournalier = null }

  const accent = getAccent()

  chartJournalier = new window.Chart(canvas, {
    type: 'line',
    data: {
      labels:   data.jours.map(j => j.date),
      datasets: [{
        label:           'Encaissements',
        data:            data.jours.map(j => j.total),
        borderColor:     '#10b981',
        backgroundColor: 'rgba(16,185,129,0.12)',
        pointBackgroundColor: '#10b981',
        pointRadius:     5,
        pointHoverRadius: 7,
        borderWidth:     2,
        fill:            true,
        tension:         0.4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1e2335',
          borderColor:     'rgba(255,255,255,0.08)',
          borderWidth:     1,
          titleColor:      '#e8eaf0',
          bodyColor:       '#a0a8c0',
          padding:         10,
          callbacks: {
            label: ctx => ` ${fmt(ctx.raw)} ${statsAnnee.value?.devise ?? 'GDES'}`
          }
        },
      },
      scales: {
        x: {
          grid:  { display: false },
          ticks: { color: '#7c83a0', font: { size: 10 } },
        },
        y: {
          grid:  { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            color: '#7c83a0',
            font:  { size: 10 },
            callback: v => fmtK(v),
          },
        },
      },
      animation: { duration: 500, easing: 'easeOutCubic' },
    }
  })
}

// ── Helpers ────────────────────────────────────────────────────────────────
const pct = (val, total) => total > 0 ? Math.round((val / total) * 100) : 0

const fmt  = (v) => new Intl.NumberFormat('fr-HT').format(Math.round(v ?? 0))

const fmtK = (v) => {
  if (v >= 1_000_000) return (v / 1_000_000).toFixed(1) + 'M'
  if (v >= 1_000)     return (v / 1_000).toFixed(0) + 'k'
  return v
}

const getAccent = () =>
  getComputedStyle(document.documentElement)
    .getPropertyValue('--accent').trim() || '#4f8ef7'

function destroyCharts() {
  if (chartAnnuel)     { chartAnnuel.destroy();     chartAnnuel     = null }
  if (chartJournalier) { chartJournalier.destroy(); chartJournalier = null }
}

function ensureChartJs() {
  return new Promise((resolve, reject) => {
    if (window.Chart) { resolve(); return }
    const s   = document.createElement('script')
    s.src     = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js'
    s.onload  = resolve
    s.onerror = reject
    document.head.appendChild(s)
  })
}

onMounted(() => chargerAnnees())
onUnmounted(() => destroyCharts())
</script>

<style scoped>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px) }
  to   { opacity: 1; transform: translateY(0)   }
}
</style>

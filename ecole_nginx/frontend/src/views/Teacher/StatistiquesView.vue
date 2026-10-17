<!-- src/views/StatistiquesView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div>
      <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Statistiques</h1>
      <p class="text-[#7c83a0] text-sm">
        Analyse des performances<template v-if="stats"> · année {{ stats.annee.nom }}</template>
      </p>
    </div>

    <p v-if="error" class="text-sm text-[#f87171] bg-[#f87171]/10 rounded-xl px-4 py-3">{{ error }}</p>

    <!-- KPIs -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="k in kpis" :key="k.label" class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-5">
        <p class="text-[11px] uppercase tracking-widest text-[#7c83a0] font-medium mb-2">{{ k.label }}</p>
        <p class="text-3xl font-bold mb-1" style="font-family:'Playfair Display',serif" :style="{ color: k.color }">{{ k.value }}</p>
        <p class="text-xs text-[#7c83a0]">{{ k.hint }}</p>
      </div>
    </div>

    <div class="grid md:grid-cols-2 gap-4">
      <!-- Bar chart -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <p class="text-base font-semibold text-[#e8eaf0] mb-5" style="font-family:'Playfair Display',serif">Moyenne par classe <span class="text-xs text-[#7c83a0] font-normal">(/10)</span></p>
        <p v-if="!classAvgs.length" class="text-sm text-[#7c83a0]">Aucune classe.</p>
        <div class="flex flex-col gap-3.5">
          <div v-for="c in classAvgs" :key="c.name" class="flex items-center gap-3">
            <span class="text-[12px] text-[#b0b5cc] w-28 flex-shrink-0 truncate" :title="c.name">{{ c.name }}</span>
            <div class="flex-1 h-2 bg-[#1e2335] rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all" :style="{ width: ((c.avg ?? 0)/10*100)+'%', background: c.color }" />
            </div>
            <span class="text-[13px] font-semibold w-9 text-right" :style="{ color: c.color }">{{ formatMoyenne(c.avg) }}</span>
          </div>
        </div>
      </div>

      <!-- Distribution -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <p class="text-base font-semibold text-[#e8eaf0] mb-5" style="font-family:'Playfair Display',serif">Distribution des notes <span class="text-xs text-[#7c83a0] font-normal">(ramenées sur 10)</span></p>
        <p v-if="!hasNotes" class="text-sm text-[#7c83a0]">Aucune note saisie pour l'instant.</p>
        <div v-else class="flex items-end gap-2 h-36">
          <div v-for="d in distribution" :key="d.tranche" class="flex-1 flex flex-col items-center gap-1">
            <span class="text-[10px] font-semibold" :style="{ color: d.color }">{{ d.pct }}%</span>
            <div class="w-full rounded-t-md min-h-[4px]" :style="{ height: (d.pct*1.1)+'px', background: d.color, opacity: 0.85 }" />
            <span class="text-[9px] text-[#7c83a0] whitespace-nowrap">{{ d.tranche }}</span>
          </div>
        </div>
      </div>

      <!-- Presence -->
      <div class="md:col-span-2 bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <p class="text-base font-semibold text-[#e8eaf0] mb-5" style="font-family:'Playfair Display',serif">Taux de présence par semaine <span class="text-xs text-[#7c83a0] font-normal">(8 dernières semaines)</span></p>
        <p v-if="!hasPresence" class="text-sm text-[#7c83a0]">Aucune présence enregistrée sur cette période.</p>
        <div v-else class="flex items-end gap-3 h-28">
          <div v-for="w in presenceData" :key="w.debut" class="flex-1 flex flex-col items-center gap-1">
            <span class="text-[11px] font-semibold text-[#b0b5cc]">{{ formatPct(w.pct) }}</span>
            <div
              class="w-full rounded-t-lg min-h-[4px]"
              :style="{
                height: ((w.pct ?? 0)*0.7)+'px',
                background: w.pct>=90 ? '#6ee7b7' : w.pct>=75 ? '#f59e0b' : '#f87171'
              }"
            />
            <span class="text-[10px] text-[#7c83a0]">{{ w.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTeacherData, colorAt, formatMoyenne, formatPct } from '@/composables/useTeacherData'

const { stats, error } = useTeacherData()

const kpis = computed(() => {
  const k = stats.value?.kpis ?? {}
  return [
    { label: 'Moyenne globale',      value: k.moyenne != null ? `${formatMoyenne(k.moyenne)}/10` : '—', color: '#4f8ef7', hint: 'Matières que vous enseignez' },
    { label: 'Taux de réussite',     value: formatPct(k.reussite),                                      color: '#6ee7b7', hint: 'Élèves notés ayant ≥ 5/10' },
    { label: 'Taux de présence',     value: formatPct(k.presence),                                      color: '#f59e0b', hint: 'Sur l\'année en cours' },
    { label: 'Élèves en difficulté', value: k.en_difficulte ?? '—',                                     color: '#f87171', hint: 'Moyenne < 5/10' },
  ]
})

const classAvgs = computed(() => (stats.value?.classes ?? []).map((c, i) => ({ name: c.nom, avg: c.moyenne, color: colorAt(i) })))

const DIST_COLORS = ['#f87171', '#f87171', '#f59e0b', '#4f8ef7', '#6ee7b7', '#a78bfa']
const distribution = computed(() => (stats.value?.distribution ?? []).map((d, i) => ({ ...d, color: DIST_COLORS[i] })))
const hasNotes = computed(() => distribution.value.some(d => d.pct > 0))

const presenceData = computed(() => (stats.value?.presence_semaines ?? []).map(w => {
  const d = new Date(w.debut)
  return { ...w, label: `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}` }
}))
const hasPresence = computed(() => presenceData.value.some(w => w.pct !== null))
</script>

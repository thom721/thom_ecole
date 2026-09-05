<!-- src/views/CalendrierView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Calendrier</h1>
        <p class="text-[#7c83a0] text-sm">{{ monthLabel }} {{ viewDate.getFullYear() }}</p>
      </div>
      <div class="flex gap-2">
        <button @click="shiftMonth(-1)" class="px-4 py-2 bg-[#1e2335] text-[#e8eaf0] rounded-xl text-sm font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">◀ {{ MOIS[(viewDate.getMonth()+11)%12] }}</button>
        <button @click="shiftMonth(1)" class="px-4 py-2 bg-[#1e2335] text-[#e8eaf0] rounded-xl text-sm font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">{{ MOIS[(viewDate.getMonth()+1)%12] }} ▶</button>
      </div>
    </div>

    <p v-if="loading" class="text-sm text-[#7c83a0]">Chargement…</p>

    <template v-else>
      <!-- Calendar grid -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-5">
        <div class="grid grid-cols-7 gap-1 mb-2">
          <div v-for="d in ['Lun','Mar','Mer','Jeu','Ven','Sam','Dim']" :key="d"
            class="text-center text-[10px] uppercase tracking-widest text-[#7c83a0] font-medium py-1.5"
          >{{ d }}</div>
        </div>
        <div class="grid grid-cols-7 gap-1">
          <div v-for="cell in calCells" :key="cell.key"
            class="min-h-[72px] rounded-xl p-2 flex flex-col gap-1 transition-colors"
            :class="[
              !cell.day ? 'opacity-0 pointer-events-none' : 'cursor-pointer hover:bg-white/[0.04]',
              cell.isToday ? 'outline outline-1' : 'bg-[#1e2335]'
            ]"
            :style="cell.isToday ? { outlineColor: 'var(--accent,#4f8ef7)', background: 'color-mix(in srgb, var(--accent,#4f8ef7) 10%, #1e2335)' } : {}"
          >
            <span class="text-[13px] font-semibold leading-none"
              :style="cell.isToday ? { color: 'var(--accent,#4f8ef7)' } : {}"
              :class="!cell.isToday ? 'text-[#e8eaf0]' : ''"
            >{{ cell.day }}</span>
            <span v-for="ev in cell.events" :key="ev.id"
              class="text-[9px] px-1.5 py-0.5 rounded font-medium truncate"
              style="background:rgba(79,142,247,0.13); color:#4f8ef7"
            >{{ ev.title }}</span>
          </div>
        </div>
      </div>

      <!-- Upcoming list -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <p class="text-base font-semibold text-[#e8eaf0] mb-4" style="font-family:'Playfair Display',serif">Événements du mois</p>
        <div class="flex flex-col gap-2.5">
          <div v-for="ev in events" :key="ev.id" class="flex items-center gap-4 p-3.5 bg-[#1e2335] rounded-xl hover:bg-white/[0.05] transition-colors cursor-pointer">
            <div class="w-11 h-11 rounded-xl flex flex-col items-center justify-center flex-shrink-0" style="background:rgba(79,142,247,0.13)">
              <span class="text-[17px] font-bold leading-none" style="color:#4f8ef7">{{ String(new Date(ev.start_date).getDate()).padStart(2,'0') }}</span>
              <span class="text-[9px] uppercase" style="color:#4f8ef7">{{ MOIS_COURTS[new Date(ev.start_date).getMonth()] }}</span>
            </div>
            <div class="flex-1">
              <p class="text-[13px] font-medium text-[#e8eaf0]">{{ ev.title }}</p>
              <p class="text-[11.5px] text-[#7c83a0]">{{ ev.location || ev.description || '' }}</p>
            </div>
          </div>
          <p v-if="!events.length" class="text-sm text-[#7c83a0] text-center py-4">Aucun événement ce mois-ci</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const MOIS = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre']
const MOIS_COURTS = ['Jan','Fév','Mars','Avr','Mai','Juin','Juil','Août','Sep','Oct','Nov','Déc']

const viewDate = ref(new Date())
const events = ref([])
const loading = ref(false)

const monthLabel = computed(() => MOIS[viewDate.value.getMonth()])

const calCells = computed(() => {
  const year = viewDate.value.getFullYear()
  const month = viewDate.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const offset = (firstDay.getDay() + 6) % 7 // lundi = 0
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const today = new Date()

  const byDay = {}
  for (const ev of events.value) {
    const d = new Date(ev.start_date).getDate()
    if (!byDay[d]) byDay[d] = []
    byDay[d].push(ev)
  }

  const cells = []
  for (let i = 0; i < offset; i++) cells.push({ key: 'e' + i, day: null, events: [] })
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({
      key: 'd' + d,
      day: d,
      events: byDay[d] || [],
      isToday: today.getFullYear() === year && today.getMonth() === month && today.getDate() === d,
    })
  }
  return cells
})

const fetchEvents = async () => {
  loading.value = true
  try {
    const { data } = await axios.get('/events/', { params: { audience: 'professeurs', published_only: true } })
    const year = viewDate.value.getFullYear()
    const month = viewDate.value.getMonth()
    events.value = (data || []).filter(ev => {
      const d = new Date(ev.start_date)
      return d.getFullYear() === year && d.getMonth() === month
    })
  } catch (error) {
    console.error('Erreur de chargement des événements', error)
  } finally {
    loading.value = false
  }
}

const shiftMonth = (delta) => {
  viewDate.value = new Date(viewDate.value.getFullYear(), viewDate.value.getMonth() + delta, 1)
}

watch(viewDate, fetchEvents)
onMounted(fetchEvents)
</script>

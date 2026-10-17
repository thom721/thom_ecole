<!-- src/views/CalendrierView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Calendrier</h1>
        <p class="text-[#7c83a0] text-sm">{{ MOIS[month] }} {{ year }}</p>
      </div>
      <div class="flex gap-2">
        <button @click="shift(-1)" class="px-4 py-2 bg-[#1e2335] text-[#e8eaf0] rounded-xl text-sm font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">◀ {{ MOIS[(month + 11) % 12] }}</button>
        <button @click="goToday" class="px-4 py-2 text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">Aujourd'hui</button>
        <button @click="shift(1)" class="px-4 py-2 bg-[#1e2335] text-[#e8eaf0] rounded-xl text-sm font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">{{ MOIS[(month + 1) % 12] }} ▶</button>
      </div>
    </div>

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
            :class="cell.isToday ? 'text-[var(--accent)]' : 'text-[#e8eaf0]'"
            :style="cell.isToday ? { color: 'var(--accent,#4f8ef7)' } : {}"
          >{{ cell.day }}</span>
          <span v-for="ev in cell.events" :key="ev.id" :title="ev.title"
            class="text-[9px] px-1.5 py-0.5 rounded font-medium truncate"
            :style="{ background: ev.color+'22', color: ev.color }"
          >{{ ev.title }}</span>
        </div>
      </div>
    </div>

    <!-- Upcoming list -->
    <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
      <p class="text-base font-semibold text-[#e8eaf0] mb-4" style="font-family:'Playfair Display',serif">Prochains événements</p>
      <p v-if="!upcomingList.length" class="text-sm text-[#7c83a0]">Aucun événement à venir.</p>
      <div class="flex flex-col gap-2.5">
        <div v-for="ev in upcomingList" :key="ev.id" class="flex items-center gap-4 p-3.5 bg-[#1e2335] rounded-xl hover:bg-white/[0.05] transition-colors cursor-pointer">
          <div class="w-11 h-11 rounded-xl flex flex-col items-center justify-center flex-shrink-0" :style="{ background: ev.color+'22' }">
            <span class="text-[17px] font-bold leading-none" :style="{ color: ev.color }">{{ ev.day }}</span>
            <span class="text-[9px] uppercase" :style="{ color: ev.color }">{{ ev.month }}</span>
          </div>
          <div class="flex-1">
            <p class="text-[13px] font-medium text-[#e8eaf0]">{{ ev.title }}</p>
            <p class="text-[11.5px] text-[#7c83a0]">{{ ev.sub }}</p>
          </div>
          <span class="text-[11px] px-2.5 py-1 rounded-full font-medium"
            :class="{
              'bg-[#4f8ef7]/10 text-[#4f8ef7]': ev.tag==='blue',
              'bg-[#f59e0b]/10 text-[#f59e0b]': ev.tag==='amber',
              'bg-[#6ee7b7]/10 text-[#6ee7b7]': ev.tag==='green',
            }"
          >{{ ev.tagLabel }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useTeacherData, MOIS } from '@/composables/useTeacherData'

const { events, upcoming } = useTeacherData()

const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth())

function shift(delta) {
  const d = new Date(year.value, month.value + delta, 1)
  year.value = d.getFullYear()
  month.value = d.getMonth()
}
function goToday() {
  year.value = now.getFullYear()
  month.value = now.getMonth()
}

// Grille lundi → dimanche ; un événement sur plusieurs jours apparaît
// sur chacun de ses jours
const calCells = computed(() => {
  const first = new Date(year.value, month.value, 1)
  const offset = (first.getDay() + 6) % 7
  const nbDays = new Date(year.value, month.value + 1, 0).getDate()
  const cells = []
  for (let i = 0; i < offset; i++) cells.push({ key: 'e' + i, day: null, events: [] })
  for (let d = 1; d <= nbDays; d++) {
    const dayStart = new Date(year.value, month.value, d)
    const dayEnd = new Date(year.value, month.value, d + 1)
    cells.push({
      key: 'd' + d,
      day: d,
      isToday: dayStart.toDateString() === now.toDateString(),
      events: events.value.filter(ev => {
        const start = ev.date
        const end = ev.end_date ? new Date(ev.end_date) : start
        return start < dayEnd && end >= dayStart
      }),
    })
  }
  return cells
})

const upcomingList = computed(() => upcoming(6))
</script>

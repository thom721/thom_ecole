<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <button class="text-sm text-gray-500 hover:underline" @click="$router.back()">{{ t('common.back') }}</button>
      <div class="flex items-center gap-3">
        <button class="text-gray-500 px-2" @click="changeMonth(-1)">←</button>
        <h1 class="text-lg font-bold text-gray-900">{{ monthLabel }}</h1>
        <button class="text-gray-500 px-2" @click="changeMonth(1)">→</button>
      </div>
    </div>

    <div class="grid grid-cols-7 gap-px bg-gray-200 border border-gray-200 rounded-xl overflow-hidden">
      <div v-for="d in t('calendar.days')" :key="d"
        class="bg-gray-50 text-center text-xs font-semibold text-gray-500 py-1.5">{{ d }}</div>

      <div v-for="(cell, i) in cells" :key="i"
        class="bg-white min-h-24 p-1.5 cursor-pointer"
        :class="{ 'bg-gray-50 text-gray-300': !cell.inMonth }"
        @click="selectedDay = cell.dateStr">
        <p class="text-xs mb-1">{{ cell.day }}</p>
        <div v-for="e in eventsForDay(cell.dateStr).slice(0, 3)" :key="e.id"
          class="text-[10px] px-1 py-0.5 rounded mb-0.5 truncate"
          :class="chipClass(e.event_type)">
          {{ e.title }}
        </div>
      </div>
    </div>

    <div v-if="selectedDay" class="bg-white border border-gray-200 rounded-xl p-4 mt-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ selectedDay }}</h2>
      <p v-if="!eventsForDay(selectedDay).length" class="text-sm text-gray-500">{{ t('calendar.noEvents') }}</p>
      <div v-for="e in eventsForDay(selectedDay)" :key="e.id" class="text-sm py-1.5 border-t border-gray-100 first:border-t-0">
        <span class="inline-block w-2 h-2 rounded-full mr-2" :class="dotClass(e.event_type)"></span>
        {{ e.title }}
        <span v-if="e.description" class="text-gray-500"> — {{ e.description }}</span>
      </div>
    </div>

    <details v-if="courseId" class="bg-white border border-gray-200 rounded-xl p-4 mt-4">
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('calendar.addEvent') }}</summary>
      <div class="mt-3 space-y-2">
        <input v-model="newTitle" :placeholder="t('calendar.titlePlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <input v-model="newStart" type="datetime-local" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onAddEvent">{{ t('common.add') }}</button>
      </div>
    </details>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCalendarStore } from '@/stores/calendar'

const { t, locale } = useI18n()
const route = useRoute()
const courseId = route.query.course_id || null
const calendar = useCalendarStore()

const today = new Date()
const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth()) // 0-indexed
const events = ref([])
const selectedDay = ref(null)
const newTitle = ref('')
const newStart = ref('')

const monthLabel = computed(() => new Date(viewYear.value, viewMonth.value, 1)
  .toLocaleDateString(locale.value === 'en' ? 'en-US' : 'fr-FR', { month: 'long', year: 'numeric' }))

function toDateStr(y, m, d) {
  return `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
}

const cells = computed(() => {
  const firstOfMonth = new Date(viewYear.value, viewMonth.value, 1)
  const startOffset = (firstOfMonth.getDay() + 6) % 7 // lundi = 0
  const daysInMonth = new Date(viewYear.value, viewMonth.value + 1, 0).getDate()
  const daysInPrevMonth = new Date(viewYear.value, viewMonth.value, 0).getDate()

  const result = []
  for (let i = 0; i < startOffset; i++) {
    const day = daysInPrevMonth - startOffset + i + 1
    const m = viewMonth.value === 0 ? 11 : viewMonth.value - 1
    const y = viewMonth.value === 0 ? viewYear.value - 1 : viewYear.value
    result.push({ day, dateStr: toDateStr(y, m, day), inMonth: false })
  }
  for (let day = 1; day <= daysInMonth; day++) {
    result.push({ day, dateStr: toDateStr(viewYear.value, viewMonth.value, day), inMonth: true })
  }
  while (result.length % 7 !== 0 || result.length < 42) {
    const day = result.length - startOffset - daysInMonth + 1
    const m = viewMonth.value === 11 ? 0 : viewMonth.value + 1
    const y = viewMonth.value === 11 ? viewYear.value + 1 : viewYear.value
    result.push({ day, dateStr: toDateStr(y, m, day), inMonth: false })
    if (result.length >= 42) break
  }
  return result
})

function eventsForDay(dateStr) {
  return events.value.filter((e) => e.start_at.slice(0, 10) === dateStr)
}

function chipClass(type) {
  if (type === 'assignment_due') return 'bg-amber-100 text-amber-800'
  if (type === 'quiz_window') return 'bg-purple-100 text-purple-800'
  return 'bg-gray-100 text-gray-700'
}

function dotClass(type) {
  if (type === 'assignment_due') return 'bg-amber-500'
  if (type === 'quiz_window') return 'bg-purple-500'
  return 'bg-gray-400'
}

async function load() {
  const from = new Date(viewYear.value, viewMonth.value, 1).toISOString()
  const to = new Date(viewYear.value, viewMonth.value + 1, 0, 23, 59, 59).toISOString()
  events.value = await calendar.fetchEvents(courseId, from, to)
}

function changeMonth(delta) {
  viewMonth.value += delta
  if (viewMonth.value < 0) { viewMonth.value = 11; viewYear.value -= 1 }
  if (viewMonth.value > 11) { viewMonth.value = 0; viewYear.value += 1 }
}

async function onAddEvent() {
  if (!newTitle.value || !newStart.value) return
  await calendar.createEvent({ course_id: courseId, title: newTitle.value, start_at: newStart.value })
  newTitle.value = ''
  newStart.value = ''
  await load()
}

watch([viewYear, viewMonth], load)
onMounted(load)
</script>

<!-- src/views/ClassesView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">

    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Mes Sessions / Années d'étude</h1>
        <p class="text-[#7c83a0] text-sm">{{ classes.length }} session{{ classes.length > 1 ? 's' : '' }}/année{{ classes.length > 1 ? 's' : '' }} d'étude ce trimestre</p>
      </div>
      <button class="px-4 py-2 text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">+ Nouvelle session/année d'étude</button>
    </div>

    <p v-if="loading" class="text-sm text-[#7c83a0]">Chargement…</p>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="cls in classes" :key="cls.name"
        class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-5 flex flex-col gap-3 hover:border-white/[0.15] transition-colors cursor-pointer"
      >
        <div class="flex items-center justify-between">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center text-[11px] font-bold" :style="{ background: cls.color+'22', color: cls.color }">{{ cls.initials }}</div>
        </div>
        <div>
          <p class="text-[18px] font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">{{ cls.name }}</p>
        </div>
        <div class="flex gap-5">
          <div>
            <p class="text-[18px] font-bold text-[#e8eaf0] leading-tight">{{ cls.students }}</p>
            <p class="text-[10px] uppercase tracking-wide text-[#7c83a0]">élèves</p>
          </div>
        </div>
        <div class="flex gap-2 pt-1 border-t border-white/[0.06]">
          <router-link to="/professeur-notes" class="flex-1 text-center py-1.5 bg-[#1e2335] text-[#e8eaf0] rounded-lg text-[12px] font-medium hover:bg-[#262d44] transition-colors cursor-pointer">Notes</router-link>
        </div>
      </div>
      <p v-if="!classes.length" class="text-sm text-[#7c83a0] col-span-full">Aucune session/année d'étude assignée</p>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const PALETTE = ['#4f8ef7','#6ee7b7','#f59e0b','#a78bfa','#f87171','#22d3ee']

const classes = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await axios.get('/mes-classes-etudiants')
    classes.value = Object.entries(data?.classes || {}).map(([name, c], i) => ({
      name,
      students: c.studentCount,
      initials: name.slice(0, 3).toUpperCase(),
      color: PALETTE[i % PALETTE.length],
    }))
  } catch (error) {
    console.error('Erreur de chargement des classes', error)
  } finally {
    loading.value = false
  }
})
</script>

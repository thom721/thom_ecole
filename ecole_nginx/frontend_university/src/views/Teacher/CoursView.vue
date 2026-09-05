<!-- src/views/CoursView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Cours & Ressources</h1>
        <p class="text-[#7c83a0] text-sm">Gérez vos supports pédagogiques</p>
      </div>
      <button class="px-4 py-2 text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">+ Ajouter un cours</button>
    </div>
    <p v-if="loading" class="text-sm text-[#7c83a0]">Chargement…</p>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="r in resources" :key="r.id"
        class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-5 flex flex-col gap-3 hover:border-white/[0.15] transition-colors cursor-pointer"
      >
        <div class="w-11 h-11 rounded-xl flex items-center justify-center text-xl" :style="{ background: r.color+'22' }">{{ r.icon }}</div>
        <div>
          <p class="text-[14px] font-semibold text-[#e8eaf0] mb-0.5">{{ r.nom }}</p>
          <p v-if="r.description" class="text-[12px] text-[#7c83a0]">{{ r.description }}</p>
        </div>
      </div>
      <p v-if="!resources.length" class="text-sm text-[#7c83a0] col-span-full">Aucun cours assigné</p>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const ICONS = ['📐','📊','📝','🎯','📚','🔢']
const PALETTE = ['#4f8ef7','#6ee7b7','#f59e0b','#a78bfa','#f87171','#22d3ee']

const resources = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await axios.get('/mes-cours')
    resources.value = (data?.cours || []).map((c, i) => ({
      ...c,
      icon: ICONS[i % ICONS.length],
      color: PALETTE[i % PALETTE.length],
    }))
  } catch (error) {
    console.error('Erreur de chargement des cours', error)
  } finally {
    loading.value = false
  }
})
</script>

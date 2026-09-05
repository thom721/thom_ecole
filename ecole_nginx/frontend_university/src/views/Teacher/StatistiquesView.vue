<!-- src/views/StatistiquesView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div>
      <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Statistiques</h1>
      <p class="text-[#7c83a0] text-sm">Vue d'ensemble de vos classes</p>
    </div>

    <p v-if="loading" class="text-sm text-[#7c83a0]">Chargement…</p>

    <template v-else>
      <!-- KPIs -->
      <div class="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="k in kpis" :key="k.label" class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-5">
          <p class="text-[11px] uppercase tracking-widest text-[#7c83a0] font-medium mb-2">{{ k.label }}</p>
          <p class="text-3xl font-bold" style="font-family:'Playfair Display',serif" :style="{ color: k.color }">{{ k.value }}</p>
        </div>
      </div>

      <!-- Presence today per class -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <p class="text-base font-semibold text-[#e8eaf0] mb-5" style="font-family:'Playfair Display',serif">Taux de présence aujourd'hui par session/année d'étude</p>
        <div v-if="classPresence.length" class="flex flex-col gap-3.5">
          <div v-for="c in classPresence" :key="c.classe" class="flex items-center gap-3">
            <span class="text-[12px] text-[#b0b5cc] w-28 flex-shrink-0">{{ c.classe }}</span>
            <div class="flex-1 h-2 bg-[#1e2335] rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all" :style="{ width: c.val+'%', background: '#4f8ef7' }" />
            </div>
            <span class="text-[13px] font-semibold w-9 text-right" style="color:#4f8ef7">{{ c.val }}%</span>
          </div>
        </div>
        <p v-else class="text-sm text-[#7c83a0]">Aucun appel enregistré aujourd'hui pour vos classes</p>
      </div>

      <p class="text-xs text-[#7c83a0]">Les moyennes de notes et la répartition par tranche ne sont pas encore disponibles — elles nécessitent un endpoint d'agrégation côté serveur.</p>
    </template>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const loading = ref(false)
const kpis = ref([])
const classPresence = ref([])

onMounted(async () => {
  loading.value = true
  try {
    const [studentsRes, presenceRes] = await Promise.all([
      axios.get('/mes-classes-etudiants'),
      axios.get('/stats-presence-aujourdhui'),
    ])
    const mesClasses = new Set(Object.keys(studentsRes.data?.classes || {}))
    classPresence.value = (presenceRes.data?.classes || []).filter(c => mesClasses.has(c.classe))

    const totalPresents = classPresence.value.reduce((s, c) => s + c.presents, 0)
    const totalInscrits = classPresence.value.reduce((s, c) => s + c.total, 0)
    const tauxPresence = totalInscrits ? Math.round((totalPresents / totalInscrits) * 100) : 0

    kpis.value = [
      { label: 'Élèves actifs',   value: studentsRes.data?.studentCount ?? 0, color: '#4f8ef7' },
      { label: 'Classes',         value: mesClasses.size,                     color: '#6ee7b7' },
      { label: 'Présence (auj.)', value: tauxPresence + '%',                  color: '#f59e0b' },
    ]
  } catch (error) {
    console.error('Erreur de chargement des statistiques', error)
  } finally {
    loading.value = false
  }
})
</script>

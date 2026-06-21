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
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="r in resources" :key="r.title"
        class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-5 flex flex-col gap-3 hover:border-white/[0.15] transition-colors cursor-pointer"
      >
        <div class="w-11 h-11 rounded-xl flex items-center justify-center text-xl" :style="{ background: r.color+'22' }">{{ r.icon }}</div>
        <div>
          <p class="text-[14px] font-semibold text-[#e8eaf0] mb-0.5">{{ r.title }}</p>
          <p class="text-[12px] text-[#7c83a0]">{{ r.class }} · {{ r.type }}</p>
        </div>
        <div class="flex items-center justify-between pt-2 border-t border-white/[0.06] mt-auto">
          <span class="text-[11px] text-[#7c83a0]">{{ r.date }}</span>
          <button class="px-3 py-1.5 bg-[#1e2335] text-[#e8eaf0] rounded-lg text-[12px] font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">Ouvrir</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
const resources = [
  { icon:'📐', title:'Cours Intégration – Ch.4',            class:'Tle S1', type:'PDF · 12 pages',         date:'15 Fév 2026', color:'#4f8ef7' },
  { icon:'📊', title:'TP Probabilités conditionnelles',     class:'Tle S2', type:'Exercices · 8 pages',    date:'12 Fév 2026', color:'#6ee7b7' },
  { icon:'📝', title:'Fiche méthode Dérivées',              class:'1re S1', type:'PDF · 4 pages',           date:'10 Fév 2026', color:'#f59e0b' },
  { icon:'🎯', title:'Exercices Géométrie 3D',              class:'1re S2', type:'Exercices · 16 pages',   date:'08 Fév 2026', color:'#a78bfa' },
  { icon:'📚', title:'Cours Arithmétique – Ch.1',           class:'2de B',  type:'PDF · 20 pages',          date:'05 Fév 2026', color:'#f87171' },
  { icon:'🔢', title:'Quiz interactif Algèbre',             class:'2de C',  type:'En ligne · 15 questions', date:'03 Fév 2026', color:'#22d3ee' },
]
</script>

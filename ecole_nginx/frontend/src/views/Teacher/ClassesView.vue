<!-- src/views/ClassesView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">

    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Mes Classes</h1>
        <p class="text-[#7c83a0] text-sm">6 classes actives ce trimestre</p>
      </div>
      <button class="px-4 py-2 text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">+ Nouvelle classe</button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="cls in classes" :key="cls.name"
        class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-5 flex flex-col gap-3 hover:border-white/[0.15] transition-colors cursor-pointer"
      >
        <div class="flex items-center justify-between">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center text-[11px] font-bold" :style="{ background: cls.color+'22', color: cls.color }">{{ cls.level }}</div>
          <span class="text-[11px] px-2.5 py-1 rounded-full font-medium"
            :class="{
              'bg-[#6ee7b7]/10 text-[#6ee7b7]': cls.status==='green',
              'bg-[#f59e0b]/10 text-[#f59e0b]': cls.status==='amber',
              'bg-[#f87171]/10 text-[#f87171]': cls.status==='red',
            }"
          >{{ cls.statusLabel }}</span>
        </div>
        <div>
          <p class="text-[18px] font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">{{ cls.name }}</p>
          <p class="text-[12px] text-[#7c83a0]">{{ cls.subject }}</p>
        </div>
        <div class="flex gap-5">
          <div>
            <p class="text-[18px] font-bold text-[#e8eaf0] leading-tight">{{ cls.students }}</p>
            <p class="text-[10px] uppercase tracking-wide text-[#7c83a0]">élèves</p>
          </div>
          <div>
            <p class="text-[18px] font-bold leading-tight" :style="{ color: cls.color }">{{ cls.avg }}</p>
            <p class="text-[10px] uppercase tracking-wide text-[#7c83a0]">moy.</p>
          </div>
          <div>
            <p class="text-[18px] font-bold text-[#e8eaf0] leading-tight">{{ cls.done }}%</p>
            <p class="text-[10px] uppercase tracking-wide text-[#7c83a0]">programme</p>
          </div>
        </div>
        <div class="w-full h-1.5 bg-[#1e2335] rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all" :style="{ width: cls.done+'%', background: cls.color }" />
        </div>
        <div class="flex gap-2 pt-1 border-t border-white/[0.06]">
          <button class="flex-1 py-1.5 bg-[#1e2335] text-[#e8eaf0] rounded-lg text-[12px] font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">Notes</button>
          <button class="flex-1 py-1.5 bg-[#1e2335] text-[#e8eaf0] rounded-lg text-[12px] font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">Élèves</button>
          <button class="flex-1 py-1.5 text-white rounded-lg text-[12px] font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">Cours</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
const classes = [
  { name:'Terminale S1', level:'Tle', subject:'Analyse · Algèbre · Géométrie',    students:28, avg:'14.2', done:78, color:'#4f8ef7', status:'green', statusLabel:'En cours'  },
  { name:'Terminale S2', level:'Tle', subject:'Probabilités · Statistiques',       students:30, avg:'13.5', done:65, color:'#6ee7b7', status:'green', statusLabel:'En cours'  },
  { name:'Première S1',  level:'1re', subject:'Fonctions · Dérivées',              students:27, avg:'12.8', done:50, color:'#f59e0b', status:'amber', statusLabel:'Attention' },
  { name:'Première S2',  level:'1re', subject:'Géométrie dans l\'espace',          students:29, avg:'15.0', done:88, color:'#a78bfa', status:'green', statusLabel:'Excellent' },
  { name:'Seconde B',    level:'2de', subject:'Arithmétique · Bases',              students:28, avg:'11.2', done:35, color:'#f87171', status:'red',   statusLabel:'À risque'  },
  { name:'Seconde C',    level:'2de', subject:'Algèbre · Équations',               students:26, avg:'13.0', done:55, color:'#22d3ee', status:'green', statusLabel:'En cours'  },
]
</script>

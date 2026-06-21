<!-- src/views/CalendrierView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Calendrier</h1>
        <p class="text-[#7c83a0] text-sm">Février 2026</p>
      </div>
      <div class="flex gap-2">
        <button class="px-4 py-2 bg-[#1e2335] text-[#e8eaf0] rounded-xl text-sm font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">◀ Janvier</button>
        <button class="px-4 py-2 bg-[#1e2335] text-[#e8eaf0] rounded-xl text-sm font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">Mars ▶</button>
        <button class="px-4 py-2 text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">+ Événement</button>
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
            cell.day === 20 ? 'outline outline-1' : 'bg-[#1e2335]'
          ]"
          :style="cell.day === 20 ? { outlineColor: 'var(--accent,#4f8ef7)', background: 'color-mix(in srgb, var(--accent,#4f8ef7) 10%, #1e2335)' } : {}"
        >
          <span class="text-[13px] font-semibold leading-none"
            :class="cell.day === 20 ? 'text-[var(--accent)]' : 'text-[#e8eaf0]'"
            :style="cell.day === 20 ? { color: 'var(--accent,#4f8ef7)' } : {}"
          >{{ cell.day }}</span>
          <span v-for="ev in cell.events" :key="ev.title"
            class="text-[9px] px-1.5 py-0.5 rounded font-medium truncate"
            :style="{ background: ev.color+'22', color: ev.color }"
          >{{ ev.title }}</span>
        </div>
      </div>
    </div>

    <!-- Upcoming list -->
    <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
      <p class="text-base font-semibold text-[#e8eaf0] mb-4" style="font-family:'Playfair Display',serif">Prochains événements</p>
      <div class="flex flex-col gap-2.5">
        <div v-for="ev in upcoming" :key="ev.title" class="flex items-center gap-4 p-3.5 bg-[#1e2335] rounded-xl hover:bg-white/[0.05] transition-colors cursor-pointer">
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
const evMap = {
  3:[{title:'Réunion pédago',color:'#f59e0b'}], 7:[{title:'DS Tle S2',color:'#4f8ef7'}],
  10:[{title:'CC 1re S1',color:'#6ee7b7'}], 14:[{title:'Vacances',color:'#a78bfa'}],
  20:[{title:'Bulletins',color:'#f87171'}], 24:[{title:'Contrôle S1',color:'#4f8ef7'}],
  26:[{title:'Remise bulletins',color:'#f59e0b'}],
}
const calCells = (() => {
  const cells = []
  for(let i=0;i<6;i++) cells.push({key:'e'+i,day:null,events:[]})
  for(let d=1;d<=28;d++) cells.push({key:'d'+d,day:d,events:evMap[d]||[]})
  return cells
})()
const upcoming = [
  {day:'24',month:'Fév', title:'Contrôle Intégration',sub:'Terminale S1 · 14h00',  color:'#4f8ef7',tag:'blue', tagLabel:'Examen' },
  {day:'26',month:'Fév', title:'Remise des bulletins', sub:'Toutes classes · 10h00',color:'#f59e0b',tag:'amber',tagLabel:'Admin'  },
  {day:'03',month:'Mars',title:'Conseil de classe',    sub:'Salle A12 · 16h30',     color:'#6ee7b7',tag:'green',tagLabel:'Réunion'},
  {day:'07',month:'Mars',title:'DS Probabilités',      sub:'Terminale S2 · 08h00',  color:'#4f8ef7',tag:'blue', tagLabel:'Examen' },
]
</script>

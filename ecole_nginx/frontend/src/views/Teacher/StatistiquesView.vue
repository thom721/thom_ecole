<!-- src/views/StatistiquesView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div>
      <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Statistiques</h1>
      <p class="text-[#7c83a0] text-sm">Analyse des performances · Trimestre 2</p>
    </div>

    <!-- KPIs -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="k in kpis" :key="k.label" class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-5">
        <p class="text-[11px] uppercase tracking-widest text-[#7c83a0] font-medium mb-2">{{ k.label }}</p>
        <p class="text-3xl font-bold mb-1" style="font-family:'Playfair Display',serif" :style="{ color: k.color }">{{ k.value }}</p>
        <p class="text-xs" :class="k.up ? 'text-[#6ee7b7]' : 'text-[#f87171]'">{{ k.trend }}</p>
      </div>
    </div>

    <div class="grid md:grid-cols-2 gap-4">
      <!-- Bar chart -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <p class="text-base font-semibold text-[#e8eaf0] mb-5" style="font-family:'Playfair Display',serif">Moyenne par classe</p>
        <div class="flex flex-col gap-3.5">
          <div v-for="c in classAvgs" :key="c.name" class="flex items-center gap-3">
            <span class="text-[12px] text-[#b0b5cc] w-28 flex-shrink-0">{{ c.name }}</span>
            <div class="flex-1 h-2 bg-[#1e2335] rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all" :style="{ width: (c.avg/20*100)+'%', background: c.color }" />
            </div>
            <span class="text-[13px] font-semibold w-9 text-right" :style="{ color: c.color }">{{ c.avg }}</span>
          </div>
        </div>
      </div>

      <!-- Distribution -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <p class="text-base font-semibold text-[#e8eaf0] mb-5" style="font-family:'Playfair Display',serif">Distribution des notes</p>
        <div class="flex items-end gap-2 h-36">
          <div v-for="d in distribution" :key="d.range" class="flex-1 flex flex-col items-center gap-1">
            <span class="text-[10px] font-semibold" :style="{ color: d.color }">{{ d.pct }}%</span>
            <div class="w-full rounded-t-md min-h-[4px]" :style="{ height: d.pct*2+'px', background: d.color, opacity: 0.85 }" />
            <span class="text-[9px] text-[#7c83a0] whitespace-nowrap">{{ d.range }}</span>
          </div>
        </div>
      </div>

      <!-- Presence -->
      <div class="md:col-span-2 bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <p class="text-base font-semibold text-[#e8eaf0] mb-5" style="font-family:'Playfair Display',serif">Taux de présence par semaine</p>
        <div class="flex items-end gap-3 h-28">
          <div v-for="w in presenceData" :key="w.week" class="flex-1 flex flex-col items-center gap-1">
            <span class="text-[11px] font-semibold text-[#b0b5cc]">{{ w.pct }}%</span>
            <div
              class="w-full rounded-t-lg min-h-[4px]"
              :style="{
                height: w.pct+'%',
                background: w.pct>=90 ? '#6ee7b7' : w.pct>=75 ? '#f59e0b' : '#f87171'
              }"
            />
            <span class="text-[10px] text-[#7c83a0]">S{{ w.week }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
const kpis = [
  { label:'Moyenne globale',     value:'13.8/20', color:'#4f8ef7', up:true,  trend:'↑ +0.4 vs T1' },
  { label:'Taux de réussite',    value:'85%',     color:'#6ee7b7', up:true,  trend:'↑ +3% vs T1'  },
  { label:'Taux de présence',    value:'91%',     color:'#f59e0b', up:false, trend:'↓ -2% vs T1'  },
  { label:'Élèves en difficulté',value:'12',      color:'#f87171', up:false, trend:'↑ +2 vs T1'   },
]
const classAvgs = [
  { name:'Terminale S1', avg:14.2, color:'#4f8ef7' }, { name:'Terminale S2', avg:13.5, color:'#6ee7b7' },
  { name:'Première S1',  avg:12.8, color:'#f59e0b' }, { name:'Première S2',  avg:15.0, color:'#a78bfa' },
  { name:'Seconde B',    avg:11.2, color:'#f87171' }, { name:'Seconde C',    avg:13.0, color:'#22d3ee' },
]
const distribution = [
  { range:'<8',   pct:5,  color:'#f87171' }, { range:'8-10', pct:10, color:'#f87171' },
  { range:'10-12',pct:20, color:'#f59e0b' }, { range:'12-14',pct:30, color:'#4f8ef7' },
  { range:'14-16',pct:22, color:'#6ee7b7' }, { range:'>16',  pct:13, color:'#a78bfa' },
]
const presenceData = [94,92,88,95,91,87,93,91].map((pct,i) => ({ week:i+1, pct }))
</script>

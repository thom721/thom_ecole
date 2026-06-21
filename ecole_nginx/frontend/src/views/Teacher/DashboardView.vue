<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>  
             
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Bonjour, {{authStore?.user?.user.username ?? authStore?.user?.user.name}} ✦</h1>       
        <p class="text-[#7c83a0] text-sm">
          {{ formattedDate }} · Semaine {{ weekOfQuarter }} du trimestre
        </p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <button class="action-btn action-btn--violet ">📅 Emploi du temps</button>
        <button class="action-btn action-btn--blue " :style="{ background: 'var(--accent,#4f8ef7)' }">+ Nouveau devoir</button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">  
    
    <AdminDashComposante title="Élèves actifs" icon="ri-building-line"      :value="myStudents.studentCount" color="amber"  @show-details=""/>
      <AdminDashComposante title="Absences"        icon="ri-calendar-close-line" :value="0"        color="rose"    @show-details="" />
      <AdminDashComposante title="Cours" icon="ri-book-open-line"    :value="0"        color="sky"     @show-details="" />
      <AdminDashComposante title="Cours programmés" icon="ri-book-open-line"    :value="94"        color="purple" />

      <!-- <div v-for="s in stats" :key="s.label"
        class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-5 relative overflow-hidden"
      >
        <div class="absolute top-0 inset-x-0 h-[2px]" :style="{ background: s.color }" />
        <p class="text-[11px] uppercase tracking-widest text-[#7c83a0] font-medium mb-2 flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :style="{ background: s.color }" />
          {{ s.label }}
        </p>
        <p class="text-4xl font-bold mb-1.5 leading-none" style="font-family:'Playfair Display',serif" :style="{ color: s.color }">{{ s.value }}</p>
        <p class="text-xs" :class="s.down ? 'text-[#f87171]' : 'text-[#6ee7b7]'">{{ s.change }}</p> 
        <div class="flex items-end gap-1 h-8 mt-1">
          <div
            v-for="(h, i) in s.spark" :key="i"
            class="flex-1 rounded-t-sm transition-all"
            :style="{
              height: h + '%',
              background: i === s.spark.length-1 ? s.color : `color-mix(in srgb, ${s.color} 20%, transparent)`
            }"
          />
        </div>
      </div> -->
    </div>

    <!-- Middle -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-4">
 
      <!-- Classes table -->
      <div class="xl:col-span-2 bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <span class="text-base font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">Mes Classes</span>
          <span class="text-xs font-medium cursor-pointer" style="color:var(--accent,#4f8ef7)">Voir tout →</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-start">
            <thead>
              <tr class="border-b border-white/[0.07]">
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Classe</th>
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Élèves</th>
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Progression</th>
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Moy.</th>
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Statut</th>
              </tr>
            </thead>
            <tbody>
                <tr 
                  v-for="(c, className) in myStudents.classes" 
                  :key="className"
                  class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors cursor-pointer"
                >
                  <td class="py-3 pr-4">
                    <p class="text-[13px] font-medium text-[#e8eaf0]">
                      {{ className }}
                    </p> 
                  </td>

                  <td class="py-3 pr-4 text-sm text-[#b0b5cc]">
                    {{ c.studentCount }}
                  </td>

                  <td class="py-3 pr-4">
                    <div class="w-20 h-1.5 bg-[#1e2335] rounded-full overflow-hidden">
                      0
                    </div>
                  </td>

                  <td class="py-3 pr-4 text-sm font-semibold text-[#e8eaf0]">
                    0
                  </td>

                  <td class="py-3">
                    0
                  </td>
                </tr>
              </tbody>
            <!-- <tbody>
              <tr v-for="c in myStudents.classes" :key="c.keys()" class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors cursor-pointer">
                <td class="py-3 pr-4">
                  <p class="text-[13px] font-medium text-[#e8eaf0]">{{ c.keys() }}</p> 
                </td>
                <td class="py-3 pr-4 text-sm text-[#b0b5cc]">{{ c.studentCount }}</td>
                <td class="py-3 pr-4">
                  <div class="w-20 h-1.5 bg-[#1e2335] rounded-full overflow-hidden">
                    <div class="h-full rounded-full" :style="{ width: c.progress+'%', background: c.color }" />
                  </div>
                </td>
                <td class="py-3 pr-4 text-sm font-semibold text-[#e8eaf0]">{{ c.avg }}</td>
                <td class="py-3">
                  <span class="text-[11px] px-2.5 py-1 rounded-full font-medium"
                    :class="{
                      'bg-[#6ee7b7]/10 text-[#6ee7b7]': c.status==='green',
                      'bg-[#f59e0b]/10 text-[#f59e0b]': c.status==='amber',
                      'bg-[#f87171]/10 text-[#f87171]': c.status==='red',
                    }"
                  >{{ c.statusLabel }}</span>
                </td>
              </tr>
            </tbody> -->
          </table>
        </div>
      </div>
      
      <!-- Events -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <span class="text-base font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">À venir</span>
          <span class="text-xs font-medium cursor-pointer" style="color:var(--accent,#4f8ef7)">Calendrier →</span>
        </div>
        <div class="flex flex-col gap-2.5">
          <div v-for="ev in events" :key="ev.title" class="flex items-center gap-3 p-3 bg-[#1e2335] rounded-xl hover:bg-white/[0.05] transition-colors cursor-pointer">
            <div class="text-center min-w-[36px] flex-shrink-0">
              <p class="text-xl font-bold leading-none text-[#e8eaf0]" style="font-family:'Playfair Display',serif">{{ ev.day }}</p>
              <p class="text-[9px] uppercase tracking-wide text-[#7c83a0]">{{ ev.month }}</p>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-[13px] font-medium text-[#e8eaf0] truncate">{{ ev.title }}</p>
              <p class="text-[11px] text-[#7c83a0]">{{ ev.sub }}</p>
            </div>
            <span class="text-[11px] px-2 py-0.5 rounded-full font-medium flex-shrink-0"
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

    <!-- Bottom -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

      <!-- Top students -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <span class="text-base font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">Élèves en vedette</span>
          <span class="text-xs font-medium cursor-pointer" style="color:var(--accent,#4f8ef7)">Classement →</span>
        </div>
        <div v-for="s in topStudents" :key="s.name" class="flex items-center gap-3 py-2.5 border-b border-white/[0.05] last:border-0">
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-[11px] font-bold text-[#0f1117] flex-shrink-0" :style="{ background: s.gradient }">{{ s.initials }}</div>
          <div class="flex-1 min-w-0">
            <p class="text-[13px] font-medium text-[#e8eaf0]">{{ s.name }}</p>
            <p class="text-[11px] text-[#7c83a0]">{{ s.class }}</p>
          </div>
          <div class="text-right">
            <p class="text-[13px] font-semibold" :style="{ color: s.gradeColor }">{{ s.grade }}</p>
            <p class="text-[11px] text-[#7c83a0]">{{ s.pct }}</p>
          </div>
        </div>
      </div>

      <!-- Activity -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <span class="text-base font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">Activité récente</span>
          <span class="text-xs font-medium cursor-pointer" style="color:var(--accent,#4f8ef7)">Tout voir →</span>
        </div>
        <div v-for="a in activities" :key="a.text" class="flex items-start gap-3 py-2.5 border-b border-white/[0.05] last:border-0">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center text-sm flex-shrink-0" :style="{ background: a.bg }">{{ a.icon }}</div>
          <div>
            <p class="text-[12.5px] text-[#b0b5cc] leading-snug" v-html="a.html" />
            <p class="text-[11px] text-[#7c83a0] mt-0.5">{{ a.time }}</p>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted,reactive,ref } from 'vue'
import AdminDashComposante from "@/components/AdminDashComposante.vue";

import { useAuthStore } from '@/stores/auth';
import axios from 'axios';
const authStore = useAuthStore(); 

const now = new Date()
const myStudents = ref({})
const formattedDate = computed(() => {
  const jours = [
    "Dimanche", "Lundi", "Mardi", "Mercredi",
    "Jeudi", "Vendredi", "Samedi"
  ]

  const mois = [
    "Janvier", "Février", "Mars", "Avril",
    "Mai", "Juin", "Juillet", "Août",
    "Septembre", "Octobre", "Novembre", "Décembre"
  ]

  const jourNom = jours[now.getDay()]
  const jourNumero = now.getDate()
  const moisNom = mois[now.getMonth()]
  const annee = now.getFullYear()

  return `${jourNom} ${jourNumero} ${moisNom} ${annee}`
})

const weekOfQuarter = computed(() => {
  const month = now.getMonth()
  const quarterStartMonth = Math.floor(month / 3) * 3
  const quarterStart = new Date(now.getFullYear(), quarterStartMonth, 1)

  const diff = now - quarterStart
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  return Math.floor(days / 7) + 1
})


const stats = reactive([
  { label:'Élèves actifs',       value: '0', change:'↑ +4 ce mois',         color:'#4f8ef7', down:false, spark:[55,70,60,85,75,100] },
  { label:'Moyenne générale',    value:'13.8',change:'↑ +0.4 pts trimestre', color:'#6ee7b7', down:false, spark:[60,65,72,68,80,90]  },
  { label:'Devoirs en attente',  value:'28',  change:'↑ +8 à corriger',      color:'#f59e0b', down:true,  spark:[40,80,55,90,45,70]  },
  { label:'Alertes absentéisme', value:'5',   change:'↓ 3 élèves à risque',  color:'#f87171', down:true,  spark:[30,50,20,60,35,45]  },
])

const classes = [
  { name:'Terminale S1', sub:'Analyse · Algèbre',   students:28, progress:78, avg:'14.2', color:'#4f8ef7', status:'green', statusLabel:'En cours' },
  { name:'Terminale S2', sub:'Probabilités',          students:30, progress:65, avg:'13.5', color:'#6ee7b7', status:'green', statusLabel:'En cours' },
  { name:'Première S1',  sub:'Fonctions · Dérivées',  students:27, progress:50, avg:'12.8', color:'#f59e0b', status:'amber', statusLabel:'Attention' },
  { name:'Première S2',  sub:'Géométrie',             students:29, progress:88, avg:'15.0', color:'#6ee7b7', status:'green', statusLabel:'Excellent' },
  { name:'Seconde B',    sub:'Arithmétique',           students:28, progress:35, avg:'11.2', color:'#f87171', status:'red',   statusLabel:'À risque'  },
]

const events = [
  { day:'24', month:'Fév',  title:'Contrôle Intégration', sub:'Terminale S1 · 14h00',    tag:'blue',  tagLabel:'Examen'  },
  { day:'26', month:'Fév',  title:'Remise des bulletins',  sub:'Toutes classes · 10h00', tag:'amber', tagLabel:'Admin'   },
  { day:'03', month:'Mars', title:'Conseil de classe',     sub:'Salle A12 · 16h30',      tag:'green', tagLabel:'Réunion' },
  { day:'07', month:'Mars', title:'DS Probabilités',       sub:'Terminale S2 · 08h00',   tag:'blue',  tagLabel:'Examen'  },
]

const topStudents = [
  { name:'Léa Aubert',     class:'Terminale S1', initials:'LA', grade:'18.5', gradeColor:'#6ee7b7', pct:'Top 1%',  gradient:'linear-gradient(135deg,#6ee7b7,#4f8ef7)'  },
  { name:'Thomas Morin',   class:'Première S2',  initials:'TM', grade:'17.8', gradeColor:'#4f8ef7', pct:'Top 3%',  gradient:'linear-gradient(135deg,#4f8ef7,#a78bfa)'  },
  { name:'Camille Mercier',class:'Terminale S2', initials:'CM', grade:'17.2', gradeColor:'#f59e0b', pct:'Top 5%',  gradient:'linear-gradient(135deg,#f59e0b,#f87171)'  },
  { name:'Noah Durand',    class:'Terminale S1', initials:'ND', grade:'16.9', gradeColor:'#4f8ef7', pct:'Top 8%',  gradient:'linear-gradient(135deg,#a78bfa,#6ee7b7)'  },
  { name:'Sophie Laurent', class:'Première S1',  initials:'SL', grade:'16.4', gradeColor:'#6ee7b7', pct:'Top 10%', gradient:'linear-gradient(135deg,#f87171,#f59e0b)'  },
]

const activities = [
  { icon:'📝', bg:'rgba(110,231,183,0.12)', html:'<span style="color:#4f8ef7;font-weight:500">Léa Aubert</span> a rendu son devoir sur les limites', time:'Il y a 12 min' },
  { icon:'⚠️', bg:'rgba(248,113,113,0.12)', html:'<span style="color:#4f8ef7;font-weight:500">Marc Bonnet</span> est absent pour la 3ᵉ fois ce mois', time:'Il y a 45 min' },
  { icon:'💬', bg:'rgba(79,142,247,0.12)',  html:'<span style="color:#4f8ef7;font-weight:500">Thomas Morin</span> a posé une question sur le cours', time:'Il y a 1h 20min' },
  { icon:'🏆', bg:'rgba(245,158,11,0.12)',  html:'<span style="color:#4f8ef7;font-weight:500">Camille Mercier</span> a obtenu <b>19/20</b>', time:'Il y a 2h 05min' },
  { icon:'📊', bg:'rgba(110,231,183,0.12)', html:'Notes du contrôle de <span style="color:#4f8ef7;font-weight:500">Terminale S1</span> publiées', time:'Hier à 18h30' },
]
onMounted(async ()=>{

  // const { data } = await axios.get(`/professeur/${authStore?.user.user?.userable_id}`)
  // professerDetails.value=data?.data

  const response = await axios.get("/mes-programmes")
  const student = await axios.get("/mes-classes-etudiants")
// programmes.value = response.data.programmes
// annee.value = response.data.annee
myStudents.value =student?.data
console.log(student.data);

})
</script>

<style>
@keyframes fadeUp { from { opacity:0; transform:translateY(14px) } to { opacity:1; transform:translateY(0) } }
</style>



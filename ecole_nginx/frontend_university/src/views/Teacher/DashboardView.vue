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
      <AdminDashComposante title="Élèves actifs"    icon="ri-building-line"       :value="myStudents.studentCount ?? 0" color="amber"  @show-details="" />
      <AdminDashComposante title="Absences (auj.)"  icon="ri-calendar-close-line" :value="absencesAujourdhui"           color="rose"   @show-details="" />
      <AdminDashComposante title="Cours"             icon="ri-book-open-line"      :value="coursCount"                   color="sky"    @show-details="" />
      <AdminDashComposante title="Cours programmés" icon="ri-book-open-line"      :value="programmesCount"              color="purple" @show-details="" />
    </div>

    <!-- Middle -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-4">
 
      <!-- Classes table -->
      <div class="xl:col-span-2 bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <span class="text-base font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">Mes Sessions / Années d'étude</span>
          <router-link to="/professeur-classes" class="text-xs font-medium cursor-pointer" style="color:var(--accent,#4f8ef7)">Voir tout →</router-link>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-start">
            <thead>
              <tr class="border-b border-white/[0.07]">
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Session / Année d'étude</th>
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Élèves</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(c, className) in myStudents.classes"
                :key="className"
                class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors cursor-pointer"
              >
                <td class="py-3 pr-4">
                  <p class="text-[13px] font-medium text-[#e8eaf0]">{{ className }}</p>
                </td>
                <td class="py-3 pr-4 text-sm text-[#b0b5cc]">{{ c.studentCount }}</td>
              </tr>
              <tr v-if="!myStudents.classes || !Object.keys(myStudents.classes).length">
                <td colspan="2" class="py-6 text-center text-sm text-[#7c83a0]">Aucune classe assignée</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Events -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <span class="text-base font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">À venir</span>
          <router-link to="/professeur-calendrier" class="text-xs font-medium cursor-pointer" style="color:var(--accent,#4f8ef7)">Calendrier →</router-link>
        </div>
        <div class="flex flex-col gap-2.5">
          <div v-for="ev in upcomingEvents" :key="ev.id" class="flex items-center gap-3 p-3 bg-[#1e2335] rounded-xl hover:bg-white/[0.05] transition-colors cursor-pointer">
            <div class="text-center min-w-[36px] flex-shrink-0">
              <p class="text-xl font-bold leading-none text-[#e8eaf0]" style="font-family:'Playfair Display',serif">{{ ev.day }}</p>
              <p class="text-[9px] uppercase tracking-wide text-[#7c83a0]">{{ ev.month }}</p>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-[13px] font-medium text-[#e8eaf0] truncate">{{ ev.title }}</p>
              <p class="text-[11px] text-[#7c83a0] truncate">{{ ev.location }}</p>
            </div>
          </div>
          <p v-if="!upcomingEvents.length" class="text-center text-sm text-[#7c83a0] py-4">Aucun événement à venir</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
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


const coursCount = ref(0)
const programmesCount = ref(0)
const absencesAujourdhui = ref(0)
const upcomingEvents = ref([])

const MOIS_COURTS = ['Jan','Fév','Mars','Avr','Mai','Juin','Juil','Août','Sep','Oct','Nov','Déc']

onMounted(async ()=>{
  try {
    const [programmesRes, studentsRes, coursRes] = await Promise.all([
      axios.get("/mes-programmes"),
      axios.get("/mes-classes-etudiants"),
      axios.get("/mes-cours"),
    ])
    myStudents.value = studentsRes?.data
    programmesCount.value = programmesRes?.data?.programmes?.length ?? 0
    coursCount.value = coursRes?.data?.cours?.length ?? 0
  } catch (error) {
    console.error("Erreur de chargement du tableau de bord", error)
  }

  try {
    const { data } = await axios.get('/stats-presence-aujourdhui')
    const mesClasses = new Set(Object.keys(myStudents.value?.classes || {}))
    absencesAujourdhui.value = (data?.classes || [])
      .filter(c => mesClasses.has(c.classe))
      .reduce((sum, c) => sum + (c.total - c.presents), 0)
  } catch (error) {
    console.error("Erreur de chargement des présences", error)
  }

  try {
    const { data } = await axios.get('/events/', { params: { audience: 'professeurs', published_only: true } })
    const today = new Date()
    upcomingEvents.value = (data || [])
      .filter(ev => new Date(ev.start_date) >= today)
      .slice(0, 4)
      .map(ev => {
        const d = new Date(ev.start_date)
        return { id: ev.id, title: ev.title, location: ev.location || '', day: String(d.getDate()).padStart(2,'0'), month: MOIS_COURTS[d.getMonth()] }
      })
  } catch (error) {
    console.error("Erreur de chargement des événements", error)
  }
})
</script>

<style>
@keyframes fadeUp { from { opacity:0; transform:translateY(14px) } to { opacity:1; transform:translateY(0) } }
</style>



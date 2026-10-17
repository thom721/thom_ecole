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
        <button @click="router.push({ name: 'teacher.calendrier' })" class="action-btn action-btn--violet ">📅 Calendrier</button>
        <button @click="router.push({ name: 'teacher.add-notes' })" class="action-btn action-btn--blue " :style="{ background: 'var(--accent,#4f8ef7)' }">+ Saisir des notes</button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">  
    
      <AdminDashComposante title="Élèves actifs"        icon="ri-group-line"          :value="kpis.etudiants ?? 0"                color="amber" />
      <AdminDashComposante title="Moyenne générale /10" icon="ri-bar-chart-line"      :value="formatMoyenne(kpis.moyenne)"        color="sky" />
      <AdminDashComposante title="Taux de réussite"     icon="ri-medal-line"          :value="formatPct(kpis.reussite)"           color="purple" />
      <AdminDashComposante title="Élèves en difficulté" icon="ri-alert-line"          :value="kpis.en_difficulte ?? 0"            color="rose" />

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
          <span @click="router.push({ name: 'teacher.classes' })" class="text-xs font-medium cursor-pointer" style="color:var(--accent,#4f8ef7)">Voir tout →</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-start">
            <thead>
              <tr class="border-b border-white/[0.07]">
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Classe</th>
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Élèves</th>
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Réussite</th>
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Moy.</th>
                <th class="text-left text-[10.5px] uppercase tracking-widest text-[#7c83a0] font-medium pb-3">Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!classes.length">
                <td colspan="5" class="py-6 text-center text-sm text-[#7c83a0]">{{ loading ? 'Chargement…' : (error || 'Aucune classe attribuée cette année.') }}</td>
              </tr>
              <tr v-for="c in classes" :key="c.classe_id" @click="router.push({ name: 'teacher.classes' })" class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors cursor-pointer">
                <td class="py-3 pr-4">
                  <p class="text-[13px] font-medium text-[#e8eaf0]">{{ c.nom }}</p>
                  <p class="text-[11px] text-[#7c83a0]">{{ c.matieres.length }} matière{{ c.matieres.length > 1 ? 's' : '' }}</p>
                </td>
                <td class="py-3 pr-4 text-sm text-[#b0b5cc]">{{ c.studentCount }}</td>
                <td class="py-3 pr-4">
                  <div class="flex items-center gap-2">
                    <div class="w-20 h-1.5 bg-[#1e2335] rounded-full overflow-hidden">
                      <div class="h-full rounded-full" :style="{ width: (c.reussite ?? 0)+'%', background: c.color }" />
                    </div>
                    <span class="text-[11px] text-[#7c83a0]">{{ formatPct(c.reussite) }}</span>
                  </div>
                </td>
                <td class="py-3 pr-4 text-sm font-semibold text-[#e8eaf0]">{{ formatMoyenne(c.moyenne) }}</td>
                <td class="py-3">
                  <span class="text-[11px] px-2.5 py-1 rounded-full font-medium"
                    :class="{
                      'bg-[#6ee7b7]/10 text-[#6ee7b7]': c.status==='green',
                      'bg-[#f59e0b]/10 text-[#f59e0b]': c.status==='amber',
                      'bg-[#f87171]/10 text-[#f87171]': c.status==='red',
                      'bg-white/[0.06] text-[#7c83a0]': c.status==='none',
                    }"
                  >{{ c.statusLabel }}</span>
                </td>
              </tr>
            </tbody>

          </table>
        </div>
      </div>
      
      <!-- Events -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <span class="text-base font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">À venir</span>
          <span @click="router.push({ name: 'teacher.calendrier' })" class="text-xs font-medium cursor-pointer" style="color:var(--accent,#4f8ef7)">Calendrier →</span>
        </div>
        <p v-if="!events.length" class="text-sm text-[#7c83a0]">Aucun événement à venir.</p>
        <div class="flex flex-col gap-2.5">
          <div v-for="ev in events" :key="ev.id" class="flex items-center gap-3 p-3 bg-[#1e2335] rounded-xl hover:bg-white/[0.05] transition-colors cursor-pointer">
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
          <span @click="router.push({ name: 'teacher.statistiques' })" class="text-xs font-medium cursor-pointer" style="color:var(--accent,#4f8ef7)">Statistiques →</span>
        </div>
        <p v-if="!topStudents.length" class="text-sm text-[#7c83a0]">Aucune note saisie pour l'instant.</p>
        <div v-for="s in topStudents" :key="s.id" class="flex items-center gap-3 py-2.5 border-b border-white/[0.05] last:border-0">
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

      <!-- Mes matières -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <span class="text-base font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">Mes matières</span>
          <span @click="router.push({ name: 'teacher.cours' })" class="text-xs font-medium cursor-pointer" style="color:var(--accent,#4f8ef7)">Cours →</span>
        </div>
        <p v-if="!programmes.length" class="text-sm text-[#7c83a0]">Aucune matière programmée cette année.</p>
        <div class="max-h-72 overflow-y-auto">
          <div v-for="(p, i) in programmes" :key="p.id" class="flex items-center gap-3 py-2.5 border-b border-white/[0.05] last:border-0">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center text-[11px] font-bold flex-shrink-0" :style="{ background: colorAt(i)+'22', color: colorAt(i) }">{{ initials(p.cours_nom) }}</div>
            <div class="flex-1 min-w-0">
              <p class="text-[13px] font-medium text-[#e8eaf0] truncate">{{ p.cours_nom }}</p>
              <p class="text-[11px] text-[#7c83a0]">{{ p.classe_nom }}<template v-if="p.jours"> · {{ p.jours }}</template><template v-if="p.heure"> · {{ p.heure }}</template></p>
            </div>
            <span class="text-[11px] text-[#7c83a0] flex-shrink-0" title="Coefficient">coef. {{ p.coefficients ?? '—' }}</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AdminDashComposante from "@/components/AdminDashComposante.vue";
import { useTeacherData, colorAt, classStatus, initials, formatMoyenne, formatPct } from '@/composables/useTeacherData'

import { useAuthStore } from '@/stores/auth';
import axios from 'axios';
const authStore = useAuthStore(); 
const router = useRouter()

const now = new Date()
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


const { stats, loading, error, upcoming, refresh } = useTeacherData()
const kpis = computed(() => stats.value?.kpis ?? {})

const classes = computed(() => (stats.value?.classes ?? []).map((c, i) => {
  const st = classStatus(c.moyenne)
  return { ...c, color: colorAt(i), status: st.status, statusLabel: st.label }
}))

const events = computed(() => upcoming(4))

const GRADIENTS = [
  'linear-gradient(135deg,#6ee7b7,#4f8ef7)', 'linear-gradient(135deg,#4f8ef7,#a78bfa)',
  'linear-gradient(135deg,#f59e0b,#f87171)', 'linear-gradient(135deg,#a78bfa,#6ee7b7)',
  'linear-gradient(135deg,#f87171,#f59e0b)',
]
const topStudents = computed(() => (stats.value?.top_etudiants ?? []).map((s, i) => ({
  id: s.etudiant_id,
  name: s.nom,
  class: s.classe,
  initials: initials(s.nom),
  grade: `${formatMoyenne(s.moyenne)}/10`,
  gradeColor: colorAt(i),
  pct: `#${i + 1}`,
  gradient: GRADIENTS[i % GRADIENTS.length],
})))

// Matières du prof (année active) avec le nom de classe lisible
const programmes = ref([])
onMounted(async () => {
  try {
    const { data } = await axios.get('/mes-programmes')
    await refresh()
    const noms = Object.fromEntries((stats.value?.classes ?? []).map(c => [c.classe_id, c.nom]))
    programmes.value = (data?.programmes ?? [])
      .map(p => ({ ...p, classe_nom: noms[p.class] ?? '' }))
      .sort((a, b) => (a.classe_nom + a.cours_nom).localeCompare(b.classe_nom + b.cours_nom))
  } catch {
    programmes.value = []
  }
})
</script>

<style>
@keyframes fadeUp { from { opacity:0; transform:translateY(14px) } to { opacity:1; transform:translateY(0) } }
</style>



<template>
  <div class="min-h-screen bg-[#faf8f3] font-sans animate-[fadeUp_0.4s_ease_both]">
    <div class="mx-auto px-4 pb-16 -mt-8">

      <!-- STUDENT HERO -->
      <div class="bg-[#0d0d14] rounded-2xl p-8 py-16 flex items-center gap-6 mb-6 relative overflow-hidden">
        <div class="absolute inset-0 opacity-10">
          <svg width="100%" height="100%">
            <defs>
              <pattern id="dots2" width="30" height="30" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="1.5" fill="white"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#dots2)"/>
          </svg>
        </div>
        <div class="absolute -top-10 -right-10 w-48 h-48 rounded-full bg-[#c9a84c]/20 blur-3xl pointer-events-none"></div>

        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-[#c9a84c] to-[#8a6520] flex items-center justify-center font-serif text-2xl font-bold text-white shrink-0 border-2 border-[#c9a84c]/40">
          {{ initials }}
        </div>

        <div>
          <h1 class="font-serif text-2xl font-bold text-white">{{ student.nom }}</h1>
          <p class="text-[#888] text-sm mt-1">
            Matricule : {{ student.matricule }} &nbsp;·&nbsp; Classe : {{ student.classe }}
          </p>
        </div>
      </div>

      <!-- STATS STRIP -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
        <div v-for="(stat, i) in stats" :key="i"
          class="bg-white rounded-xl p-5 border-[1.5px] border-[#ede9de] relative overflow-hidden hover:-translate-y-0.5 hover:shadow-lg transition-all">
          <div class="absolute top-0 left-0 right-0 h-[3px]" :style="{ background: stat.color }"></div>
          <div class="text-[0.7rem] font-semibold tracking-widest uppercase text-[#999] mb-2">{{ stat.label }}</div>
          <div v-if="!isLoading" class="font-serif text-3xl font-bold leading-none" :style="{ color: stat.color }">
            {{ stat.value }}
          </div>
          <svg v-else class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <div class="text-xs text-[#aaa] mt-1.5">{{ stat.sub }}</div>
        </div>
      </div>

      <!-- TABLE TITLE -->
      <div class="flex items-center gap-3 mb-3">
        <span class="font-serif text-lg font-bold">Détail par cours</span>
        <div class="flex-1 h-px bg-[#e0dbd0]"></div>
        <button
          @click="submitPdf('/imprime-releve-credits', { etudiant_id: authStore.user.user.userable_id }, 'releve')"
          :disabled="loadingMap['releve']"
          class="text-[0.78rem] font-semibold text-[#c9a84c] hover:underline cursor-pointer disabled:opacity-50"
        >
          <svg v-if="loadingMap['releve']" class="animate-spin w-4 h-4 inline" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <span v-else>🖨 Imprimer le relevé</span>
        </button>
      </div>

      <div class="bg-white rounded-xl overflow-hidden shadow-md mb-6">
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-[#0d0d14]">
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#c9a84c]">Cours</th>
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#888]">Crédits</th>
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#888]">Intra</th>
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#888]">Final</th>
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#888]">Crédits obtenus</th>
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#888]">Statut</th>
            </tr>
          </thead>
          <tbody v-if="!isLoading">
            <tr v-if="inscriptions.length === 0">
              <td colspan="6" class="px-5 py-6 text-center text-[#888]">
                Aucune inscription au système à crédits pour le moment.
              </td>
            </tr>
            <tr v-for="i in inscriptions" :key="i.id" class="border-b border-[#f0ece0] last:border-b-0 hover:bg-[#faf8f3] transition-colors">
              <td class="px-5 py-4">
                <div class="font-semibold text-sm text-[#0d0d14]">{{ coursNom(i.cours_id) }}</div>
              </td>
              <td class="px-5 py-4 text-sm text-[#888]">{{ i.credits }}</td>
              <td class="px-5 py-4 text-sm text-[#888]">{{ i.note_intra ?? '—' }}</td>
              <td class="px-5 py-4 text-sm text-[#888]">{{ i.note_finale ?? '—' }}</td>
              <td class="px-5 py-4 text-sm text-[#888]">{{ i.credits_obtenus ?? '—' }}</td>
              <td class="px-5 py-4">
                <span class="text-xs px-2.5 py-1 rounded-full font-medium" :class="statutClass(i.statut)">
                  {{ statutLabel(i.statut) }}
                </span>
              </td>
            </tr>
          </tbody>
          <tbody v-else>
            <tr>
              <td colspan="6" class="px-5 py-6 text-center">
                Chargement...
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePdfWithLoading } from '@/stores/usePdf'
import axios from 'axios'

const authStore = useAuthStore()
const { submitPdf, loadingMap } = usePdfWithLoading()

const student = ref({ nom: '', matricule: '', classe: '' })
const initials = computed(() => {
  const parts = student.value.nom.split(' ')
  return (parts[0]?.[0] || '') + (parts[1]?.[0] || '')
})

const isLoading = ref(true)
const progresData = ref(null)
const coursAll = ref([])

const inscriptions = computed(() => progresData.value?.inscriptions || [])
const coursNom = (id) => coursAll.value.find(c => c.id === id)?.cours_nom || id

const stats = computed(() => [
  { label: 'GPA',              value: progresData.value?.gpa ?? '—',            sub: 'moyenne pondérée / 100', color: '#c9a84c' },
  { label: 'Crédits tentés',   value: progresData.value?.credits_tentes ?? 0,   sub: 'sur ce cursus',          color: '#1a3a6b' },
  { label: 'Crédits validés',  value: progresData.value?.credits_valides ?? 0,  sub: 'vers le diplôme',        color: '#1a7a4a' },
])

const statutClass = (statut) => ({
  en_cours:   'bg-slate-100 text-slate-600',
  valide:     'bg-emerald-100 text-emerald-700',
  echoue:     'bg-red-100 text-red-700',
  abandonne:  'bg-gray-100 text-gray-400',
}[statut] || 'bg-slate-100 text-slate-600')

const statutLabel = (statut) => ({
  en_cours: 'En cours', valide: 'Validé', echoue: 'Échoué', abandonne: 'Abandonné',
}[statut] || statut)

onMounted(async () => {
  if (!authStore.user) await authStore.initializeAuth()
  const etudiantId = authStore.user.user.userable_id

  try {
    const [{ data: etudiantRes }, { data: progres }, { data: cours }] = await Promise.all([
      axios.get(`/etudiant/${etudiantId}`),
      axios.get(`/credits/etudiants/${etudiantId}/progres`),
      axios.get('/cours'),
    ])

    const etudiant = etudiantRes.data
    const dernierClasseEtudiant = etudiant.classes_etudiant?.at(-1)
    const dernierEtudiantFaculte = etudiant.etudiant_facultes?.at(-1)
    student.value = {
      nom: `${etudiant?.nom} ${etudiant?.prenom}`,
      matricule: etudiant?.identifiant,
      classe: dernierEtudiantFaculte?.classes?.nom_classe || dernierClasseEtudiant?.classes?.nom_classe,
    }

    progresData.value = progres
    coursAll.value = Array.isArray(cours) ? cours : (cours?.data ?? [])
  } catch (e) {
    console.error('Erreur chargement progrès crédits:', e)
  } finally {
    isLoading.value = false
  }
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

.font-serif { font-family: 'Playfair Display', serif; }
.font-sans  { font-family: 'DM Sans', sans-serif; }
</style>

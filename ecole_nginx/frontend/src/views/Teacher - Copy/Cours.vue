<template>
  <div class="notes-page min-h-screen bg-[#0a0c10] text-white font-sans">

    <!-- ░░ HEADER ░░ -->
    <div class="relative overflow-hidden border-b border-white/5 px-8 pt-10 pb-8">
      <!-- Ambient glow -->
      <div class="pointer-events-none absolute -top-24 -left-24 w-96 h-96 rounded-full bg-indigo-600/10 blur-3xl"></div>
      <div class="pointer-events-none absolute -top-12 right-0 w-72 h-72 rounded-full bg-violet-600/8 blur-3xl"></div>

      <div class="relative flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <p class="text-xs tracking-[0.25em] uppercase text-indigo-400 mb-1">Espace Professeur</p>
          <h1 class="text-3xl font-bold tracking-tight text-white">
            Mes <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400">Cours & Notes</span>
          </h1>
          <p class="mt-1 text-sm text-white/40">Consultez et gérez les notes par cours, classe et année académique</p>
        </div>

        <!-- Sélecteur d'année -->
        <div class="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-4 py-2 backdrop-blur-sm">
          <svg class="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
          <span class="text-xs text-white/50 mr-1">Année</span>
          <select
            v-model="selectedYear"
            class="bg-transparent text-sm font-semibold text-white border-none outline-none cursor-pointer"
          >
            <option v-for="y in years" :key="y.value" :value="y.value" class="bg-[#1a1d26]">
              {{ y.label }}
            </option>
          </select>
          <span v-if="selectedYear === currentYear" class="ml-2 text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            Actuelle
          </span>
        </div>
      </div>

      <!-- Stats rapides -->
      <div class="relative mt-8 grid grid-cols-2 md:grid-cols-4 gap-3">
        <div v-for="stat in quickStats" :key="stat.label"
          class="group rounded-xl border border-white/5 bg-white/3 hover:bg-white/6 hover:border-white/10 transition-all px-4 py-3">
          <p class="text-2xl font-bold" :class="stat.color">{{ stat.value }}</p>
          <p class="text-xs text-white/40 mt-0.5">{{ stat.label }}</p>
        </div>
      </div>
    </div>

    <!-- ░░ BODY ░░ -->
    <div class="px-8 py-8 space-y-6">

      <!-- Onglets : Tous / Passé / Actuel -->
      <div class="flex items-center gap-1 bg-white/4 border border-white/6 rounded-xl p-1 w-fit">
        <button
          v-for="tab in tabs" :key="tab.value"
          @click="activeTab = tab.value"
          class="relative px-5 py-2 rounded-lg text-sm font-medium transition-all duration-200"
          :class="activeTab === tab.value
            ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/40'
            : 'text-white/40 hover:text-white/70'"
        >
          {{ tab.label }}
          <span v-if="tab.count" class="ml-2 text-[10px] opacity-70">{{ tab.count }}</span>
        </button>
      </div>

      <!-- Grille des cours -->
      <div v-if="filteredCours.length" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        <div
          v-for="cours in filteredCours"
          :key="cours.id"
          class="group relative rounded-2xl border overflow-hidden cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl"
          :class="[
            cours.isActive
              ? 'border-indigo-500/30 hover:border-indigo-500/60 hover:shadow-indigo-900/30'
              : 'border-white/6 hover:border-white/15 hover:shadow-black/40'
          ]"
          @click="selectCours(cours)"
        >
          <!-- Card gradient top bar -->
          <div class="h-1 w-full" :style="`background: linear-gradient(to right, ${cours.color1}, ${cours.color2})`"></div>

          <div class="bg-[#0e1018] p-5">
            <!-- Header cours -->
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0"
                  :style="`background: ${cours.color1}20`">
                  {{ cours.icon }}
                </div>
                <div>
                  <h3 class="font-semibold text-sm text-white leading-tight">{{ cours.nom }}</h3>
                  <p class="text-xs text-white/40 mt-0.5">{{ cours.code }}</p>
                </div>
              </div>
              <span class="text-[10px] px-2 py-1 rounded-full shrink-0 font-medium"
                :class="cours.isActive
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25'
                  : 'bg-white/6 text-white/40 border border-white/8'">
                {{ cours.isActive ? 'En cours' : 'Terminé' }}
              </span>
            </div>

            <!-- Infos -->
            <div class="mt-4 grid grid-cols-3 gap-2 text-center">
              <div class="rounded-lg bg-white/3 py-2 px-1">
                <p class="text-base font-bold text-white">{{ cours.classe }}</p>
                <p class="text-[10px] text-white/35 mt-0.5">Classe</p>
              </div>
              <div class="rounded-lg bg-white/3 py-2 px-1">
                <p class="text-base font-bold text-white">{{ cours.etudiants }}</p>
                <p class="text-[10px] text-white/35 mt-0.5">Étudiants</p>
              </div>
              <div class="rounded-lg bg-white/3 py-2 px-1">
                <p class="text-base font-bold" :class="moyenneColor(cours.moyenne)">{{ cours.moyenne }}%</p>
                <p class="text-[10px] text-white/35 mt-0.5">Moyenne</p>
              </div>
            </div>

            <!-- Horaire -->
            <div class="mt-4 flex flex-wrap gap-2">
              <div v-for="h in cours.horaires" :key="h"
                class="flex items-center gap-1.5 text-[11px] text-white/50 bg-white/4 border border-white/6 rounded-lg px-2.5 py-1">
                <svg class="w-3 h-3 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                {{ h }}
              </div>
            </div>

            <!-- Progress bar notes saisies -->
            <div class="mt-4">
              <div class="flex justify-between text-[10px] text-white/35 mb-1.5">
                <span>Notes saisies</span>
                <span>{{ cours.notesSaisies }}/{{ cours.etudiants }}</span>
              </div>
              <div class="h-1.5 w-full bg-white/6 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all duration-700"
                  :style="`width: ${(cours.notesSaisies/cours.etudiants)*100}%; background: linear-gradient(to right, ${cours.color1}, ${cours.color2})`">
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="mt-4 flex gap-2">
              <button class="flex-1 text-xs py-2 rounded-lg border border-white/8 text-white/50 hover:text-white hover:border-white/20 hover:bg-white/4 transition-all">
                Voir les notes
              </button>
              <button v-if="cours.isActive"
                class="flex-1 text-xs py-2 rounded-lg text-white font-medium transition-all hover:brightness-110"
                :style="`background: linear-gradient(to right, ${cours.color1}, ${cours.color2})`">
                + Ajouter note
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="flex flex-col items-center justify-center py-24 text-center">
        <div class="w-16 h-16 rounded-2xl bg-white/4 border border-white/8 flex items-center justify-center text-2xl mb-4">📭</div>
        <p class="text-white/50 text-sm">Aucun cours pour cette période</p>
        <p class="text-white/25 text-xs mt-1">Essayez une autre année ou un autre filtre</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// ── Années académiques ──────────────────────────────────────────
const currentYear = '2024-2025'
const selectedYear = ref(currentYear)

const years = [
  { value: '2024-2025', label: '2024 — 2025' },
  { value: '2023-2024', label: '2023 — 2024' },
  { value: '2022-2023', label: '2022 — 2023' },
]

// ── Onglets ─────────────────────────────────────────────────────
const activeTab = ref('all')
const tabs = [
  { label: 'Tous',    value: 'all',  count: null },
  { label: 'En cours', value: 'active', count: null },
  { label: 'Terminés', value: 'past',   count: null },
]

// ── Données cours (mock) ─────────────────────────────────────────
const allCours = ref([
  {
    id: 1, nom: 'Mathématiques Avancées', code: 'MATH-301', icon: '∑',
    classe: '3A', etudiants: 28, moyenne: 72, notesSaisies: 28,
    horaires: ['Lun 08h-10h', 'Jeu 10h-12h'],
    color1: '#6366f1', color2: '#8b5cf6',
    annee: '2024-2025', isActive: true,
  },
  {
    id: 2, nom: 'Algorithmique & Structures', code: 'INFO-201', icon: '⌨',
    classe: '2B', etudiants: 32, moyenne: 68, notesSaisies: 30,
    horaires: ['Mar 14h-16h', 'Ven 08h-10h'],
    color1: '#0ea5e9', color2: '#6366f1',
    annee: '2024-2025', isActive: true,
  },
  {
    id: 3, nom: 'Physique Quantique', code: 'PHYS-401', icon: '⚛',
    classe: '4A', etudiants: 20, moyenne: 61, notesSaisies: 20,
    horaires: ['Mer 10h-12h'],
    color1: '#f59e0b', color2: '#ef4444',
    annee: '2024-2025', isActive: false,
  },
  {
    id: 4, nom: 'Bases de Données', code: 'INFO-301', icon: '🗄',
    classe: '3B', etudiants: 25, moyenne: 77, notesSaisies: 25,
    horaires: ['Lun 14h-16h', 'Jeu 08h-10h'],
    color1: '#10b981', color2: '#0ea5e9',
    annee: '2023-2024', isActive: false,
  },
  {
    id: 5, nom: 'Réseaux Informatiques', code: 'INFO-202', icon: '🌐',
    classe: '2A', etudiants: 30, moyenne: 70, notesSaisies: 28,
    horaires: ['Mar 08h-10h'],
    color1: '#8b5cf6', color2: '#ec4899',
    annee: '2023-2024', isActive: false,
  },
])

// ── Filtres ──────────────────────────────────────────────────────
const filteredCours = computed(() => {
  return allCours.value.filter(c => {
    const matchYear = c.annee === selectedYear.value
    const matchTab =
      activeTab.value === 'all' ? true :
      activeTab.value === 'active' ? c.isActive :
      !c.isActive
    return matchYear && matchTab
  })
})

// ── Stats rapides ────────────────────────────────────────────────
const quickStats = computed(() => {
  const list = allCours.value.filter(c => c.annee === selectedYear.value)
  const active = list.filter(c => c.isActive)
  const totalEtu = list.reduce((a, c) => a + c.etudiants, 0)
  const avgMoy = list.length ? Math.round(list.reduce((a, c) => a + c.moyenne, 0) / list.length) : 0
  return [
    { label: 'Cours au total',   value: list.length,   color: 'text-indigo-400' },
    { label: 'Cours actifs',     value: active.length, color: 'text-emerald-400' },
    { label: 'Étudiants suivis', value: totalEtu,      color: 'text-sky-400' },
    { label: 'Moyenne générale', value: avgMoy + '%',  color: 'text-violet-400' },
  ]
})

// ── Helpers ──────────────────────────────────────────────────────
function moyenneColor(m) {
  if (m >= 75) return 'text-emerald-400'
  if (m >= 60) return 'text-amber-400'
  return 'text-red-400'
}

function selectCours(cours) {
  console.log('Cours sélectionné :', cours)
  // → router.push({ name: 'teacher.notes-detail', params: { id: cours.id } })
}
</script>

<style scoped>
.notes-page {
  font-family: 'DM Sans', 'Nunito', ui-sans-serif, system-ui, sans-serif;
}
select option {
  background-color: #1a1d26;
  color: white;
}
</style>
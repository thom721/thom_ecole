<template>
  <div class="min-h-screen bg-[#faf8f3] font-sans animate-[fadeUp_0.4s_ease_both]">


    <div class="mx-auto px-4 pb-16 -mt-8">

      <!-- STUDENT HERO -->
      <div class="bg-[#0d0d14] rounded-2xl p-8 py-16 flex items-center gap-6 mb-6 relative overflow-hidden">
        <!-- Glow -->
              <div class="absolute inset-0 opacity-10">
        <svg width="100%" height="100%">
          <defs>
            <pattern id="dots" width="30" height="30" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1.5" fill="white"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dots)"/>
        </svg>
      </div>
        <div class="absolute -top-10 -right-10 w-48 h-48 rounded-full bg-[#c9a84c]/20 blur-3xl pointer-events-none"></div>
        <!-- Watermark -->
        <span class="absolute bottom-2 right-6 font-serif text-6xl font-black text-white/[0.03] select-none pointer-events-none leading-none">"Excellence"</span>

        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-[#c9a84c] to-[#8a6520] flex items-center justify-center font-serif text-2xl font-bold text-white shrink-0 border-2 border-[#c9a84c]/40">
          {{ initials }}
        </div>

        <div>
          <h1 class="font-serif text-2xl font-bold text-white">{{ student?.nom }}</h1>
          <p class="text-[#888] text-sm mt-1">
            Matricule : {{ student?.matricule }} &nbsp;·&nbsp; Classe : {{ student?.classe }} &nbsp;·&nbsp; Année : {{ student?.annee }}
          </p>
          <div class="flex gap-2 mt-3 flex-wrap">
            <span v-for="badge in student?.badges" :key="badge?.label"
              :class="badge.type === 'gold'
                ? 'bg-[#c9a84c]/20 text-[#c9a84c] border border-[#c9a84c]/30'
                : 'bg-[#1a3a6b]/50 text-[#7eb3ff] border border-[#7eb3ff]/20'"
              class="px-3 py-1 rounded-full text-xs font-semibold">
              {{ badge?.label }}
            </span>
          </div>
        </div>
      </div>
 
      <!-- CONTROLS -->
      <div class="flex gap-3 mb-4 items-center flex-wrap print:hidden">
        <!-- View toggle -->
        <div class="flex bg-[#f0ece0] rounded-lg p-1 gap-1">
          <button
          
            v-for="v in views" :key="v.key"
            @click="selectMonth(v.key)"
            :class="currentView === v.key ? 'bg-[#0d0d14] text-white shadow' : 'text-[#777] hover:text-[#0d0d14]'"
            class="px-4 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer">
            {{ v.label }}
          </button>
        </div> 
        <!-- Month select -->
        <!-- <select v-if="currentView === 'mois'"
          v-model="currentMonth"
          @change="selectMonth(currentMonth)"
          class="px-3 py-2 rounded-lg border-[1.5px] border-[#e0dbd0] bg-white text-sm text-[#0d0d14] outline-none focus:border-[#c9a84c] cursor-pointer">
          <option  v-for="m in months" :key="m.key" :value="m.key">{{ m.label }}</option>
        </select> -->

        <select v-if="currentView === 'mois'"
          v-model="currentMonth"
          @change="selectMonth(currentMonth)"
          class="px-3 py-2 rounded-lg border-[1.5px] border-[#e0dbd0] bg-white text-sm text-[#0d0d14] outline-none focus:border-[#c9a84c] cursor-pointer">
          <option 
            v-for="m in months" :key="m.key" :value="m.key"
            :disabled="month_payes && !month_payes.includes(m.key)"
            :class="month_payes && !month_payes.includes(m.key) ? 'text-gray-300' : ''">
            {{ m.label }} {{ !month_payes?.includes(m.key) ? '🔒' : '' }}
          </option>
        </select>

        <select class="px-3 py-2 rounded-lg border-[1.5px] border-[#e0dbd0] bg-white text-sm text-[#0d0d14] outline-none focus:border-[#c9a84c] cursor-pointer">
          <option>Toutes les matières</option>
          <option>Sciences</option>
          <option>Lettres</option>
          <option>Langues</option>
        </select>
      </div>

      <!-- MONTH TABS @click="currentMonth = m.key"-->
      <div v-if="currentView === 'mois'"
        class="flex gap-2 overflow-x-auto pb-2 mb-5 scrollbar-hide print:hidden">
        <!-- <button
          v-for="m in months" :key="m.key"
          :disabled="!month_payes.includes(groupe.mois)"
          @click="selectMonth(m.key)"
          :class="currentMonth === m.key
            ? 'bg-[#c9a84c] border-[#c9a84c] text-[#0d0d14]'
            : 'bg-white border-[#e0dbd0] text-[#888] hover:border-[#c9a84c] hover:text-[#c9a84c]'"
          class="shrink-0 px-4 py-1.5 rounded-full text-xs font-semibold border-[1.5px] transition-all cursor-pointer">
          {{ m.short }}
        </button> -->
          <button
            v-for="m in months" :key="m.key"
            :disabled="!month_payes.includes(m.key)"
            @click="month_payes.includes(m.key) && selectMonth(m.key)"
            :class="[
              currentMonth === m.key
                ? 'bg-[#c9a84c] border-[#c9a84c] text-[#0d0d14]'
                : month_payes.includes(m.key)
                  ? 'bg-white border-[#e0dbd0] text-[#888] hover:border-[#c9a84c] hover:text-[#c9a84c]'
                  : 'bg-[#f5f5f5] border-[#e0e0e0] text-[#ccc] cursor-not-allowed opacity-50'
            ]"
            class="shrink-0 px-4 py-1.5 rounded-full text-xs font-semibold border-[1.5px] transition-all">
            {{ m.short }} {{ !month_payes.includes(m.key) ? '🔒' : '' }}
          </button>
      </div>



      <!-- STATS STRIP -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div v-for="(stat, i) in currentStats" :key="i"
          class="bg-white rounded-xl p-5 border-[1.5px] border-[#ede9de] relative overflow-hidden hover:-translate-y-0.5 hover:shadow-lg transition-all">
          <div class="absolute top-0 left-0 right-0 h-[3px]" :style="{ background: stat.color }"></div>
          <div class="text-[0.7rem] font-semibold tracking-widest uppercase text-[#999] mb-2">{{ stat.label }}</div>
          <div v-if="!is_all_loading" class="font-serif text-3xl font-bold leading-none" :style="{ color: stat.color }">

            {{ notes.length > 0 ? stat.value :'0' }}<span v-if="stat.sup && notes.length > 0" class="text-lg">{{ stat.sup }}</span>
          </div>
           <svg v-else class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                      </svg>
          <div class="text-xs text-[#aaa] mt-1.5">{{ notes.length > 0 ? stat.sub :'' }}</div>
        </div>
      </div>
       

      <!-- TABLE TITLE -->
      <div class="flex items-center gap-3 mb-3">
        <span class="font-serif text-lg font-bold">{{ currentBulletin.titre }}</span>
        <div class="flex-1 h-px bg-[#e0dbd0]"></div>
      </div>

 

      <div class="bg-white rounded-xl overflow-hidden shadow-md mb-6" id="bulletinTable">
        <div class="flex justify-end items-center mx-4 gap-4">
          <span v-if="currentMonth !== 'all' && notes.length > 0" class="ms-2">
                <button v-if="month_payes && month_payes.includes(currentMonth)"
                      @click="submitPdf('/imprime-bulletin', { bulletin: bulletin_id, mois: currentMonth },currentMonth)"
                      
                      class="text-[0.78rem] font-semibold text-[#c9a84c] hover:underline cursor-pointer" :disabled="loadingMap[currentMonth] === true">
                    
                        <svg v-if="loadingMap[currentMonth] === true" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>Génération...
                      </svg>
                      <span v-else>🖨 Bulletin {{ currentMonth }}</span> 
                    </button>
                    <!-- <p v-if="error" class="text-red-500 text-sm">{{ error }}</p> -->
        </span>
       
          <button v-if="mois_bloques && mois_bloques.length <=0"
                  @click="submitPdf('/imprime-bulletin', { bulletin: bulletin_id, mois: 'all' },'all')"
                  
                  class="text-[0.78rem] font-semibold text-[#c9a84c] hover:underline cursor-pointer" :disabled="loadingMap['all'] === true">
                
                    <svg v-if="loadingMap['all'] === true" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>Génération...
                  </svg>
                  <span v-else>🖨 Bulletin Annuel </span> 
                </button>
                <!-- <p v-if="error" class="text-red-500 text-sm">{{ error }}uuu</p>  -->
        </div>
         <div>
        </div>
        <!-- {{month_payes}} -->
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-[#0d0d14]">
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#c9a84c]">Matière</th>
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#888]">Coef.</th>
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#888]">Note</th>
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#888] hidden md:table-cell">Moy. Classe</th>
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#888] hidden sm:table-cell">Progression</th>
              <th class="px-5 py-3.5 text-left text-[0.7rem] font-semibold tracking-widest uppercase text-[#888]">Mention </th>
            </tr>
          </thead>
          <tbody v-if="!is_all_loading">

            <tr v-if="notes.length === 0">
              <td colspan="6" class="px-5 py-6 text-center text-[#888]">
                Aucune note trouvée pour {{ currentMonth }}
              </td>
            </tr>

            <!-- <template v-else-if="currentMonth === 'all'">
              <template v-for="groupe in notes" :key="groupe.mois">

                 <template v-if="month_payes.includes(groupe.mois)">
                <tr class="bg-[#e8e4d9]">
                  <td colspan="5" class="px-5 py-2 font-bold text-sm text-[#555] tracking-wide">
                    📅 {{ groupe.mois }}
                  </td>

                  <td class="px-5 py-3.5 print:hidden">
                          <button
                            @click="submitPdf('/imprime-bulletin', { bulletin: bulletin_id, mois: groupe.mois },groupe.mois)"
                            
                            class="text-[0.78rem] font-semibold text-[#c9a84c] hover:underline cursor-pointer" :disabled="loadingMap[groupe.mois] === true">
                          
                              <svg v-if="loadingMap[groupe.mois] === true" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>Génération...
                            </svg>
                            <span v-else>🖨 Bulletin</span> 
                          </button>
                        </td>
                </tr>

                <tr v-for="m in groupe.notes" :key="m.matiere"
                  class="border-b border-[#f0ece0] last:border-b-0 hover:bg-[#faf8f3] transition-colors">
                  <td class="px-5 py-4">
                    <div class="font-semibold text-sm text-[#0d0d14]">{{ m.matiere }}</div>
                  </td>
                  <td class="px-5 py-4">
                    <span class="w-7 h-7 rounded-full bg-[#f0ece0] inline-flex items-center justify-center text-xs font-bold text-[#666]">
                      {{ m.coef }}
                    </span>
                  </td>
                  <td class="px-5 py-4">
                    <span class="font-serif text-sm font-bold" :class="getAppreciation((m.note / m.coef) * 100).class">{{ m.note }}</span>
                    <span class="text-[#bbb] text-xs">/{{ m.coef }}</span>
                  </td>
                  <td class="px-5 py-4 text-sm text-[#888] hidden md:table-cell">{{ m.moyClasse }}</td>
                  <td class="px-5 py-4 hidden sm:table-cell">
                    <div class="bg-[#f0ece0] rounded h-1.5 w-20 overflow-hidden">
                      <div class="h-full rounded transition-all duration-700"
                        :style="{ width: ((m.note / m.coef) * 100) + '%', background: noteClass((m.note / m.coef) * 100).bar }">
                      </div>
                    </div>
                  </td>
                  <td class="px-5 py-4">
                    <span class="text-xs px-2.5 py-1 rounded-full font-medium"
                      :class="getAppreciation((m.note / m.coef) * 100).class">
                      {{ getAppreciation((m.note / m.coef) * 100).label }}
                    </span>
                  </td>
                </tr>

              </template>
              </template>
            </template> -->

            <template v-else-if="currentMonth === 'all'">
              <template v-for="groupe in notes" :key="groupe.mois">
                <template v-if="month_payes.includes(groupe.mois)">
                  
                  <!-- En-tête cliquable -->
                  <tr class="bg-[#e8e4d9] cursor-pointer select-none"
                    @click="openMois = openMois === groupe.mois ? null : groupe.mois">
                    <td colspan="5" class="px-5 py-2 font-bold text-sm text-[#555] tracking-wide">
                      <span class="mr-2 transition-transform inline-block"
                        :class="openMois === groupe.mois ? 'rotate-90' : ''">▶</span>
                      📅 {{ groupe.mois }}
                      <span v-if="openMois !== groupe.mois" class="ml-2 text-xs text-[#999] font-normal">
                        ({{ groupe.notes.length }} matières — cliquer pour déployer)
                      </span>
                    </td>
                    <td class="px-5 py-3.5 print:hidden">
                      <button
                        v-if="openMois === groupe.mois"
                        @click.stop="submitPdf('/imprime-bulletin', { bulletin: bulletin_id, mois: groupe.mois }, groupe.mois)"
                        class="text-[0.78rem] font-semibold text-[#c9a84c] hover:underline cursor-pointer"
                        :disabled="loadingMap[groupe.mois] === true">
                        <svg v-if="loadingMap[groupe.mois] === true" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                        </svg>
                        <span v-else>🖨 Bulletin</span>
                      </button>
                    </td>
                  </tr>

                  <!-- Lignes de notes — visibles seulement si ouvert -->
                  <template v-if="openMois === groupe.mois">
                    <tr v-for="m in groupe.notes" :key="m.matiere"
                      class="border-b border-[#f0ece0] last:border-b-0 hover:bg-[#faf8f3] transition-colors">
                      <td class="px-5 py-4">
                        <div class="font-semibold text-sm text-[#0d0d14]">{{ m.matiere }}</div>
                      </td>
                      <td class="px-5 py-4">
                        <span class="w-7 h-7 rounded-full bg-[#f0ece0] inline-flex items-center justify-center text-xs font-bold text-[#666]">
                          {{ m.coef }}
                        </span>
                      </td>
                      <td class="px-5 py-4">
                        <span class="font-serif text-sm font-bold" :class="getAppreciation((m.note / m.coef) * 100).class">{{ m.note }}</span>
                        <span class="text-[#bbb] text-xs">/{{ m.coef }}</span>
                      </td>
                      <td class="px-5 py-4 text-sm text-[#888] hidden md:table-cell">{{ m.moyClasse }}</td>
                      <td class="px-5 py-4 hidden sm:table-cell">
                        <div class="bg-[#f0ece0] rounded h-1.5 w-20 overflow-hidden">
                          <div class="h-full rounded transition-all duration-700"
                            :style="{ width: ((m.note / m.coef) * 100) + '%', background: noteClass((m.note / m.coef) * 100).bar }">
                          </div>
                        </div>
                      </td>
                      <td class="px-5 py-4">
                        <span class="text-xs px-2.5 py-1 rounded-full font-medium"
                          :class="getAppreciation((m.note / m.coef) * 100).class">
                          {{ getAppreciation((m.note / m.coef) * 100).label }}
                        </span>
                      </td>
                    </tr>
                  </template>

                </template>
              </template>
            </template>

            <!-- MODE MOIS SPÉCIFIQUE -->
            <template v-else>
              <tr v-for="m in notes" :key="m.matiere"
                class="border-b border-[#f0ece0] last:border-b-0 hover:bg-[#faf8f3] transition-colors">
                <td class="px-5 py-2">
                  <div class="font-semibold text-sm text-[#0d0d14]">{{ m.matiere }}</div>
                </td>
                <td class="px-5 py-2">
                  <span class="w-7 h-7 rounded-full bg-[#f0ece0] inline-flex items-center justify-center text-xs font-bold text-[#666]">
                    {{ m.coef }}
                  </span>
                </td>
                <td class="px-5 py-2">
                  <span class="font-serif text-sm font-bold" :class="getAppreciation((m.note / m.coef) * 100).class">{{ m.note }}</span>
                  <span class="text-[#bbb] text-xs">/{{ m.coef }}</span>
                </td>
                <td class="px-5 py-2 text-sm text-[#888] hidden md:table-cell">{{ m.moyClasse }}</td>
                <td class="px-5 py-2 hidden sm:table-cell">
                  <div class="bg-[#f0ece0] rounded h-1.5 w-20 overflow-hidden">
                    <div class="h-full rounded transition-all duration-700"
                      :style="{ width: ((m.note / m.coef) * 100) + '%', background: noteClass((m.note / m.coef) * 100).bar }">
                    </div>
                  </div>
                </td>
                <td class="px-5 py-2">
                  <span class="text-xs px-2.5 py-1 rounded-full font-medium"
                    :class="getAppreciation((m.note / m.coef) * 100).class">
                    {{ getAppreciation((m.note / m.coef) * 100).label }}
                  </span>
                </td>
              </tr>
            </template>

            
            <tr class="bg-[#f0ece0] border-t-2 border-[#e0dbd0]">
              <td class="px-5 py-3.5 font-bold text-sm" colspan="2">Moyenne générale pondérée</td>
              <td class="px-5 py-3.5">
                <span class="font-serif text-xl font-bold" :class="noteClass(moyenneGenerale).text">{{ moyenne }}</span>
                <span class="text-[#bbb] text-xs">/10</span>
              </td>
              <td colspan="3"></td>
            </tr>

          </tbody>
          <tbody v-else>
            <tr>
              <td colspan="6" class="px-5 py-6 text-center">
                  Recherche... <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                      </svg>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="bg-gradient-to-br from-[#0d0d14] to-[#1a1a2e] rounded-xl p-6 flex items-start gap-5 mb-6">
        <span class="font-serif text-4xl text-[#c9a84c] leading-none shrink-0 mt-1">❝</span>
        <div>
          <p class="text-white font-semibold text-sm mb-1">Appréciation du conseil de classe</p>
          <p class="text-[#ccc] text-sm leading-relaxed">{{ currentBulletin.appr }}</p>
        </div>
      </div>

    </div>
 
  </div>
</template>

<script setup>
import { ref, computed, onMounted,watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'; 
const bulletinData = ref(null)
 const authStore = useAuthStore(); 
 import { usePdfWithLoading } from '@/stores/usePdf';
const { submitPdf, loading, error, loadingMap } = usePdfWithLoading()

const openMois = ref(null) // mois actuellement ouvert


 const getAppreciation = (pourcentage) => {
  if (pourcentage >= 80) return { label: ' Excellent',  class: 'bg-emerald-100 text-emerald-700' }
  if (pourcentage >= 60) return { label: ' Bien',       class: 'bg-sky-100 text-sky-700'         }
  if (pourcentage >= 50) return { label: ' Passable',   class: 'bg-amber-100 text-amber-700'     }
  return                         { label: ' Insuffisant', class: 'bg-red-100 text-red-700'         }
}

/* ── STUDENT ── */
const student = ref({
  nom: 'Jean-David Pierre',
  matricule: 'ETU-2024-0187',
  classe: 'Terminale A',
  annee: '2024–2025',
  badges: [
    { label: '🏅 Major de classe', type: 'gold' },
    { label: '📚 Section Littéraire', type: 'blue' },
  ]
})

const initials = computed(() => {
  const parts = student.value.nom.split(' ')
  return (parts[0]?.[0] || '') + (parts[1]?.[0] || '')
})
 
const views = [
  { key: 'mois', label: 'Par mois' },
  { key: 'annee', label: 'Annuel' },
]
const currentView = ref('mois')
const is_all_loading = ref(false)

 
const defaultMatieres = (seed = 1) => [
  { nom: 'Philosophie',   code: 'PHI-01', coef: 4, note: 14 + seed, moyClasse: 12.0 },
  { nom: 'Français',      code: 'FRA-01', coef: 4, note: 15 + seed, moyClasse: 13.0 },
  { nom: 'Histoire-Géo',  code: 'HIS-01', coef: 3, note: 13 + seed, moyClasse: 12.0 },
  { nom: 'Mathématiques', code: 'MAT-01', coef: 3, note: 10,         moyClasse: 10.0 },
  { nom: 'Anglais',       code: 'ANG-01', coef: 3, note: 15 + seed, moyClasse: 14.0 },
  { nom: 'Espagnol',      code: 'ESP-01', coef: 2, note: 14,         moyClasse: 13.0 },
  { nom: 'Sciences Nat.', code: 'SCN-01', coef: 2, note: 13,         moyClasse: 11.0 },
  { nom: 'Éd. Physique',  code: 'EPS-01', coef: 1, note: 16,         moyClasse: 15.0 },
]

const bulletins = computed(() => dataStudent.value?.data_etudiant || {
  jan: {
    titre: 'Bulletin — Janvier 2025',
    appr: 'Excellent mois. Jean-David fait preuve d\'une rigueur remarquable et d\'une grande implication dans toutes les matières.',
    matieres: [
      { nom: 'Philosophie',   code: 'PHI-01', coef: 4, note: 18, moyClasse: 12.5 },
      { nom: 'Français',      code: 'FRA-01', coef: 4, note: 16, moyClasse: 13.2 },
      { nom: 'Histoire-Géo',  code: 'HIS-01', coef: 3, note: 15, moyClasse: 12.8 },
      { nom: 'Mathématiques', code: 'MAT-01', coef: 3, note: 11, moyClasse: 10.4 },
      { nom: 'Anglais',       code: 'ANG-01', coef: 3, note: 17, moyClasse: 14.1 },
      { nom: 'Espagnol',      code: 'ESP-01', coef: 2, note: 16, moyClasse: 13.9 },
      { nom: 'Sciences Nat.', code: 'SCN-01', coef: 2, note: 14, moyClasse: 11.8 },
      { nom: 'Éd. Physique',  code: 'EPS-01', coef: 1, note: 17, moyClasse: 15.0 },
    ]
  },
  fev: {
    titre: 'Bulletin — Février 2025',
    appr: 'Bon mois dans l\'ensemble. L\'effort fourni en langues est notable, quelques baisses en sciences à surveiller.',
    matieres: [
      { nom: 'Philosophie',   code: 'PHI-01', coef: 4, note: 16, moyClasse: 12.0 },
      { nom: 'Français',      code: 'FRA-01', coef: 4, note: 15, moyClasse: 12.8 },
      { nom: 'Histoire-Géo',  code: 'HIS-01', coef: 3, note: 14, moyClasse: 12.5 },
      { nom: 'Mathématiques', code: 'MAT-01', coef: 3, note: 12, moyClasse: 10.1 },
      { nom: 'Anglais',       code: 'ANG-01', coef: 3, note: 17, moyClasse: 14.5 },
      { nom: 'Espagnol',      code: 'ESP-01', coef: 2, note: 15, moyClasse: 13.5 },
      { nom: 'Sciences Nat.', code: 'SCN-01', coef: 2, note: 10, moyClasse: 11.2 },
      { nom: 'Éd. Physique',  code: 'EPS-01', coef: 1, note: 18, moyClasse: 15.3 },
    ]
  },
  annee: {
    titre: 'Bulletin Annuel 2024–2025',
    appr: 'Excellente année scolaire. Jean-David s\'est illustré par sa constance et son excellence dans les matières littéraires.',
    matieres: [
      { nom: 'Philosophie',   code: 'PHI-01', coef: 4, note: 17.5, moyClasse: 12.3 },
      { nom: 'Français',      code: 'FRA-01', coef: 4, note: 15.8, moyClasse: 13.0 },
      { nom: 'Histoire-Géo',  code: 'HIS-01', coef: 3, note: 14.7, moyClasse: 12.6 },
      { nom: 'Mathématiques', code: 'MAT-01', coef: 3, note: 11.4, moyClasse: 10.3 },
      { nom: 'Anglais',       code: 'ANG-01', coef: 3, note: 16.9, moyClasse: 14.2 },
      { nom: 'Espagnol',      code: 'ESP-01', coef: 2, note: 15.6, moyClasse: 13.7 },
      { nom: 'Sciences Nat.', code: 'SCN-01', coef: 2, note: 12.8, moyClasse: 11.5 },
      { nom: 'Éd. Physique',  code: 'EPS-01', coef: 1, note: 17.2, moyClasse: 15.1 },
    ]
  },
})


const props = defineProps({
  bulletinData: { type: Object, default: null }
})
 

const dataStudent   = computed(() => bulletinData.value?.data_student   || {})
const allHeaders    = computed(() => bulletinData.value?.allHeaders      || [])
const result        = computed(() => bulletinData.value?.result          || {})
const moyenneClasse = computed(() => bulletinData.value?.moyenne_classe  || 0)
const dataEtudiant  = computed(() => dataStudent.value?.data_etudiant    || {})
 


const months = computed(() =>
  allHeaders.value.map(h => ({
    label: h,
    short: h.slice(0, 3),
    key:   h
  }))
)

const currentMonth = ref('all') // 'all' = annuel

// const notes = computed(()=>{     
//     return Object.entries(dataEtudiant.value).map(([matiere, details]) => {

//       const notes_mensuelles = Object.values(details.notes);
//       const moyenne = notes_mensuelles.reduce((a, b) => a + b, 0) / notes_mensuelles.length;
      
//         let note_a_afficher;
        
//         if (currentMonth.value === 'all') {
          
//           const notes = Object.values(details.notes);
//           note_a_afficher = notes.reduce((a, b) => a + b, 0) / notes.length;
//         } else {
          
//           note_a_afficher = details.notes[currentMonth.value] || 0;
//         }
        
//       if (details.notes.hasOwnProperty(currentMonth.value) || currentMonth.value == 'all') {
//       return {
//         matiere: matiere,
//         note: Math.round(note_a_afficher * 10) / 10, // Arrondir à 1 décimale
//         coef: parseInt(details.coefficients),
//         noteMax: details.coefficients ?? 20,
//         prof: details.professeur_id, // Ou chercher le nom du prof si vous avez une table
//       };
//     }else{
// return {}
//     }
//     })
// })

const notes1 = computed(() => {
  return Object.entries(dataEtudiant.value).map(([matiere, details]) => {
    
    // Filtrer d'abord
    if (currentMonth.value !== 'all' && !details.notes.hasOwnProperty(currentMonth.value)) {
      return null; // on filtrera après
    }

    let note_a_afficher;

    if (currentMonth.value === 'all') {
      const vals = Object.values(details.notes);
      note_a_afficher = vals.reduce((a, b) => a + b, 0) / vals.length;
    } else {
      note_a_afficher = details.notes[currentMonth.value];
    }

    return {
      matiere,
      note: Math.round(note_a_afficher * 10) / 10,
      coef: parseInt(details.coefficients),
      noteMax: details.coefficients ?? 20,
      prof: details.professeur_id,
    };

  }).filter(m => m !== null); // ✅ Supprimer les null
});

const notes = computed(() => {
  if (currentMonth.value === 'all') {
    // Récupérer tous les mois disponibles
    const tousMois = new Set();
    Object.values(dataEtudiant.value).forEach(details => {
      Object.keys(details.notes).forEach(mois => tousMois.add(mois));
    });

    // Retourner un tableau par mois
    return [...tousMois].map(mois => ({
      mois,
      notes: Object.entries(dataEtudiant.value)
        .filter(([_, details]) => details.notes.hasOwnProperty(mois))
        .map(([matiere, details]) => ({
          matiere,
          note: Math.round(details.notes[mois] * 10) / 10,
          coef: parseInt(details.coefficients),
          prof: details.professeur_id,
        }))
    }));
  }

  // Mois spécifique — même logique qu'avant
  return Object.entries(dataEtudiant.value)
    .filter(([_, details]) => details.notes.hasOwnProperty(currentMonth.value))
    .map(([matiere, details]) => ({
      matiere,
      note: Math.round(details.notes[currentMonth.value] * 10) / 10,
      coef: parseInt(details.coefficients),
      prof: details.professeur_id,
    }));
});

const meilleureMatiere = computed(() => {
  if (!notes.value || notes.value.length === 0) return null

  const liste = currentMonth.value === 'all'
    ? notes.value.flatMap(g => g.notes)  // tous les mois
    : notes.value

  if (liste.length === 0) return null

  return liste.reduce((best, m) => {
    const pct = m.note / m.coef
    const bestPct = best.note / best.coef
    return pct > bestPct ? m : best
  })
})

const plusFaibleMatiere = computed(() => {
  if (!notes.value || notes.value.length === 0) return null

  const liste = currentMonth.value === 'all'
    ? notes.value.flatMap(g => g.notes)
    : notes.value

  if (liste.length === 0) return null

  return liste.reduce((worst, m) => {
    const pct = m.note / m.coef
    const worstPct = worst.note / worst.coef
    return pct < worstPct ? m : worst
  })
})
 
const moyenneGenerale = computed(() =>
  currentMonth.value === 'all'
    ? result.value.moyenne
    : null // calculer si dispo
)


/* ── CURRENT BULLETIN ── */
const currentKey = computed(() => currentView.value === 'annee' ? 'annee' : currentMonth.value)

// const currentBulletin = computed(() => {
//   const d = bulletins.value[currentKey.value] 
//   return {
//     titre:`Bulletin `,//— ${m?.label || currentKey.value}`,
//     appr: 'Résultats satisfaisants pour ce mois. Continuez vos efforts dans toutes les matières.',
//     matieres: defaultMatieres(),
//   }
// })

const currentBulletin = computed(() => {
  const moisLabel = currentMonth.value === 'all' 
    ? 'Annuel' 
    : currentMonth.value

  const liste = currentMonth.value === 'all'
    ? notes.value.flatMap(g => g.notes)
    : notes.value

  if (!liste || liste.length === 0) {
    return {
      titre: `Bulletin — ${moisLabel}`,
      appr: 'Aucune note disponible pour cette période.',
      matieres: []
    }
  }

  // Moyenne générale
  const totalNote = liste.reduce((sum, m) => sum + m.note, 0)
  const totalCoef = liste.reduce((sum, m) => sum + m.coef, 0)
  const moy = totalCoef > 0 ? ((totalNote / totalCoef) * 10).toFixed(2) : 0

  // Appréciation automatique
  const appreciation = parseFloat(moy) >= 8 
    ? '🌟 Excellents résultats ! Continuez sur cette lancée.'
    : parseFloat(moy) >= 6 
      ? '👍 Résultats satisfaisants. Continuez vos efforts.'
      : parseFloat(moy) >= 5
        ? '⚠️ Résultats moyens. Des efforts supplémentaires sont nécessaires.'
        : '❌ Résultats insuffisants. Un travail sérieux est indispensable.'

  return {
    titre: `Bulletin — ${moisLabel}`,
    appr: appreciation,
    matieres: liste
  }
})

/* ── COMPUTED MOYENNE ── */
// const moyenneGenerale1 = computed(() => {
//   const mats = currentBulletin.value.matieres
//   const total = mats.reduce((acc, m) => acc + m.note * m.coef, 0)
//   const coefs = mats.reduce((acc, m) => acc + m.coef, 0)
//   return (total / coefs).toFixed(2)
// })

// const bestNote = computed(() => {
//   const mats = currentBulletin.value.matieres
//   return mats.reduce((best, m) => m.note > best.note ? m : best, mats[0])
// })

// const weakNote = computed(() => {
//   const mats = currentBulletin.value.matieres
//   return mats.reduce((weak, m) => m.note < weak.note ? m : weak, mats[0])
// })
 
/* ── STATS ── */
const currentStats = computed(() => [
  { label: 'Moyenne générale', value: moyenne.value, sub: 'sur 10 points',        color: '#c9a84c' },
  { label: 'Meilleure note',   value: meilleureMatiere?.value?.note,  sub: meilleureMatiere?.value?.matiere,     color: '#1a7a4a' },
  { label: 'À améliorer',      value: plusFaibleMatiere?.value?.note,  sub: plusFaibleMatiere?.value?.matiere,     color: '#c0392b' },
  { label: 'Rang / Classe',    value: rang.value,                   sub: `sur ${student_value.value} élèves`,  color: '#1a3a6b', sup: 'e' },
])

/* ── HELPERS ── */
function getMention(note) {
  if (note >= 16) return { label: 'Excellent' }
  if (note >= 14) return { label: 'Bien' }
  if (note >= 10) return { label: 'Moyen' }
  return { label: 'Insuffisant' }
}

const programme_notes = ref({
  annee_academique: '',
  etudiant_id: '',
  mois:'all'
});

const animated = ref(false)
onMounted(async () => {
    if (!authStore.user) await authStore.initializeAuth();
  setTimeout(() => { animated.value = true }, 100)
  const { data } = await axios.get(`/etudiant/${authStore.user.user.userable_id}`)
  const etudiant = data.data
  // console.log(etudiant.nom);
  const dernierClasseEtudiant = etudiant.classes_etudiant?.at(-1);  
  const dernierEtudiantFaculte = etudiant.etudiant_facultes?.at(-1);
  const last_year = dernierClasseEtudiant?.annee_academiques?.annee_academique || "Non definie"


  student.value ={
    nom: `${etudiant?.nom} ${etudiant?.prenom}`,
    matricule: etudiant?.identifiant,
    classe: dernierClasseEtudiant?.classes?.nom_classe,
    annee: last_year,
  badges: [
    { label: '🏅 Major de classe', type: 'gold' }
    // { label: '📚 Section Littéraire', type: 'blue' },
  ]
  }
 

  programme_notes.value = {
  annee_academique: dernierClasseEtudiant.annee_academiques.annee_academique,
  etudiant_id: authStore.user.user.userable_id,
  mois:'all'
}

  reload_data_notes()
})

const bulletin_id = ref('')
const rang = computed(() => bulletinData.value?.result.rang)
const moyenne = computed(() => bulletinData.value?.result.moyenne)
const moyenne_classe = computed(() => bulletinData.value?.moyenne_classe)
const student_value = computed(() => bulletinData.value?.student_value)
const month_payes = ref(null)
const mois_bloques = ref(null)

const reload_data_notes = async ()=>  {
  is_all_loading.value=true
    try {    
      const response = await axios.post('/student-notes', {
      annee_academique: programme_notes.value.annee_academique,
      etudiant_id: programme_notes.value.etudiant_id,
      mois:currentMonth.value
      });
      bulletinData.value = response.data
      const data = response.data?.data_student;
      bulletin_id.value = response?.data?.bulletin_id
      await get_payment_status(programme_notes.value.annee_academique)
    is_all_loading.value=false
    } catch (error) {
      is_all_loading.value=false
      console.error('Erreur:', error.response?.data || error.message);
    }
      
}

const get_payment_status = async (last_year)=>{
  try {
    const response = await axios.post('/get-paiement-statut',{ 
      etudiant_id: authStore.user.user.userable_id,
      annee_academique: last_year  
    });
    const data = response.data;
    month_payes.value=response.data.mois_accessibles 
    mois_bloques.value=response.data.mois_bloques 
    
  } catch (error) {
    
  }
}

const selectMonth = async (moisKey) => {
  if(moisKey=='annee' || moisKey=='mois'){
    currentMonth.value = 'all'
    currentView.value = moisKey 
  }else{
    currentMonth.value = moisKey
  }
  
  await reload_data_notes()
}

function noteClass(note) {
  if (note >= 80) return {
    text: 'text-[#1a7a4a]',
    bar: '#1a7a4a',
    pill: 'bg-[#e8f5ee] text-[#1a7a4a]'
  }
  if (note >= 60) return {
    text: 'text-[#1a3a6b]',
    bar: '#1a3a6b',
    pill: 'bg-[#e8eef8] text-[#1a3a6b]'
  }
  if (note >= 50) return {
    text: 'text-[#9a7a20]',
    bar: '#c9a84c',
    pill: 'bg-[#fdf6e3] text-[#9a7a20]'
  }
  return {
    text: 'text-[#c0392b]',
    bar: '#c0392b',
    pill: 'bg-[#fdecea] text-[#c0392b]'
  }
}

watch(notes, (val) => {
  if (val && val.length > 0 && month_payes.value && month_payes.value.length > 0) {
    const premier = val.find(g => month_payes.value.includes(g.mois))
    if (premier) openMois.value = premier.mois
  }
}, { immediate: true })
 
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

.font-serif { font-family: 'Playfair Display', serif; }
.font-sans  { font-family: 'DM Sans', sans-serif; }

.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }

@media print {
  .print\:hidden { display: none !important; }
}
</style>
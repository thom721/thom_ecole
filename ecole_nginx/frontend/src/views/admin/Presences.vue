<template>
  <div class="animate-[fadeUp_0.3s_ease_both]">

    <!-- Tabs -->
    <div class="flex border-b border-white/[0.07] mb-6">
      <button
        v-for="t in tabs" :key="t.key"
        @click="activeSub = t.key"
        :class="[
          'px-4 py-2.5 text-[13.5px] font-medium border-b-2 -mb-px transition-colors',
          activeSub === t.key
            ? 'border-[var(--accent)] text-[var(--accent)]'
            : 'border-transparent text-[#7c83a0] hover:text-[#e8eaf0]'
        ]"
      >{{ t.label }}</button>
    </div>

    <!-- ════════════════════════════════
         APPEL DU JOUR
    ════════════════════════════════ -->
    <!-- {{ annee_global }} -->
    <div v-if="activeSub === 'appel'">

      <!-- Filtres -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-4 mb-5 grid grid-cols-1 md:grid-cols-5 items-center gap-3 flex-wrap">

        <!-- Niveau -->
        <div class="flex flex-col gap-1 min-w-0">
          <label class="text-[10.5px] uppercase tracking-wider text-[#7c83a0] font-semibold">Niveau</label>
          <select
            v-model="selectedNiveauId"
            @change="onNiveauChange"
            class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition min-w-[120px]"
          >
            <option value="">-- Niveau --</option>
            <option v-for="n in niveau_global" :key="n.id" :value="n.id">{{ n.name }}</option>
          </select>
        </div>

        <!-- Classe -->
        <div class="flex flex-col gap-1 min-w-0">
          <label class="text-[10.5px] uppercase tracking-wider text-[#7c83a0] font-semibold">Classe</label>
          <select
            v-model="selectedClasseId"
            @change="chargerEleves"
            :disabled="!selectedNiveauId"
            class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition disabled:opacity-40 min-w-[130px]"
          >
            <option value="">-- Classe --</option>
            <option v-for="c in classesFiltrees" :key="c.id" :value="c.id">{{ c.nom_classe }}</option>
          </select>
        </div>

        <!-- Année académique → mappée sur annee_academique_id -->
        <div class="flex flex-col gap-1 min-w-0">
          <label class="text-[10.5px] uppercase tracking-wider text-[#7c83a0] font-semibold">Année</label>
          <select
            v-model="selectedAnneeId"
            @change="chargerEleves"
            class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition min-w-[130px]"
          >
            <option value="">-- Année --</option>
            <option v-for="a in annee_global" :key="a.id" :value="a.id">{{ a.libelle ?? a.annee_academique }}</option>
          </select>
        </div>

        <!-- Date → mappée sur date_daujourdhui -->
        <div class="flex flex-col gap-1 min-w-0">
          <label class="text-[10.5px] uppercase tracking-wider text-[#7c83a0] font-semibold">Date</label>
          <input
            v-model="selectedDate"
            type="date"
            class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition"
          />
        </div>

        <!-- Compteurs -->
        <div class="flex gap-2 ml-auto shrink-0 items-end pb-0.5 w-full">
          <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500/15 text-emerald-400 text-nowrap">
            ✓ {{ presentsCount }} présents
          </span>
          <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-red-500/15 text-red-400 text-nowrap">
            ✗ {{ absentsCount }} absents
          </span>
        </div>
      </div>

      <!-- État : sélection incomplète -->
      <div v-if="!selectedClasseId || !selectedAnneeId"
           class="bg-[#171b26] border border-white/[0.07] rounded-xl p-16 text-center">
        <svg class="w-10 h-10 text-[#7c83a0]/20 mx-auto mb-3" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
        </svg>
        <p class="text-[13px] text-[#7c83a0]">Sélectionnez une classe et une année académique</p>
      </div>

      <!-- Chargement élèves -->
      <div v-else-if="loadingEleves"
           class="bg-[#171b26] border border-white/[0.07] rounded-xl p-16 flex flex-col items-center gap-3">
        <div class="w-6 h-6 border-2 border-[var(--accent)]/20 border-t-[var(--accent)] rounded-full animate-spin"></div>
        <p class="text-[13px] text-[#7c83a0]">Chargement des élèves…</p>
      </div>

      <!-- Tableau appel -->
      <div v-else class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">

        <!-- Header -->
        <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between gap-3 flex-wrap">
          <div class="flex items-center gap-2">
            <span class="text-[13.5px] font-medium text-[#e8eaf0]">{{ classeLabel }}</span>
            <span class="font-mono text-[11.5px] text-[#7c83a0] capitalize">— {{ dateLabel }}</span>
            <!-- Badge "déjà enregistré" -->
            <span v-if="dejaEnregistre"
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10.5px] font-medium bg-[var(--accent)]/15 text-[var(--accent)]">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
              </svg>
              Déjà enregistré
            </span>
          </div>
          <div class="flex gap-2">
            <button
              @click="marquerTous(true)"
              class="text-xs font-medium text-white px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 transition-colors"
            >Tous présents</button>
            <button
              @click="marquerTous(false)"
              class="text-xs font-medium text-white px-3 py-1.5 rounded-lg bg-red-600/80 hover:bg-red-600 transition-colors"
            >Tous absents</button>
            <button
              @click="enregistrerAppel"
              :disabled="saving || eleves.length === 0"
              class="text-xs font-medium text-white px-4 py-1.5 rounded-lg transition-all disabled:opacity-50 flex items-center gap-1.5"
              :style="{ background: 'var(--accent)' }"
            >
              <span v-if="saving" class="w-3 h-3 border border-white/30 border-t-white rounded-full animate-spin shrink-0"></span>
              {{ saving ? 'Enregistrement…' : 'Enregistrer l\'appel' }}
            </button>
          </div>
        </div>

        <!-- Feedback succès -->
        <Transition
          enter-active-class="transition-all duration-300 overflow-hidden"
          enter-from-class="opacity-0 max-h-0"
          enter-to-class="opacity-100 max-h-12"
          leave-active-class="transition-all duration-200 overflow-hidden"
          leave-from-class="opacity-100 max-h-12"
          leave-to-class="opacity-0 max-h-0"
        >
          <div v-if="saveSuccess"
               class="px-5 py-2.5 bg-emerald-500/10 border-b border-emerald-500/20 text-[12.5px] text-emerald-400 flex items-center gap-2">
            <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
            </svg>
            Appel enregistré — {{ presentsCount }} présents / {{ absentsCount }} absents
          </div>
        </Transition>

        <!-- Feedback erreur -->
        <Transition
          enter-active-class="transition-all duration-300 overflow-hidden"
          enter-from-class="opacity-0 max-h-0"
          enter-to-class="opacity-100 max-h-12"
          leave-active-class="transition-all duration-200 overflow-hidden"
          leave-from-class="opacity-100 max-h-12"
          leave-to-class="opacity-0 max-h-0"
        >
          <div v-if="saveError"
               class="px-5 py-2.5 bg-red-500/10 border-b border-red-500/20 text-[12.5px] text-red-400 flex items-center gap-2">
            <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/>
            </svg>
            {{ saveError }}
          </div>
        </Transition>

        <!-- Aucun élève -->
        <div v-if="eleves.length === 0"
             class="px-5 py-10 text-center text-[13px] text-[#7c83a0]">
          Aucun élève inscrit dans cette classe
        </div>

        <!-- Rows élèves -->
        <!-- Colonne valeur = Boolean → bouton Présent (true) / Absent (false) -->
        <div v-else class="divide-y divide-white/[0.05]">
          <div
            v-for="(eleve, index) in eleves" :key="eleve.id"
            :class="[
              'flex items-center gap-3 px-5 py-3 transition-colors',
              eleve.valeur === false ? 'bg-red-500/[0.03]' : 'hover:bg-white/[0.02]'
            ]"
          >
            <!-- Numéro -->
            <span class="text-[11px] font-mono text-[#7c83a0]/50 w-5 text-right shrink-0">
              {{ index + 1 }}
            </span>

            <!-- Avatar -->
            <div
              class="w-7 h-7 rounded-full shrink-0 flex items-center justify-center text-[11px] font-bold text-[#0f1117]"
              :style="{
                background: eleve.valeur === null
                  ? '#374151'
                  : eleve.valeur
                    ? `color-mix(in srgb, var(--accent) 75%, #6ee7b7)`
                    : '#7f1d1d'
              }"
            >{{ eleve.initiales }}</div>

            <!-- Nom -->
            <span class="flex-1 text-[13.5px] font-medium truncate"
                  :class="eleve.valeur === false ? 'text-[#9ca3af]' : 'text-[#e8eaf0]'">
              {{ eleve.nom }}
            </span>

            <!-- Matricule -->
            <span v-if="eleve.matricule"
                  class="hidden lg:block font-mono text-[11px] text-[#7c83a0]/50 shrink-0">
              {{ eleve.matricule }}
            </span>

            <!-- Toggle Présent / Absent
                 valeur = true  → Présent
                 valeur = false → Absent
                 valeur = null  → Non marqué (état initial)
            -->
            <div class="flex gap-1.5 shrink-0">
              <button
                @click="eleve.valeur = true"
                :class="[
                  'text-xs px-4 py-1.5 rounded-lg border font-medium transition-all',
                  eleve.valeur === true
                    ? 'bg-emerald-500 text-white border-emerald-500 shadow-sm shadow-emerald-500/25'
                    : 'border-white/[0.1] text-[#7c83a0] hover:border-emerald-500/40 hover:text-emerald-400'
                ]"
              >
                <span class="flex items-center gap-1">
                  <svg v-if="eleve.valeur === true" class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
                  </svg>
                  Présent
                </span>
              </button>

              <button
                @click="eleve.valeur = false"
                :class="[
                  'text-xs px-4 py-1.5 rounded-lg border font-medium transition-all',
                  eleve.valeur === false
                    ? 'bg-red-500 text-white border-red-500 shadow-sm shadow-red-500/25'
                    : 'border-white/[0.1] text-[#7c83a0] hover:border-red-500/40 hover:text-red-400'
                ]"
              >
                <span class="flex items-center gap-1">
                  <svg v-if="eleve.valeur === false" class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                  Absent
                </span>
              </button>
            </div>
          </div>
        </div>

        <!-- Footer récap -->
        <div v-if="eleves.length > 0"
             class="px-5 py-2.5 border-t border-white/[0.07] bg-[#13161f] flex items-center gap-5 text-[12px]">
          <span class="text-[#7c83a0]">
            Total : <strong class="text-[#e8eaf0]">{{ eleves.length }}</strong>
          </span>
          <span class="text-emerald-400">
            Présents : <strong>{{ presentsCount }}</strong>
          </span>
          <span class="text-red-400">
            Absents : <strong>{{ absentsCount }}</strong>
          </span>
          <span class="text-[#7c83a0]">
            Non marqués : <strong class="text-amber-400">{{ nonMarquesCount }}</strong>
          </span>
          <span class="ml-auto font-mono text-[#7c83a0]">
            <span class="text-emerald-400 font-semibold">{{ tauxPresence }}%</span> présence
          </span>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════
         HISTORIQUE
    ════════════════════════════════ -->
    <div v-if="activeSub === 'historique'">
      <!-- Filtres historique -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-4 mb-5 grid grid-cols-1 md:grid-cols-6  items-center gap-3 flex-wrap">
        <div class="flex flex-col gap-1">
          <label class="text-[10.5px] uppercase tracking-wider text-[#7c83a0] font-semibold">Niveau</label>
          <select v-model="histNiveauId" @change="onHistNiveauChange"
            class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition min-w-[120px]">
            <option value="">-- Niveau / Cycle / Séction--</option>
            <option v-for="n in niveau_global" :key="n.id" :value="n.id">{{ n.name }}</option>
          </select>
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-[10.5px] uppercase tracking-wider text-[#7c83a0] font-semibold">Classe</label>
          <select v-model="histClasseId" @change="chargerHistorique"
            class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition min-w-[130px]">
            <option value="">-- Toutes --</option>
            <option v-for="c in histClassesFiltrees" :key="c.id" :value="c.id">{{ c.nom_classe }}</option>
          </select>
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-[10.5px] uppercase tracking-wider text-[#7c83a0] font-semibold">Année acad.</label>
          <select v-model="histAnneeId" @change="chargerHistorique"
            class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition min-w-[130px]">
            <option value="">-- Toutes --</option>
            <option v-for="a in annee_global" :key="a.id" :value="a.id">{{ a.libelle ?? a.annee_academique }}</option>
          </select>
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-[10.5px] uppercase tracking-wider text-[#7c83a0] font-semibold">Mois</label>
          <input v-model="histMois" type="month" @change="chargerHistorique"
            class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition" />
        </div>
      </div>

      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07]">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">Résumé des absences</span>
        </div>
        <div v-if="loadingHist" class="p-12 flex justify-center">
          <div class="w-5 h-5 border-2 border-[var(--accent)]/20 border-t-[var(--accent)] rounded-full animate-spin"></div>
        </div>
        <table v-else class="w-full">
          <thead>
            <tr class="bg-[#13161f]">
              <th v-for="h in ['Élève','Classe','Absences (valeur=false)','Jours total','Taux de présence']" :key="h"
                  class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider whitespace-nowrap">
                {{ h }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="historique.length === 0">
              <td colspan="5" class="px-4 py-10 text-center text-[13px] text-[#7c83a0]">Aucune donnée</td>
            </tr>
            <tr v-for="h in historique" :key="h.id"
                class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
              <td class="px-4 py-3 text-[13.5px] font-medium text-[#e8eaf0]">{{ h.nom }}</td>
              <td class="px-4 py-3 text-[13px] text-[#7c83a0]">{{ h.classe }}</td>
              <td class="px-4 py-3">
                <span :class="['font-mono font-semibold', h.absences > 5 ? 'text-red-400' : h.absences > 2 ? 'text-amber-400' : 'text-[#e8eaf0]']">
                  {{ h.absences }}
                </span>
              </td>
              <td class="px-4 py-3 font-mono text-[#7c83a0]">{{ h.total_jours }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2.5">
                  <div class="w-20 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-500"
                         :class="h.taux > 80 ? 'bg-emerald-500' : h.taux > 60 ? 'bg-amber-500' : 'bg-red-500'"
                         :style="{ width: h.taux + '%' }"></div>
                  </div>
                  <span :class="['text-xs font-mono font-semibold min-w-[36px]',
                    h.taux > 80 ? 'text-emerald-400' : h.taux > 60 ? 'text-amber-400' : 'text-red-400']">
                    {{ h.taux }}%
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ════════════════════════════════
         STATISTIQUES
    ════════════════════════════════ -->
    <div v-if="activeSub === 'stats'">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-5">
        <div v-for="s in statCards" :key="s.label"
             class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5 text-center">
          <p :class="['text-[22px] font-bold font-mono leading-none', s.color]">{{ s.value }}</p>
          <p class="text-xs text-[#7c83a0] mt-2 leading-tight">{{ s.label }}</p>
        </div>
      </div>
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
        <p class="text-[13.5px] font-medium text-[#e8eaf0] mb-5">Présence par classe</p>
        <div class="space-y-4">
          <div v-for="s in statsClasses" :key="s.classe">
            <div class="flex justify-between mb-1.5">
              <span class="text-[13px] font-medium text-[#a0a8c0]">{{ s.classe }}</span>
              <span class="text-[12px] font-mono text-[#7c83a0]">{{ s.val }}%</span>
            </div>
            <div class="h-2 bg-white/[0.06] rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-700"
                   :class="s.val > 85 ? 'bg-emerald-500' : s.val > 70 ? 'bg-amber-500' : 'bg-red-500'"
                   :style="{ width: s.val + '%' }">ererer</div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import {  useSchoolStore,useSchoolStoreInfo } from '@/stores/schoolStore'
import axios from 'axios' 


// ── Store (même que votre layout) ──────────────────────────────────────────
const schoolStore = useSchoolStore()
const { niveau, classes, annee } = storeToRefs(schoolStore)
const {classes_global,annee_global,niveau_global} =useSchoolStoreInfo()
// annee → annee_academique_id dans la table Presence

const tabs = [
  { key: 'appel',      label: 'Appel du jour' },
  { key: 'historique', label: 'Historique'    },
  { key: 'stats',      label: 'Statistiques'  },
]
const activeSub = ref('appel')

// ══════════════════════════════════════════════════════════════════════════
//  APPEL
// ══════════════════════════════════════════════════════════════════════════
const selectedNiveauId = ref('')
const selectedClasseId = ref('')
const selectedAnneeId  = ref('')                              // → annee_academique_id
const selectedDate     = ref(new Date().toISOString().split('T')[0])  // → date_daujourdhui

const loadingEleves  = ref(false)
const saving         = ref(false)
const saveSuccess    = ref(false)
const saveError      = ref('')
const dejaEnregistre = ref(false)

// Tableau réactif : chaque élève a un champ `valeur` (Boolean | null)
// null = pas encore marqué, true = présent, false = absent
const eleves = reactive([])

// Classes filtrées par niveau
const classesFiltrees1 = computed(() =>
  !selectedNiveauId.value
    ? (classes.value ?? [])
    : (classes.value ?? []).filter(c => c.niveau_id == selectedNiveauId.value)
)

watch(activeSub, (newVal) => {
  if (newVal === 'stats') {
    console.log("Onglet stats actif")
    get_stat()
  }
})

// const classesFiltrees1 = computed(() => {
//   const all = classes.value ?? []

//   if (!selectedNiveauId.value) return all

//   return all.filter(
//     c => String(c.niveau_id) === String(selectedNiveauId.value)
//   )
// })

const classesParNiveau = computed(() => {
  const map = {}

  for (const c of classes_global ?? []) {
    if (!map[c.niveau_id]) map[c.niveau_id] = []
    map[c.niveau_id].push(c)
  }

  return map
})

const classesFiltrees = computed(() => {
  if (!selectedNiveauId.value)
    return classes_global.value ?? []

  return classesParNiveau.value[selectedNiveauId.value] ?? []
})



const classeLabel = computed(() => {
  const c = (classes_global ?? []).find(c => c.id == selectedClasseId.value)
  return c?.nom_classe ?? '—'
})
const dateLabel = computed(() =>
  new Date(selectedDate.value + 'T12:00:00').toLocaleDateString('fr-FR', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
  })
)

// Compteurs — basés sur valeur Boolean (pas de retard dans le modèle)
const presentsCount   = computed(() => eleves.filter(e => e.valeur === true).length)
const absentsCount    = computed(() => eleves.filter(e => e.valeur === false).length)
const nonMarquesCount = computed(() => eleves.filter(e => e.valeur === null).length)
const tauxPresence    = computed(() =>
  eleves.length > 0
    ? Math.round((presentsCount.value / eleves.length) * 100)
    : 0
)

function onNiveauChange() {
  selectedClasseId.value = ''
  eleves.splice(0)
  dejaEnregistre.value = false
}

// Charger les élèves de la classe sélectionnée
async function chargerEleves() {
  if (!selectedClasseId.value || !selectedAnneeId.value) return

  loadingEleves.value  = true
  saveSuccess.value    = false
  saveError.value      = ''
  dejaEnregistre.value = false
  eleves.splice(0)

  try {
    // 1. Récupérer les élèves de la classe
    const { data } = await axios.get(
      `/classes/${selectedClasseId.value}/etudiants`,
      { params: { annee_academique_id: selectedAnneeId.value } }
    )
    const liste = Array.isArray(data) ? data : (data.data ?? [])

    liste.forEach(e => {
      eleves.push({
        id:        e.id,
        nom:       [e.prenom, e.nom].filter(Boolean).join(' ') || e.name || '—',
        initiales: mkInitiales(e.prenom ?? '', e.nom ?? e.name ?? ''),
        matricule: e.matricule ?? null,
        valeur:    null,   // null = pas encore marqué
      })
    })

    // 2. Pré-remplir si l'appel a déjà été fait aujourd'hui
    await preRemplirAppel()

  } catch (err) {
    console.error('[Présences] chargerEleves :', err)
    saveError.value = 'Impossible de charger les élèves.'
    setTimeout(() => saveError.value = '', 4000)
  } finally {
    loadingEleves.value = false
  }
}

// Vérifier si un appel existe déjà pour cette classe+date
// GET /api/presences/jour → { etudiant_id: valeur, ... }
async function preRemplirAppel() {
  try {
    const { data } = await axios.get('/presences/jour', {
      params: {
        classes_id:          selectedClasseId.value,
        annee_academique_id: selectedAnneeId.value,
        date:                selectedDate.value,
      }
    })

    // data = { "uuid-etudiant-1": true, "uuid-etudiant-2": false, ... }
    if (Object.keys(data).length > 0) {
      dejaEnregistre.value = true
      eleves.forEach(e => {
        if (data[e.id] !== undefined) {
          e.valeur = data[e.id]   // true ou false
        }
      })
    }
  } catch {
    // Pas d'appel existant → on laisse null (normal)
  }
}

// Marquer tous les élèves avec la même valeur Boolean
function marquerTous(valeur) {   // valeur = true | false
  eleves.forEach(e => e.valeur = valeur)
}

 
async function enregistrerAppel() {
  if (!selectedClasseId.value || !selectedAnneeId.value || eleves.length === 0) return

  // Les élèves non marqués sont considérés absents (valeur=false)
  saving.value      = true
  saveSuccess.value = false
  saveError.value   = ''

  try {
    const payload = {
      classes_id:          selectedClasseId.value,   // classes_id (pas classe_id)
      annee_academique_id: selectedAnneeId.value,
      date_daujourdhui:    selectedDate.value,        // "2025-02-24"
      presences: eleves.map(e => ({
        etudiant_id: e.id,
        valeur:      e.valeur ?? false,               // null → false (absent)
      })),
    }

    await axios.post('/presences', payload)

    saveSuccess.value    = true
    dejaEnregistre.value = true
    setTimeout(() => saveSuccess.value = false, 4000)

  } catch (err) {
    console.error('[Présences] enregistrerAppel :', err)
    const msg = err?.response?.data?.detail ?? err?.response?.data?.message
    saveError.value = msg || "Erreur lors de l'enregistrement."
    setTimeout(() => saveError.value = '', 5000)
  } finally {
    saving.value = false
  }
}

// ══════════════════════════════════════════════════════════════════════════
//  HISTORIQUE
// ══════════════════════════════════════════════════════════════════════════
const histNiveauId = ref('')
const histClasseId = ref('')
const histAnneeId  = ref('')
const histMois     = ref(new Date().toISOString().slice(0, 7))
const loadingHist  = ref(false)
const historique   = reactive([])

const histClassesFiltrees = computed(() =>
  !histNiveauId.value
    ? (classes_global ?? [])
    : (classes_global ?? []).filter(c => c.niveau_id == histNiveauId.value)
)

async function get_stat() {
  const data = await axios.get("/stats-presence-aujourdhui")
  statCards.value = [
  { value: `${data?.data?.global?.taux_presence}%`, label: 'Taux de présence global', color: 'text-emerald-400' },
  { value: data?.data?.global.total_inscrits, label: 'Élèves inscrits', color: 'text-[#e8eaf0]' },
  { value: data?.data?.global.absents, label: "Absents aujourd'hui", color: 'text-red-400' },
  { value: 0, label: "Retards (non applicable)", color: 'text-[#7c83a0]' },
]

statsClasses.value = data?.data?.classes
  // console.log(data?.data);
  
}

function onHistNiveauChange() {
  histClasseId.value = ''
  chargerHistorique()
}

async function chargerHistorique() {
  loadingHist.value = true
  historique.splice(0)

  try {
    const { data } = await axios.get('/presences/historique', {
      params: {
        classe_id:           histClasseId.value  || undefined,
        annee_academique_id: histAnneeId.value   || undefined,
        mois:                histMois.value       || undefined,
      }
    })
    const liste = Array.isArray(data) ? data : (data.data ?? [])

    liste.forEach(h => historique.push({
      id:          h.id,
      nom:         h.nom,
      classe:      h.classe,
      absences:    h.absences,       // nb de valeur=false
      total_jours: h.total_jours ?? (h.absences + Math.round(h.taux / 100 * (h.absences + 1))),
      taux:        h.taux,           // calculé côté FastAPI
    }))

  } catch (err) {
    console.error('[Présences] historique :', err)
  } finally {
    loadingHist.value = false
  }
}

// ══════════════════════════════════════════════════════════════════════════
//  STATS (à brancher sur votre API)
// ══════════════════════════════════════════════════════════════════════════
const statCards = ref({})
const statsClasses = ref({})

// ── Helper ─────────────────────────────────────────────────────────────────
function mkInitiales(prenom, nom) {
  return ((prenom[0] ?? '') + (nom[0] ?? '')).toUpperCase() || '??'
}
</script>

<style scoped>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px) }
  to   { opacity: 1; transform: translateY(0)   }
}
</style>

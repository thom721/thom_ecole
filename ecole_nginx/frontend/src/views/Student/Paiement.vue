<template>
  <div class="min-h-screen bg-[#f4f6f9] font-sans animate-[fadeUp_0.4s_ease_both]">


    <div class="mx-auto px-4 -mt-8 pb-16">

      <!-- STUDENT HERO -->
      <div class="bg-[#0d0d14] rounded-2xl p-8 py-16 flex items-center gap-6 mb-6 relative overflow-hidden">

      <div class="absolute inset-0 opacity-10">
        <svg width="100%" height="100%">
          <defs>
            <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1.5" fill="white"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dots)"/>
        </svg>
      </div>

        <div class="absolute -top-12 -right-12 w-56 h-56 rounded-full bg-[#c9a84c]/15 blur-3xl pointer-events-none"></div>
        <div class="absolute bottom-2 right-6 font-serif text-6xl font-black text-white/[0.03] select-none pointer-events-none leading-none py-8">"Paiements"</div>

        <div class="w-14 h-14 rounded-full bg-gradient-to-br from-[#c9a84c] to-[#8a6520] flex items-center justify-center font-serif text-xl font-bold text-white shrink-0 border-2 border-[#c9a84c]/40">
          {{ initials }}
        </div>

        <div class="flex-1 py-8">
          <h1 class="font-serif text-2xl font-bold text-white">{{ paiement?.details_etudiant?.nom || 'Jean-David Pierre' }}</h1>
          <p class="text-[#888] text-sm mt-1">
            Année : {{ paiement?.details_etudiant?.annee_academique }} &nbsp;·&nbsp;
            <span class="text-[#c9a84c]">{{ paiement?.details_etudiant?.aide_financiere || 'Aucune bourse' }}</span>
          </p>
        </div>

        <!-- QUICK TOTALS -->
        <div class="flex gap-4 shrink-0">
          <div class="text-center">
            <div class="text-[0.65rem] font-semibold tracking-widest uppercase text-[#555] mb-1">Scolarité totale</div>
            <div class="font-serif text-xl font-bold text-white">{{ fmt(totalDu) }}</div>
          </div>
          <div class="w-px bg-[#222]"></div>
          <div class="text-center">
            <div class="text-[0.65rem] font-semibold tracking-widest uppercase text-[#555] mb-1">Payé</div>
            <div class="font-serif text-xl font-bold text-[#1a7a4a]">{{ fmt(totalPaye) }}</div>
          </div>
          <div class="w-px bg-[#222]"></div>
          <div class="text-center">
            <div class="text-[0.65rem] font-semibold tracking-widest uppercase text-[#555] mb-1">Restant</div>
            <div class="font-serif text-xl font-bold" :class="totalRestant > 0 ? 'text-[#e74c3c]' : 'text-[#1a7a4a]'">
              {{ fmt(totalRestant) }}
            </div>
          </div>
        </div>
      </div>

      <!-- CONTROLS -->
      <div class="flex gap-3 mb-5 flex-wrap items-center print:hidden">
        <div class="flex bg-white rounded-lg p-1 gap-1 border border-[#e0dbd0] shadow-sm">
          <button v-for="v in views" :key="v.key"
            @click="currentView = v.key"
            :class="currentView === v.key ? 'bg-[#0d0d14] text-white shadow' : 'text-[#777] hover:text-[#0d0d14]'"
            class="px-4 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer">
            {{ v.label }}
          </button>
        </div>

        <select v-if="currentView === 'versement'"
          v-model="currentMonth"
          class="px-3 py-2 rounded-lg border border-[#e0dbd0] bg-white text-sm text-[#0d0d14] outline-none focus:border-[#c9a84c] cursor-pointer shadow-sm">
          <option v-for="(m,key) in moisDisponibles" :key="key" :value="key">{{ key }}</option>
        </select>
      </div> 
      <!-- MONTH TABS -->
      <div v-if="currentView === 'versement'"
        class="flex gap-2 overflow-x-auto pb-2 mb-5 scrollbar-hide print:hidden">
        <button v-for="(m,index) in moisDisponibles" :key="index"
          @click="currentMonth = index"
          :class="currentMonth === index
            ? 'bg-[#c9a84c] border-[#c9a84c] text-[#0d0d14]'
            : 'bg-white border-[#e0dbd0] text-[#888] hover:border-[#c9a84c] hover:text-[#c9a84c]'"
          class="shrink-0 px-4 py-1.5 rounded-full text-xs font-semibold border transition-all cursor-pointer shadow-sm">
          {{ m }}
        </button>
      </div>

      <!-- ── VUE MENSUELLE ── -->
      <template v-if="currentView === 'versement'">
        <div v-if="currentMoisData" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <!-- Stat cards -->
          <div class="bg-white rounded-xl p-5 border border-[#e8e4d8] shadow-sm relative overflow-hidden hover:-translate-y-0.5 hover:shadow-md transition-all">
            <div class="absolute top-0 left-0 right-0 h-[3px] bg-[#c9a84c]"></div>
            <div class="text-[0.68rem] font-semibold tracking-widest uppercase text-[#999] mb-2">Mensualité</div>
            <div class="font-serif text-2xl font-bold text-[#c9a84c]">{{ fmt(currentMoisData.montant_du) }}</div>
            <div class="text-xs text-[#aaa] mt-1">Montant dû ce mois</div>
          </div>
          <div class="bg-white rounded-xl p-5 border border-[#e8e4d8] shadow-sm relative overflow-hidden hover:-translate-y-0.5 hover:shadow-md transition-all">
            <div class="absolute top-0 left-0 right-0 h-[3px] bg-[#1a7a4a]"></div>
            <div class="text-[0.68rem] font-semibold tracking-widest uppercase text-[#999] mb-2">Versé</div>
            <div class="font-serif text-2xl font-bold text-[#1a7a4a]">{{ fmt(currentMoisData.montant_paye) }}</div>
            <div class="text-xs text-[#aaa] mt-1">Total versé ce mois</div>
          </div>
          <div class="bg-white rounded-xl p-5 border border-[#e8e4d8] shadow-sm relative overflow-hidden hover:-translate-y-0.5 hover:shadow-md transition-all">
            <div class="absolute top-0 left-0 right-0 h-[3px]" :class="currentMoisData.restant > 0 ? 'bg-[#e74c3c]' : 'bg-[#1a7a4a]'"></div>
            <div class="text-[0.68rem] font-semibold tracking-widest uppercase text-[#999] mb-2">Restant</div>
            <div class="font-serif text-2xl font-bold" :class="currentMoisData.restant > 0 ? 'text-[#e74c3c]' : 'text-[#1a7a4a]'">
              {{ fmt(currentMoisData.restant) }}
            </div>
            <div class="text-xs mt-1" :class="currentMoisData.restant > 0 ? 'text-[#e74c3c]/70' : 'text-[#1a7a4a]/70'">
              {{ currentMoisData.restant > 0 ? 'Solde impayé' : '✓ Soldé' }}
            </div>
          </div>
        </div>

        <!-- Progress bar -->
        <div v-if="currentMoisData" class="bg-white rounded-xl p-5 border border-[#e8e4d8] shadow-sm mb-5">
          <div class="flex justify-between items-center mb-3">
            <span class="text-sm font-semibold text-[#0d0d14]">Progression du paiement</span>
            <span class="text-sm font-bold" :class="currentMoisData.pct >= 100 ? 'text-[#1a7a4a]' : 'text-[#c9a84c]'">
              {{ currentMoisData.pct }}%
            </span>
          </div>
          <div class="bg-[#f0ece0] rounded-full h-3 overflow-hidden">
            <div class="h-full rounded-full transition-all duration-700"
              :style="{ width: currentMoisData.pct + '%', background: currentMoisData.pct >= 100 ? '#1a7a4a' : '#c9a84c' }">
            </div>
          </div>
          <div class="flex justify-between mt-2 text-[0.7rem] text-[#bbb]">
            <span>0 HTG</span>
            <span>{{ fmt(currentMoisData.montant_du) }}</span>
          </div>
        </div>

        <!-- Versements list -->
        <div class="bg-white rounded-xl overflow-hidden border border-[#e8e4d8] shadow-sm mb-5">
          <div class="px-6 py-4 border-b border-[#f0ece0] flex items-center gap-3">
            <span class="font-serif text-base font-bold text-[#0d0d14]">Versements effectués</span>
            <span class="flex-1 h-px bg-[#f0ece0]"></span>
            <span class="bg-[#0d0d14] text-[#c9a84c] text-xs font-bold px-2.5 py-1 rounded-full">
              {{ versements?.length || 0 }}
            </span>
          </div>
          <table class="w-full border-collapse">
            <thead>
              <tr class="bg-[#faf8f3]">
                <th class="px-5 py-3 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#bbb]">#</th>
                <th class="px-5 py-3 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#bbb]">Date</th>
                <th class="px-5 py-3 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#bbb]">Montant</th>
                <th class="px-5 py-3 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#bbb] hidden sm:table-cell">Mode</th>
                <th class="px-5 py-3 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#bbb]">Statut</th>
                <th class="px-5 py-3 print:hidden"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!versements?.length">
                <td colspan="6" class="px-5 py-8 text-center text-[#bbb] text-sm">Aucun versement na ete enregistre</td>
              </tr>
              <tr v-for="(v, i) in versements" :key="i"
                class="border-t border-[#f0ece0] hover:bg-[#faf8f3] transition-colors">
                <td class="px-5 py-3.5 text-sm text-[#bbb] font-mono">{{ String(i + 1).padStart(2, '0') }}</td>
                <td class="px-5 py-3.5 text-sm text-[#0d0d14]">{{ formatDate(v.date, true) }}</td>
                <td class="px-5 py-3.5">
                  <span class="font-serif text-base font-bold text-[#1a7a4a]">{{ fmt(v.depot) }}</span>
                </td>
                <td class="px-5 py-3.5 text-sm text-[#888] hidden sm:table-cell">{{ v.mode || 'Cash' }}</td>
                <td class="px-5 py-3.5">
                  <span class="px-2.5 py-1 rounded-full text-[0.68rem] font-bold bg-[#e8f5ee] text-[#1a7a4a]">✓ Validé</span>
                </td>
                
                 <td class="px-5 py-3.5 print:hidden">
                    <button
                      @click="submitPdf('/print-recu', { id: paiement_id, key: i }, i)"
                      
                      class="text-[0.78rem] font-semibold text-[#c9a84c] hover:underline cursor-pointer" :disabled="loadingMap[i] === true" >  
                      <svg v-if="loadingMap[i] === true" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>Génération...
                      </svg>
                     <span v-else>🖨 Reçu</span>
                    </button>
                    <p v-if="error[i]" class="text-red-500 text-sm">{{ error }}</p>
                  </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <!-- ── VUE ANNUELLE ── -->
      <template v-if="currentView === 'annee'">

        <!-- Récap global -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <div v-for="s in statsAnnuelles" :key="s.label"
            class="bg-white rounded-xl p-2 border border-[#e8e4d8] shadow-sm relative overflow-hidden hover:-translate-y-0.5 hover:shadow-md transition-all">
            <div class="absolute top-0 left-0 right-0 h-[3px]" :style="{ background: s.color }"></div>
            <div class="text-[0.65rem] font-semibold tracking-widest uppercase text-[#999] mb-2">{{ s.label }}</div>
            <div class="font-serif text-2xl font-bold" :style="{ color: s.color }">{{ s.value }}</div>
            <div class="text-xs text-[#aaa] mt-1">{{ s.sub }}</div>
          </div>
        </div>

        <!-- Table mois par mois -->
        <div class="bg-white rounded-xl overflow-hidden border border-[#e8e4d8] shadow-sm mb-5">
          <div class="px-6 py-4 border-b border-[#f0ece0]">
            <span class="font-serif text-base font-bold text-[#0d0d14]">Récapitulatif annuel</span>
          </div>
          <table class="w-full border-collapse">
            <thead>
              <tr class="bg-[#0d0d14]">
                <th class="px-5 py-3.5 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#c9a84c]">Mois / Versement</th>
                <th class="px-5 py-3.5 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#888]">Dû</th>
                <th class="px-5 py-3.5 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#888]">Versé</th>
                <th class="px-5 py-3.5 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#888]">Restant</th>
                <th class="px-5 py-3.5 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#888] hidden sm:table-cell">Versements</th>
                <th class="px-5 py-3.5 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#888]">Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in moisAnnuels" :key="m.key"
                class="border-t border-[#f0ece0] hover:bg-[#faf8f3] transition-colors cursor-pointer"
                @click="goToMois(m.key)">
                <td class="px-5 py-3.5">
                  <div class="font-semibold text-sm text-[#0d0d14]">{{ m.label }}</div>
                </td>
                <td class="px-5 py-3.5 text-sm text-[#888]">{{ fmt(m.montant_du) }}</td>
                <td class="px-5 py-3.5">
                  <span class="font-serif text-base font-bold text-[#1a7a4a]">{{ fmt(m.montant_paye) }}</span>
                </td>
                <td class="px-5 py-3.5">
                  <span class="font-serif text-base font-bold"
                    :class="m.restant > 0 ? 'text-[#e74c3c]' : 'text-[#1a7a4a]'">
                    {{ fmt(m.restant) }}
                  </span>
                </td>
                <td class="px-5 py-3.5 text-sm text-[#888] hidden sm:table-cell">
                  {{ m.versements?.length || 0 }} versement(s)
                </td>
                <td class="px-5 py-3.5">
                  <div class="flex items-center gap-2">
                    <div class="bg-[#f0ece0] rounded-full h-1.5 w-16 overflow-hidden">
                      <div class="h-full rounded-full"
                        :style="{ width: m.pct + '%', background: m.pct >= 100 ? '#1a7a4a' : m.pct > 0 ? '#c9a84c' : '#e74c3c' }">
                      </div>
                    </div>
                    <span class="text-[0.68rem] font-bold"
                      :class="m.pct >= 100 ? 'text-[#1a7a4a]' : m.pct > 0 ? 'text-[#c9a84c]' : 'text-[#e74c3c]'">
                      {{ m.pct }}%
                    </span>
                  </div>
                </td>
              </tr>

              <!-- TOTAL -->
              <tr class="bg-[#f0ece0] border-t-2 border-[#e0dbd0]">
                <td class="px-5 py-3.5 font-bold text-sm">TOTAL</td>
                <td class="px-5 py-3.5 font-bold text-sm">{{ fmt(totalDu) }}</td>
                <td class="px-5 py-3.5">
                  <span class="font-serif text-base font-bold text-[#1a7a4a]">{{ fmt(totalPaye) }}</span>
                </td>
                <td class="px-5 py-3.5">
                  <span class="font-serif text-base font-bold" :class="totalRestant > 0 ? 'text-[#e74c3c]' : 'text-[#1a7a4a]'">
                    {{ fmt(totalRestant) }}
                  </span>
                </td>
                <td colspan="2"></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Accessoires -->
        <div v-if="details.accessoires?.length" class="bg-white rounded-xl overflow-hidden border border-[#e8e4d8] shadow-sm mb-5">
          <div class="px-6 py-4 border-b border-[#f0ece0]">
            <span class="font-serif text-base font-bold text-[#0d0d14]">Accessoires & Frais divers</span>
          </div>
          <table class="w-full border-collapse">
            <thead>
              <tr class="bg-[#faf8f3]">
                <th class="px-5 py-3 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#bbb]">Désignation</th>
                <th class="px-5 py-3 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#bbb]">Montant</th>
                <th class="px-5 py-3 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#bbb]">Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(acc, i) in details.accessoires" :key="i"
                class="border-t border-[#f0ece0] hover:bg-[#faf8f3] transition-colors">
                <td class="px-5 py-3.5 text-sm font-semibold text-[#0d0d14]">{{ acc.nom || acc.designation }}</td>
                <td class="px-5 py-3.5">
                  <span class="font-serif text-base font-bold text-[#c9a84c]">{{ fmt(acc.montant) }}</span>
                </td>
                <td class="px-5 py-3.5">
                  <span :class="acc.paye ? 'bg-[#e8f5ee] text-[#1a7a4a]' : 'bg-[#fdecea] text-[#e74c3c]'"
                    class="px-2.5 py-1 rounded-full text-[0.68rem] font-bold">
                    {{ acc.paye ? '✓ Payé' : '✗ Impayé' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

       
 <!-- _allMonths1{{ _allMonths1 }}
 <br>
echeancesList {{ echeancesList  }} -->
<!-- <p class="py-2 bg-red-100">
  {{ paiement?.info_paiement }}
</p>
 
{{ versements }}

<p class="py-2 bg-yellow-100">
  {{ echeances }}
</p>
<p class="py-4 bg-red-100">
  {{ details }}
</p> -->
<!-- <p class="py-2 bg-yellow-100">
  {{ infoP }}
</p> -->

      <!-- AIDE FINANCIÈRE BADGE -->
      <div v-if="paiement.aide_financiere && paiement.aide_financiere !== 'Aucune'"
        class="bg-gradient-to-br from-[#0d0d14] to-[#1a1a2e] rounded-xl p-5 flex items-center gap-4">
        <div class="w-10 h-10 rounded-full bg-[#c9a84c]/20 flex items-center justify-center text-lg shrink-0">🎓</div>
        <div>
          <p class="text-white font-semibold text-sm">Aide financière accordée</p>
          <p class="text-[#c9a84c] text-sm font-bold">{{ paiement.aide_financiere }}</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, computed,onMounted } from 'vue'
import { storeToRefs } from 'pinia'; 
import { useAuthStore } from '@/stores/auth'
import { usePdfWithLoading } from '@/stores/usePdf';
const authStore = useAuthStore(); 
const { user, isAdmin, isTeacher, roleNames } = storeToRefs(authStore);
 
const { submitPdf, loading, error, loadingMap } = usePdfWithLoading()

//  const imprimerBulletin = () => submitPdf('/print/bulletin', {
//   etudiant_id: props.etudiantId,
//   mois: currentMonth.value,
// })
const paiementData = ref({})

const demoData = {
  etudiant_nom: 'Jean-David Pierre',
  annee_academique: '2025/2026',
  paiement_details: {
    info_paiement: {
      total_scolarite: 85000,
    },
    aide_financiere: 'Démie Bourse',
    accessoires: [
      { nom: 'Frais d\'inscription', montant: 5000, paye: true },
      { nom: 'Uniforme scolaire',    montant: 3500, paye: true },
      { nom: 'Manuel scolaire',      montant: 2800, paye: false },
    ],
    mois: {
      sept: { montant_du: 7000, montant_paye: 7000, versements: [{ date: '2025-09-05', montant: 7000, mode: 'Cash' }] },
      oct:  { montant_du: 7000, montant_paye: 5000, versements: [{ date: '2025-10-03', montant: 3000, mode: 'Cash' }, { date: '2025-10-18', montant: 2000, mode: 'Virement' }] },
      nov:  { montant_du: 7000, montant_paye: 7000, versements: [{ date: '2025-11-04', montant: 7000, mode: 'Cash' }] },
      dec:  { montant_du: 7000, montant_paye: 3500, versements: [{ date: '2025-12-06', montant: 3500, mode: 'Cash' }] },
      jan:  { montant_du: 7000, montant_paye: 0,    versements: [] },
      fev:  { montant_du: 7000, montant_paye: 0,    versements: [] },
      mar:  { montant_du: 7000, montant_paye: 0,    versements: [] },
      avr:  { montant_du: 7000, montant_paye: 0,    versements: [] },
      mai:  { montant_du: 7000, montant_paye: 0,    versements: [] },
      juin: { montant_du: 7000, montant_paye: 0,    versements: [] },
    }
  }
}

const paiement = computed(() => paiementData.value || demoData)
const details  = computed(() => paiement.value.paiement_details || {})

const details1   = computed(() => paiement.value.details_etudiant)
const infoP     = computed(() => paiement.value.info_paiement)      // objet clé=date
const echeances = computed(() => paiement.value.check_echeance)     // { "1er Versement": 22500, ... }
const aide      = computed(() => paiement.value.aide_financiere)

const versements = computed(() => {
  const info = paiement.value?.info_paiement
  if (!info) return []
  return Object.entries(info).map(([date, v]) => ({ date, ...v }))
})

/* ── INITIALS ── */
const initials = computed(() => {
  const fullName = paiement.value.details_etudiant?.nom + paiement.value.details_etudiant?.prenom
  const parts = (fullName || '').split(' ')
  return (parts[0]?.[0] || '') + (parts[1]?.[0] || '')
})

/* ── VIEWS ── */
const views = [
  { key: 'versement',  label: 'Par versement' },
  { key: 'annee', label: 'Annuel' },
]
const currentView  = ref('versement')
const currentMonth = ref('oct')

/* ── MOIS CONFIG ── */

const allMonths = [
  { key: 'sept', label: 'Septembre', short: 'Sep' },
  { key: 'oct',  label: 'Octobre',   short: 'Oct' },
  { key: 'nov',  label: 'Novembre',  short: 'Nov' },
  { key: 'dec',  label: 'Décembre',  short: 'Déc' },
  { key: 'jan',  label: 'Janvier',   short: 'Jan' },
  { key: 'fev',  label: 'Février',   short: 'Fév' },
  { key: 'mar',  label: 'Mars',      short: 'Mar' },
  { key: 'avr',  label: 'Avril',     short: 'Avr' },
  { key: 'mai',  label: 'Mai',       short: 'Mai' },
  { key: 'juin', label: 'Juin',      short: 'Juin' },
]

const _allMonths1 = computed(() => {
  const ech = paiement.value?.check_echeance || {}
  return Object.entries(ech).map(([label, montant]) => ({
    key: label,        // "1er Versement"
    label,             // "1er Versement"
    montant,           // 22500
  }))
})

const echeancesList = computed(() => {
  const ech = paiement.value?.check_echeance || {}
  const infos = Object.values(paiement.value?.info_paiement || {})

  return Object.entries(ech).map(([label, montant]) => {
    const acquitte = infos.some(v =>
      v.status_paiement?.some(s => s.startsWith('Acqt') && s.includes(label))
    )
    const enCours = infos.some(v =>
      v.status_paiement?.some(s => s.startsWith('Avns') && s.includes(label))
    )
    return {
      key: label,
      label,
      montant,
      statut: acquitte ? 'acquitte' : enCours ? 'en_cours' : 'impaye'
    }
  })
})

const moisDisponibles = computed(() =>
    paiement.value.check_echeance
  // allMonths.filter(m => details.value.mois?.[m.key])
)

/* ── CURRENT MONTH DATA ── */
const currentMoisData = computed(() => {
  const raw = details.value.mois?.[currentMonth.value]
  if (!raw) return null
  const restant = (raw.montant_du || 0) - (raw.montant_paye || 0)
  const pct = raw.montant_du > 0 ? Math.round((raw.montant_paye / raw.montant_du) * 100) : 0
  return { ...raw, restant: Math.max(restant, 0), pct: Math.min(pct, 100) }
})

/* ── ANNUAL DATA ── */
const moisAnnuels1 = computed(() =>
  allMonths
    .filter(m => details.value.mois?.[m.key])
    .map(m => {
      const raw = details.value.mois[m.key]
      const restant = Math.max((raw.montant_du || 0) - (raw.montant_paye || 0), 0)
      const pct = raw.montant_du > 0 ? Math.round((raw.montant_paye / raw.montant_du) * 100) : 0
      return { ...m, ...raw, restant, pct: Math.min(pct, 100) }
    })
)

const dernierVersement = computed(() => {
  const info = infoP.value
  if (!info || !Object.keys(info).length) return null

  // Trier les clés par date et prendre la dernière
  const derniereDate = Object.keys(info).sort((a, b) => {
    const parseDate = d => {
      const [datePart, timePart] = d.split(' ')
      const [day, month, year] = datePart.split('-')
      return new Date(`${year}-${month}-${day} ${timePart}`)
    }
    return parseDate(a) - parseDate(b)
  }).at(-1)

  return info[derniereDate]
})

// Directement disponibles depuis le dernier versement
const totalPaye    = computed(() => dernierVersement.value?.total_verse  || 0)
const totalDu  = computed(() => dernierVersement.value?.total_annuel || 0)
const totalRestant = computed(() =>totalDu.value - totalPaye.value) //dernierVersement.value?.balance      || 0)


const moisAnnuels = computed(() => {
  const ech = paiement.value?.check_echeance || {}
  const infos = Object.values(infoP.value || {})

  return Object.entries(ech).map(([label, montant]) => {
    // Chercher le versement correspondant dans info_paiement
    const versement = infos.find(v =>
      v.status_paiement?.some(s => s.includes(label))
    )

    const acquitte = infos.some(v =>
      v.status_paiement?.some(s => s.startsWith('Acqt') && s.includes(label))
    )
    const enCours = infos.some(v =>
      v.status_paiement?.some(s => s.startsWith('Avns') && s.includes(label))
    )

    const montant_paye = acquitte ? montant : enCours ? (versement?.depot_et_avance || 0) : 0
    const restant      = Math.max(montant - montant_paye, 0)
    const pct          = montant > 0 ? Math.min(Math.round((montant_paye / montant) * 100), 100) : 0

    return {
      key:          label,           // "1er Versement"
      label,                         // "1er Versement"
      montant_du:   montant,         // 22500
      montant_paye,                  // 22500 ou 0
      restant,                       // 0 ou 4500
      pct,                           // 100 ou 0
      statut:       acquitte ? 'acquitte' : enCours ? 'en_cours' : 'impaye',
      versements:   infos.filter(v =>
        v.status_paiement?.some(s => s.includes(label))
      )
    }
  })
})


const statsAnnuelles = computed(() => [
  { label: 'Scolarité totale', value: fmt(details.value.info_paiement?.total_scolarite || totalDu.value), sub: 'Montant annuel', color: '#c9a84c' },
  { label: 'Total versé',      value: fmt(totalPaye.value),    sub: 'Cumulé sur l\'année', color: '#1a7a4a' },
  { label: 'Solde restant',    value: fmt(totalRestant.value), sub: totalRestant.value > 0 ? 'À régler' : 'Soldé ✓', color: totalRestant.value > 0 ? '#e74c3c' : '#1a7a4a' },
  { label: 'Mois / Vers. payés',
    value: moisAnnuels.value.filter(m => m.pct >= 100).length + '/' + moisAnnuels.value.length,
    sub: 'Mois / Vers. complets',
    color: '#1a3a6b' },
])

/* ── HELPERS ── */
function fmt(n) {
  if (n === undefined || n === null) return '—'
  return new Intl.NumberFormat('fr-HT', { style: 'currency', currency: 'HTG', minimumFractionDigits: 0 }).format(n)
}


function formatDate(d, avecHeure = false) {
  if (!d) return '—'
  const [datePart, timePart] = d.split(' ')
  const [day, month, year] = datePart.split('-')
  const date = new Date(`${year}-${month}-${day}`)
  const dateStr = date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
  return avecHeure && timePart ? `${dateStr} à ${timePart}` : dateStr
}
 

function goToMois(key) {
  currentView.value = 'mois'
  currentMonth.value = key
}


function printVersement(v, i) {
  const m = allMonths.find(x => x.key === currentMonth.value)
 
}
const paiement_id=ref('')
const reload_data_paie = async (last_year)=>  {   
    try {      
  const response = await axios.post('/student-paiments', {
    etudiant_id: authStore?.user?.user?.userable_id,
    annee_academique: last_year ?? student.value?.annee
  });
  
  const data = response.data?.show_paiement;
  const echeance = data?.paiement_details?.paiement_details?.check_echeance
  // const status_bourse = data?.paiement_details?.paiement_details?.aide_financiere
  const info_paiement = data?.paiement_details?.paiement_details?.info_paiement
  const details_etudiant = data?.paiement_details?.paiement_details?.details_etudiant
  paiement_id.value= response.data.show_paiement?.id
  paiementData.value =data?.paiement_details?.paiement_details

  console.log('Données reçues response:', response.data); 
  
} catch (error) {
  console.error('Erreur:', error.response?.data || error.message);
}
  
}

onMounted(()=>{
  reload_data_paie('2025/2026')
})
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
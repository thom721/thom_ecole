<template>
  <div class="animate-[fadeUp_0.4s_ease_both]">

    <!-- Tabs -->
    <div class="flex border-b border-white/[0.07] mb-6">
      <button v-for="t in tabs" :key="t.key" @click="activeSub = t.key"
        :class="['px-4 py-2.5 text-[13.5px] font-medium border-b-2 -mb-px transition-colors',
          activeSub === t.key ? 'border-[var(--accent)] text-[var(--accent)]' : 'border-transparent text-[#7c83a0] hover:text-[#e8eaf0]']">
        {{ t.label }}
      </button>
    </div>

    <!-- ══ VENTES ══════════════════════════════════════════════════ -->
    <div v-if="activeSub === 'vente'">
      <!-- Stats cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
        <div v-for="c in ventesCards" :key="c.label" class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
          <p class="text-xs text-[#7c83a0] mb-2">{{ c.label }}</p>
          <p :class="['text-[22px] font-semibold font-mono tracking-tight leading-none', c.color]">
            {{ c.value }} <span class="text-base font-sans font-normal text-[#7c83a0]">{{ c.unit }}</span>
          </p>
          <p v-if="c.sub" class="text-xs mt-2" :class="c.subColor ?? 'text-[#7c83a0]'">{{ c.sub }}</p>
        </div>
      </div>

      <!-- Table + recherche -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between gap-3">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">
            Transactions · <span class="text-[#7c83a0] font-mono text-xs">{{ ventesMeta.total ?? 0 }}</span>
          </span>
          <input v-model="venteSearch" @input="debounceVente" type="text" placeholder="Rechercher…"
            class="text-[12px] bg-[#0d1117] border border-white/[0.08] rounded-lg px-3 py-1.5 text-[#c9d1d9] focus:outline-none focus:border-[var(--accent)]/40 w-48"/>
        </div>

        <!-- Skeleton -->
        <div v-if="venteLoading" class="animate-pulse px-5 py-4 space-y-3">
          <div v-for="i in 6" :key="i" class="h-8 bg-white/[0.04] rounded"></div>
        </div>

        <table v-else class="w-full">
          <thead>
            <tr class="bg-[#13161f]">
              <th v-for="h in ['###','Élève','Montant','Date','Action']" :key="h"
                  class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="ventes.length === 0"><td colspan="5" class="px-4 py-8 text-center text-[#7c83a0] text-sm">Aucune vente trouvée</td></tr>
            <tr v-for="t in ventes" :key="t.id" class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
              <td class="px-4 py-3 text-[13px] font-mono text-[#7c83a0]">{{ t.order_itemId }}</td>
              <td class="px-4 py-3 text-[13.5px] font-medium text-[#e8eaf0]">{{ t.nom }}</td>
              <td class="px-4 py-3 font-mono text-[13.5px]" :class="t.total > 0 ? 'text-emerald-400' : 'text-[#e8eaf0]'">
                {{ Number(t.total).toLocaleString('fr-FR') }} HTG
              </td>
              <td class="px-4 py-3 font-mono text-xs text-[#7c83a0]">{{ t.date }}</td>
              <td class="px-4 py-3">
                <button class="inline-flex items-center gap-1.5 px-3 py-1 bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-md text-[11px] font-medium hover:bg-sky-500/20 transition-colors">Reçu</button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div v-if="ventesMeta.last_page > 1" class="px-5 py-3 border-t border-white/[0.05] flex items-center justify-between">
          <span class="text-xs text-[#7c83a0]">Page {{ ventesMeta.current_page }} / {{ ventesMeta.last_page }}</span>
          <div class="flex items-center gap-1">
            <button @click="ventePage = ventePage - 1; fetchVentes()" :disabled="ventePage <= 1"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">‹</button>
            <template v-for="p in paginationPages(ventesMeta)" :key="p">
              <button v-if="p !== '...'" @click="ventePage = p; fetchVentes()"
                :class="['px-2.5 py-1 rounded text-xs transition',
                  p === ventesMeta.current_page ? 'bg-[var(--accent)]/20 text-[var(--accent)]' : 'text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06]']">{{ p }}</button>
              <span v-else class="px-1 text-[#7c83a0] text-xs">…</span>
            </template>
            <button @click="ventePage = ventePage + 1; fetchVentes()" :disabled="ventePage >= ventesMeta.last_page"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">›</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ DÉPENSES ════════════════════════════════════════════════ -->
    <div v-if="activeSub === 'depense'">
      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
        <div v-for="c in depenseCards" :key="c.label" class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
          <p class="text-xs text-[#7c83a0] mb-2">{{ c.label }}</p>
          <p :class="['text-[22px] font-semibold font-mono tracking-tight leading-none', c.color]">
            {{ c.value }} <span class="text-base font-sans font-normal text-[#7c83a0]">HTG</span>
          </p>
        </div>
      </div>

      <!-- Table dépenses -->
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between gap-3">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">
            Dépenses · <span class="text-[#7c83a0] font-mono text-xs">{{ depenseMeta.total ?? 0 }}</span>
          </span>
          <input v-model="depenseSearch" @input="debounceDepense" type="text" placeholder="Rechercher…"
            class="text-[12px] bg-[#0d1117] border border-white/[0.08] rounded-lg px-3 py-1.5 text-[#c9d1d9] focus:outline-none focus:border-[var(--accent)]/40 w-48"/>
        </div>

        <div v-if="depenseLoading" class="animate-pulse px-5 py-4 space-y-3">
          <div v-for="i in 6" :key="i" class="h-8 bg-white/[0.04] rounded"></div>
        </div>

        <table v-else class="w-full">
          <thead>
            <tr class="bg-[#13161f]">
              <th v-for="h in ['Description','Montant dépensé','Date','Enregistré par']" :key="h"
                  class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="depenses.length === 0"><td colspan="4" class="px-4 py-8 text-center text-[#7c83a0] text-sm">Aucune dépense trouvée</td></tr>
            <tr v-for="d in depenses" :key="d.id" class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
              <td class="px-4 py-3 text-[13.5px] text-[#e8eaf0]">{{ d.description }}</td>
              <td class="px-4 py-3 font-mono text-[13.5px] text-red-400 font-semibold">
                − {{ Number(d.prix).toLocaleString('fr-FR') }} HTG
              </td>
              <td class="px-4 py-3 font-mono text-xs text-[#7c83a0]">{{ d.date }}</td>
              <td class="px-4 py-3 text-[12px] text-[#7c83a0]">{{ d.user_name ?? '—' }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="depenseMeta.last_page > 1" class="px-5 py-3 border-t border-white/[0.05] flex items-center justify-between">
          <span class="text-xs text-[#7c83a0]">Page {{ depenseMeta.current_page }} / {{ depenseMeta.last_page }}</span>
          <div class="flex items-center gap-1">
            <button @click="depensePage--; fetchDepenses()" :disabled="depensePage <= 1"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">‹</button>
            <template v-for="p in paginationPages(depenseMeta)" :key="p">
              <button v-if="p !== '...'" @click="depensePage = p; fetchDepenses()"
                :class="['px-2.5 py-1 rounded text-xs transition',
                  p === depenseMeta.current_page ? 'bg-[var(--accent)]/20 text-[var(--accent)]' : 'text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06]']">{{ p }}</button>
              <span v-else class="px-1 text-[#7c83a0] text-xs">…</span>
            </template>
            <button @click="depensePage++; fetchDepenses()" :disabled="depensePage >= depenseMeta.last_page"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">›</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ PRÊTS ════════════════════════════════════════════════════ -->
    <div v-if="activeSub === 'pret'">
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">Prêts en cours</span>
        </div>
        <table class="w-full">
          <thead>
            <tr class="bg-[#13161f]">
              <th v-for="h in ['Bénéficiaire','Montant','Remboursé','Échéance','Statut']" :key="h"
                  class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!prets.length"><td colspan="5" class="px-4 py-8 text-center text-[#7c83a0] text-sm">Aucun prêt</td></tr>
            <tr v-for="p in prets" :key="p.id" class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
              <td class="px-4 py-3 text-[13.5px] font-medium text-[#e8eaf0]">{{ p.user }}</td>
              <td class="px-4 py-3 font-mono text-[13.5px] text-[#e8eaf0]">{{ p.amount }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2.5">
                  <div class="w-20 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                    <div class="h-full rounded-full" :style="{ width: pourcentagePaye(p.amount, p.remaining_balance) + '%', background: 'var(--accent)' }"></div>
                  </div>
                  <span class="font-mono text-xs text-[#7c83a0]">{{ p.pct }}%</span>
                </div>
              </td>
              <td class="px-4 py-3 font-mono text-xs text-[#7c83a0]">{{ p.term_months }} Mois</td>
              <td class="px-4 py-3">
                <span :class="['inline-flex items-center px-2 py-0.5 rounded-full text-[11.5px] font-medium',
                  p.statut === 'Pending' ? 'bg-[var(--accent)]/15 text-[var(--accent)]' : 'bg-emerald-500/15 text-emerald-400']">
                  {{ p.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ══ AUTRES TRANSACTIONS ══════════════════════════════════════ -->
    <div v-if="activeSub === 'autre'">
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between gap-3">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">
            Autres transactions · <span class="text-[#7c83a0] font-mono text-xs">{{ autreMeta.total ?? 0 }}</span>
          </span>
          <input v-model="autreSearch" @input="debounceAutre" type="text" placeholder="Rechercher…"
            class="text-[12px] bg-[#0d1117] border border-white/[0.08] rounded-lg px-3 py-1.5 text-[#c9d1d9] focus:outline-none focus:border-[var(--accent)]/40 w-48"/>
        </div>

        <div v-if="autreLoading" class="animate-pulse px-5 py-4 space-y-3">
          <div v-for="i in 6" :key="i" class="h-10 bg-white/[0.04] rounded"></div>
        </div>

        <table v-else class="w-full">
          <thead>
            <tr class="bg-[#13161f]">
              <th v-for="h in ['Description','Élève','Montant','Date','Enregistré par']" :key="h"
                  class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="autresTx.length === 0"><td colspan="5" class="px-4 py-8 text-center text-[#7c83a0] text-sm">Aucune transaction</td></tr>
            <tr v-for="a in autresTx" :key="a.id" class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
              <td class="px-4 py-3 text-[13.5px] text-[#e8eaf0]">
                {{ a.description }}
                <span v-if="a.description_supplementaire" class="ml-1 text-xs text-[#7c83a0]">({{ a.description_supplementaire }})</span>
              </td>
              <td class="px-4 py-3 text-[12px] text-[#7c83a0]">
                {{ a.etudiant ? `${a.etudiant.nom ?? ''} ${a.etudiant.prenom ?? ''}`.trim() : '—' }}
              </td>
              <td class="px-4 py-3 font-mono text-[13.5px] text-amber-400 font-semibold">
                {{ Number(a.montant).toLocaleString('fr-FR') }} HTG
              </td>
              <td class="px-4 py-3 font-mono text-xs text-[#7c83a0]">{{ a.date }}</td>
              <td class="px-4 py-3 text-[12px] text-[#7c83a0]">{{ a.utilisateur ?? '—' }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="autreMeta.last_page > 1" class="px-5 py-3 border-t border-white/[0.05] flex items-center justify-between">
          <span class="text-xs text-[#7c83a0]">Page {{ autreMeta.current_page }} / {{ autreMeta.last_page }}</span>
          <div class="flex items-center gap-1">
            <button @click="autrePage--; fetchAutres()" :disabled="autrePage <= 1"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">‹</button>
            <template v-for="p in paginationPages(autreMeta)" :key="p">
              <button v-if="p !== '...'" @click="autrePage = p; fetchAutres()"
                :class="['px-2.5 py-1 rounded text-xs transition',
                  p === autreMeta.current_page ? 'bg-[var(--accent)]/20 text-[var(--accent)]' : 'text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06]']">{{ p }}</button>
              <span v-else class="px-1 text-[#7c83a0] text-xs">…</span>
            </template>
            <button @click="autrePage++; fetchAutres()" :disabled="autrePage >= autreMeta.last_page"
              class="px-2.5 py-1 rounded text-xs text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.06] disabled:opacity-30 transition">›</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import axios from 'axios'
import { onMounted, ref, watch } from 'vue'

const url = import.meta.env.VITE_APP_BASE_URL

const activeSub = ref('vente')
const tabs = [
  { key: 'vente',   label: 'Ventes' },
  { key: 'depense', label: 'Dépenses' },
  { key: 'pret',    label: 'Prêts' },
  { key: 'autre',   label: 'Autres transactions' },
]

// ── Ventes ────────────────────────────────────────────────────────────────
const ventesCards  = ref([])
const ventes       = ref([])
const ventesMeta   = ref({ current_page:1, last_page:1, total:0 })
const ventePage    = ref(1)
const venteSearch  = ref('')
const venteLoading = ref(false)
let venteTimer = null

const fetchVentes = async () => {
  venteLoading.value = true
  try {
    const { data } = await axios.get(`${url}/vente`, {
      params: { page: ventePage.value, per_page: 20, search: venteSearch.value || undefined }
    })
    ventes.value   = data.data
    ventesMeta.value = data.meta
  } catch (e) { console.error('[Ventes]', e) }
  finally { venteLoading.value = false }
}

const debounceVente = () => {
  clearTimeout(venteTimer)
  venteTimer = setTimeout(() => { ventePage.value = 1; fetchVentes() }, 350)
}

// ── Stats ventes ──────────────────────────────────────────────────────────
const fetchVenteStats = async () => {
  try {
    const { data } = await axios.get(`${url}/stats-ventes`)
    ventesCards.value = data.ventesCards ?? []
  } catch (e) { console.error('[VenteStats]', e) }
}

// ── Dépenses ──────────────────────────────────────────────────────────────
const depenseCards  = ref([])
const depenses      = ref([])
const depenseMeta   = ref({ current_page:1, last_page:1, total:0 })
const depensePage   = ref(1)
const depenseSearch = ref('')
const depenseLoading= ref(false)
let depenseTimer = null

const fetchDepenses = async () => {
  depenseLoading.value = true
  try {
    const { data } = await axios.get(`${url}/depense`, {
      params: { page: depensePage.value, per_page: 20, search: depenseSearch.value || undefined }
    })
    depenses.value    = data.data
    depenseMeta.value = data.meta
  } catch (e) { console.error('[Depenses]', e) }
  finally { depenseLoading.value = false }
}

const debounceDepense = () => {
  clearTimeout(depenseTimer)
  depenseTimer = setTimeout(() => { depensePage.value = 1; fetchDepenses() }, 350)
}

const fetchDepenseStats = async () => {
  try {
    const { data } = await axios.get(`${url}/stats-depenses`)
    depenseCards.value = data.depenseCards ?? []
  } catch (e) { console.error('[DepenseStats]', e) }
}

// ── Prêts ─────────────────────────────────────────────────────────────────
const prets = ref([])
const fetchPrets = async () => {
  try {
    const { data } = await axios.get(`${url}/get-loans`)
    prets.value = data?.data ?? []
  } catch (e) { console.error('[Prets]', e) }
}

// ── Autres transactions ───────────────────────────────────────────────────
const autresTx    = ref([])
const autreMeta   = ref({ current_page:1, last_page:1, total:0 })
const autrePage   = ref(1)
const autreSearch = ref('')
const autreLoading= ref(false)
let autreTimer = null

const fetchAutres = async () => {
  autreLoading.value = true
  try {
    const { data } = await axios.get(`${url}/other-transactions`, {
      params: { page: autrePage.value, per_page: 20 }
    })
    autresTx.value  = data.data ?? []
    autreMeta.value = {
      current_page: data.current_page ?? 1,
      last_page:    data.last_page    ?? 1,
      total:        data.total        ?? 0,
    }
  } catch (e) { console.error('[Autres]', e) }
  finally { autreLoading.value = false }
}

const debounceAutre = () => {
  clearTimeout(autreTimer)
  autreTimer = setTimeout(() => { autrePage.value = 1; fetchAutres() }, 350)
}

// ── Pagination helper ─────────────────────────────────────────────────────
const paginationPages = (meta) => {
  const cur = meta.current_page, last = meta.last_page
  if (last <= 7) return Array.from({ length: last }, (_, i) => i + 1)
  const pages = [1]
  if (cur > 3) pages.push('...')
  for (let p = Math.max(2, cur - 1); p <= Math.min(last - 1, cur + 1); p++) pages.push(p)
  if (cur < last - 2) pages.push('...')
  pages.push(last)
  return pages
}

// ── Navigation ────────────────────────────────────────────────────────────
watch(activeSub, (val) => {
  if (val === 'vente')   { fetchVenteStats(); fetchVentes() }
  if (val === 'depense') { fetchDepenseStats(); fetchDepenses() }
  if (val === 'pret')    { fetchPrets() }
  if (val === 'autre')   { fetchAutres() }
})

const pourcentagePaye = (amount, remaining) => {
  const total = amount + remaining
  return total > 0 ? Math.round((amount / total) * 100) : 0
}

onMounted(() => {
  fetchVenteStats()
  fetchVentes()
})
</script>

<style scoped>
@keyframes fadeUp {
  from { opacity:0; transform:translateY(8px) }
  to   { opacity:1; transform:translateY(0)   }
}
</style>

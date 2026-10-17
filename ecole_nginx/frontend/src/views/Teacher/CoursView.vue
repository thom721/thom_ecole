<!-- src/views/CoursView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Cours & Ressources</h1>
        <p class="text-[#7c83a0] text-sm">
          <template v-if="loadingCours">Chargement…</template>
          <template v-else>{{ programmes.length }} matière{{ programmes.length > 1 ? 's' : '' }} programmée{{ programmes.length > 1 ? 's' : '' }}<template v-if="annee"> · année {{ annee }}</template></template>
        </p>
      </div>
      <input
        v-model="search"
        type="search"
        placeholder="Rechercher une matière…"
        class="w-full sm:w-64 bg-[#1e2335] border border-white/10 rounded-xl px-4 py-2 text-[#e8eaf0] text-sm outline-none focus:border-white/20 transition-colors"
      />
    </div>

    <p v-if="errorCours" class="text-sm text-[#f87171] bg-[#f87171]/10 rounded-xl px-4 py-3">{{ errorCours }}</p>

    <div v-else-if="!loadingCours && !groups.length" class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-8 text-center text-[#7c83a0] text-sm">
      {{ search ? 'Aucune matière ne correspond à la recherche.' : 'Aucune matière ne vous est attribuée pour l\'année en cours.' }}
    </div>

    <section v-for="g in groups" :key="g.classe_id" class="flex flex-col gap-3">
      <div class="flex items-center gap-3">
        <span class="w-2 h-2 rounded-full" :style="{ background: g.color }" />
        <h2 class="text-lg font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">{{ g.nom }}</h2>
        <span class="text-[12px] text-[#7c83a0]">{{ g.items.length }} matière{{ g.items.length > 1 ? 's' : '' }}<template v-if="g.studentCount != null"> · {{ g.studentCount }} élèves</template></span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div v-for="p in g.items" :key="p.id"
          class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-5 flex flex-col gap-3 hover:border-white/[0.15] transition-colors"
        >
          <div class="flex items-start gap-3">
            <div class="w-11 h-11 rounded-xl flex items-center justify-center text-[13px] font-bold flex-shrink-0" :style="{ background: g.color+'22', color: g.color }">{{ initials(p.cours_nom) }}</div>
            <div class="min-w-0">
              <p class="text-[14px] font-semibold text-[#e8eaf0] mb-0.5 truncate" :title="p.cours_nom">{{ p.cours_nom }}</p>
              <p class="text-[12px] text-[#7c83a0]">{{ horaire(p) }}</p>
            </div>
          </div>
          <div class="flex gap-5">
            <div>
              <p class="text-[15px] font-bold text-[#e8eaf0] leading-tight">{{ p.coefficients ?? '—' }}</p>
              <p class="text-[10px] uppercase tracking-wide text-[#7c83a0]">coefficient</p>
            </div>
            <div>
              <p class="text-[15px] font-bold text-[#e8eaf0] leading-tight">{{ p.note_de_passage && Number(p.note_de_passage) > 0 ? p.note_de_passage : '—' }}</p>
              <p class="text-[10px] uppercase tracking-wide text-[#7c83a0]">note de passage</p>
            </div>
            <div v-if="p.session">
              <p class="text-[15px] font-bold text-[#e8eaf0] leading-tight">{{ p.session }}</p>
              <p class="text-[10px] uppercase tracking-wide text-[#7c83a0]">session</p>
            </div>
          </div>
          <div class="flex items-center justify-end pt-2 border-t border-white/[0.06] mt-auto">
            <button @click="router.push({ name: 'teacher.add-notes' })" class="px-3 py-1.5 text-white rounded-lg text-[12px] font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">Saisir des notes</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useTeacherData, colorAt, initials } from '@/composables/useTeacherData'

const router = useRouter()
const { stats, refresh } = useTeacherData()

const programmes = ref([])
const annee = ref('')
const loadingCours = ref(true)
const errorCours = ref('')
const search = ref('')

onMounted(async () => {
  try {
    const { data } = await axios.get('/mes-programmes')
    programmes.value = data?.programmes ?? []
    annee.value = data?.annee?.nom ?? ''
  } catch (e) {
    errorCours.value = e?.response?.data?.detail || 'Impossible de charger vos matières.'
  } finally {
    loadingCours.value = false
  }
  refresh()
})

function horaire(p) {
  const parts = [p.jours, p.heure].filter(Boolean)
  return parts.length ? parts.join(' · ') : 'Horaire non défini'
}

// Regroupement par classe ; noms et effectifs issus de /mes-statistiques-prof
const groups = computed(() => {
  const infos = Object.fromEntries((stats.value?.classes ?? []).map((c, i) => [c.classe_id, { ...c, color: colorAt(i) }]))
  const q = search.value.trim().toLowerCase()
  const byClass = {}
  for (const p of programmes.value) {
    if (q && !(p.cours_nom || '').toLowerCase().includes(q)) continue
    const key = p.class || 'sans-classe'
    byClass[key] ??= { classe_id: key, nom: infos[key]?.nom ?? 'Classe non définie', studentCount: infos[key]?.studentCount ?? null, color: infos[key]?.color ?? colorAt(0), items: [] }
    byClass[key].items.push(p)
  }
  return Object.values(byClass)
    .map(g => ({ ...g, items: g.items.sort((a, b) => (a.cours_nom || '').localeCompare(b.cours_nom || '')) }))
    .sort((a, b) => a.nom.localeCompare(b.nom))
})
</script>

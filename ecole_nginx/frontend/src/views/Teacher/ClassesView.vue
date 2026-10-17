<!-- src/views/ClassesView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">

    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Mes Classes</h1>
        <p class="text-[#7c83a0] text-sm">
          <template v-if="stats">{{ classes.length }} classe{{ classes.length > 1 ? 's' : '' }} · année {{ stats.annee.nom }}</template>
          <template v-else-if="loading">Chargement…</template>
        </p>
      </div>
    </div>

    <p v-if="error" class="text-sm text-[#f87171] bg-[#f87171]/10 rounded-xl px-4 py-3">{{ error }}</p>

    <div v-else-if="stats && !classes.length" class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-8 text-center text-[#7c83a0] text-sm">
      Aucune classe ne vous est attribuée pour l'année {{ stats.annee.nom }}.
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="cls in classes" :key="cls.classe_id"
        class="bg-[#171b26] border border-white/[0.07] rounded-2xl p-5 flex flex-col gap-3 hover:border-white/[0.15] transition-colors"
      >
        <div class="flex items-center justify-between">
          <div class="h-9 min-w-9 px-2 rounded-xl flex items-center justify-center text-[11px] font-bold" :style="{ background: cls.color+'22', color: cls.color }">{{ cls.level }}</div>
          <span class="text-[11px] px-2.5 py-1 rounded-full font-medium"
            :class="{
              'bg-[#6ee7b7]/10 text-[#6ee7b7]': cls.status==='green',
              'bg-[#f59e0b]/10 text-[#f59e0b]': cls.status==='amber',
              'bg-[#f87171]/10 text-[#f87171]': cls.status==='red',
              'bg-white/[0.06] text-[#7c83a0]': cls.status==='none',
            }"
          >{{ cls.statusLabel }}</span>
        </div>
        <div>
          <p class="text-[18px] font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">{{ cls.nom }}</p>
          <p class="text-[12px] text-[#7c83a0] line-clamp-2" :title="cls.matieres.join(' · ')">
            <span v-if="cls.niveau">{{ cls.niveau }} — </span>{{ cls.matieres.join(' · ') }}
          </p>
        </div>
        <div class="flex gap-5">
          <div>
            <p class="text-[18px] font-bold text-[#e8eaf0] leading-tight">{{ cls.studentCount }}</p>
            <p class="text-[10px] uppercase tracking-wide text-[#7c83a0]">élèves</p>
          </div>
          <div>
            <p class="text-[18px] font-bold leading-tight" :style="{ color: cls.color }">{{ formatMoyenne(cls.moyenne) }}</p>
            <p class="text-[10px] uppercase tracking-wide text-[#7c83a0]">moy. /10</p>
          </div>
          <div>
            <p class="text-[18px] font-bold text-[#e8eaf0] leading-tight">{{ formatPct(cls.reussite) }}</p>
            <p class="text-[10px] uppercase tracking-wide text-[#7c83a0]">réussite</p>
          </div>
          <div>
            <p class="text-[18px] font-bold text-[#e8eaf0] leading-tight">{{ formatPct(cls.presence) }}</p>
            <p class="text-[10px] uppercase tracking-wide text-[#7c83a0]">présence</p>
          </div>
        </div>
        <div class="w-full h-1.5 bg-[#1e2335] rounded-full overflow-hidden" :title="`${cls.reussite ?? 0}% des élèves notés ont la moyenne`">
          <div class="h-full rounded-full transition-all" :style="{ width: (cls.reussite ?? 0)+'%', background: cls.color }" />
        </div>

        <!-- Liste des élèves (dépliable) -->
        <div v-if="openStudents === cls.classe_id" class="max-h-56 overflow-y-auto flex flex-col gap-1 bg-[#1e2335] rounded-xl p-2">
          <p v-if="!studentsOf(cls).length" class="text-[12px] text-[#7c83a0] p-2">Aucun élève inscrit.</p>
          <div v-for="e in studentsOf(cls)" :key="e.id" class="flex items-center justify-between px-2 py-1.5 rounded-lg hover:bg-white/[0.04]">
            <span class="text-[12.5px] text-[#e8eaf0]">{{ e.prenom }} {{ e.nom }}</span>
            <span class="text-[11px] text-[#7c83a0]">{{ e.identifiant }}</span>
          </div>
        </div>

        <div class="flex gap-2 pt-1 border-t border-white/[0.06]">
          <button @click="router.push({ name: 'teacher.notes' })" class="flex-1 py-1.5 bg-[#1e2335] text-[#e8eaf0] rounded-lg text-[12px] font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">Notes</button>
          <button @click="toggleStudents(cls)" class="flex-1 py-1.5 bg-[#1e2335] text-[#e8eaf0] rounded-lg text-[12px] font-medium hover:bg-[#262d44] transition-colors cursor-pointer border-0">
            {{ openStudents === cls.classe_id ? 'Masquer' : 'Élèves' }}
          </button>
          <button @click="router.push({ name: 'teacher.cours' })" class="flex-1 py-1.5 text-white rounded-lg text-[12px] font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">Cours</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useTeacherData, colorAt, classStatus, levelTag, formatMoyenne, formatPct } from '@/composables/useTeacherData'

const router = useRouter()
const { stats, loading, error } = useTeacherData()

const classes = computed(() => (stats.value?.classes ?? []).map((c, i) => {
  const s = classStatus(c.moyenne)
  return { ...c, level: levelTag(c.nom), color: colorAt(i), status: s.status, statusLabel: s.label }
}))

// Élèves par nom de classe, chargés au premier dépliage
const openStudents = ref(null)
const studentsByClass = ref(null)
async function toggleStudents(cls) {
  if (openStudents.value === cls.classe_id) {
    openStudents.value = null
    return
  }
  if (!studentsByClass.value) {
    try {
      const { data } = await axios.get('/mes-classes-etudiants')
      studentsByClass.value = data?.classes ?? {}
    } catch {
      studentsByClass.value = {}
    }
  }
  openStudents.value = cls.classe_id
}
const studentsOf = (cls) =>
  [...(studentsByClass.value?.[cls.nom]?.etudiants ?? [])].sort((a, b) => (a.nom || '').localeCompare(b.nom || ''))
</script>

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

    <!-- ── Appel du jour ── -->
    <div v-if="activeSub === 'appel'">
      <div class="flex items-center justify-between mb-4 gap-4 flex-wrap">
        <div class="flex items-center gap-2">
          <select class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition">
            <option>6ème A</option><option>6ème B</option><option>5ème A</option><option>4ème A</option>
          </select>
          <select class="text-[13px] border border-white/[0.1] rounded-lg px-3 py-2 bg-[#13161f] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition">
            <option>Matin (8h00)</option><option>Après-midi (13h00)</option>
          </select>
        </div>
        <div class="flex gap-2">
          <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500/15 text-emerald-400">
            Présents : {{ presentsCount }}
          </span>
          <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-red-500/15 text-red-400">
            Absents : {{ absentsCount }}
          </span>
        </div>
      </div>

      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07] flex items-center justify-between">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">Liste des élèves — 6ème A</span>
          <div class="flex gap-2">
            <button
              @click="marquerTous('present')"
              class="text-xs font-medium text-white px-3 py-1.5 rounded-lg transition-opacity hover:opacity-80 bg-emerald-600"
            >Tous présents</button>
            <button class="text-xs font-medium bg-white/[0.07] text-[#a0a8c0] px-3 py-1.5 rounded-lg hover:bg-white/[0.12] transition-colors">
              Enregistrer
            </button>
          </div>
        </div>

        <div class="divide-y divide-white/[0.05]">
          <div
            v-for="eleve in eleves" :key="eleve.id"
            class="flex items-center gap-4 px-5 py-3 hover:bg-white/[0.02] transition-colors"
          >
            <div class="w-7 h-7 rounded-full bg-white/[0.08] flex items-center justify-center shrink-0">
              <span class="text-[11px] font-bold text-[#a0a8c0]">{{ eleve.initiales }}</span>
            </div>
            <span class="flex-1 text-[13.5px] text-[#e8eaf0] font-medium">{{ eleve.nom }}</span>
            <div class="flex gap-1.5">
              <button
                @click="eleve.statut = 'present'"
                :class="['text-xs px-3 py-1 rounded-lg border font-medium transition-all',
                  eleve.statut === 'present'
                    ? 'bg-emerald-500 text-white border-emerald-500'
                    : 'border-white/[0.1] text-[#7c83a0] hover:border-emerald-500/50 hover:text-emerald-400']"
              >Présent</button>
              <button
                @click="eleve.statut = 'absent'"
                :class="['text-xs px-3 py-1 rounded-lg border font-medium transition-all',
                  eleve.statut === 'absent'
                    ? 'bg-red-500 text-white border-red-500'
                    : 'border-white/[0.1] text-[#7c83a0] hover:border-red-500/50 hover:text-red-400']"
              >Absent</button>
              <button
                @click="eleve.statut = 'retard'"
                :class="['text-xs px-3 py-1 rounded-lg border font-medium transition-all',
                  eleve.statut === 'retard'
                    ? 'bg-amber-500 text-white border-amber-500'
                    : 'border-white/[0.1] text-[#7c83a0] hover:border-amber-500/50 hover:text-amber-400']"
              >Retard</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Historique ── -->
    <div v-if="activeSub === 'historique'">
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
        <div class="px-5 py-3 border-b border-white/[0.07]">
          <span class="text-[13.5px] font-medium text-[#e8eaf0]">Historique des absences — Février 2025</span>
        </div>
        <table class="w-full">
          <thead>
            <tr class="bg-[#13161f]">
              <th v-for="h in ['Élève','Classe','Absences','Retards','Taux de présence']" :key="h"
                  class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">
                {{ h }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="h in historique" :key="h.id"
                class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
              <td class="px-4 py-3 text-[13.5px] font-medium text-[#e8eaf0]">{{ h.nom }}</td>
              <td class="px-4 py-3 text-[13px] text-[#7c83a0]">{{ h.classe }}</td>
              <td class="px-4 py-3 font-mono text-[#e8eaf0]">{{ h.absences }}</td>
              <td class="px-4 py-3 font-mono text-amber-400">{{ h.retards }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2.5">
                  <div class="w-16 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-500"
                      :class="h.taux > 80 ? 'bg-emerald-500' : h.taux > 60 ? 'bg-amber-500' : 'bg-red-500'"
                      :style="{ width: h.taux + '%' }"
                    ></div>
                  </div>
                  <span :class="['text-xs font-mono font-semibold',
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

    <!-- ── Statistiques ── -->
    <div v-if="activeSub === 'stats'">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-5">
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
              <div
                class="h-full rounded-full transition-all duration-700"
                :class="s.val > 85 ? 'bg-emerald-500' : s.val > 70 ? 'bg-amber-500' : 'bg-red-500'"
                :style="{ width: s.val + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const activeSub = ref('appel')

const tabs = [
  { key: 'appel',      label: 'Appel du jour' },
  { key: 'historique', label: 'Historique'    },
  { key: 'stats',      label: 'Statistiques'  },
]

/* ── Appel ── */
const eleves = reactive([
  { id:1, nom:'Axelle Benoît',       initiales:'AB', statut:'present' },
  { id:2, nom:'Carlos Dorival',      initiales:'CD', statut:'absent'  },
  { id:3, nom:'Diane Étienne',       initiales:'DE', statut:'present' },
  { id:4, nom:'Fabrice Guerrier',    initiales:'FG', statut:'retard'  },
  { id:5, nom:'Ingrid Joseph',       initiales:'IJ', statut:'present' },
  { id:6, nom:'Karl Lafleur',        initiales:'KL', statut:'present' },
  { id:7, nom:'Marie-Noëlle Pierre', initiales:'MN', statut:'absent'  },
  { id:8, nom:'Oscar Théodore',      initiales:'OT', statut:'present' },
])
const presentsCount = computed(() => eleves.filter(e => e.statut === 'present').length)
const absentsCount  = computed(() => eleves.filter(e => e.statut === 'absent').length)
const marquerTous   = (s) => eleves.forEach(e => e.statut = s)

/* ── Historique ── */
const historique = [
  { id:1, nom:'Carlos Dorival',      classe:'6ème A', absences:8,  retards:2, taux:65 },
  { id:2, nom:'Marie-Noëlle Pierre', classe:'6ème A', absences:3,  retards:1, taux:88 },
  { id:3, nom:'Jean-Paul Moise',     classe:'5ème B', absences:1,  retards:0, taux:96 },
  { id:4, nom:'Sandra Voltaire',     classe:'4ème A', absences:12, retards:5, taux:52 },
  { id:5, nom:'Bruno Innocent',      classe:'6ème B', absences:2,  retards:3, taux:91 },
]

/* ── Stats ── */
const statCards = [
  { value:'87%', label:'Taux de présence global', color:'text-emerald-400' },
  { value:'248', label:'Élèves inscrits',          color:'text-[#e8eaf0]'  },
  { value:'32',  label:"Absents aujourd'hui",      color:'text-red-400'    },
  { value:'8',   label:"Retards aujourd'hui",      color:'text-amber-400'  },
]
const statsClasses = [
  { classe:'6ème A', val:87 }, { classe:'6ème B', val:92 },
  { classe:'5ème A', val:78 }, { classe:'5ème B', val:95 },
  { classe:'4ème A', val:69 }, { classe:'4ème B', val:84 },
]
</script>

<style scoped>
@keyframes fadeUp {
  from { opacity:0; transform:translateY(8px) }
  to   { opacity:1; transform:translateY(0)   }
}
</style>

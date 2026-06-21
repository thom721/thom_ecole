<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({
  etudiants: { type: Array, default: () => [] },
  cours:     { type: Object, default: () => ({}) },
  date:      { type: String, default: () => new Date().toISOString().split('T')[0] },
});

const emit = defineEmits(['submitted']);

const url = import.meta.env.VITE_APP_BASE_URL ?? '';

// ── État de présence : 'present' | 'absent' | 'retard'
const attendance = ref({});
const isSubmitting = ref(false);
const submitted    = ref(false);
const remarque     = ref('');

// Init : tous présents par défaut
onMounted(() => {
  props.etudiants.forEach(e => {
    attendance.value[e.id] = 'present';
  });
});

const setStatus = (id, status) => {
  attendance.value[id] = status;
};

const stats = computed(() => {
  const vals = Object.values(attendance.value);
  return {
    present: vals.filter(v => v === 'present').length,
    absent:  vals.filter(v => v === 'absent').length,
    retard:  vals.filter(v => v === 'retard').length,
    total:   props.etudiants.length,
  };
});

const allPresent  = () => props.etudiants.forEach(e => attendance.value[e.id] = 'present');
const allAbsent   = () => props.etudiants.forEach(e => attendance.value[e.id] = 'absent');

const submitAppel = async () => {
  isSubmitting.value = true;
  try {
    const payload = {
      date:     props.date,
      cours_id: props.cours?.id,
      remarque: remarque.value,
      presences: props.etudiants.map(e => ({
        etudiant_id: e.id,
        statut:      attendance.value[e.id] ?? 'present',
      })),
    };
    await axios.post(`${url}/appel`, payload);
    submitted.value = true;
    emit('submitted', payload);
  } catch (e) {
    console.error(e);
  } finally {
    isSubmitting.value = false;
  }
};

const statusConfig = {
  present: { label: 'Présent',  bg: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400', dot: 'bg-emerald-400' },
  absent:  { label: 'Absent',   bg: 'bg-red-500/15 border-red-500/30 text-red-400',             dot: 'bg-red-400'     },
  retard:  { label: 'Retard',   bg: 'bg-amber-500/15 border-amber-500/30 text-amber-400',       dot: 'bg-amber-400'   },
};

const initials = (nom, prenom) =>
  `${(prenom?.[0] ?? '').toUpperCase()}${(nom?.[0] ?? '').toUpperCase()}`;

const avatarColor = (id) => {
  const colors = [
    'bg-[#4f8ef7]/20 text-[#7aaeff]',
    'bg-emerald-500/20 text-emerald-400',
    'bg-violet-500/20 text-violet-400',
    'bg-amber-500/20 text-amber-400',
    'bg-sky-500/20 text-sky-400',
    'bg-rose-500/20 text-rose-400',
  ];
  const hash = id.charCodeAt(0) + id.charCodeAt(id.length - 1);
  return colors[hash % colors.length];
};
</script>

<template>
  <div style="background: #0f1117; min-height: 100vh; font-family: 'DM Sans', 'Segoe UI', sans-serif;">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 pt-6 pb-16">

      <!-- ── Header ── -->
      <div class="flex items-center gap-3 mb-6">
        <div class="w-9 h-9 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center shrink-0">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6" class="w-5 h-5 text-sky-400">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z"/>
          </svg>
        </div>
        <div>
          <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Feuille d'appel</h1>
          <p class="text-[12px] text-[#7c83a0]">{{ cours?.nom ?? 'Cours' }} · {{ date }}</p>
        </div>
      </div>

      <!-- ── Succès ── -->
      <div v-if="submitted" class="flex flex-col items-center justify-center py-16 gap-4">
        <div class="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-7 h-7 text-emerald-400">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
          </svg>
        </div>
        <p class="text-[15px] font-semibold text-[#e8eaf0]">Appel enregistré !</p>
        <p class="text-[12px] text-[#7c83a0]">{{ stats.present }} présents · {{ stats.absent }} absents · {{ stats.retard }} en retard</p>
        <button @click="submitted = false" class="mt-2 text-[12px] text-[#7aaeff] hover:text-[#4f8ef7] transition-colors">
          Modifier l'appel
        </button>
      </div>

      <template v-else>

        <!-- ── Stats ── -->
        <div class="grid grid-cols-3 gap-3 mb-5">
          <div class="bg-[#161b26] rounded-xl border border-white/[0.07] px-4 py-3 text-center">
            <div class="text-[22px] font-bold text-emerald-400">{{ stats.present }}</div>
            <div class="text-[10px] text-[#7c83a0] uppercase tracking-wider mt-0.5">Présents</div>
          </div>
          <div class="bg-[#161b26] rounded-xl border border-white/[0.07] px-4 py-3 text-center">
            <div class="text-[22px] font-bold text-red-400">{{ stats.absent }}</div>
            <div class="text-[10px] text-[#7c83a0] uppercase tracking-wider mt-0.5">Absents</div>
          </div>
          <div class="bg-[#161b26] rounded-xl border border-white/[0.07] px-4 py-3 text-center">
            <div class="text-[22px] font-bold text-amber-400">{{ stats.retard }}</div>
            <div class="text-[10px] text-[#7c83a0] uppercase tracking-wider mt-0.5">Retards</div>
          </div>
        </div>

        <!-- Barre de progression -->
        <div class="h-1.5 bg-white/[0.05] rounded-full overflow-hidden mb-5 flex">
          <div class="bg-emerald-500 transition-all duration-300"
            :style="{ width: (stats.present / stats.total * 100) + '%' }" />
          <div class="bg-amber-500 transition-all duration-300"
            :style="{ width: (stats.retard / stats.total * 100) + '%' }" />
          <div class="bg-red-500 transition-all duration-300"
            :style="{ width: (stats.absent / stats.total * 100) + '%' }" />
        </div>

        <!-- ── Actions rapides ── -->
        <div class="flex items-center justify-between mb-4">
          <span class="text-[11px] text-[#7c83a0]">{{ stats.total }} élèves</span>
          <div class="flex gap-2">
            <button @click="allPresent"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-lg text-[11px] font-medium hover:bg-emerald-500/20 transition-colors">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2" class="w-3 h-3"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
              Tous présents
            </button>
            <button @click="allAbsent"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-500/10 text-red-400 border border-red-500/20 rounded-lg text-[11px] font-medium hover:bg-red-500/20 transition-colors">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2" class="w-3 h-3"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              Tous absents
            </button>
          </div>
        </div>

        <!-- ── Liste des élèves ── -->
        <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden mb-4">

          <!-- En-tête colonnes -->
          <div class="hidden sm:grid grid-cols-[auto_1fr_auto] gap-4 px-5 py-3 bg-[#0d1117]/50 border-b border-white/[0.05]">
            <span class="text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62] w-8">#</span>
            <span class="text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Élève</span>
            <span class="text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62] text-center w-48">Statut</span>
          </div>

          <!-- Lignes -->
          <div
            v-for="(etudiant, index) in etudiants"
            :key="etudiant.id"
            class="flex flex-col sm:grid sm:grid-cols-[auto_1fr_auto] sm:gap-4 items-start sm:items-center px-5 py-3 transition-colors hover:bg-white/[0.01]"
            :class="{ 'border-t border-white/[0.04]': index > 0 }"
          >
            <!-- Numéro -->
            <span class="hidden sm:flex w-8 text-[11px] text-[#3d4d62] font-mono">{{ String(index + 1).padStart(2, '0') }}</span>

            <!-- Identité -->
            <div class="flex items-center gap-3 mb-2 sm:mb-0 w-full sm:w-auto">
              <div class="w-8 h-8 rounded-lg flex items-center justify-center text-[11px] font-bold shrink-0"
                :class="avatarColor(etudiant.id)">
                {{ initials(etudiant.nom, etudiant.prenom) }}
              </div>
              <div class="min-w-0">
                <p class="text-[13px] font-medium text-[#c9d1d9] truncate">
                  {{ etudiant.prenom }} <span class="font-semibold text-[#e8eaf0]">{{ etudiant.nom }}</span>
                </p>
                <p class="text-[10px] text-[#3d4d62] font-mono">{{ etudiant.identifiant }}</p>
              </div>
            </div>

            <!-- Boutons statut -->
            <div class="flex gap-1.5 w-full sm:w-auto">
              <button
                v-for="(cfg, key) in statusConfig"
                :key="key"
                @click="setStatus(etudiant.id, key)"
                class="flex-1 sm:flex-none inline-flex items-center justify-center gap-1 px-2.5 py-1.5 rounded-lg border text-[11px] font-medium transition-all duration-150"
                :class="attendance[etudiant.id] === key
                  ? cfg.bg + ' shadow-sm'
                  : 'bg-transparent border-white/[0.06] text-[#3d4d62] hover:border-white/[0.12] hover:text-[#7c83a0]'"
              >
                <span class="w-1.5 h-1.5 rounded-full shrink-0"
                  :class="attendance[etudiant.id] === key ? cfg.dot : 'bg-[#3d4d62]'" />
                {{ cfg.label }}
              </button>
            </div>
          </div>
        </div>

        <!-- ── Remarque ── -->
        <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] px-5 py-4 mb-4">
          <label class="block text-[10px] font-semibold uppercase tracking-wider text-[#7c83a0] mb-2">
            Remarque (optionnel)
          </label>
          <textarea
            v-model="remarque"
            rows="2"
            placeholder="Ex: Cours suspendu 10 min, devoir remis…"
            class="w-full bg-[#0d1117] border border-white/[0.08] text-[#c9d1d9] rounded-xl px-4 py-2.5 text-[13px] placeholder-[#3d4d62] outline-none focus:border-[#4f8ef7]/35 resize-none transition-colors"
          />
        </div>

        <!-- ── Footer ── -->
        <div class="flex items-center justify-between">
          <span class="text-[12px] text-[#7c83a0]">
            <span class="text-emerald-400 font-semibold">{{ stats.present }}</span>/{{ stats.total }} présents
          </span>
          <button
            @click="submitAppel"
            :disabled="isSubmitting"
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-[#4f8ef7]/15 text-[#7aaeff] border border-[#4f8ef7]/25 rounded-xl text-[13px] font-medium hover:bg-[#4f8ef7]/25 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="isSubmitting" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
            </svg>
            <svg v-else fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
            </svg>
            <span>{{ isSubmitting ? 'Envoi…' : 'Soumettre l\'appel' }}</span>
          </button>
        </div>

      </template>
    </div>
  </div>
</template>

<style scoped>
textarea::placeholder { color: #3d4d62; }
</style>

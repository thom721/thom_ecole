<script setup>
import { ref } from "vue";
import axios from "axios";
import Swal from "sweetalert2";
import InsertNotesComponents from "@/components/InsertNotesComponents.vue";
import InputError from "@/components/InputError.vue";

const url = import.meta.env.VITE_APP_BASE_URL;

const students    = ref([]);
const list_cours  = ref([]);
const evaluation  = ref('');
const data_students = ref({});
const isSubmitting  = ref(false);
const isdata        = ref(false);
const errors        = ref({});
const isLoading     = ref(false);

const handleSearchStart = () => { isLoading.value = true; students.value = []; };
const handleSearchError = () => { isLoading.value = false; };

const saveFormNote = ref({
  examen: '', controle: '', cours: '', coefficients: '',
  note_de_passage: '', annee_academique: '', type_matiere: '',
  professeur_id: '', change_cours: ''
});

const evalOptions = {
  controle: [
    { value: 'Contr. I',   title: 'Contrôle I' },
    { value: 'Contr. II',  title: 'Contrôle II' },
    { value: 'Contr. III', title: 'Contrôle III' },
  ],
  trimestre: [
    { value: 'Trimestre I',   title: 'Trimestre I' },
    { value: 'Trimestre II',  title: 'Trimestre II' },
    { value: 'Trimestre III', title: 'Trimestre III' },
  ],
};

const handleDataFetched = (data) => {
  if (!data) return;
  isLoading.value = false;
  saveFormNote.value.cours            = data.datas.cours?.cours_nom || '';
  saveFormNote.value.coefficients     = data.datas.cours?.coefficients || '';
  saveFormNote.value.annee_academique = data.datas.annee || '';
  saveFormNote.value.note_de_passage  = data.datas.cours?.note_de_passage || '';
  saveFormNote.value.type_matiere     = data.datas.cours.type_matiere;
  saveFormNote.value.controle         = data.datas.examEcheance?.evaluation_par || '';
  list_cours.value = data.datas.list_cours || [];
  data_students.value = {
    session:      data.datas.session,
    examEcheance: data.datas.examEcheance,
    month:        data.datas.month,
    nom_classe:   data.datas.cours?.nom_classe,
  };
  students.value = data.datas.result.map(s => ({ ...s, note: '' }));
  isdata.value = true;
};

const showSwal = (text, icon = 'info') =>
  Swal.fire({ position: 'top-end', text, icon, showConfirmButton: false, timer: 2000 });

const evaluationChange = async (e) => {
  evaluation.value = e.target.value;
  const payload = {
    ...saveFormNote.value,
    examen: evaluation.value,
    notes: students.value.map(s => ({ id: s.id, identifiant: s.identifiant })),
  };
  try {
    const res = await axios.post(`${url}/cours-etudiant-edit-note`, payload);
    if (res.status === 200 && res.data.success)
      res.data.success.forEach(item => {
        const s = students.value.find(s => s.id === item.etudiant_id);
        if (s) s.note = item.note;
      });
  } catch (err) {
    showSwal(err.response?.data?.errors?.cours || 'Erreur de chargement', 'error');
  }
};

const coursChange = (e) => {
  const cours = list_cours.value.find(c => c.id == e.target.value);
  if (cours) {
    Object.assign(saveFormNote.value, {
      cours: cours.cours_nom, coefficients: cours.coefficients,
      note_de_passage: cours.note_de_passage, type_matiere: cours.type_matiere,
      professeur_id: cours.professeur_id,
    });
    students.value.forEach(s => s.note = '');
  }
};

const submitNotes = async () => {
  isSubmitting.value = true;
  errors.value = {};
  const payload = {
    ...saveFormNote.value,
    notes: students.value.map(s => ({ id: s.id, identifiant: s.identifiant, note: s.note })),
  };
  try {
    const res = await axios.post(`${url}/coursEtudiant`, payload);
    if (res.data.success) {
      showSwal(res.data.success, 'success');
      saveFormNote.value.examen = '';
      saveFormNote.value.change_cours = '';
      students.value.forEach(s => s.note = '');
    }
  } catch (err) {
    errors.value = err.response?.data?.errors || {};
    showSwal('Veuillez vérifier les notes saisies', 'error');
  } finally {
    isSubmitting.value = false;
  }
};
const month = ["Septembre", "Octobre", "Novembre", "Décembre", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août"]
</script>

<template>
  <div class="mx-auto px-4 pb-20 animate-[fadeUp_0.4s_ease_both]">

    <!-- ── Recherche initiale ── -->
    <InsertNotesComponents
      v-if="!isdata"
      route="cours-etudiant-add-note"
      @search-started="handleSearchStart"
      @search-error="handleSearchError"
      @result-fetched="handleDataFetched"
    />

    <!-- ── Loader ── -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center pb-16 gap-4">
      <div class="relative w-10 h-10">
        <span class="absolute inset-0 rounded-full border-2 border-transparent border-t-blue-500 animate-spin" />
        <span class="absolute inset-1 rounded-full border-2 border-transparent border-t-blue-400 animate-spin [animation-duration:0.8s]" />
        <span class="absolute inset-2 rounded-full border-2 border-transparent border-t-blue-300 animate-spin [animation-duration:0.6s]" />
      </div>
      <p class="text-sm text-slate-400 tracking-wide">Récupération de la liste des étudiants…</p>
    </div>

    <!-- ── Carte principale ── -->
    <div
      v-if="!isLoading && students.length > 0"
      class="bg-[#161b27] border border-white/[0.07] rounded-2xl overflow-hidden animate-[slideUp_0.3s_ease_both] p-6"
    >

      <!-- En-tête -->
      <div class="bg-[#1a2033] border-b border-white/[0.07] px-6 p-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">

          <!-- Info cours -->
          <div class="flex flex-col gap-2">
            <div class="flex items-baseline gap-2 flex-wrap">
              <span class="text-[10px] uppercase tracking-widest font-semibold text-slate-500">Cours</span>
              <span class="text-sm font-semibold text-blue-400">{{ saveFormNote.cours }}</span>
            </div>
            <div class="flex items-baseline gap-2 flex-wrap">
              <span class="text-[10px] uppercase tracking-widest font-semibold text-slate-500">Classe · Année</span>
              <span class="text-sm text-slate-300">
                {{ data_students.nom_classe }}
                <span class="text-slate-600 mx-1">·</span>
                {{ saveFormNote.annee_academique }}
              </span>
            </div>
            <div class="flex flex-wrap gap-2 mt-1">
              <span class="text-[11px] px-2.5 py-0.5 rounded-full bg-white/[0.05] border border-white/[0.08] text-slate-400 font-semibold">
                Coeff. {{ saveFormNote.coefficients }}
              </span>
              <span class="text-[11px] px-2.5 py-0.5 rounded-full bg-white/[0.05] border border-white/[0.08] text-slate-400 font-semibold">
                Passage {{ saveFormNote.note_de_passage }}
              </span>
              <span class="text-[11px] px-2.5 py-0.5 rounded-full bg-white/[0.05] border border-white/[0.08] text-slate-500">
                {{ saveFormNote.type_matiere }}
              </span>
              <span class="text-[11px] px-2.5 py-0.5 rounded-full bg-white/[0.05] border border-white/[0.08] text-slate-500 tracking-wide">
            {{ students.length }} étudiant{{ students.length > 1 ? 's' : '' }}
          </span>
            </div>
          </div>

          <!-- Changer matière -->
          <div class="flex flex-col gap-1.5">
            <label class="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
              Changer de matière
            </label>
            <div class="relative">
              <select
                v-model="saveFormNote.change_cours"
                @change="coursChange"
                class="w-full appearance-none bg-[#1e2436] border border-white/[0.1] rounded-lg px-3 py-2 pr-8 text-sm text-slate-200 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
              >
                <option value="" disabled>Sélectionnez une matière</option>
                <option v-for="c in list_cours" :key="c.id" :value="c.id">{{ c.cours_nom }}</option>
              </select>
              <i class="ri-arrow-down-s-line absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
            </div>
          </div>

          <!-- Type d'évaluation -->
          <div class="flex flex-col gap-1.5">
            <label class="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
              Type d'évaluation
            </label>

            <!-- Radio session -->
            <div v-if="data_students.session" class="flex gap-5 py-1.5">
              <label
                v-for="opt in [{ value: 'intra', label: 'Intra' }, { value: 'finale', label: 'Final' }]"
                :key="opt.value"
                class="flex items-center gap-2 cursor-pointer group"
              >
                <input type="radio" v-model="saveFormNote.controle" :value="opt.value" class="hidden" />
                <span
                  class="w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors"
                  :class="saveFormNote.controle === opt.value
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-white/20 group-hover:border-white/40'"
                >
                  <span
                    v-if="saveFormNote.controle === opt.value"
                    class="w-1.5 h-1.5 rounded-full bg-blue-400"
                  />
                </span>
                <span
                  class="text-sm transition-colors"
                  :class="saveFormNote.controle === opt.value ? 'text-blue-400 font-semibold' : 'text-slate-400 group-hover:text-slate-300'"
                >{{ opt.label }}</span>
              </label>
            </div>

            <!-- Select évaluation -->
            <div v-else class="relative">
              <select
                v-model="saveFormNote.examen"
                @change="evaluationChange"
                class="w-full appearance-none bg-[#1e2436] border border-white/[0.1] rounded-lg px-3 py-2 pr-8 text-sm text-slate-200 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
              >
                <option value="" disabled>Choisir l'examen</option>
                <template v-if="data_students.examEcheance?.evaluation_par?.toLowerCase() === 'mois'">
                  <!-- data_students.month (val, ) -->
                  <option v-for="key in month" :key="key" :value="key">{{ key }}</option>
                </template>
                <template v-else-if="data_students.examEcheance?.evaluation_par === 'Controle'">
                  <option v-for="opt in evalOptions.controle" :key="opt.value" :value="opt.value">{{ opt.title }}</option>
                </template>
                <template v-else-if="data_students.examEcheance?.evaluation_par === 'Trimestre'">
                  <option v-for="opt in evalOptions.trimestre" :key="opt.value" :value="opt.value">{{ opt.title }}</option>
                </template>
              </select>
              <i class="ri-arrow-down-s-line absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
            </div>
            <p v-if="errors.examen?.[0]" class="text-xs text-red-400 mt-0.5">{{ errors.examen[0] }}</p>
          </div>

        </div>
      </div>

      <!-- Tableau -->
      <form @submit.prevent="submitNotes">
        <div class="overflow-x-auto">
          <table class="w-full border-collapse text-sm">
            <thead>
              <tr class="border-b border-white/[0.07] bg-[#1a2033]">
                <th class="px-4 py-3 text-[10px] uppercase tracking-widest text-slate-500 font-semibold text-center w-12">#</th>
                <th class="px-4 py-3 text-[10px] uppercase tracking-widest text-slate-500 font-semibold text-left">Identifiant</th>
                <th class="px-4 py-3 text-[10px] uppercase tracking-widest text-slate-500 font-semibold text-left">Nom &amp; Prénom</th>
                <th class="px-4 py-3 text-[10px] uppercase tracking-widest text-slate-500 font-semibold text-center w-28">
                  {{ saveFormNote.controle || evaluation || 'Note' }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(student, index) in students"
                :key="student.id"
                class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors duration-100"
                :class="index % 2 === 1 ? 'bg-white/[0.01]' : ''"
                :style="{ animation: 'rowIn 0.2s ease both', animationDelay: `${index * 14}ms` }"
              >
                <td class="px-4 py-2.5 text-center text-xs text-slate-600 tabular-nums">{{ index + 1 }}</td>

                <td class="px-4 py-2.5">
                  <code class="text-[11px] font-mono bg-white/[0.05] border border-white/[0.07] text-slate-400 px-2 py-0.5 rounded-md tracking-wide">
                    {{ student.identifiant }}
                  </code>
                </td>

                <td class="px-4 py-2.5 text-slate-300 font-medium">
                  {{ student.nom }} {{ student.prenom }}
                </td>

                <td class="px-4 py-2.5 text-center">
                  <div class="inline-flex flex-col items-center gap-1">
                    <input
                      type="number"
                      v-model="student.note"
                      step="0.1" min="0"
                      class="w-16 text-center font-bold text-slate-100 bg-[#1e2436] border rounded-lg py-1.5 outline-none transition-all appearance-none [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                      :class="errors[`notes.${index}.note`]
                        ? 'border-red-500/60 ring-2 ring-red-500/20'
                        : 'border-white/[0.1] focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'"
                    />
                    <p v-if="errors[`notes.${index}.note`]" class="text-[10px] text-red-400">
                      {{ errors[`notes.${index}.note`][0] }}
                    </p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between px-6 py-4 bg-[#1a2033] border-t border-white/[0.07]">
          <span class="text-xs text-slate-500 font-medium tracking-wide">
            {{ students.length }} étudiant{{ students.length > 1 ? 's' : '' }}
          </span>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="inline-flex items-center gap-2 px-6 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold tracking-wide shadow-[0_2px_14px_rgba(16,185,129,0.25)] hover:shadow-[0_4px_20px_rgba(16,185,129,0.35)] disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-150 hover:-translate-y-px active:translate-y-0"
          >
            <svg v-if="isSubmitting" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <i v-else class="ri-save-3-line text-base" />
            {{ isSubmitting ? 'Enregistrement…' : 'Enregistrer les notes' }}
          </button>
        </div>
      </form>

    </div>
  </div>
</template>

<style scoped>
@keyframes slideUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes rowIn {
  from { opacity: 0; transform: translateX(-4px); }
  to   { opacity: 1; transform: translateX(0); }
}
</style>

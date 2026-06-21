<script setup> 
import { ref, onMounted } from "vue";
import axios from 'axios';
import InputError from "@/components/InputError.vue";
import Swal from 'sweetalert2';
import { useSchoolStore } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';

const url = import.meta.env.VITE_APP_BASE_URL;

const props = defineProps({ 
  route: String,
});

const emit = defineEmits(['result-fetched', 'search-started', 'search-error']);

const schoolStore = useSchoolStore(); 
const { niveau, professeur, annee, classes, faculte, cours, loading } = storeToRefs(schoolStore);

onMounted(() => schoolStore.fetchAllDependencies());

const getClassesByNiveau = (niveauId) => {
  if (!niveauId || !classes.value) return [];  
  return classes.value.filter(c => c.niveau_id === niveauId);
};

const choseNiveau     = ref([]);
const classe_actuelle = ref([]); 
const errors          = ref({});
const isSubmitting    = ref(false);

const formNote = ref({
  cours: '', niveau: '', annee_academique: '',
  faculte: '', session: '', class: '',
});

const fetchNiveauData = async () => {
  if (!formNote.value.niveau) return;
  try {
    const res = await axios.get(`${url}/niveau-with-class/${formNote.value.niveau}`);
    choseNiveau.value     = res.data.niveau;
    cours.value           = res.data.cours;
    classe_actuelle.value = res.data.classe_actuelle;
    Object.assign(formNote.value, { cours: '', faculte: '', session: '', class: '' });
    errors.value = {};
  } catch (e) {
    console.error("Erreur lors de la récupération du niveau", e);
  }
};

const submitNote = async () => {
  isSubmitting.value = true;
  errors.value = {};
  emit('search-started');
  try {
    const response = await axios.post(`${url}/${props.route}`, formNote.value);
    if (response.status === 200) {
      Swal.fire({ icon:'success', title:'Succès', text:"Données récupérées. Passage à l'étape suivante…", timer:1500, showConfirmButton:false });
      emit('result-fetched', response.data);
    }
  } catch (error) {
    emit('search-error');
    if (error.response?.data?.detail?.errors) {
      Swal.fire('Erreur', error.response.data.detail.errors.warning, 'error');
    } else if (error.response?.data?.detail) {
      Swal.fire('Erreur', error.response.data.detail, 'error');
    } else if (error.response?.status === 422) {
      errors.value = error.response.data.errors;
    } else {
      Swal.fire('Erreur', 'Une erreur inattendue est survenue', 'error');
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <form
    @submit.prevent="submitNote"
    class="bg-[#161b27] border border-white/[0.07] rounded-2xl p-6 animate-[slideUp_0.3s_ease_both]"
  >
    <!-- Titre section -->
    <div class="flex items-center gap-3 mb-6 pb-4 border-b border-white/[0.06]">
      <div class="w-1 h-5 rounded-full bg-blue-500" />
      <h2 class="text-sm font-semibold text-slate-300 tracking-wide uppercase">Recherche d'étudiants</h2>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">

      <!-- Cycle -->
      <div class="flex flex-col gap-1.5">
        <label for="niveau" class="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
          Cycle
        </label>
        <div class="relative">
          <select
            id="niveau"
            v-model="formNote.niveau"
            @change="fetchNiveauData"
            class="w-full appearance-none bg-[#1e2436] border border-white/[0.1] rounded-lg px-3 py-2.5 pr-8 text-sm text-slate-200 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer disabled:opacity-40"
            :class="{ 'border-red-500/60 ring-2 ring-red-500/20': errors.niveau }"
          >
            <option value="" disabled>Choisir un Cycle</option>
            <option v-for="n in niveau" :key="n.id" :value="n.id">{{ n.name }}</option>
          </select>
          <i class="ri-arrow-down-s-line absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-base" />
        </div>
        <p v-if="errors.niveau" class="text-[11px] text-red-400">{{ errors.niveau[0] }}</p>
      </div>

      <!-- Cours / Matière -->
      <div class="flex flex-col gap-1.5">
        <label for="cours" class="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
          Cours / Matière
        </label>
        <div class="relative">
          <select
            id="cours"
            v-model="formNote.cours"
            class="w-full appearance-none bg-[#1e2436] border border-white/[0.1] rounded-lg px-3 py-2.5 pr-8 text-sm text-slate-200 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
            :class="{ 'border-red-500/60 ring-2 ring-red-500/20': errors.cours }"
          >
            <option value="" disabled>Choisir une Matière</option>
            <option v-for="c in cours" :key="c.id" :value="c.id">{{ c.cours_nom }}</option>
          </select>
          <i class="ri-arrow-down-s-line absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-base" />
        </div>
        <p v-if="errors.cours" class="text-[11px] text-red-400">{{ errors.cours[0] }}</p>
      </div>

      <!-- Faculté / Option (conditionnel) -->
      <div
        v-if="choseNiveau.name === 'Universitaire' || choseNiveau.name === 'Technique'"
        class="flex flex-col gap-1.5"
      >
        <label for="faculte" class="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
          Faculté / Option
        </label>
        <div class="relative">
          <select
            id="faculte"
            v-model="formNote.faculte"
            class="w-full appearance-none bg-[#1e2436] border border-white/[0.1] rounded-lg px-3 py-2.5 pr-8 text-sm text-slate-200 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
            :class="{ 'border-red-500/60 ring-2 ring-red-500/20': errors.faculte }"
          >
            <option value="" disabled>Faculté / Option</option>
            <option v-for="f in faculte" :key="f.id" :value="f.id">{{ f.nom }}</option>
          </select>
          <i class="ri-arrow-down-s-line absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-base" />
        </div>
        <p v-if="errors.faculte" class="text-[11px] text-red-400">{{ errors.faculte[0] }}</p>
      </div>

      <!-- Classe -->
      <div class="flex flex-col gap-1.5">
        <label for="class" class="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
          Classe
        </label>
        <div class="relative">
          <select
            id="class"
            v-model="formNote.class"
            class="w-full appearance-none bg-[#1e2436] border border-white/[0.1] rounded-lg px-3 py-2.5 pr-8 text-sm text-slate-200 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
            :class="{ 'border-red-500/60 ring-2 ring-red-500/20': errors.class }"
          >
            <option value="" disabled>Choisir une Classe</option>
            <option
              v-for="cls in getClassesByNiveau(formNote.niveau)"
              :key="cls.id"
              :value="cls.id"
            >{{ cls.nom_classe }}</option>
          </select>
          <i class="ri-arrow-down-s-line absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-base" />
        </div>
        <p v-if="errors.class" class="text-[11px] text-red-400">{{ errors.class[0] }}</p>
      </div>

      <!-- Année Académique -->
      <div class="flex flex-col gap-1.5">
        <label for="annee_academique" class="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
          Année Académique
        </label>
        <div class="relative">
          <select
            id="annee_academique"
            v-model="formNote.annee_academique"
            class="w-full appearance-none bg-[#1e2436] border border-white/[0.1] rounded-lg px-3 py-2.5 pr-8 text-sm text-slate-200 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
            :class="{ 'border-red-500/60 ring-2 ring-red-500/20': errors.annee_academique }"
          >
            <option value="" disabled>Année Académique</option>
            <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
          </select>
          <i class="ri-arrow-down-s-line absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-base" />
        </div>
        <p v-if="errors.annee_academique" class="text-[11px] text-red-400">{{ errors.annee_academique[0] }}</p>
      </div>

      <!-- Session (conditionnel) -->
      <div
        v-if="choseNiveau.name === 'Universitaire' || choseNiveau.name === 'Professionel'"
        class="flex flex-col gap-1.5"
      >
        <label for="session" class="text-[10px] uppercase tracking-widest font-semibold text-slate-500">
          Session
        </label>
        <div class="relative">
          <select
            id="session"
            v-model="formNote.session"
            class="w-full appearance-none bg-[#1e2436] border border-white/[0.1] rounded-lg px-3 py-2.5 pr-8 text-sm text-slate-200 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all cursor-pointer"
            :class="{ 'border-red-500/60 ring-2 ring-red-500/20': errors.session }"
          >
            <option value="" disabled>Choisir une Session</option>
            <option value="1ere">1ère</option>
            <option value="2eme">2ème</option>
          </select>
          <i class="ri-arrow-down-s-line absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none text-base" />
        </div>
        <p v-if="errors.session" class="text-[11px] text-red-400">{{ errors.session[0] }}</p>
      </div>

      <!-- Bouton submit -->
      <div class="flex items-end">
        <button
          type="submit"
          :disabled="isSubmitting"
          class="inline-flex items-center gap-2 w-full justify-center px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold tracking-wide shadow-[0_2px_14px_rgba(59,130,246,0.25)] hover:shadow-[0_4px_20px_rgba(59,130,246,0.35)] disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-150 hover:-translate-y-px active:translate-y-0"
        >
          <svg v-if="isSubmitting" class="w-3.5 h-3.5 animate-spin shrink-0" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <i v-else class="ri-search-2-line text-base" />
          {{ isSubmitting ? 'Chargement…' : 'Suivant' }}
        </button>
      </div>

    </div>
  </form>
</template>

<style scoped>
@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import AdminLayout from '@/layouts/AdminLayout.vue';
import Swal from "sweetalert2";

defineOptions({ layout: AdminLayout });

const url = import.meta.env.VITE_APP_BASE_URL;

import { useSchoolStore } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';

const schoolStore = useSchoolStore();
const { niveau, professeur, annee, classes, faculte, cours, loading } = storeToRefs(schoolStore);

onMounted(() => { schoolStore.fetchAllDependencies(); });

const programmeCours = ref([]);
const errors        = ref({});
const isSubmitting  = ref(false);

const cours_id_in_prog  = ref([]);
const fetch_actual_class = ref([]);
const choseNiveau       = ref({});

onMounted(async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const id = urlParams.get("id");
  if (id) {
    try {
      const response = await axios.get(`${url}/programme/${id}`);
      const p = response.data.data;
      await fechNiveauData(p.niveau_id);
      programmeCours.value = [{
        id: p.id, cours_id: p.cours_id, niveau_id: p.niveau_id,
        professeur_id: p.profId, faculte_id: p.faculte_id,
        annee_academique: p.annee_academique_id, coefficients: p.coefficients,
        jours: p.jours, heure: p.heure, class: p.class, session: p.session,
      }];
    } catch (e) { console.error("Erreur chargement programme:", e); }
  } else {
    addEmptyRow();
  }
});

const addEmptyRow = () => {
  programmeCours.value.push({
    id: "", cours_id: "", niveau_id: "", professeur_id: "", faculte_id: "",
    annee_academique: "", coefficients: "", jours: "", heure: "", class: "", session: "",
  });
};

const removeProgramme = (index) => {
  if (programmeCours.value.length > 1) programmeCours.value.splice(index, 1);
};

const fechNiveauData = async (niveauId) => {
  if (!niveauId) return;
  try {
    const res = await axios.get(`${url}/niveau-with-class/${niveauId}`);
    choseNiveau.value      = res.data.niveau;
    cours_id_in_prog.value = res.data.cours;
    fetch_actual_class.value = res.data.classe_actuelle;
  } catch (e) { console.error(e); }
};

const handleNiveauChange = (event) => { fechNiveauData(event.target.value); };

const submitProgramme = async () => {
  isSubmitting.value = true;
  errors.value = {};
  try {
    const response = await axios.post(`${url}/programme`, { programmeCoursObject: programmeCours.value });
    if (response.status === 200 || response.status === 201) {
      Swal.fire("Enregistré !", "Le programme a été mis à jour avec succès.", "success");
      if (!programmeCours.value[0].id) { programmeCours.value = []; addEmptyRow(); }
    }
  } catch (error) {
    if (error.response?.status === 422) errors.value = error.response.data.errors;
    else Swal.fire("Erreur", "Impossible de sauvegarder le programme.", "error");
  } finally {
    isSubmitting.value = false;
  }
};

const getClassesByNiveau = (niveauId) => {
  if (!niveauId || !classes.value) return [];
  return classes.value.filter(c => c.niveau_id === niveauId);
};

const jours = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"];
</script>

<template>
  <div style="background: #0f1117; min-height: 100vh; font-family: 'DM Sans', 'Segoe UI', sans-serif;">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 pb-8 animate-[fadeUp_0.4s_ease_both]">

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-16 gap-3">
        <svg class="animate-spin w-5 h-5 text-[#7aaeff]" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
        </svg>
        <span class="text-[13px] text-[#7c83a0]">Chargement des données…</span>
      </div>

      <template v-else>
        <!-- ── Header ── -->
        <div class="mb-6">
          <h1 class="text-[22px] font-bold text-[#e8eaf0] tracking-tight">Programmation des cours</h1>
          <p class="text-[13px] text-[#7c83a0] mt-0.5">Affectez des professeurs et des horaires aux matières par classe.</p>
        </div>

        <!-- ── Form ── -->
        <form @submit.prevent="submitProgramme" class="space-y-3">

          <!-- ── Ligne de programme ── -->
          <div
            v-for="(programme, index) in programmeCours"
            :key="index"
            class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden"
          >
            <!-- Badge numéro de ligne -->
            <div class="flex items-center justify-between px-5 py-3 border-b border-white/[0.05] bg-[#0d1117]/40">
              <div class="flex items-center gap-2">
                <span class="inline-flex items-center justify-center w-5 h-5 rounded-md bg-[#4f8ef7]/10 text-[#7aaeff] text-[11px] font-bold border border-[#4f8ef7]/20">
                  {{ index + 1 }}
                </span>
                <span class="text-[12px] font-medium text-[#7c83a0]">Programmation {{ index + 1 }}</span>
              </div>
              <button
                v-if="programmeCours.length > 1"
                type="button"
                @click="removeProgramme(index)"
                class="flex items-center gap-1.5 text-[11px] text-[#3d4d62] hover:text-red-400 transition-colors px-2 py-1 rounded-lg hover:bg-red-500/8"
              >
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/>
                </svg>
                Supprimer
              </button>
            </div>

            <!-- Champs -->
            <div class="p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

              <!-- Niveau -->
              <div class="flex flex-col gap-1.5">
                <label class="prog-label">Niveau d'étude</label>
                <select v-model="programme.niveau_id" @change="handleNiveauChange($event, index)" class="prog-select">
                  <option value="" disabled>Choisir Niveau</option>
                  <option v-for="n in niveau" :key="n.id" :value="n.id">{{ n.name }}</option>
                </select>
                <p v-if="errors[`programmeCoursObject.${index}.niveau_id`]" class="prog-error">
                  {{ errors[`programmeCoursObject.${index}.niveau_id`][0] }}
                </p>
              </div>

              <!-- Cours -->
              <div class="flex flex-col gap-1.5">
                <label class="prog-label">Cours / Matière</label>
                <select v-model="programme.cours_id" class="prog-select">
                  <option value="" disabled>Choisir Matière</option>
                  <option v-for="c in cours" :key="c.id" :value="c.id">{{ c.cours_nom }}</option>
                </select>
                <p v-if="errors[`programmeCoursObject.${index}.cours_id`]" class="prog-error">
                  {{ errors[`programmeCoursObject.${index}.cours_id`][0] }}
                </p>
              </div>

              <!-- Professeur -->
              <div class="flex flex-col gap-1.5">
                <label class="prog-label">Professeur</label>
                <select v-model="programme.professeur_id" class="prog-select">
                  <option value="" disabled>Choisir Professeur</option>
                  <option v-for="p in professeur" :key="p.id" :value="p.id">{{ p.prenom }} {{ p.nom }}</option>
                </select>
              </div>

              <!-- Coefficients -->
              <div class="flex flex-col gap-1.5">
                <label class="prog-label">Coefficients</label>
                <input v-model="programme.coefficients" type="number" placeholder="1" class="prog-input" />
              </div>

              <!-- Faculté (conditionnel) -->
              <div v-if="choseNiveau.name === 'Universitaire' || choseNiveau.name === 'Professionel'" class="flex flex-col gap-1.5">
                <label class="prog-label">Faculté / Option</label>
                <select v-model="programme.faculte_id" class="prog-select">
                  <option value="" disabled>Choisir Option</option>
                  <option v-for="f in faculte" :key="f.id" :value="f.id">{{ f.nom }}</option>
                </select>
              </div>

              <!-- Classe -->
              <div class="flex flex-col gap-1.5">
                <label class="prog-label">Classe</label>
                <select v-model="programme.class" class="prog-select">
                  <option value="" disabled>Choisir Classe</option>
                  <option v-for="cls in getClassesByNiveau(programme.niveau_id)" :key="cls.id" :value="cls.id">
                    {{ cls.nom_classe }}
                  </option>
                </select>
              </div>

              <!-- Année Académique -->
              <div class="flex flex-col gap-1.5">
                <label class="prog-label">Année Académique</label>
                <select v-model="programme.annee_academique" class="prog-select">
                  <option value="" disabled>Choisir</option>
                  <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
                </select>
              </div>

              <!-- Jour -->
              <div class="flex flex-col gap-1.5">
                <label class="prog-label">Jour</label>
                <select v-model="programme.jours" class="prog-select">
                  <option value="" disabled>Choisir</option>
                  <option v-for="j in jours" :key="j" :value="j.toLowerCase()">{{ j }}</option>
                </select>
              </div>

              <!-- Heure -->
              <div class="flex flex-col gap-1.5">
                <label class="prog-label">Horaire</label>
                <input v-model="programme.heure" type="text" placeholder="08:00 - 10:00" class="prog-input" />
              </div>

            </div>
          </div>

          <!-- ── Footer actions ── -->
          <div class="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#161b26] rounded-2xl border border-white/[0.07] px-5 py-4">
            <button
              type="button"
              @click="addEmptyRow"
              class="flex items-center gap-2 text-[13px] font-medium text-[#7aaeff] hover:text-[#4f8ef7] transition-colors group"
            >
              <span class="flex items-center justify-center w-6 h-6 rounded-lg bg-[#4f8ef7]/10 border border-[#4f8ef7]/20 group-hover:bg-[#4f8ef7]/20 transition-colors">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5" class="w-3.5 h-3.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
                </svg>
              </span>
              Ajouter une programmation
            </button>

            <div class="flex items-center gap-3">
              <span class="text-[12px] text-[#7c83a0]">
                {{ programmeCours.length }} entrée{{ programmeCours.length > 1 ? 's' : '' }}
              </span>
              <button
                type="submit"
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
                <span>{{ isSubmitting ? 'Sauvegarde…' : 'Sauvegarder le Programme' }}</span>
              </button>
            </div>
          </div>

        </form>
      </template>
    </div>
  </div>
</template>

<style scoped>
.prog-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #7c83a0;
}

.prog-input {
  width: 100%;
  background: #0d1117;
  border: 1px solid rgba(255,255,255,0.08);
  color: #c9d1d9;
  border-radius: 10px;
  padding: 7px 11px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}
.prog-input::placeholder { color: #3d4d62; }
.prog-input:focus { border-color: rgba(79,142,247,0.35); }
.prog-input[type=number]::-webkit-inner-spin-button,
.prog-input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; }
.prog-input[type=number] { -moz-appearance: textfield; }

.prog-select {
  width: 100%;
  background: #0d1117;
  border: 1px solid rgba(255,255,255,0.08);
  color: #c9d1d9;
  border-radius: 10px;
  padding: 7px 28px 7px 11px;
  font-size: 13px;
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%237c83a0' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19.5 8.25l-7.5 7.5-7.5-7.5'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 9px center;
  background-size: 13px;
  transition: border-color 0.15s;
}
.prog-select:focus { border-color: rgba(79,142,247,0.35); }
.prog-select option { background: #161b26; color: #c9d1d9; }

.prog-error {
  font-size: 11px;
  color: #f87171;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>

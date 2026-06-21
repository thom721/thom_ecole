<script setup>
import { ref } from "vue";
import axios from "axios";
import AdminLayout from '@/layouts/AdminLayout.vue';
import Swal from "sweetalert2";

defineOptions({ layout: AdminLayout });

const url = import.meta.env.VITE_APP_BASE_URL;

const props = defineProps({
  niveau: Object,
});

const choseNiveau = ref({});
const courses = ref([
  { cours_nom: "", note_de_passage: "", type_matiere: "" },
]);
const errors = ref({});
const isSubmitting = ref(false);

const addCours = () => {
  courses.value.push({ cours_nom: "", note_de_passage: "", type_matiere: "" });
};

const removeCours = (index) => {
  if (courses.value.length > 1) courses.value.splice(index, 1);
};

const submitCours = async () => {
  isSubmitting.value = true;
  errors.value = {};
  try {
    const response = await axios.post(`${url}/cours`, { CoursesObject: courses.value });
    if (response.status === 200 || response.status === 201) {
      Swal.fire("Succès", "Les cours ont été enregistrés", "success");
      courses.value = [{ cours_nom: "", note_de_passage: "", type_matiere: "" }];
    }
  } catch (error) {
    if (error.response?.status === 422) errors.value = error.response.data.errors;
    else Swal.fire("Erreur", "Un problème est survenu lors de l'enregistrement", "error");
  } finally {
    isSubmitting.value = false;
  }
};

const fechNiveau = async (id) => {
  try {
    const res = await axios.get(`${url}/niveau-with-class/${id}`);
    choseNiveau.value = res.data.niveau;
  } catch (error) { console.error(error); }
};
</script>

<template>
  <div
    class="min-h-screen animate-[fadeUp_0.4s_ease_both]"
    style="background: #0f1117; font-family: 'DM Sans', 'Segoe UI', sans-serif;"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 pb-8">

      <!-- ── Header ── -->
      <div class="mb-6">
        <h1 class="text-[22px] font-bold text-[#e8eaf0] tracking-tight">Ajouter des Matières</h1>
        <p class="text-[13px] text-[#7c83a0] mt-0.5">Vous pouvez ajouter plusieurs lignes pour enregistrer plusieurs cours à la fois.</p>
      </div>

      <!-- ── Formulaire ── -->
      <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] overflow-hidden">

        <!-- En-tête des colonnes -->
        <div class="hidden md:grid md:grid-cols-[1fr_1fr_1fr_44px] gap-4 px-5 py-3 bg-[#0d1117]/60 border-b border-white/[0.05]">
          <span class="text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Nom Cours / Matière</span>
          <span class="text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Type de matière</span>
          <span class="text-[10px] font-semibold uppercase tracking-wider text-[#3d4d62]">Note de passage</span>
          <span></span>
        </div>

        <!-- Lignes de cours -->
        <form @submit.prevent="submitCours">
          <div
            v-for="(cours, index) in courses"
            :key="index"
            class="grid grid-cols-1 md:grid-cols-[1fr_1fr_1fr_44px] gap-3 px-5 py-4 transition-colors hover:bg-white/[0.01]"
            :class="{ 'border-t border-white/[0.05]': index > 0 }"
          >
            <!-- Nom -->
            <div class="flex flex-col gap-1.5">
              <label class="md:hidden text-[10px] font-semibold uppercase tracking-wider text-[#7c83a0]">Nom Cours / Matière</label>
              <input
                :id="'nom_'+index"
                v-model="cours.cours_nom"
                type="text"
                placeholder="Ex: Mathématiques"
                class="course-input"
                :class="{ 'border-red-500/40': errors[`CoursesObject.${index}.cours_nom`] }"
              />
              <p v-if="errors[`CoursesObject.${index}.cours_nom`]" class="text-[11px] text-red-400 flex items-center gap-1">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="w-3 h-3 shrink-0"><path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z"/></svg>
                {{ errors[`CoursesObject.${index}.cours_nom`][0] }}
              </p>
            </div>

            <!-- Type -->
            <div class="flex flex-col gap-1.5">
              <label class="md:hidden text-[10px] font-semibold uppercase tracking-wider text-[#7c83a0]">Type de matière</label>
              <select :id="'type_'+index" v-model="cours.type_matiere" class="course-select">
                <option value="" disabled>Sélectionnez un type</option>
                <option value="base">Matière de base</option>
                <option value="orale">Matière orale</option>
              </select>
            </div>

            <!-- Note de passage -->
            <div class="flex flex-col gap-1.5">
              <label class="md:hidden text-[10px] font-semibold uppercase tracking-wider text-[#7c83a0]">Note de passage</label>
              <input
                :id="'note_'+index"
                v-model="cours.note_de_passage"
                type="number"
                placeholder="60"
                class="course-input"
                :class="{ 'border-red-500/40': errors[`CoursesObject.${index}.note_de_passage`] }"
              />
              <p v-if="errors[`CoursesObject.${index}.note_de_passage`]" class="text-[11px] text-red-400 flex items-center gap-1">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="w-3 h-3 shrink-0"><path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z"/></svg>
                {{ errors[`CoursesObject.${index}.note_de_passage`][0] }}
              </p>
            </div>

            <!-- Supprimer -->
            <div class="flex items-start justify-center pt-0.5">
              <button
                v-if="courses.length > 1"
                type="button"
                @click="removeCours(index)"
                class="w-8 h-8 flex items-center justify-center rounded-lg text-[#3d4d62] hover:text-red-400 hover:bg-red-500/10 transition-colors"
                title="Supprimer cette ligne"
              >
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-4 h-4">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Footer du formulaire -->
          <div class="flex flex-col sm:flex-row items-center justify-between gap-3 px-5 py-4 border-t border-white/[0.06] bg-[#0d1117]/30">

            <!-- Ajouter ligne -->
            <button
              type="button"
              @click="addCours"
              class="flex items-center gap-2 text-[13px] font-medium text-[#7aaeff] hover:text-[#4f8ef7] transition-colors group"
            >
              <span class="flex items-center justify-center w-6 h-6 rounded-lg bg-[#4f8ef7]/10 border border-[#4f8ef7]/20 group-hover:bg-[#4f8ef7]/20 transition-colors">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5" class="w-3.5 h-3.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
                </svg>
              </span>
              Ajouter une ligne
            </button>

            <!-- Compteur + Enregistrer -->
            <div class="flex items-center gap-3">
              <span class="text-[12px] text-[#7c83a0]">
                {{ courses.length }} matière{{ courses.length > 1 ? 's' : '' }}
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
                <span>{{ isSubmitting ? 'Enregistrement…' : 'Enregistrer tout' }}</span>
              </button>
            </div>

          </div>
        </form>
      </div>

      <!-- ── Info helper ── -->
      <div class="flex items-start gap-3 mt-4 p-4 bg-[#4f8ef7]/5 border border-[#4f8ef7]/12 rounded-xl">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-4 h-4 text-[#7aaeff]/60 shrink-0 mt-0.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"/>
        </svg>
        <p class="text-[12px] text-[#7c83a0] leading-relaxed">
          Cliquez sur <span class="text-[#7aaeff]">Ajouter une ligne</span> pour enregistrer plusieurs matières en une seule fois. Toutes les lignes seront soumises ensemble.
        </p>
      </div>

    </div>
  </div>
</template>

<style scoped>
.course-input {
  width: 100%;
  background: #0d1117;
  border: 1px solid rgba(255,255,255,0.08);
  color: #c9d1d9;
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}
.course-input::placeholder { color: #3d4d62; }
.course-input:focus { border-color: rgba(79,142,247,0.35); }
/* Remove number input arrows */
.course-input[type=number]::-webkit-inner-spin-button,
.course-input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
.course-input[type=number] { -moz-appearance: textfield; }

.course-select {
  width: 100%;
  background: #0d1117;
  border: 1px solid rgba(255,255,255,0.08);
  color: #c9d1d9;
  border-radius: 10px;
  padding: 8px 30px 8px 12px;
  font-size: 13px;
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%237c83a0' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19.5 8.25l-7.5 7.5-7.5-7.5'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 14px;
  transition: border-color 0.15s;
}
.course-select:focus { border-color: rgba(79,142,247,0.35); }
.course-select option { background: #161b26; color: #c9d1d9; }
</style>

<script setup>
import { ref } from "vue";
import axios from "axios";
import AdminLayout from '@/layouts/AdminLayout.vue'; 
import InputLabel from "@/components/InputLabel.vue";
import TextInput from "@/components/TextInput.vue";
import PrimaryButton from "@/components/PrimaryButton.vue";
import Swal from "sweetalert2";

defineOptions({ layout: AdminLayout });

const url = import.meta.env.VITE_APP_BASE_URL;

const props = defineProps({
  niveau: Object, // Reçu depuis le parent ou le routeur
});

// --- ÉTATS ---
const choseNiveau = ref({});
const courses = ref([
  {
    cours_nom: "",
    note_de_passage: "",
    type_matiere: "",
  },
]);

const errors = ref({});
const isSubmitting = ref(false);

// --- LOGIQUE DES LIGNES ---
const addCours = () => {
  courses.value.push({
    cours_nom: "",
    note_de_passage: "",
    type_matiere: "",
  });
};

const removeCours = (index) => {
  if (courses.value.length > 1) {
    courses.value.splice(index, 1);
  }
};

// --- SOUMISSION ---
const submitCours = async () => {
  isSubmitting.value = true;
  errors.value = {};

  try {
    const response = await axios.post(`${url}/cours`, {
      CoursesObject: courses.value
    });

    if (response.status === 200 || response.status === 201) {
      Swal.fire("Succès", "Les cours ont été enregistrés", "success");
      // Réinitialiser le formulaire
      courses.value = [{ cours_nom: "", note_de_passage: "", type_matiere: "" }];
    }
  } catch (error) {
    if (error.response && error.response.status === 422) {
      errors.value = error.response.data.errors;
    } else {
      Swal.fire("Erreur", "Un problème est survenu lors de l'enregistrement", "error");
    }
  } finally {
    isSubmitting.value = false;
  }
};

// Exemple de fetch si tu as besoin de charger des infos au changement de niveau
const fechNiveau = async (id) => {
  try {
    const res = await axios.get(`${url}/niveau-with-class/${id}`);
    choseNiveau.value = res.data.niveau;
  } catch (error) {
    console.error(error);
  }
};
</script>

<template>
  <div class="max-w-7xl px-4 mx-auto pt-8 pb-14">
    <div class="mb-6">
      <h1 class="text-2xl  text-slate-700">Ajouter des Matières</h1>
      <p class="text-slate-500">Vous pouvez ajouter plusieurs lignes pour enregistrer plusieurs cours à la fois.</p>
    </div>

    <form @submit.prevent="submitCours" class="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
      
      <div v-for="(cours, index) in courses" :key="index" 
           class="grid md:grid-cols-4 gap-4 py-4 items-end transition-all"
           :class="{ 'border-t border-slate-100 mt-2': index > 0 }">

        <div class="flex-1">
          <InputLabel :for="'nom_'+index" value="Nom Cours / Matière" />
          <TextInput 
            :id="'nom_'+index" 
            v-model="cours.cours_nom" 
            type="text" 
            class="w-full mt-1 border-slate-200 focus:border-sky-500 focus:ring-sky-500 rounded-md shadow-sm"
            placeholder="Ex: Mathématiques"
          />
          <p class="text-red-500 text-xs mt-1" v-if="errors[`CoursesObject.${index}.cours_nom`]">
            {{ errors[`CoursesObject.${index}.cours_nom`][0] }}
          </p>
        </div>

        <div class="flex-1">
          <InputLabel :for="'type_'+index" value="Type de matière" />
          <select 
            :id="'type_'+index" 
            v-model="cours.type_matiere"
            class="w-full mt-1 border-slate-200 focus:border-sky-500 focus:ring-sky-500 rounded-md shadow-sm text-sm p-[9px] bg-white"
          >
            <option value="" disabled>Sélectionnez un type</option>
            <option value="base">Matière de base</option>
            <option value="orale">Matière orale</option>
          </select>
        </div>

        <div class="flex-1">
          <InputLabel :for="'note_'+index" value="Note de passage" />
          <TextInput 
            :id="'note_'+index" 
            v-model="cours.note_de_passage" 
            type="number" 
            class="w-full mt-1 border-slate-200 focus:border-sky-500 focus:ring-sky-500 rounded-md shadow-sm"
            placeholder="60"
          />
          <p class="text-red-500 text-xs mt-1" v-if="errors[`CoursesObject.${index}.note_de_passage`]">
            {{ errors[`CoursesObject.${index}.note_de_passage`][0] }}
          </p>
        </div>

        <div class="flex items-center justify-center pb-2">
          <button 
            type="button"
            @click="removeCours(index)" 
            v-if="courses.length > 1"
            class="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
            title="Supprimer cette ligne"
          >
            <i class="far fa-trash-can text-lg"></i>
          </button>
        </div>
      </div>

      <div class="mt-8 pt-6 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-4">
        <button 
          type="button"
          @click="addCours" 
          class="flex items-center text-sky-600 hover:text-sky-700 font-medium transition-colors"
        >
          <i class="fas fa-plus-circle me-2"></i> Ajouter une nouvelle ligne
        </button>

        <PrimaryButton 
          type="submit" 
          :disabled="isSubmitting"
          :class="{ 'opacity-50 cursor-not-allowed': isSubmitting }"
          class="w-full md:w-auto px-10 py-3 bg-sky-600 hover:bg-sky-700 text-white rounded-lg shadow-md transition-all uppercase tracking-widest text-xs "
        >
          <span v-if="isSubmitting">Enregistrement...</span>
          <span v-else>Enregistrer tout</span>
        </PrimaryButton>
      </div>
    </form>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import AdminLayout from '@/layouts/AdminLayout.vue'; 
import InputLabel from "@/components/InputLabel.vue";
import TextInput from "@/components/TextInput.vue";
import PrimaryButton from "@/components/PrimaryButton.vue";
import Swal from "sweetalert2";

defineOptions({ layout: AdminLayout });

const url = import.meta.env.VITE_APP_BASE_URL;
 
import { useSchoolStore } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';

const schoolStore = useSchoolStore();
// storeToRefs permet de garder la réactivité
const { niveau, professeur, annee,classes,faculte,cours, loading } = storeToRefs(schoolStore);

onMounted(() => {
  schoolStore.fetchAllDependencies();
}); 


// --- ÉTATS ---
const programmeCours = ref([]);
const errors = ref({});
const isSubmitting = ref(false);

// Données chargées dynamiquement selon le niveau
const cours_id_in_prog = ref([]);
const fetch_actual_class = ref([]);
const choseNiveau = ref({});

// --- INITIALISATION ---
onMounted(async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const id = urlParams.get("id");

  if (id) {
    // Mode ÉDITION
    try {
      const response = await axios.get(`${url}/programme/${id}`);
      const p = response.data.data;
      
      // Charger les dépendances du niveau (cours, classes) pour ce programme
      await fechNiveauData(p.niveau_id);

      programmeCours.value = [{
        id: p.id,
        cours_id: p.cours_id,
        niveau_id: p.niveau_id,
        professeur_id: p.profId, // Attention à la correspondance des clés API
        faculte_id: p.faculte_id,
        annee_academique: p.annee_academique_id,
        coefficients: p.coefficients,
        jours: p.jours,
        heure: p.heure,
        class: p.class,
        session: p.session,
      }];
    } catch (e) {
      console.error("Erreur chargement programme:", e);
    }
  } else {
    // Mode CRÉATION
    addEmptyRow();
  }
});

// --- LOGIQUE FORMULAIRE ---
const addEmptyRow = () => {
  programmeCours.value.push({
    id: "",
    cours_id: "",
    niveau_id: "",
    professeur_id: "",
    faculte_id: "",
    annee_academique: "",
    coefficients: "",
    jours: "",
    heure: "",
    class: "",
    session: "",
  });
};

const removeProgramme = (index) => {
  if (programmeCours.value.length > 1) {
    programmeCours.value.splice(index, 1);
  }
};

const fechNiveauData = async (niveauId) => {
  if (!niveauId) return;
  try {
    const res = await axios.get(`${url}/niveau-with-class/${niveauId}`);
    choseNiveau.value = res.data.niveau;
    cours_id_in_prog.value = res.data.cours;
    fetch_actual_class.value = res.data.classe_actuelle;
  } catch (e) {
    console.error(e);
  }
};

const handleNiveauChange = (event, index) => {
  const val = event.target.value;
  fechNiveauData(val);
};

// --- SOUMISSION ---
const submitProgramme = async () => {
  isSubmitting.value = true;
  errors.value = {};

  try {
    const response = await axios.post(`${url}/programme`, {
      programmeCoursObject: programmeCours.value
    });

    if (response.status === 200 || response.status === 201) {
      Swal.fire("Enregistré !", "Le programme a été mis à jour avec succès.", "success");
      if (!programmeCours.value[0].id) {
         programmeCours.value = [];
         addEmptyRow();
      }
    }
  } catch (error) {
    if (error.response?.status === 422) {
      errors.value = error.response.data.errors;
    } else {
      Swal.fire("Erreur", "Impossible de sauvegarder le programme.", "error");
    }
  } finally {
    isSubmitting.value = false;
  }
};

// Helper pour filtrer les classes par niveau (si non chargé via API)
const getClassesByNiveau = (niveauId) => { 
  if (!niveauId || !classes.value) return [];  
  return classes.value.filter(c => c.niveau_id === niveauId);
};
</script>

<template>
       <div v-if="loading" class="text-center p-5">
     Chargement des données...
  </div>
   
  <div v-else class="max-w-7xl px-4 mx-auto pt-6 pb-14 text-slate-700">
    <div class="mb-8">
      <h1 class="text-2xl ">Programmation des cours</h1>
      <p class="text-slate-500 text-sm">Affectez des professeurs et des horaires aux matières par classe.</p>
    </div>

    <form @submit.prevent="submitProgramme" class="space-y-6">
      <div v-for="(programme, index) in programmeCours" :key="index" 
           class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm transition-all"
           :class="{ 'border-l-4 border-l-orange-400': index > 0 }">
        
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          
          <div>
            <InputLabel value="Niveau d'étude" />
            <select v-model="programme.niveau_id" @change="handleNiveauChange($event, index)" class="input-field">
              <option value="" disabled>Choisir Niveau</option>
              <option v-for="n in niveau" :key="n.id" :value="n.id">{{ n.name }}</option>
            </select>
            <p v-if="errors[`programmeCoursObject.${index}.niveau_id`]" class="error-msg">{{ errors[`programmeCoursObject.${index}.niveau_id`][0] }}</p>
          </div>

          <div>
            <InputLabel value="Cours / Matière" />
            <select v-model="programme.cours_id" class="input-field">
              <option value="" disabled>Choisir Matière</option>
              <option v-for="c in cours" :key="c.id" :value="c.id">{{ c.cours_nom }}</option>
            </select>
            <p v-if="errors[`programmeCoursObject.${index}.cours_id`]" class="error-msg">{{ errors[`programmeCoursObject.${index}.cours_id`][0] }}</p>
          </div>

          <div>
            <InputLabel value="Professeur" />
            <select v-model="programme.professeur_id" class="input-field">
              <option value="" disabled>Choisir Professeur</option>
              <option v-for="p in professeur" :key="p.id" :value="p.id">{{ p.prenom }} {{ p.nom }}</option>
            </select>
          </div>

          <div>
            <InputLabel value="Coefficients" />
            <TextInput v-model="programme.coefficients" type="number" class="w-full mt-1" />
          </div>

          <div v-if="choseNiveau.name === 'Universitaire' || choseNiveau.name === 'Professionel'">
            <InputLabel value="Faculté / Option" />
            <select v-model="programme.faculte_id" class="input-field">
              <option value="" disabled>Choisir Option</option>
              <option v-for="f in faculte" :key="f.id" :value="f.id">{{ f.nom }}</option>
            </select>
          </div>

          <div>
            <InputLabel value="Classe" />
            <!-- <select v-model="programme.class" class="input-field">
              <option value="" disabled>Choisir Classe</option>
              <option v-for="cls in (fetch_actual_class.length ? fetch_actual_class : getClassesByNiveau(programme.niveau_id))" 
                      :key="cls.id" :value="cls.id">{{ cls.nom_classe }}</option>
            </select> -->
            <select v-model="programme.class" class="input-field">
               <option value="" disabled>Choisir Classe</option>
               <option v-for="cls in getClassesByNiveau(programme.niveau_id)" 
                         :key="cls.id" 
                         :value="cls.id">
               {{ cls.nom_classe }}
               </option>
               </select>
          </div>

          <div>
            <InputLabel value="Année Académique" />
            <select v-model="programme.annee_academique" class="input-field">
              <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
            </select>
          </div>

          <div>
            <InputLabel value="Jour" />
            <select v-model="programme.jours" class="input-field">
              <option value="lundi">Lundi</option>
              <option value="mardi">Mardi</option>
              <option value="mercredi">Mercredi</option>
              <option value="jeudi">Jeudi</option>
              <option value="vendredi">Vendredi</option>
              <option value="samedi">Samedi</option>
            </select>
          </div>

          <div>
            <InputLabel value="Heure (ex: 08:00 - 10:00)" />
            <TextInput v-model="programme.heure" type="text" class="w-full mt-1" />
          </div>

          <div class="flex items-end justify-center pb-1">
            <button type="button" @click="removeProgramme(index)" class="text-red-500 hover:bg-red-50 p-2 rounded-lg transition-all">
              <i class="far fa-trash-can text-lg"></i>
            </button>
          </div>
        </div>
      </div>

      <div class="flex flex-col md:flex-row justify-between items-center gap-4 bg-slate-50 p-4 rounded-xl">
        <button type="button" @click="addEmptyRow" class="text-sky-600  hover:underline">
          <i class="fas fa-plus-circle me-1"></i> Ajouter une autre programmation
        </button>

        <PrimaryButton :disabled="isSubmitting" class="w-full md:w-auto px-12 py-3 bg-sky-600">
          {{ isSubmitting ? 'Traitement...' : 'Sauvegarder le Programme' }}
        </PrimaryButton>
      </div>
    </form>
  </div>
</template>

 
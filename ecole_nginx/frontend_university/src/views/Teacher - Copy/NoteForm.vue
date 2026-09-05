<script setup>
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import Swal from "sweetalert2";
// import AdminLayout from '@/layouts/AdminLayout.vue'; 
import TextInput from "@/components/TextInput.vue";
import InsertNotesComponents from "@/components/InsertNotesComponents.vue";
import PrimaryButton from "@/components/PrimaryButton.vue";
import InputError from "@/components/InputError.vue";
import InputLabel from "@/components/InputLabel.vue";
 
// defineOptions({ layout: AdminLayout });

const url = import.meta.env.VITE_APP_BASE_URL;

// --- ÉTATS ---
const students = ref([]);
const list_cours = ref([]);
const evaluation = ref('');
const data_students = ref({})
const isSubmitting = ref(false);
const isdata = ref(false);
const errors = ref({});

const isLoading = ref(false); // État de chargement

const handleSearchStart = () => {
  isLoading.value = true;
  students.value = []; // On vide la liste précédente pendant la recherche
};

const handleSearchError =()=>{
  isLoading.value = false;
}
// Formulaire réactif (Remplace useForm)
const saveFormNote = ref({
  examen: '',
  controle: '',
  cours: '',
  coefficients: '',
  note_de_passage: '',
  annee_academique: '',
  type_matiere:  '',
  professeur_id: '',
  change_cours: ''
});

// Options d'évaluations
const evalOptions = {
  session: [
    { value: '1 ere Session', title: '1ère Session' },
    { value: '2 eme Session', title: '2ème Session' }
  ],
  controle: [
    { value: 'Contr. I', title: 'Contrôle I' },
    { value: 'Contr. II', title: 'Contrôle II' },
    { value: 'Contr. III', title: 'Contrôle III' }
  ],
  trimestre: [
    { value: 'Trimestre I', title: 'Trimestre I' },
    { value: 'Trimestre II', title: 'Trimestre II' },
    { value: 'Trimestre III', title: 'Trimestre III' }
  ]
};

// --- INITIALISATION ---
// onMounted(() => {
//   if (props.data_students?.result) {
//     // On clone les étudiants et on leur ajoute une propriété 'note' réactive
//     students.value = props.data_students.result.map(s => ({
//       ...s,
//       note: '' // Initialement vide
//     }));
//   }
// });

const handleDataFetched = (data) => {
  if (data) {
     isLoading.value = false;
    // 1. On remplit les informations du cours/formulaire
    saveFormNote.value.cours = data.datas.cours?.cours_nom || '';
    saveFormNote.value.coefficients = data.datas.cours?.coefficients || '';
    saveFormNote.value.annee_academique = data.datas.annee || '';
    saveFormNote.value.note_de_passage = data.datas.cours?.note_de_passage || '';
    saveFormNote.value.type_matiere = data.datas.cours.type_matiere;
     saveFormNote.value.controle = data.datas.examEcheance?.evaluation_par || '';
    list_cours.value = data.datas.list_cours || []
    // 2. On remplit la liste des étudiants pour le tableau
    data_students.value={
     "session":data.datas.session,
     "examEcheance":data.datas.examEcheance,
     "month":data.datas.month,
     "nom_classe":data.datas.cours?.nom_classe
     }
    students.value = data.datas.result.map(s => ({
      ...s,
      note: '' // On prépare le champ note pour chaque étudiant
    }));
isdata.value=true
    console.log("Données reçues et formulaire rempli !",data.datas);
  }
};

const showSwal = (text, icon = 'info') => {
  Swal.fire({
    position: "top-end",
    text: text,
    icon: icon,
    showConfirmButton: false,
    timer: 2000,
  });
};

// --- LOGIQUE ---

// Charger les notes existantes quand on change d'évaluation
const evaluationChange = async (e) => {
  evaluation.value = e.target.value;
  
  const payload = {
    ...saveFormNote.value,
    examen: evaluation.value,
    notes: students.value.map(s => ({ id: s.id, identifiant: s.identifiant }))
  };

  try {
    const res = await axios.post(`${url}/cours-etudiant-edit-note`, payload);
    if (res.status === 200 && res.data.success) {
      // On met à jour les notes dans notre tableau réactif
      res.data.success.forEach(item => {
        const student = students.value.find(s => s.id === item.etudiant_id);
        if (student) student.note = item.note;
      });
    }
  } catch (err) {
    showSwal(err.response?.data?.errors?.cours || "Erreur de chargement", 'error');
  }
};

const coursChange = (e) => {
  const selectedId = e.target.value;
  const cours = list_cours.value.find(c => c.id == selectedId);
  
  if (cours) {
    saveFormNote.value.cours = cours.cours_nom;
    saveFormNote.value.coefficients = cours.coefficients;
    saveFormNote.value.note_de_passage = cours.note_de_passage;
    saveFormNote.value.type_matiere = cours.type_matiere;
    saveFormNote.value.professeur_id = cours.professeur_id;
    // Reset des notes visuelles
    students.value.forEach(s => s.note = '');
  }
};

const submitNotes = async () => {
  isSubmitting.value = true;
  errors.value = {};

  const payload = {
    ...saveFormNote.value,
    notes: students.value.map(s => ({
      id: s.id,
      identifiant: s.identifiant,
      note: s.note
    }))
  };

  try {
    const res = await axios.post(`${url}/coursEtudiant`, payload);
    if (res.data.success) {
      showSwal(res.data.success, 'success');
      saveFormNote.value.examen = "";
      saveFormNote.value.change_cours = "";
      students.value.forEach(s => s.note = '');
    }
  } catch (err) {
    console.log(err);
    
    errors.value = err.response?.data?.errors || {};
    showSwal("Veuillez vérifier les notes saisies", 'error');
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="max-w-7xl px-4 mx-auto pb-16 text-slate-600">

     <InsertNotesComponents v-if="!isdata"
     route="cours-etudiant-add-note" 
     @search-started="handleSearchStart"
     @search-error="handleSearchError"
      @result-fetched="handleDataFetched" />

     <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
      <p class="mt-4 text-slate-500 font-medium">Récupération de la liste des étudiants...</p>
    </div> 
    <!-- <div v-if="data_students?.result" class="mt-6 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden"> -->
      <div v-if="!isLoading && students.length > 0" class="mt-6 animate-fade-in"> 
      <div class="p-6 bg-slate-50 border-b border-slate-100">
        <div class="grid md:grid-cols-3 gap-6 items-end">
          
          <div>
            <p class="text-sm text-slate-400 uppercase font-bold tracking-wider">Cours : <span class="text-sky-600 ml-8">{{ saveFormNote.cours }}</span> </p> 
            <p class="font-medium">
              Classe - Ann&eacute;e <span class="text-sky-600 ml-8">{{ data_students.nom_classe }} — {{ saveFormNote.annee_academique }}</span>
            </p>
          </div>
          
          <div>
            <InputLabel value="Changer de Matière" />
            <select @change="coursChange" v-model="saveFormNote.change_cours" class="input-select">
              <option value="" disabled>Sélectionnez une matière</option>
              <option v-for="c in list_cours" :key="c.id" :value="c.id">
                {{ c.cours_nom }}
              </option>
            </select>
          </div>

          <div>
            <InputLabel value="Type d'Évaluation" />
            
            <div v-if="data_students.session" class="flex gap-4 py-2">
              <label class="flex items-center cursor-pointer">
                <input type="radio" v-model="saveFormNote.controle" value="intra" class="text-sky-600 focus:ring-sky-500">
                <span class="ms-2 font-bold">Intra</span>
              </label>
              <label class="flex items-center cursor-pointer">
                <input type="radio" v-model="saveFormNote.controle" value="finale" class="text-sky-600 focus:ring-sky-500">
                <span class="ms-2 font-bold">Final</span>
              </label>
            </div>

            <select v-else @change="evaluationChange" v-model="saveFormNote.examen" class="input-select">
              <option value="" disabled>Choisir l'examen</option>
              
              <template v-if="data_students.examEcheance?.evaluation_par?.toLowerCase() === 'mois'">
                <option v-for="(val, key) in data_students.month" :key="key" :value="key">{{ key }}</option>
              </template>

              <template v-else-if="data_students.examEcheance?.evaluation_par === 'Controle'">
                <option v-for="opt in evalOptions.controle" :key="opt.value" :value="opt.value">{{ opt.title }}</option>
              </template>

              <template v-else-if="data_students.examEcheance?.evaluation_par === 'Trimestre'">
                <option v-for="opt in evalOptions.trimestre" :key="opt.value" :value="opt.value">{{ opt.title }}</option>
              </template>
            </select>
            <InputError :message="errors.examen?.[0]" />
          </div>

        </div>
      </div>

      <form @submit.prevent="submitNotes">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead class="bg-slate-800 text-white">
              <tr>
                <th class="p-2 text-sm font-semibold uppercase">#</th>
                <th class="p-2 text-sm font-semibold uppercase">Identifiant</th>
                <th class="p-2 text-sm font-semibold uppercase">Nom & Prénom</th>
                <th class="p-2 text-sm font-semibold uppercase w-32 text-center bg-slate-700">
                  {{ saveFormNote.controle || evaluation || 'Note' }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="(student, index) in students" :key="student.id" class="hover:bg-slate-50 transition-colors">
                <td class="p-2 text-slate-400 text-sm">{{ index + 1 }}</td>
                <td class="p-2">
                  <span class="font-mono text-xs bg-slate-100 px-2 py-1 rounded text-slate-600">
                    {{ student.identifiant }}
                  </span>
                </td>
                <td class="p-2 font-medium text-slate-700">
                  {{ student.nom }} {{ student.prenom }}
                </td>
                <td class="p-2 bg-slate-50/50">
                  <div class="flex flex-col items-center">
                    <input 
                      type="number" 
                      v-model="student.note"
                      step="0.1"
                      min="0" 
                      class="w-20 text-center font-bold py-1 rounded border border-slate-300 focus:border-sky-500 focus:ring-sky-500 shadow-sm"
                      :class="{'border-red-500 bg-red-50': errors[`notes.${index}.note`]}"
                    />
                    <span v-if="errors[`notes.${index}.note`]" class="text-[10px] text-red-500 mt-1">
                      {{ errors[`notes.${index}.note`][0] }}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="p-6 bg-slate-50 border-t border-slate-200 flex justify-end">
          <PrimaryButton :disabled="isSubmitting" class="px-12 py-2 bg-emerald-600 hover:bg-emerald-700">
            {{ isSubmitting ? 'Enregistrement...' : 'Enregistrer les notes' }}
          </PrimaryButton>
        </div>
      </form>
    </div>
  </div>
</template>
 
<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
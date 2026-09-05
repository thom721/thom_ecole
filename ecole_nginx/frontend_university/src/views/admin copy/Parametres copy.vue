<script setup>
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import Swal from "sweetalert2";

// Composants (À adapter selon ton projet)
import DialogModal from "@/components/DialogModal.vue";
import InputLabel from "@/components/InputLabel.vue";
import TextInput from "@/components/TextInput.vue";
import InputError from "@/components/InputError.vue";

const url = import.meta.env.VITE_APP_BASE_URL;
 
const modals = ref({
  grade: false,
  faculte: false,
  year: false,
  class: false,
  exam: false,
  payment: false,
  frais: false
});

const changeButton = ref(false);
 
const dataLists = ref({
  classes: { data: [], meta: {} },
  payments: { data: [], meta: {} },
  facultes: { data: [], meta: {} },
  exams: { data: [], meta: {} },
  years: { data: [], meta: {} },
  frais: []
});
 
const selections = ref({
  niveaux: [],
  facultesDisponibles: [],
  anneesAcademiques: [],
  classesDisponibles: []
});
 
const formFaculte = ref({ id: "", nom: "", nb_annee: "" });
const formYear = ref({ id: "", date_debut: "", date_fin: "", niveau_detude: "" });
const formClass = ref({ id: "", niveau_id: "", faculte_id: "", annee_detude: "" });
const formFrais = ref({ id: "", niveau_id: "", prix: "", anneeAc: "" });

const formPayment = ref({
  id: "",
  niveau_id: "",
  faculte_id: "",
  classe: "",
  echeance: "",
  devise: "HTG",
  anneeAcademique: "",
  nb_echeance: 0,
  montant: "",
  montant_par: {},
  accessoires: []
});
 
const loadAllData = async () => {
  fetchData('classes', '/classes');
  fetchData('payments', '/parametrePaiement');
  fetchData('years', '/anneeAcademique');
  fetchData('exams', '/paramsExam');
  fetchFrais();
  loadNiveaux();
};

const fetchData = async (key, endpoint, page = 1) => {
  try {
    const res = await axios.get(`${url}${endpoint}`, { params: { page } });
    dataLists.value[key] = res.data;
    console.log(res.data);
    
  } catch (e) { console.error(e); }
};

const loadNiveaux = async () => {
  const res = await axios.get(`${url}/niveau`);
  selections.value.niveaux = res.data.data;
};

const fetchFrais = async () => {
  const res = await axios.get(`${url}/fraisDinscription`);
  dataLists.value.frais = res.data.data;
};

onMounted(loadAllData);

// --- Logique Spécifique (Niveau / Faculté) ---
const handleNiveauChange = async (niveauId) => {
  try {
    const res = await axios.get(`${url}/niveau-with-class/${niveauId}`);
    selections.value.facultesDisponibles = res.data.facultes;
    selections.value.classesDisponibles = res.data.classe_actuelle;
    
    // Reset si ce n'est pas de l'édition
    if (!changeButton.value) {
      formClass.value.faculte_id = "";
    }
  } catch (e) { console.error(e); }
};

// --- Actions CRUD ---
const saveClass = async () => {
  try {
    await axios.post(`${url}/classes`, formClass.value);
    modals.value.class = false;
    fetchData('classes', '/classes');
    Swal.fire("Succès", "La classe a été enregistrée", "success");
  } catch (e) {
    console.error(e);
  }
};

const editClass = async (id) => {
  const res = await axios.get(`${url}/classes/${id}`);
  const d = res.data.data;
  formClass.value = { 
    id: d.id, 
    niveau_id: d.niveau_id, 
    annee_detude: d.nom_classe,
    faculte_id: d.faculte_id 
  };
  await handleNiveauChange(d.niveau_id);
  changeButton.value = true;
  modals.value.class = true;
};

// --- Gestion des Accessoires (Paiement) ---
const addAccessoire = () => {
  formPayment.value.accessoires.push({ type_daccessoire: '', prix: '' });
};

const removeAccessoire = (index) => {
  formPayment.value.accessoires.splice(index, 1);
};

// --- Helpers de Modales ---
const openModal = (type) => {
  changeButton.value = false;
  // Reset des formulaires ici selon le type
  modals.value[type] = true;
};

const generateEcheanceInputs = (e) => {
  const count = parseInt(e.target.value, 10) || 0;
  formPayment.value.montant_par = {}; // Reset
   
  for (let i = 1; i <= count; i++) {
    formPayment.value.montant_par[`Versement ${i}`] = "";
  }
};

const submitPaymentParams = async () => {
  try {
    const response = await axios.post(`${url}/parametrePaiement`, formPayment.value);
    if (response.status === 200) {
      modals.value.payment = false;
      fetchData('payments', '/parametrePaiement');
      Swal.fire("Succès", "Paramètres de paiement enregistrés", "success");
      resetPaymentForm();
    }
  } catch (error) { 
    if (error.response?.data) {
      formPayment.value.errors = error.response.data;
    }
  }
};

const resetPaymentForm = () => {
  formPayment.value = {
    id: "", niveau_id: "", faculte_id: "", classe: "",
    echeance: "", devise: "HTG", anneeAcademique: "",
    nb_echeance: 0, montant: "", montant_par: {}, accessoires: []
  };
};

// --- Logique des Frais d'Inscription ---

const storeFrais = async () => {
  try {
    await axios.post(`${url}/fraisDinscription`, formFrais.value);
    modals.value.frais = false;
    fetchFrais();
    Swal.fire("Mis à jour", "Les frais ont été enregistrés", "success");
  } catch (e) { console.error(e); }
};

const editFrais = (item) => {
  formFrais.value = { ...item };
  changeButton.value = true;
  modals.value.frais = true;
};

const formExam = ref({
  id: "",
  niveau_id: "",
  annee_academique_id: "",
  evaluation_par: "",  
});

 
const submitExamParams = async () => {
  try {
    const res = await axios.post(`${url}/paramsExam`, formExam.value);
    if (res.status === 200) {
      modals.value.exam = false;
      fetchData('exams', '/paramsExam');
      Swal.fire("Configuré", "Le mode d'évaluation a été mis à jour", "success");
      formExam.value = { id: "", niveau_id: "", annee_academique_id: "", evaluation_par: "" };
    }
  } catch (e) {
    console.error("Erreur param examen:", e);
  }
};

 
const editExam = (item) => {
  formExam.value = {
    id: item.id,
    niveau_id: item.niveau_id,
    annee_academique_id: item.annee_academique_id,
    evaluation_par: item.evaluation_par
  };
  changeButton.value = true;
  modals.value.exam = true;
};

// Fonction universelle pour charger les données avec pagination
// const fetchData = async (key, endpoint, page = 1) => {
//   try {
//     const res = await axios.get(`${url}${endpoint}`, { 
//       params: { page: page } 
//     });
//     // Laravel retourne les données dans res.data.data 
//     // et les infos de pagination à la racine de res.data
//     dataLists.value[key] = res.data; 
//   } catch (e) { 
//     console.error(`Erreur chargement ${key}:`, e); 
//   }
// };


</script>
<!-- <div class="p-4 border-t bg-slate-50/50">
  <Paginated 
    :links="dataLists.classes.links" 
    @change-page="(page) => fetchData('classes', '/api/classes', page)" 
  />
</div> -->

<template>
  <div class="space-y-8">
    <div class="flex flex-wrap gap-3 pb-6 border-b">
      <button @click="openModal('class')" class="btn-primary">
        <i class="fas fa-chalkboard mr-2"></i> Nouvelle Classe
      </button>
      <button @click="openModal('year')" class="btn-white">
        <i class="fas fa-calendar-alt mr-2"></i> Année Académique
      </button>
      <button @click="openModal('payment')" class="btn-white">
        <i class="fas fa-money-check-alt mr-2"></i> Paramètres Paiement
      </button>
      <button @click="openModal('frais')" class="btn-white text-emerald-600 border-emerald-200">
        <i class="fas fa-tag mr-2"></i> Frais d'Inscription
      </button>
    </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 mt-8">
    
    <section class="card shadow-md">
      <div class="card-header flex justify-between items-center">
        <span>Configurations des Écolages</span>
        <button @click="openModal('payment')" class="text-xs bg-sky-100 text-sky-700 px-2 py-1 rounded">
          <i class="fas fa-plus mr-1"></i> Nouveau
        </button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="bg-slate-50 text-slate-500 uppercase text-xs">
            <tr>
              <th class="px-4 py-3">Classe</th>
              <th class="px-4 py-3">Montant</th>
              <th class="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="pay in dataLists.payments.data" :key="pay.id" class="hover:bg-slate-50">
              <td class="px-4 py-3">
                <span class="font-bold text-slate-700">{{ pay.classe }}</span>
                <p class="text-[10px] text-slate-400">{{ pay.echeance }} ({{ pay.devise }})</p>
              </td>
              <td class="px-4 py-3 font-mono text-emerald-600 font-bold">
                {{ pay.montant }}
              </td>
              <td class="px-4 py-3 text-right">
                <button class="p-2 hover:text-sky-600"><i class="fas fa-cog"></i></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="card shadow-md border-emerald-100">
      <div class="card-header bg-emerald-50 text-emerald-800 border-emerald-100">
        Frais d'Inscription par Cycle
      </div>
      <div class="p-0">
        <table class="w-full text-sm">
          <tbody class="divide-y divide-emerald-50">
            <tr v-for="f in dataLists.frais" :key="f.id" class="hover:bg-emerald-50/30">
              <td class="px-6 py-4">
                <div class="text-xs text-slate-400 uppercase tracking-wider">Cycle</div>
                <div class="font-bold text-slate-700">{{ f.niveau?.name }}</div>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="text-lg font-black text-emerald-600">{{ f.prix }} <small>HTG</small></div>
                <button @click="editFrais(f)" class="text-[10px] text-sky-500 underline uppercase">Modifier</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
      
      <section class="card">
        <div class="card-header">Classes & Niveaux</div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 border-b">
              <tr>
                <th class="px-4 py-3 text-left">Niveau</th>
                <th class="px-4 py-3 text-left">Classe</th>
                <th class="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="item in dataLists.classes.data" :key="item.id">
                <td class="px-4 py-3 font-medium">{{ item.niveau?.name }}</td>
                <td class="px-4 py-3">{{ item.nom_classe }}</td>
                <td class="px-4 py-3 text-right">
                  <button @click="editClass(item.id)" class="text-sky-500 hover:bg-sky-50 p-2 rounded">
                    <i class="fas fa-edit"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="card">
        <div class="card-header">Années Académiques</div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm text-left">
            <thead class="bg-slate-50 border-b">
              <tr>
                <th class="px-4 py-3">Période</th>
                <th class="px-4 py-3">Cycle</th>
                <th class="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="y in dataLists.years.data" :key="y.id">
                <td class="px-4 py-3 font-bold">{{ y.annee_academique }}</td>
                <td class="px-4 py-3">{{ y.niveau_detude }}</td>
                <td class="px-4 py-3 text-right">
                   <i class="fas fa-edit text-sky-400 cursor-pointer"></i>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <DialogModal :show="modals.class" @close="modals.class = false">
      <template #title>Configuration de la Classe</template>
      <template #content>
        <div class="space-y-4 p-2">
          <div>
            <InputLabel value="Cycle d'étude" />
            <select v-model="formClass.niveau_id" @change="handleNiveauChange($event.target.value)" class="input-normal">
              <option value="">Sélectionner...</option>
              <option v-for="n in selections.niveaux" :key="n.id" :value="n.id">{{ n.name }}</option>
            </select>
          </div>

          <div v-if="selections.facultesDisponibles.length > 0">
            <InputLabel value="Domaine / Faculté" />
            <select v-model="formClass.faculte_id" class="input-normal">
              <option v-for="f in selections.facultesDisponibles" :key="f.id" :value="f.id">{{ f.nom }}</option>
            </select>
          </div>

          <div>
            <InputLabel value="Nom de la classe (ex: 3ème Année)" />
            <TextInput v-model="formClass.annee_detude" placeholder="Ex: 9ème Fondamentale" />
          </div>
        </div>
      </template>
      <template #footer>
        <button @click="saveClass" class="btn-primary">
          {{ changeButton ? 'Mettre à jour' : 'Enregistrer' }}
        </button>
      </template>
    </DialogModal>
  <DialogModal :show="modals.payment" @close="modals.payment = false" max-width="3xl">
    <template #title>Paramétrage Financier</template>
    <template #content>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-2">
        
        <div class="space-y-4">
          <div>
            <InputLabel value="Cycle & Classe" />
            <select v-model="formPayment.niveau_id" @change="handleNiveauChange($event.target.value)" class="input-normal">
              <option v-for="n in selections.niveaux" :key="n.id" :value="n.id">{{ n.name }}</option>
            </select>
            <select v-model="formPayment.classe" class="input-normal mt-2">
              <option v-for="c in selections.classesDisponibles" :key="c.id" :value="c.nom_classe">{{ c.nom_classe }}</option>
            </select>
          </div>

          <div>
            <InputLabel value="Mode de versement" />
            <select v-model="formPayment.echeance" class="input-normal">
              <option value="Mensuel">Mensuel</option>
              <option value="Trimestriel">Trimestriel</option>
              <option value="Versement">Par Versement Spécifique</option>
            </select>
          </div>

          <div v-if="formPayment.echeance === 'Versement'">
            <InputLabel value="Nombre de versements" />
            <input type="number" @input="generateEcheanceInputs" v-model="formPayment.nb_echeance" class="input-normal" />
          </div>
        </div>

        <div class="space-y-4">
          <div class="bg-slate-50 p-4 rounded-xl border border-slate-200">
            <InputLabel value="Montant Total de l'écolage" />
            <div class="relative">
              <input type="text" v-model="formPayment.montant" class="input-normal text-xl font-bold text-emerald-700" placeholder="0.00" />
              <span class="absolute right-3 top-3 font-bold text-slate-400">{{ formPayment.devise }}</span>
            </div>
          </div>

          <div v-if="Object.keys(formPayment.montant_par).length > 0" class="max-h-40 overflow-y-auto p-2 border rounded-lg bg-white">
            <div v-for="(val, label) in formPayment.montant_par" :key="label" class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold text-slate-500">{{ label }} :</span>
              <input type="text" v-model="formPayment.montant_par[label]" class="w-32 p-1 border-b focus:border-sky-500 text-right" placeholder="Montant" />
            </div>
          </div>
        </div>
      </div>

      <div class="mt-6 border-t pt-4">
        <div class="flex justify-between items-center mb-4">
          <h4 class="font-bold text-slate-700 text-sm italic">Accessoires Obligatoires (1er Versement)</h4>
          <button @click="addAccessoire" class="text-xs text-sky-600 font-bold">+ Ajouter</button>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div v-for="(acc, index) in formPayment.accessoires" :key="index" class="flex gap-2 mb-2">
            <input v-model="acc.type_daccessoire" placeholder="Ex: Badge" class="input-normal text-xs" />
            <input v-model="acc.prix" placeholder="Prix" class="w-20 input-normal text-xs" />
            <button @click="removeAccessoire(index)" class="text-rose-500 px-2">×</button>
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <button @click="submitPaymentParams" class="btn-primary w-full md:w-auto">Enregistrer la Configuration</button>
    </template>
  </DialogModal>
  
   <div class="mt-8">
    <section class="card border-amber-100 shadow-lg">
      <div class="card-header bg-amber-50 text-amber-800 border-amber-100 flex justify-between items-center">
        <div class="flex items-center">
          <i class="fas fa-graduation-cap mr-2"></i>
          <span>Système d'Évaluation & Examens</span>
        </div>
        <button @click="openModal('exam')" class="btn-white text-xs py-1 px-3 border-amber-200 hover:bg-amber-100">
          Configurer un Cycle
        </button>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-amber-50/50 text-amber-900/60 uppercase text-[10px] font-black">
            <tr>
              <th class="px-6 py-3 text-left">Cycle / Niveau</th>
              <th class="px-6 py-3 text-left">Année Académique</th>
              <th class="px-6 py-3 text-left">Mode d'Évaluation</th>
              <th class="px-6 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-amber-50">
            <tr v-for="ex in dataLists.exams.data" :key="ex.id" class="hover:bg-amber-50/20 transition">
              <td class="px-6 py-4 font-bold text-slate-700">
                {{ ex.niveau?.name || 'N/A' }}
              </td>
              <td class="px-6 py-4">
                <span class="bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs">
                  {{ ex.annee_academique?.annee_academique || 'N/A' }}
                </span>
              </td>
              <td class="px-6 py-4 text-amber-700 font-medium italic">
                Par {{ ex.evaluation_par }}
              </td>
              <td class="px-6 py-4 text-right">
                <button @click="editExam(ex)" class="text-amber-500 hover:text-amber-700 p-2">
                  <i class="fas fa-pen-nib"></i>
                </button>
              </td>
            </tr>
            <tr v-if="dataLists.exams.data.length === 0">
              <td colspan="4" class="px-6 py-10 text-center text-slate-400 italic">
                Aucune configuration d'examen définie.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>


  <DialogModal :show="modals.exam" @close="modals.exam = false">
    <template #title>Paramètres d'Évaluation</template>
    <template #content>
      <div class="space-y-5 p-2">
        <div>
          <InputLabel value="Cycle d'enseignement" />
          <select v-model="formExam.niveau_id" class="input-normal">
            <option value="" disabled>Choisir le cycle</option>
            <option v-for="n in selections.niveaux" :key="n.id" :value="n.id">{{ n.name }}</option>
          </select>
        </div>

        <div>
          <InputLabel value="Année Académique concernée" />
          <select v-model="formExam.annee_academique_id" class="input-normal">
            <option value="" disabled>Sélectionner l'année</option>
            <option v-for="y in dataLists.years.data" :key="y.id" :value="y.id">
              {{ y.annee_academique }}
            </option>
          </select>
        </div>

        <div>
          <InputLabel value="Découpage de l'année (Évaluation par...)" />
          <div class="grid grid-cols-2 gap-3 mt-2">
            <label class="flex items-center p-3 border rounded-xl cursor-pointer hover:bg-slate-50 transition" :class="{'border-sky-500 bg-sky-50': formExam.evaluation_par === 'Trimestre'}">
              <input type="radio" v-model="formExam.evaluation_par" value="Trimestre" class="hidden" />
              <span class="text-sm font-medium">Trimestre</span>
            </label>
            <label class="flex items-center p-3 border rounded-xl cursor-pointer hover:bg-slate-50 transition" :class="{'border-sky-500 bg-sky-50': formExam.evaluation_par === 'Semestre'}">
              <input type="radio" v-model="formExam.evaluation_par" value="Semestre" class="hidden" />
              <span class="text-sm font-medium">Semestre</span>
            </label>
            <label class="flex items-center p-3 border rounded-xl cursor-pointer hover:bg-slate-50 transition" :class="{'border-sky-500 bg-sky-50': formExam.evaluation_par === 'Contrôle'}">
              <input type="radio" v-model="formExam.evaluation_par" value="Contrôle" class="hidden" />
              <span class="text-sm font-medium">Contrôle Continu</span>
            </label>
            <label class="flex items-center p-3 border rounded-xl cursor-pointer hover:bg-slate-50 transition" :class="{'border-sky-500 bg-sky-50': formExam.evaluation_par === 'Session'}">
              <input type="radio" v-model="formExam.evaluation_par" value="Session" class="hidden" />
              <span class="text-sm font-medium">Session (Univ)</span>
            </label>
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <button @click="submitExamParams" class="btn-primary">
        {{ changeButton ? 'Modifier la config' : 'Valider la configuration' }}
      </button>
    </template>
  </DialogModal>
</div>
</template>
 
 
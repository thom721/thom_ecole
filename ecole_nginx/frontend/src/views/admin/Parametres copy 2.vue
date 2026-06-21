<script setup>
import { ref, onMounted, computed,watch } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2'; 
import AdminLayout from '@/layouts/AdminLayout.vue';
import Checkbox from '@/components/Checkbox.vue';
import InputError from '@/components/InputError.vue';
import InputLabel from '@/components/InputLabel.vue';
import Paginated from '@/components/Paginated.vue';
import TextInput from '@/components/TextInput.vue';
import PrimaryButton from '@/components/PrimaryButton.vue';
import StyleModal from '@/components/StyleModal.vue';
import DangerButton from '@/components/DangerButton.vue';
import Pagination from '@/components/Pagination.vue';


import { useSchoolStore } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';

const router = useRouter();
const url = import.meta.env.VITE_APP_BASE_URL;


const schoolStore = useSchoolStore();
const { niveau, professeur, annee,classes,faculte,cours, loading } = storeToRefs(schoolStore);
onMounted(() => {
  schoolStore.fetchAllDependencies();
}); 

const getClassesByNiveau = (niveauId) => { 
  if (!niveauId || !classes.value) return [];  
  return classes.value.filter(c => c.niveau_id === niveauId);
};

// Refs pour les modaux
const grade_etude = ref(false);
const faculte_profession = ref(false);
const anneeAcademique = ref(false);
const niveau_detude_modal_classe = ref(false);
const exam_params = ref(false);
const Payment_params_show = ref(false);
const frais = ref(false);
const changeButton = ref(false);

// Refs pour les données
const nbControleOrVersementOrtrimestre = ref([]);
const versementEntriesForm = ref([]);
const editMontantPar = ref(false);
const annee_niveau_detude_classique = ref([]);
// const faculte = ref([]);
const niveauUniver = ref(false);
const anneeFac_forPayment = ref([]);
const echeance = ref('');
const choseNiveau = ref([]);
const niveau_et = ref([]);
const classeParams = ref({ data: [], meta: {}});
const paimentParams = ref({ data: [], meta: {} });
const facultePaginate = ref({ data: [], meta: {} });
const anneeAcademiquePaginate = ref({ data: [], meta: {} });
const annee_paginate = ref({ data: [], meta: {} });
const examPaginate = ref({ data: [], meta: {} });
const frais_paginate = ref([]);
// const niveau = ref([]);
const faculte_niv = ref([]);

// Accessoires
const accessoireTypes = ref(['Maillot', 'Badge', 'Tenue de Sport', 'Initiale']);
const accessoires = ref([{ type_daccessoire: '', prix: '' }]);

// Forms
const form = ref({
  id: '',
  nom: '',
  nb_annee: '',
  errors: {}
});

const formyear = ref({
  id: '',
  date_debut: '',
  date_fin: '',
  niveau_detude: '',
  errors: {}
});

const formNiveau = ref({
  id: '',
  niveau_id: '',
  faculte_id: '',
  nom_classe: '',
  errors: {}
});

const formExamParam = ref({
  id: '',
  niveau_id: '',
  annee_academique_id: '',
  evaluation_par: '',
  errors: {}
});

const formgrade = ref({
  id: '',
  name: '',
  errors: {}
});

const paymentFormParams = ref({
  id: '',
  niveau_id: '',
  faculte_id: '',
  classe: '',
  echeance: '',
  devise: '',
  anneeAcademique: '',
  nb_echeance: '',
  montant: '',
  montant_par: {},
  accessoires: [],
  errors: {}
});

const formFrais = ref({
  id: '',
  niveau_id: '',
  prix: '',
  anneeAc: '',
  errors: {}
});

// Mounted
onMounted(async () => {
  await Promise.all([
    getParamForExam(),
    getClasses(),
    getPaymentParams(),
    getYear(),
    getFraisDinscription(),
    getNiveaux(),
    getFacultes()
  ]);
});

// Methods - API Calls
const getNiveaux = async () => {
  try {
    const response = await axios.get(`${url}/niveau`);
    niveau.value = response.data.data || response.data;
  } catch (error) {
    console.error('Error fetching niveaux:', error);
  }
};

const getFacultes = async () => {
  try {
    const response = await axios.get(`${url}/get-all-faculte`);
    faculte_niv.value = response.data.data || response.data;
    facultePaginate.value = response.data;
  } catch (error) {
    console.error('Error fetching facultes:', error);
  }
};

const actionOnRadionButton = async (event) => {
  formNiveau.value.faculte_id = '';
  formNiveau.value.nom_classe = '';
  console.log(event);
  
  try {
    const response = await axios.get(`${url}/niveau-with-class/${event.target.value}`);
    choseNiveau.value = response.data.niveau;
    annee_niveau_detude_classique.value = response.data.annee;
    faculte.value = response.data.facultes;
    anneeFac_forPayment.value = response.data.classe_actuelle;

    if (paymentFormParams.value.id === '') {
      paymentFormParams.value.faculte_id = '';
      paymentFormParams.value.classe = '';
      paymentFormParams.value.devise = '';
      paymentFormParams.value.montant = '';
    }

    niveauUniver.value = response.data.niveau.name === 'Universitaire';
  } catch (error) {
    console.error(error);
  }
};

const actionFillRadionNiveauButton = async () => {
  try {
    const response = await axios.get(`${url}/niveau`);
    niveau_et.value = response.data.data;
  } catch (error) {
    console.error(error);
  }
};

const actionFillMenuButton = async (niveau) => {
  try {
    const response = await axios.get(`${url}/niveau-with-class/${niveau}`);
    anneeFac_forPayment.value = response.data.classe_actuelle;
  } catch (error) {
    console.error(error);
  }
};

// FACULTE CRUD
const facModalShow = () => {
  faculte_profession.value = true;
};

const facModalClose = () => {
  faculte_profession.value = false;
  changeButton.value = false;
  form.value = { id: '', nom: '', nb_annee: '', errors: {} };
};

const submitFac = async () => {
  try {
    const response = await axios.post(`${url}/post-faculte`, form.value);
    
    if (response.status === 200) {
      showSwalSuccess('Faculté ajoutée avec succès');
      await getFacultes();
      facModalClose();
    }
  } catch (error) {
    // console.log(error.response);
    
    if (error.response?.data?.errors) {
      form.value.errors = error.response.data.errors;
    }
    showSwalError('Erreur lors de l\'ajout de la faculté');
  }
};

// YEAR CRUD
const yearModalShow = () => {
  anneeAcademique.value = true;
};

const yearModalClose = () => {
  anneeAcademique.value = false;
  changeButton.value = false;
  formyear.value = { id: '', date_debut: '', date_fin: '', niveau_detude: '', errors: {} };
};

const submitYear = async () => {
  try {
    const response = await axios.post(`${url}/anneeAcademique`, formyear.value);
    
    if (response.status === 200) {
      showSwalSuccess('Année académique ajoutée avec succès');
      await getYear();
      yearModalClose();
    }
  } catch (error) {
    console.log(error.response);
    if (error.response?.data?.errors) {
      formyear.value.errors = error.response.data.errors;
    }
    showSwalError('Erreur lors de l\'ajout de l\'année');
  }
};

const getYear = async () => {
  try {
    const response = await axios.get(`${url}/anneeAcademique`);
    if (response.status === 200) {
      anneeAcademiquePaginate.value = response.data;
      annee_paginate.value = response.data;
    }
  } catch (error) {
    console.error(error);
  }
};

// NIVEAU/CLASSE CRUD
const niveauModalShow = () => {
  actionFillRadionNiveauButton();
  niveau_detude_modal_classe.value = true;
};

const niveauModalClose = () => {
  niveau_detude_modal_classe.value = false;
  choseNiveau.value = '';
  changeButton.value = false;
  formNiveau.value = { id: '', niveau_id: '', faculte_id: '', nom_classe: '', errors: {} };
};

const submitNiveau = async () => {
  try {
    const response = await axios.post(`${url}/classes`, formNiveau.value);
    
    if (response.status === 200) {
      showSwalSuccess('Classe ajoutée avec succès');
      await getClasses();
      niveauModalClose();
    }
  } catch (error) {
    console.log(error.response);
    
    if (error.response?.data?.errors) {
      formNiveau.value.errors = error.response.data.errors;
    }
    showSwalError('Erreur lors de l\'ajout de la classe');
  }
};

const getClasses = async (page = 1) => {
  try {
    const response = await axios.get(`${url}/classes`, { params: { page: page } });
    if (response.status === 200) {
      classeParams.value = response.data;
    } 
    
  } catch (error) {
    console.error(error);
  }
};

// FRAIS D'INSCRIPTION
const fraisModalShow = () => {
  frais.value = true;
};

const fraisModalClose = () => {
  frais.value = false;
  changeButton.value = false;
  formFrais.value = { id: '', niveau_id: '', prix: '', anneeAc: '', errors: {} };
};

const storeFraisDinscription = async () => {
  try {
    const response = await axios.post(`${url}/fraisDinscription`, formFrais.value);
    
    if (response.status === 200) {
      showSwalSuccess('Frais d\'inscription ajoutés avec succès');
      await getFraisDinscription();
      fraisModalClose();
    }
  } catch (error) {
    console.log(error.response);
    
    if (error.response?.data?.errors) {
      formFrais.value.errors = error.response.data.errors;
    }
    showSwalError('Erreur lors de l\'ajout des frais');
  }
};

const getFraisDinscription = async () => {
  try {
    const response = await axios.get(`${url}/fraisDinscription`);
    if (response.status === 200) {
      frais_paginate.value = response.data.data;
    }
  } catch (error) {
    console.error(error);
  }
};

const editFrais = (fraisData) => {
  formFrais.value.id = fraisData.id;
  formFrais.value.niveau_id = fraisData.niveau_id;
  formFrais.value.prix = fraisData.prix;
  formFrais.value.anneeAc = fraisData.anneeAc;
  changeButton.value = true;
  fraisModalShow();
};

// EXAM PARAMS
const examParamsModalShow = () => {
  exam_params.value = true;
};

const examParamsModalClose = () => {
  formExamParam.value = { id: '', niveau_id: '', annee_academique_id: '', evaluation_par: '', errors: {} };
  exam_params.value = false;
  changeButton.value = false;
};

const getParamForExam = async (page=1) => {
  try {
    const response = await axios.get(`${url}/paramsExam`, { params: { page:page } });
    if (response.status === 200) {
      examPaginate.value = response.data;
    }
  } catch (error) {
    console.error(error);
  }
};

const submitParamForExam = async () => {
  try {
    const response = await axios.post(`${url}/paramsExam`, formExamParam.value);
    
    if (response.status === 200) {
      showSwalSuccess('Paramètres d\'examen ajoutés avec succès');
      await getParamForExam();
      examParamsModalClose();
    }
  } catch (error) {
    if (error.response?.data?.errors) {
      formExamParam.value.errors = error.response.data.errors;
    }
    showSwalError('Erreur lors de l\'ajout des paramètres');
  }
};

// PAYMENT PARAMS
const paymentParamsModalShow = () => {
  actionFillRadionNiveauButton();
  Payment_params_show.value = true;
};

const paymentParamsModalClose = () => {
  Payment_params_show.value = false;
  changeButton.value = false;
  paymentFormParams.value = {
    id: '',
    niveau_id: '',
    faculte_id: '',
    classe: '',
    echeance: '',
    devise: '',
    anneeAcademique: '',
    nb_echeance: '',
    montant: '',
    montant_par: {},
    accessoires: [],
    errors: {}
  };
  accessoires.value = [{ type_daccessoire: '', prix: '' }];
};

const submitPaymentParams = async () => {
  paymentFormParams.value.accessoires = accessoires.value;
  
  try {
    const response = await axios.post(`${url}/parametrePaiement`, paymentFormParams.value);
    
    if (response.status === 200) {
      showSwalSuccess('Paramètres de paiement ajoutés avec succès');
      await getPaymentParams();
      paymentParamsModalClose();
    }
  } catch (error) {
    if (error.response?.data) {
      paymentFormParams.value.errors = error.response.data;
    }
    showSwalError('Erreur lors de l\'ajout des paramètres');
  }
};

const getPaymentParams = async (page=1) => {
  try {
    const response = await axios.get(`${url}/parametrePaiement`, { params: { page:page } });
    if (response.status === 200) { 
      
      paimentParams.value = response.data;
    }
  } catch (error) {
    console.error(error);
  }
};

const GenereVersementInput = (e) => {
  editMontantPar.value = false;
  nbControleOrVersementOrtrimestre.value = Array.from(
    { length: parseInt(e.target.value, 10) || 0 },
    () => ''
  );
  paymentFormParams.value.montant_par = {};
};

const changeEcheance = (e) => {
  echeance.value = e.target.value;
  editMontantPar.value = false;
  paymentFormParams.value.montant_par = {};
  paymentFormParams.value.nb_echeance = '';
  nbControleOrVersementOrtrimestre.value = [];
};

// ACCESSOIRES
const addAccessoire = () => {
  accessoires.value.push({ type_daccessoire: '', prix: '' });
};

const removeAccessoire = (index) => {
  accessoires.value.splice(index, 1);
};

// ACTIONS ON ROWS
const actionsOnClasse = async (event) => {
  const classeId = event.target.closest('td').dataset.set;
  const id = event.target.id;

  switch (id) {
    case 'delete_classe':
      // Implement delete
      break;

    case 'edit_classe':
      try {
        const response = await axios.get(`${url}/classes/${classeId}`);
        formNiveau.value.niveau_id = response.data.data.niveau_id;
        formNiveau.value.id = response.data.data.id;
        formNiveau.value.nom_classe = response.data.data.nom_classe;
        changeButton.value = true;
        niveauModalShow();
      } catch (error) {
        console.error(error);
      }
      break;

    case 'delete_year':
      // Implement delete
      break;

    case 'edit_year':
      try {
        const response = await axios.get(`${url}/anneeAcademique/${classeId}`);
        formyear.value.id = response.data.data.id;
        formyear.value.date_debut = response.data.data.date_debut;
        formyear.value.date_fin = response.data.data.date_fin;
        formyear.value.niveau_detude = response.data.data.niveau_detude;
        changeButton.value = true;
        yearModalShow();
      } catch (error) {
        console.error(error);
      }
      break;

    case 'delete_paiement':
      // Implement delete
      break;

    case 'edit_paiement':
      try {
        const response = await axios.get(`${url}/parametrePaiement/${classeId}`);
        const data = response.data?.data;
        console.log(data);
        
        paymentFormParams.value.id = data.id;
        paymentFormParams.value.niveau_id = data.niveau_id;
        await actionFillMenuButton(data.niveau_id);

        paymentFormParams.value.faculte_id = data.faculte_id;
        paymentFormParams.value.classe = data.classe;
        paymentFormParams.value.echeance = data.echeance;
        echeance.value = data.echeance;
        paymentFormParams.value.devise = data.devise;
        paymentFormParams.value.anneeAcademique = data.anneeAcademique;
        paymentFormParams.value.nb_echeance = data.nb_echeance;
        paymentFormParams.value.montant = data.montant;
        paymentFormParams.value.montant_par = data.montant_par;

        if (data.montant_par && echeance.value === 'Versement') {
          try {
            const montant_par = data.montant_par;
            if (montant_par.Versement) {
              versementEntriesForm.value = Object.entries(montant_par.Versement);
              editMontantPar.value = true;
              paymentFormParams.value.montant_par = {};
              for (const [key, value] of versementEntriesForm.value) {
                paymentFormParams.value.montant_par[key] = value;
              }
            }
          } catch (error) {
            console.error('Erreur lors du parsing de montant_par:', error);
          }
        }

        changeButton.value = true;
        paymentParamsModalShow();
      } catch (error) {
        console.error(error);
      }
      break;

    case 'delete_exam':
      // Implement delete
      break;

    case 'edit_exam':
      try {
        const response = await axios.get(`${url}/paramsExam/${classeId}`);
        if (response.status === 200) {
          formExamParam.value.id = response.data.data.id;
          formExamParam.value.niveau_id = response.data.data.niveau_id;
          formExamParam.value.annee_academique_id = response.data.data.annee_academique_id;
          formExamParam.value.evaluation_par = response.data.data.evaluation_par;
          changeButton.value = true;
          examParamsModalShow();
        }
      } catch (error) {
        console.error(error);
      }
      break;

    default:
      break;
  }
};



const goToPage = async (page, urlSearch, receiveData) => { 
  // receiveData.value.loading = true;  
  try { 
    const response = await axios.get(urlSearch, { 
      params: { page: page } 
    }); 
      receiveData.value =  response.data.data
 
    console.log(`Navigation vers la page ${page} réussie urlSearch ${urlSearch} `);
    console.log(classeParams.value);
    
    // localStorage.setItem('currentPage', page);

  } catch (error) {
    console.error('Error fetching page:', error);
  } finally {
    // receiveData.value.loading = false;
  }
};

const changePageForFac = (link) => {
  if (link.url) {
    const urlParams = new URLSearchParams(link.url.split('?')[1]);
    const page = urlParams.has('page') ? parseInt(urlParams.get('page')) : 1;
    goToPage(page, `${url}/faculte-paginate-search`, facultePaginate);
  }
};

const changePageForYear = (link) => {
  if (link.url) {
    const urlParams = new URLSearchParams(link.url.split('?')[1]);
    const page = urlParams.has('page') ? parseInt(urlParams.get('page')) : 1;
    goToPage(page, `${url}/anneeAcademique`, annee_paginate);
  }
};

// SWAL HELPERS
const showSwalSuccess = (text) => {
  Swal.fire({
    position: 'top-end',
    text: text,
    showConfirmButton: false,
    timer: 2000,
    color: '#34a853',
  });
};

const showSwalError = (text) => {
  Swal.fire({
    position: 'top-end',
    text: text,
    showConfirmButton: false,
    timer: 2000,
    color: '#e94335',
  });
};
const gradeModalClose = ()=>{
  console.log('');
  
}
</script>

<template> 
    <div class="pb-10 animate-[fadeUp_0.4s_ease_both]">
      <div class="max-w-7xl px-4 mx-auto sm:px-6 lg:px-8 pt-4">
        
        <!-- ===================================== -->
        <!-- MODAL: Grade/Niveau -->
        <!-- ===================================== -->
        <StyleModal :show="grade_etude" @close="gradeModalClose">
          <template #title>
            <h5 class="text-slate-500 text-lg">Niveau</h5>
            <button type="button" class="btn-close" @click="gradeModalClose"></button>
          </template>
          <template #content>
            <form @submit.prevent="submitgrade">
              <div class="modal-body">
                <div class="mb-2">
                  <InputLabel for="name" value="Nom du Niveau" />
                  <TextInput 
                    id="name" 
                    v-model="formgrade.name" 
                    type="text" 
                    class="" 
                    autofocus
                    placeholder="Exp: Primaire" 
                  />
                  <InputError class="mt-2" :message="formgrade.errors.name" />
                </div>
              </div>
              <div class="mt-4 gap-4 flex justify-end">
                <DangerButton type="button" @click="gradeModalClose">Close</DangerButton>
                <PrimaryButton type="submit">
                  <span v-if="changeButton">Modifier</span>
                  <span v-else>Enregistrer</span>
                </PrimaryButton>
              </div>
            </form>
          </template>
        </StyleModal>

        <!-- ===================================== -->
        <!-- MODAL: Faculté/Profession -->
        <!-- ===================================== -->
        <StyleModal :show="faculte_profession" @close="facModalClose">
          <template #title>
            <h5 class="text-slate-500 text-lg">Facultés / Profession</h5>
            <button type="button" class="btn-close" @click="facModalClose"></button>
          </template>
          <template #content>
            <form @submit.prevent="submitFac">
              <div class="modal-body">
                <div class="mb-2">
                  <InputLabel for="nom" value="Domaine d'étude" />
                  <TextInput id="nom" v-model="form.nom" type="text" class="" autofocus />
                  <InputError class="mt-2" :message="form.errors.nom" />
                </div>
                <div>
                  <InputLabel for="nb_annee" value="Nbre de sessions" />
                  <TextInput id="nb_annee" v-model="form.nb_annee" type="text" class="" />
                  <InputError class="mt-2" :message="form.errors.nb_annee" />
                </div>
              </div>
              <div class="mt-4 gap-4 flex justify-end">
                <DangerButton type="button" @click="facModalClose">Close</DangerButton>
                <PrimaryButton type="submit">
                  <span v-if="changeButton">Modifier</span>
                  <span v-else>Enregistrer</span>
                </PrimaryButton>
              </div>
            </form>
          </template>
        </StyleModal>

        <!-- ===================================== -->
        <!-- MODAL: Année Académique -->
        <!-- ===================================== -->
        <StyleModal :show="anneeAcademique" @close="yearModalClose">
          <template #title>
            <h5 class="text-slate-500 text-lg">Année Académique</h5>
            <button type="button" class="btn-close" @click="yearModalClose"></button>
          </template>
          <template #content>
            <form @submit.prevent="submitYear">
              <div class="modal-body">
                <div>
                  <InputLabel for="date_debut" value="Début" />
                  <TextInput 
                    id="date_debut" 
                    v-model="formyear.date_debut" 
                    type="date" 
                    class="" 
                    autofocus 
                  />
                  <InputError class="mt-2" :message="formyear.errors.date_debut" />
                </div>

                <div class="my-2">
                  <InputLabel for="date_fin" value="Fin" />
                  <TextInput 
                    id="date_fin" 
                    v-model="formyear.date_fin" 
                    type="date" 
                    class="" 
                  />
                  <InputError class="mt-2" :message="formyear.errors.date_fin" />
                </div>

                     <div>
                  <InputLabel for="status" value="Status" />
                  <select class="select" v-model="formyear.status" id="status"> 
                    <option disabled="true">Status</option>
                    <option value="1">Actif</option>
                    <option value="1">Inactif</option>
                  </select>
                  <InputError class="mt-2" :message="formyear.errors.status" />
                </div>
              </div>

                <!-- <div>
                  <InputLabel for="niveau_detude" value="Cycle" />
                  <select class="select" v-model="formyear.niveau_detude" id="niveau_detude">
                    <option value="" disabled>Choisir un Cycle</option>
                    <option v-for="niv in niveau" :key="niv.id" :value="niv.name">
                      {{ niv.name }}
                    </option>
                  </select>
                  <InputError class="mt-2" :message="formyear.errors.niveau_detude" />
                </div>
              </div> -->
              <div class="mt-4 gap-4 flex justify-end">
                <DangerButton type="button" @click="yearModalClose">Close</DangerButton>
                <PrimaryButton type="submit">
                  <span v-if="changeButton">Modifier</span>
                  <span v-else>Enregistrer</span>
                </PrimaryButton>
              </div>
            </form>
          </template>
        </StyleModal>

        <!-- ===================================== -->
        <!-- MODAL: Classe -->
        <!-- ===================================== -->
        <StyleModal :show="niveau_detude_modal_classe" @close="niveauModalClose">
          <template #title>
            <h5 class="text-slate-500 text-lg">Classe</h5>
            <button type="button" class="btn-close" @click="niveauModalClose"></button>
          </template>
          <template #content>
            <form @submit.prevent="submitNiveau">
              <div class="modal-body">
                <div class="mb-2">
                  <InputLabel for="Niveau" value="Cycle" />
                  <select
                    class="select"
                    id="Niveau"
                    v-model="formNiveau.niveau_id"
                    @change="actionOnRadionButton($event)"
                  >
                    <option value="" disabled selected>Cycle</option>
                    <option v-for="niv in niveau" :value="niv.id" :key="niv.id">
                      {{ niv.name }}
                    </option>
                  </select>
                </div>

                <div v-if="choseNiveau && choseNiveau.name == 'Universitaire'">
                  <InputLabel for="faculte_id" value="Domaine d'étude" />
                  <select class="select" v-model="formNiveau.faculte_id">
                    <option value="" disabled selected>Domaine d'étude</option>
                    <option v-for="fac in faculte" :key="fac.id" :value="fac.id">
                      {{ fac.nom }}
                    </option>
                  </select>
                </div>

                <div class="my-2">
                  <InputLabel for="nom_classe" value="Classe" />
                  <TextInput 
                    id="nom_classe" 
                    v-model="formNiveau.nom_classe" 
                    type="text" 
                    class="" 
                  />
                  <InputError class="mt-2" :message="formNiveau.errors.nom_classe" />
                </div>
              </div>
              <div class="mt-4 gap-4 flex justify-end">
                <DangerButton type="button" @click="niveauModalClose">Close</DangerButton>
                <PrimaryButton type="submit">
                  <span v-if="changeButton">Modifier</span>
                  <span v-else>Enregistrer</span>
                </PrimaryButton>
              </div>
            </form>
          </template>
        </StyleModal>

        <!-- ===================================== -->
        <!-- MODAL: Frais d'inscription -->
        <!-- ===================================== -->
        <StyleModal :show="frais" @close="fraisModalClose">
          <template #title>
            <h5 class="text-slate-500 text-lg">Frais d'inscription</h5>
            <button type="button" class="btn-close" @click="fraisModalClose"></button>
          </template>
          <template #content>
            <form @submit.prevent="storeFraisDinscription">
              <div>
                <InputLabel for="niveau_id" value="Cycle" />
                <select class="select" v-model="formFrais.niveau_id" id="niveau_id">
                  <option value="" disabled>Choisir un Cycle</option>
                  <option v-for="niv in niveau" :key="niv.id" :value="niv.id">
                    {{ niv.name }}
                  </option>
                </select>
                <InputError class="mt-2" :message="formFrais.errors.niveau_id" />
              </div>

              <div class="my-2">
                <InputLabel for="anneea_academique" value="Année Academique" />
                <select class="select" v-model="formFrais.anneeAc" id="anneea_academique">
                  <option value="" disabled>Choisir l'année académique</option>
                  <option 
                    v-for="AnneeAcademique in anneeAcademiquePaginate.data" 
                    :key="AnneeAcademique.id"
                    :value="AnneeAcademique.id"
                  >
                    {{ AnneeAcademique.annee_academique }}
                  </option>
                </select>
                <InputError class="mt-2" :message="formFrais.errors.anneeAc" />
              </div>

              <div>
                <InputLabel for="Prix" value="Prix" />
                <TextInput id="Prix" v-model="formFrais.prix" type="text" class="" autofocus />
                <InputError class="mt-2" :message="formFrais.errors.prix" />
              </div>

              <div class="mt-4 gap-4 flex justify-end">
                <DangerButton type="button" @click="fraisModalClose">Close</DangerButton>
                <PrimaryButton type="submit">
                  <span v-if="changeButton">Modifier</span>
                  <span v-else>Enregistrer</span>
                </PrimaryButton>
              </div>
            </form>
          </template>
        </StyleModal>

        <!-- ===================================== -->
        <!-- MODAL: Paramètres des Examens -->
        <!-- ===================================== -->
        <StyleModal :show="exam_params" @close="examParamsModalClose">
          <template #title>
            <h5 class="text-slate-500 text-lg">Paramètres des Examens</h5>
            <button type="button" class="btn-close" @click="examParamsModalClose"></button>
          </template>
          <template #content>
            <form @submit.prevent="submitParamForExam">
              <div class="modal-body">
                <div>
                  <InputLabel for="evaluation" value="Evaluation / Examen par" />
                  <select class="select" v-model="formExamParam.evaluation_par" id="evaluation">
                    <option value="" disabled>Méthode d'evaluation</option>
                    <option value="mois">Mois</option>
                    <option value="session">Session</option>
                    <option value="semestre">Semestre</option>
                    <option value="Trimestre">Trimestre</option>
                    <option value="Controle">Contrôle</option>
                  </select>
                  <InputError class="mt-2" :message="formExamParam.errors.evaluation_par" />
                </div>

                <div class="my-4">
                  <InputLabel for="anneea_academique" value="Année Academique" />
                  <select 
                    class="select" 
                    v-model="formExamParam.annee_academique_id" 
                    id="anneea_academique"
                  >
                    <option value="" disabled>Choisir l'année académique</option>
                    <option 
                      v-for="AnneeAcademique in anneeAcademiquePaginate.data" 
                      :key="AnneeAcademique.id"
                      :value="AnneeAcademique.id"
                    >
                      {{ AnneeAcademique.annee_academique }}
                    </option>
                  </select>
                  <InputError class="mt-2" :message="formExamParam.errors.annee_academique_id" />
                </div>

                <div>
                  <InputLabel for="niveau_id" value="Cycle" />
                  <select class="select" v-model="formExamParam.niveau_id" id="niveau_id">
                    <option value="" disabled>Cycle</option>
                    <option v-for="niv in niveau" :key="niv.id" :value="niv.id">
                      {{ niv.name }}
                    </option>
                  </select>
                  <InputError class="mt-2" :message="formExamParam.errors.niveau_id" />
                </div>
              </div>

              <div class="mt-4 gap-4 flex justify-end">
                <DangerButton type="button" @click="examParamsModalClose">Close</DangerButton>
                <PrimaryButton type="submit">
                  <span v-if="changeButton">Modifier</span>
                  <span v-else>Enregistrer</span>
                </PrimaryButton>
              </div>
            </form>
          </template>
        </StyleModal>

        <!-- ===================================== -->
        <!-- MODAL: Paramètres des Paiements (GRAND MODAL) -->
        <!-- ===================================== -->
        <StyleModal :show="Payment_params_show" @close="paymentParamsModalClose">
          <template #title>
            <h5 class="modal-title text-center text-xl text-slate-500">
              Paramètres des paiements
            </h5>
            <button type="button" class="btn-close" @click="paymentParamsModalClose"></button>
          </template>
          <template #content>
            <p class="px-2 bg-slate-200" v-if="Object.keys(paymentFormParams.errors).length > 0">
              {{ paymentFormParams.errors }}
            </p>
            
            <form @submit.prevent="submitPaymentParams">
              <div class="modal-body">
                <!-- Cycle -->
                <div class="mb-4">
                  <InputLabel for="niveau" value="Cycle" />
                  <select 
                    @change="actionOnRadionButton($event)" 
                    v-model="paymentFormParams.niveau_id" 
                    class="select" 
                    id="niveau"
                  >
                    <option value="" disabled>Choisir un cycle</option>
                    <option v-for="niv in niveau" :key="niv.id" :value="niv.id">
                      {{ niv.name }}
                    </option>
                  </select>
                  <InputError class="mt-2" :message="paymentFormParams.errors.niveau_id" />
                </div>

                <!-- Faculté (si Universitaire) -->
                <div v-if="niveauUniver" class="mb-4">
                  <InputLabel for="faculte" value="Domaine d'étude" />
                  <select 
                    v-if="faculte.length > 0" 
                    v-model="paymentFormParams.faculte_id" 
                    class="select" 
                    id="faculte"
                  >
                    <option value="" disabled>Choisir une faculté</option>
                    <option v-for="fac in faculte" :key="fac.id" :value="fac.id">
                      {{ fac.nom }}
                    </option>
                  </select>
                  <InputError class="mt-2" :message="paymentFormParams.errors.faculte_id" />
                </div>

                <!-- Classe -->
                <div class="mb-4">
                  <InputLabel for="classe" value="Classe" />
                  <select class="select" id="classe" v-model="paymentFormParams.classe">
                    <option value="">Choisir une classe</option>
                    <option 
                      v-for="classe in getClassesByNiveau(paymentFormParams.niveau_id)"
                      :key="classe.id"
                      :value="classe.id"
                      :selected="paymentFormParams.classe == classe.id"
                    >
                      {{ classe.nom_classe }}
                    </option>
                  </select>
                  <InputError class="mt-2" :message="paymentFormParams.errors.classe" />
                </div>

                <!-- Année Académique -->
                <div class="mb-4">
                  <InputLabel for="anneea_academique" value="Année Academique" />
                  <select 
                    class="select" 
                    v-model="paymentFormParams.anneeAcademique" 
                    id="anneea_academique"
                  >
                    <option value="" disabled>Choisir l'année académique</option>
                    <option 
                      v-for="AnneeAcademique in anneeAcademiquePaginate.data" 
                      :key="AnneeAcademique.id"
                      :value="AnneeAcademique.id"
                    >
                      {{ AnneeAcademique.annee_academique }}
                    </option>
                  </select>
                  <InputError class="mt-2" :message="paymentFormParams.errors.anneeAcademique" />
                </div>

                <!-- Échéance & Nombre -->
                <div class="mb-4 flex justify-between gap-4">
                  <div class="w-full md:w-6/12">
                    <InputLabel for="echeance" value="Payer par:" />
                    <select 
                      class="select" 
                      v-model="paymentFormParams.echeance" 
                      @change="changeEcheance" 
                      id="echeance"
                    >
                      <option value="" disabled>Choisir</option>
                      <option value="mois">Mois</option>
                      <option value="Controle">Contrôle</option>
                      <option value="Trimestre">Trimestre</option>
                      <option value="Versement">Versement</option>
                      <option value="Session">Session</option>
                    </select>
                    <InputError class="mt-2" :message="paymentFormParams.errors.echeance" />
                  </div>

                  <div class="w-full md:w-6/12">
                    <InputLabel for="nb_echeance" :value="'Nbres de ' + echeance" />
                    <select 
                      @change="GenereVersementInput" 
                      :disabled="echeance === 'mois'" 
                      class="select w-full"
                      v-model="paymentFormParams.nb_echeance"
                      id="nb_echeance"
                    >
                      <option v-if="echeance == 'mois'" selected value="9">9 mois</option>
                      <option value="1">1</option>
                      <option value="2">2</option>
                      <option value="3">3</option>
                      <option value="4">4</option>
                      <option value="5">5</option>
                    </select>
                    <InputError class="mt-2" :message="paymentFormParams.errors.nb_echeance" />
                  </div>
                </div>

                <!-- Montants par Versement/Contrôle/Trimestre -->
                <div v-if="echeance !== 'mois'" class="mb-2">
                  <!-- Mode Edition -->
                  <div v-if="editMontantPar" class="flex flex-col md:flex-row gap-2">
                    <div 
                      v-for="(value, key, index) in paymentFormParams.montant_par" 
                      :key="index" 
                      class="flex-1"
                    >
                      <InputLabel 
                        :for="echeance + (index + 1)" 
                        :value="echeance + ' ' + (index + 1)" 
                      />
                      <TextInput 
                        :id="echeance + (index + 1)" 
                        type="text" 
                        v-model="paymentFormParams.montant_par[key]"
                        class="" 
                      />
                    </div>
                  </div>

                  <!-- Mode Création -->
                  <div v-else class="flex flex-col md:flex-row gap-2">
                    <div 
                      v-for="(nbControle, index) in nbControleOrVersementOrtrimestre" 
                      :key="index" 
                      class="flex-1"
                    >
                      <InputLabel 
                        :for="echeance + (index + 1)" 
                        :value="echeance + ' ' + (index + 1)" 
                      />
                      <TextInput 
                        :id="echeance + (index + 1)" 
                        type="text"
                        v-model="paymentFormParams.montant_par[`${echeance}_${index + 1}_${paymentFormParams.anneeAcademique}`]"
                        class="" 
                      />
                    </div>
                  </div>
                  <InputError class="mt-2" :message="paymentFormParams.errors.montant_par" />
                </div>

                <!-- ACCESSOIRES SECTION -->
                <div class="mb-2">
                  <h2 class="text-[17px]  mb-2">Ajouter des accessoires</h2>

                  <div 
                    v-for="(accessoire, index) in accessoires" 
                    :key="index"
                    class="mb-2 flex justify-between md:gap-4 items-center"
                  >
                    <div class="w-full">
                      <select v-model="accessoire.type_daccessoire" class="select">
                        <option value="" disabled>Type d'accessoire</option>
                        <option v-for="type in accessoireTypes" :key="type" :value="type">
                          {{ type }}
                        </option>
                      </select>
                      <span 
                        class="text-red-500 text-sm"
                        v-if="paymentFormParams.errors && paymentFormParams.errors[`accessoires.${index}.type_daccessoire`]"
                      >
                        {{ paymentFormParams.errors[`accessoires.${index}.type_daccessoire`] }}
                      </span>
                    </div>

                    <div class="w-full">
                      <input 
                        v-model="accessoire.prix" 
                        type="text" 
                        placeholder="Prix" 
                        class="input-normal" 
                      />
                      <span 
                        class="text-red-500 text-sm"
                        v-if="paymentFormParams.errors && paymentFormParams.errors[`accessoires.${index}.prix`]"
                      >
                        {{ paymentFormParams.errors[`accessoires.${index}.prix`] }}
                      </span>
                    </div>

                    <div>
                      <button 
                        type="button" 
                        @click="removeAccessoire(index)"
                        class="text-red-500 px-4 py-1 rounded hover:text-red-600"
                      >
                        Supprimer
                      </button>
                    </div>
                  </div>

                  <button 
                    type="button" 
                    @click="addAccessoire"
                    class="text-blue-500  px-4 py-1 rounded hover:text-blue-600"
                  >
                    <span class="inline-flex text-lg">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
                        <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
                      </svg>
                    </span>
                    Ajouter
                  </button>
                </div>

                <!-- Devise & Montant -->
                <div class="mb-4 w-full" :class="{ 'flex justify-between gap-4': echeance == 'mois' }">
                  <div class="w-full">
                    <InputLabel for="devise" value="Devise" />
                    <select class="select" id="devise" v-model="paymentFormParams.devise">
                      <option value="" disabled>Choisir</option>
                      <option value="GDES">GDES</option>
                      <option value="$HT">$HT</option>
                      <option value="USD">USD</option>
                    </select>
                    <InputError class="mt-2" :message="paymentFormParams.errors.devise" />
                  </div>

                  <div v-if="echeance == 'mois'" class="w-full">
                    <InputLabel for="montant" value="Montant" />
                    <TextInput 
                      id="montant" 
                      v-model="paymentFormParams.montant" 
                      type="text" 
                      class="" 
                    />
                    <InputError class="mt-2" :message="paymentFormParams.errors.montant" />
                  </div>
                </div>
              </div>

              <div class="flex justify-end gap-4">
                <DangerButton type="button" @click="paymentParamsModalClose">
                  Close
                </DangerButton>
                <PrimaryButton type="submit">
                  <span v-if="changeButton">Modifier</span>
                  <span v-else>Enregistrer</span>
                </PrimaryButton>
              </div>
            </form>
          </template>
        </StyleModal>

        <!-- ===================================== -->
        <!-- TABLES SECTION -->
        <!-- ===================================== -->
        <div class="row">
          <!-- Table: Exam Params -->
          <div class="col-sm-12 col-md-6 col-lg-6">
            <section class="mb-4">
              <div class="card border shadow-2 bg-white rounded-lg">
                <div class="card-header text-center py-0">
                  <PrimaryButton type="button" @click="examParamsModalShow" class="ms-3 mb-2">
                    Paramètres des Examens
                  </PrimaryButton>
                  <h5 class="mb-0 text-center text-lg text-slate-600">
                    <strong>Paramètres des Examens</strong>
                  </h5>
                </div>
                <div class="card-body p-0">
                  <div class="overflow-x-auto mt-2">
                    <table class="w-full text-sm text-center text-gray-500">
                      <thead class="text-md text-slate-100 uppercase bg-sky-300 px-2">
                        <tr>
                          <th class="py-1.5 fw-bold">Cycle</th>
                          <th class="py-1 fw-bold">Evaluation</th>
                          <th class="py-1 fw-bold">Année A.</th>
                          <th class="py-1 fw-bold">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-if="!examPaginate.data || examPaginate.data.length === 0"
                        >
                          <td colspan="4" class="py-4 text-gray-400">Aucun paramètre</td>
                        </tr>
                        <tr
                          v-else
                          :class="{ 'bg-slate-50': index % 2 == 1 }"
                          v-for="(exam_param, index) in examPaginate.data"
                          :key="exam_param.id"
                        >
                          <td class="text-sm td">{{ exam_param.niveau_name }}</td>
                          <td class="text-sm td">{{ exam_param.evaluation_par }}</td>
                          <td class="text-sm td">{{ exam_param.annee_academique }}</td>
                          <td class="text-sm td" :data-set="exam_param.id" @click="actionsOnClasse">
                            <i class="ri-delete-bin-6-line text-red-500 cursor-pointer" id="delete_exam"></i>
                            <i class="ri-edit-circle-fill text-yellow-500 cursor-pointer ms-3" id="edit_exam"></i>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                    <Pagination 
                      :meta="examPaginate.meta" 
                      @change-page="(page) => getExams(page)" 
                    />
                </div>
            
              </div>
            </section>
          </div>

          <!-- Table: Facultés -->
          <div class="col-sm-12 col-md-6 col-lg-6">
            <section class="mb-4">
              <div class="card border shadow-2 bg-white rounded-lg">
                <div class="card-header text-center py-0">
                  <PrimaryButton type="button" @click="facModalShow" class="ms-3 mb-2">
                    Ajouter une faculté
                  </PrimaryButton>
                  <h5 class="mb-0 text-center text-lg text-slate-600">
                    <strong>Faculté / Profession</strong>
                  </h5>
                </div>
                <div class="card-body p-0">
                  <div class="overflow-x-auto mt-2">
                    <table class="w-full text-sm text-center text-gray-500">
                      <thead class="text-md text-slate-100 uppercase bg-gray-600 px-2">
                        <tr>
                          <th class="py-1 fw-bold">Nom</th>
                          <th class="py-1 fw-bold">Nbre de sessions</th>
                          <th class="py-1 fw-bold">Status</th>
                          <th class="py-1 fw-bold">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-if="!facultePaginate.data || facultePaginate.data.length === 0"
                        >
                          <td colspan="4" class="py-4 text-gray-400">Aucune faculté</td>
                        </tr>
                        <tr
                          v-else
                          :class="{ 'bg-slate-50': index % 2 == 1 }"
                          v-for="(fetch_fac, index) in facultePaginate.data"
                          :key="fetch_fac.id"
                        >
                          <td class="text-sm td">{{ fetch_fac.nom }}</td>
                          <td class="text-sm td">{{ fetch_fac.nb_annee }}</td>
                          <td class="text-sm td">
                            <span class="text-green-500" v-if="fetch_fac.status == 1">Actif</span>
                            <span class="text-red-500" v-else>Inactif</span>
                          </td>
                          <td class="text-sm td">
                            <i class="ri-delete-bin-6-line text-red-500 cursor-pointer"></i>
                            <i class="ri-edit-circle-fill text-yellow-500 cursor-pointer ms-3"></i>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                <div
                  v-if="facultePaginate?.meta?.links"
                  class="mt-2 flex justify-end text-slate-500 px-2 pb-2"
                >
                  <span
                    style="cursor: pointer"
                    v-for="link in facultePaginate.meta.links"
                    :key="link.label"
                    @click="changePageForFac(link)"
                    v-html="link.label"
                    class="me-2"
                    :class="{
                      'text-slate-400 cursor-not-allowed': !link.url,
                      ' text-sky-500': link.active,
                    }"
                  />
                </div>
              </div>
            </section>
          </div>

          <!-- Table: Années Académiques -->
          <div class="col-sm-12 col-md-6 col-lg-6">
            <section class="mb-4">
              <div class="card border shadow-2 bg-white rounded-lg">
                <div class="card-header text-center py-0">
                  <PrimaryButton type="button" @click="yearModalShow" class="ms-3 mb-2">
                    Ajouter une Année
                  </PrimaryButton>
                  <h5 class="mb-0 text-center text-lg text-slate-600">
                    <strong>Année Académique</strong>
                  </h5>
                </div>
                <div class="card-body p-0">
                  <div class="overflow-x-auto mt-2">
                    <table class="w-full text-sm text-center text-gray-500">
                      <thead class="text-md text-slate-100 uppercase bg-sky-300 px-2">
                        <tr>
                          <th class="py-1.5 fw-bold">Début</th>
                          <th class="py-1 fw-bold">Fin</th>
                          <th class="py-1 fw-bold">A. Académique</th>
                          <th class="py-1 fw-bold">Status</th>
                          <th class="py-1 fw-bold">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-if="!annee_paginate.data || annee_paginate.data.length === 0"
                        >
                          <td colspan="5" class="py-4 text-gray-400">Aucune année</td>
                        </tr>
                        <tr
                          v-else
                          :class="{ 'bg-slate-50': index % 2 == 1 }"
                          v-for="(fetch_anne, index) in annee_paginate.data"
                          :key="fetch_anne.id"
                        >
                          <td class="text-sm td">{{ fetch_anne.date_debut }}</td>
                          <td class="text-sm td">{{ fetch_anne.date_fin }}</td>
                          <td class="text-sm td">{{ fetch_anne.annee_academique }}</td>
                          <td class="text-sm td">
                            <span class="text-green-500" v-if="fetch_anne.status == 1">Actif</span>
                            <span class="text-red-500" v-else>Inactif</span>
                          </td>
                          <td class="text-sm td" :data-set="fetch_anne.id" @click="actionsOnClasse">
                            <i class="ri-delete-bin-6-line text-red-500 cursor-pointer" id="delete_year"></i>
                            <i class="ri-edit-circle-fill text-yellow-500 cursor-pointer ms-3" id="edit_year"></i>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                <div
                  v-if="annee_paginate?.meta?.links"
                  class="mt-2 flex justify-end text-slate-500 px-2 pb-2"
                >
                  <span
                    style="cursor: pointer"
                    v-for="link in annee_paginate.meta.links"
                    :key="link.label"
                    @click="changePageForYear(link)"
                    v-html="link.label"
                    class="me-2"
                    :class="{
                      'text-slate-400 cursor-not-allowed': !link.url,
                      ' text-sky-500': link.active,
                    }"
                  />
                </div>
              </div>
            </section>
          </div>
        </div>

        <!-- Second Row -->
        <div class="row py-6">
          <!-- <p class="text-slate-500 bg-sky-300">{{ classeParams }}</p> -->
          <!-- Table: Classes -->
          <div class="col-sm-12 col-md-6 col-lg-6">
            <section class="mb-4">
              <div class="card border shadow-2 bg-white rounded-lg">
                <div class="card-header text-center py-0">
                  <PrimaryButton type="button" @click="niveauModalShow" class="ms-3 mb-2">
                    Ajouter une Classe
                  </PrimaryButton>
                  <h5 class="mb-0 text-center text-lg text-slate-600">
                    <strong>Classe</strong>
                  </h5>
                </div>
                <div class="card-body p-0">
                  <div class="overflow-x-auto mt-2">
                    <table class="w-full text-sm text-center text-gray-500">
                      <thead class="text-md text-slate-100 uppercase bg-sky-300 px-2">
                        <tr>
                          <th class="py-1.5 fw-bold">Cycle / Niveau</th>
                          <th class="py-1 fw-bold">Classe</th>
                          <th class="py-1 fw-bold">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-if="!classeParams.data || classeParams.data.length === 0"
                        >
                          <td colspan="3" class="py-4 text-gray-400">Aucune classe</td>
                        </tr>
                        <tr
                          v-else
                          :class="{ 'bg-slate-50': index % 2 == 1 }"
                          v-for="(niveau_detude, index) in classeParams.data"
                          :key="niveau_detude.id"
                        >
                          <td class="text-sm td">{{ niveau_detude.niveau }}</td>
                          <td class="text-sm td">{{ niveau_detude.nom_classe }}</td>
                          <td class="text-sm td" :data-set="niveau_detude.id" @click="actionsOnClasse">
                            <i class="ri-delete-bin-6-line text-red-500 cursor-pointer" id="delete_classe"></i>
                            <i class="ri-edit-circle-fill text-yellow-500 cursor-pointer ms-3" id="edit_classe"></i>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                <div
                  v-if="classeParams.meta"
                  class="mt-2 flex justify-end text-slate-500 px-2 pb-2"
                > 
                <Pagination
                    :meta="classeParams.meta" 
                    @change-page="getClasses" 
                  />

                </div>
              </div>
            </section>
          </div>

          <!-- Table: Payment Params -->
          <div class="col-sm-12 col-md-6 col-lg-6 py-6">
            <section class="mb-4">
              <div class="card border shadow-2 bg-white rounded-lg">
                <div class="card-header text-center py-0">
                  <PrimaryButton type="button" @click="paymentParamsModalShow" class="ms-3 mb-2">
                    Paramètres des paiements
                  </PrimaryButton>
                  <h5 class="mb-0 text-center text-lg text-slate-600">
                    <strong>Paramètres des paiements</strong>
                  </h5>
                </div>
                <div class="card-body p-0">
                  <div class="overflow-x-auto mt-2">
                    <table class="w-full text-sm text-center text-gray-500">
                      <thead class="text-md text-slate-100 uppercase bg-sky-300 px-2">
                        <tr>
                          <th class="py-1.5 fw-bold">Montant</th>
                          <th class="py-1 fw-bold">Cycle</th>
                          <th class="py-1 fw-bold">Classe</th>
                          <th class="py-1 fw-bold">Paiement par</th>
                          <th class="py-1 fw-bold">Année A.</th>
                          <th class="py-1 fw-bold">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-if="!paimentParams.data || paimentParams.data.length === 0"
                        >
                          <td colspan="6" class="py-4 text-gray-400">Aucun paramètre</td>
                        </tr>
                        <tr
                          v-else
                          :class="{ 'bg-slate-50': index % 2 == 1 }"
                          v-for="(payment_params, index) in paimentParams.data"
                          :key="payment_params.id"
                        >
                          <td class="text-sm td">
                            <span v-if="payment_params.echeance == 'mois'">
                              <span class="badge badge-secondary">{{ payment_params.devise }}</span>
                              {{ payment_params.montant }}
                            </span>
                            <span v-else class="badge bg-green-500 text-white">Autres</span>
                          </td>
                          <td class="text-sm td">{{ payment_params.niveau_name }}</td>
                          <td class="text-sm td">{{ payment_params.classe }}</td>
                          <td class="text-sm td">{{ payment_params.echeance }}</td>
                          <td class="text-sm td">{{ payment_params.anneeAc }}</td>
                          <td class="text-sm td" :data-set="payment_params.id" @click="actionsOnClasse">
                            <i class="ri-delete-bin-6-line text-red-500 cursor-pointer" id="delete_paiement"></i>
                            <i class="ri-edit-circle-fill text-yellow-500 cursor-pointer ms-3" id="edit_paiement"></i>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                <div
                  v-if="paimentParams.meta"
                  class="mt-2 flex justify-end text-slate-500 px-2 pb-2"
                > 
                <Pagination
                    :meta="paimentParams.meta" 
                    @change-page="getPaymentParams" 
                  />
              
                </div>
               
              </div>
            </section>
          </div>
        </div>

        <!-- Table: Frais d'inscription -->
        <div class="col-sm-12 col-md-6 col-lg-6">
          <section class="mb-4">
            <div class="card border shadow-2 bg-white rounded-lg">
              <div class="card-header text-center py-0">
                <PrimaryButton type="button" @click="fraisModalShow" class="ms-3 mb-2">
                  Ajouter frais
                </PrimaryButton>
                <h5 class="mb-0 text-center text-lg text-slate-600">
                  <strong>Frais d'inscription</strong>
                </h5>
              </div>
              <div class="card-body p-0">
                <div class="overflow-x-auto mt-2">
                  <table class="w-full text-sm text-center text-gray-500">
                    <thead class="text-md text-slate-100 uppercase bg-sky-300 px-2">
                      <tr>
                        <th class="py-1 fw-bold">Cycle</th>
                        <th class="py-1 fw-bold">Année A.</th>
                        <th class="py-1 fw-bold">Prix</th>
                        <th class="py-1 fw-bold">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                    
                      <tr 
                        :class="{ 'bg-slate-50': index % 2 == 1 }"
                        v-for="(fraisItem, index) in frais_paginate"
                        :key="fraisItem.id"
                      >
                        <td class="text-sm td">{{ fraisItem.niveau }}</td>
                        <td class="text-sm td">{{ fraisItem.annee_academique }}</td>
                        <td class="text-sm td">{{ fraisItem.prix }}</td>
                        <td class="text-sm td">
                          <i class="ri-delete-bin-6-line text-red-500 cursor-pointer"></i>
                          <i 
                            class="ri-edit-circle-fill text-yellow-500 cursor-pointer ms-3" 
                            @click="editFrais(fraisItem)"
                          ></i>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </section>
        </div>

      </div>
    </div>
  


</template>


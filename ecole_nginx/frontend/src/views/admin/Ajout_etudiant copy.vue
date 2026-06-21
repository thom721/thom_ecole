<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import Swal from 'sweetalert2'; 
import InputError from '@/components/InputError.vue';
import InputLabel from '@/components/InputLabel.vue';
import PrimaryButton from '@/components/PrimaryButton.vue';
import TextInput from '@/components/TextInput.vue'; 
import DialogModal from '@/components/DialogModal.vue';

const router = useRouter();
const route = useRoute();
const url = import.meta.env.VITE_APP_BASE_URL;

import { useSchoolStore,useSchoolStoreInfo } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';
const {classes_global,annee_global,niveau_global} =useSchoolStoreInfo()
 
const schoolStore = useSchoolStore();
const { niveau, professeur, annee,classes,faculte,cours, loading } = storeToRefs(schoolStore);
schoolStore.fetchAllDependencies();

const toast = ref({ show: false, msg: '', ok: true })
const notify = (msg, ok = true) => {
  toast.value = { show: true, msg, ok }
  setTimeout(() => (toast.value.show = false), 3000)
}
 

// Props simulés - à récupérer via API
const annee_academique = ref([]);
const niveau_et = ref([]);
const studentDetails = ref(null);
const studentData = ref([]);
const showPayment = ref(false);
const searchForDetails = ref(false);
 
const choseNiveau = ref({});
const fetch_actual_class = ref([]);
const activeEdit = ref(false);
const classe_actuelle_ = ref('');

// Refs pour le modal et accordéons
let openAccordionIndex = ref(null);
let openAccordionIndexPieces = ref(null);
let parcours_cours = ref([]);
let parcours_paiement = ref([]);
let parcours_notes = ref([]);
let searhStudent = ref('');

// Documents
const documentTypes = ref([
  'Attestation',
  'Certificat',
  'Certificat de naissance',
  'Carte d\'identité',
  'Diplôme',
  'Relevé de notes',
  'Photo d\'identité',
  'Autre',
]);

const documents = ref([
  {
    type_de_document: '',
    document_numero: '',
    document_date_dexpiration: '',
    document_status: '',
    document_image: '',
    etudiant_id: '',
  },
]);

// Form
const formEtudiant = ref({
  documentss: [],
  id: '',
  dernier_etablissement: '',
  nisu: '',
  aide_financiere: 'Aucune',
  nom: '',
  prenom: '',
  telephone: '',
  sexe: '',
  date_de_naissance: '',
  adresse: '',
  lieu_de_naissance: '',
  religion: '',
  niveau_id: '',
  classe_actuelle_id: '',
  annee_academique_id: '',
  faculte_id: '',
  email: '',
  
  // Responsable
  nom_responsable: '',
  prenom_responsable: '',
  email_responsable: '',
  relation_responsable: '',
  sexe_responsable: '',
  telephone_responsable: '',
  metier_responsable: '',
  adresse_responsable: '',
  
  errors: {}
});

// Computed
const studentDetailsShow = computed(() => {
  return route.params.etudiantId !== undefined;
});

// Methods
const showSwalInfo = (text, color) => {
  Swal.fire({
    position: "top-end",
    text: text,
    showConfirmButton: false,
    timer: 3000,
    color: color,
  });
};

const actionOnRadionButton = async () => {
  fetch_actual_class.value = [];
  formEtudiant.value.classe_actuelle_id = '';
  formEtudiant.value.faculte_id = '';

  try {
    const response = await axios.get(`${url}/niveau-with-class/${formEtudiant.value.niveau_id}`);

    if (response.status === 200) {
      choseNiveau.value = response.data.niveau;
      fetch_actual_class.value = response.data.classe_actuelle;
      faculte.value = response.data.facultes;
    }
  } catch (error) {
    console.error("Erreur lors de la récupération des données :", error);
  }
};

const addDocument = () => {
  documents.value.push({
    type_de_document: '',
    document_numero: '',
    document_date_dexpiration: '',
    document_status: '',
    document_image: '',
    etudiant_id: '',
  });
};

const removeDocument = (index) => {
  documents.value.splice(index, 1);
};

const handleFileChange = (event, index) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = () => {
      documents.value[index].document_image = reader.result;
    };
    reader.readAsDataURL(file);
  }
};

const submitEtudiant = async () => {
  formEtudiant.value.documentss = documents.value;
  formEtudiant.value.errors = {};
  
  try {
    const response = await axios.post(`${url}/etudiant`, formEtudiant.value
    // , {
    //   headers: {
    //     'Content-Type': 'multipart/form-data',
    //   },
    // }
  );

    if (response.data) {
      showSwalInfo(response.data.success, '#34a853');
      
      // Rediriger vers la liste ou recharger
      if (formEtudiant.value.id) {
        // Mode édition
        await fetchStudentDetails(formEtudiant.value.id);
      } else {
        // Mode création - rediriger vers la liste
        router.push('/students');
      }
    }
  } catch (error) {
    console.log(error.response?.data);
    if (error.response?.data?.detail) {
      showSwalInfo(error.response?.data?.detail,"red")
    }
    
    if (error.response?.data?.errors) {
      formEtudiant.value.errors = error.response.data.errors;
    }
    // console.error('Erreur lors du téléchargement des documents :', error);
  }
};

const toggleAccordionForParcours = async (index, classes_id, niveauId, annee_academique, studentId) => {
  const content = document.getElementById(`content_Par-${index}`);
  const icon = document.getElementById(`icon_Par-${index}`);

  const minusSVG = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
      <path d="M3.75 7.25a.75.75 0 0 0 0 1.5h8.5a.75.75 0 0 0 0-1.5h-8.5Z" />
    </svg>
  `;

  const plusSVG = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
      <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
    </svg>
  `;

  if (openAccordionIndex.value === index) {
    content.style.maxHeight = '0';
    icon.innerHTML = plusSVG;
    openAccordionIndex.value = null;
    return;
  }

  if (openAccordionIndex.value !== null) {
    const previousContent = document.getElementById(`content_Par-${openAccordionIndex.value}`);
    const previousIcon = document.getElementById(`icon_Par-${openAccordionIndex.value}`);
    if (previousContent) {
      previousContent.style.maxHeight = '0';
      previousIcon.innerHTML = plusSVG;
    }
  }

  content.style.maxHeight = content.scrollHeight + 'px';
  icon.innerHTML = minusSVG;
  openAccordionIndex.value = index;

  try {
    const response = await axios.get(`${url}/api/parcours-etudiant`, {
      params: {
        student_id: studentId,
        classes_id: classes_id,
        annee_academique_id: annee_academique,
        niveau_id: niveauId,
      },
    });

    if (response.status === 200) {
      parcours_cours.value = response.data.cours;
      parcours_paiement.value = response.data.notes;
      parcours_notes.value = response.data.paiements;
    }
  } catch (error) {
    console.error(error);
  }
};

const toggleAccordionForPieces = (index) => {
  const content = document.getElementById(`content-${index}`);
  const icon = document.getElementById(`icon-${index}`);

  const minusSVG = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
      <path d="M3.75 7.25a.75.75 0 0 0 0 1.5h8.5a.75.75 0 0 0 0-1.5h-8.5Z" />
    </svg>
  `;

  const plusSVG = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
      <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
    </svg>
  `;

  if (openAccordionIndexPieces.value === index) {
    content.style.maxHeight = '0';
    icon.innerHTML = plusSVG;
    openAccordionIndexPieces.value = null;
    return;
  }

  if (openAccordionIndexPieces.value !== null) {
    const previousContent = document.getElementById(`content-${openAccordionIndexPieces.value}`);
    const previousIcon = document.getElementById(`icon-${openAccordionIndexPieces.value}`);
    if (previousContent) {
      previousContent.style.maxHeight = '0';
      previousIcon.innerHTML = plusSVG;
    }
  }

  content.style.maxHeight = content.scrollHeight + 'px';
  icon.innerHTML = minusSVG;
  openAccordionIndexPieces.value = index;
};

const fetchStudent = async () => {
  const val = searhStudent.value;
  
  try {
    const response = await axios.post(`${url}/fetch-student-paiement`, { val });

    if (response.status === 200) {
      showPayment.value = true;
      studentData.value = response.data.data;
      searchForDetails.value = true;
    }
  } catch (error) {
    console.error(error);
  }
};

const searchForDetailsClose = () => {
  searchForDetails.value = false;
};

const showStudentDetails = async (studentId) => {
  try {
    const response = await axios.get(`${url}/student-details/${studentId}`);
    
    if (response.status === 200) {
      studentDetails.value = response.data.details;
    }
  } catch (error) {
    console.error(error);
  }
};
const toDateInput = (dateStr) => {
  if (!dateStr) return '' 
  return dateStr.split(' ')[0]
}
const fetchStudentDetails = async (studentId) => {
  try {
    const response = await axios.get(`${url}/etudiant/${studentId}`);
    
    if (response.status === 200) {
      const data = response.data.data; 
      // console.log(data);
      
      studentDetails.value = data;

      // Remplir le formulaire
      const dernierClasseEtudiant = data.classes_etudiant?.at(-1); 
      
      const dernierEtudiantFaculte = data.etudiant_facultes?.at(-1);

      formEtudiant.value = {
        id: data.id || '',
        dernier_etablissement: data.dernier_etablissement || '',
        nisu: data.nisu || '',
        aide_financiere: data.aide_financiere || 'Aucune',
        nom: data.nom || '',
        prenom: data.prenom || '',
        telephone: data.telephone || '',
        sexe: data.sexe || '',
        date_de_naissance: toDateInput(data.date_de_naissance) || '',
        adresse: data.adresse || '',
        lieu_de_naissance: data.lieu_de_naissance || '',
        religion: data.religion || '',
        niveau_id: dernierClasseEtudiant
          ? dernierClasseEtudiant.niveau_id
          : (dernierEtudiantFaculte ? dernierEtudiantFaculte.niveau_id : ''),
        classe_actuelle_id: dernierClasseEtudiant
          ? dernierClasseEtudiant.classes_id
          : (dernierEtudiantFaculte ? dernierEtudiantFaculte.classes_id : ''),
        annee_academique_id: dernierClasseEtudiant
          ? dernierClasseEtudiant.annee_academique_id
          : (dernierEtudiantFaculte ? dernierEtudiantFaculte.annee_academique_id : ''),
        faculte_id: dernierEtudiantFaculte ? dernierEtudiantFaculte.faculte_id : '',
        email: data.email || '',
        
        // Responsable
        nom_responsable: data.responsable?.nom_responsable || '',
        prenom_responsable: data.responsable?.prenom_responsable || '',
        email_responsable: data.responsable?.email_responsable || '',
        relation_responsable: data.responsable?.relation_responsable || '',
        sexe_responsable: data.responsable?.sexe_responsable || '',
        telephone_responsable: data.responsable?.telephone_responsable || '',
        metier_responsable: data.responsable?.metier_responsable || '',
        adresse_responsable: data.responsable?.adresse_responsable || '',
        
        errors: {}
      };

      classe_actuelle_.value = dernierClasseEtudiant
        ? dernierClasseEtudiant.classes?.nom_classe || ''
        : (dernierEtudiantFaculte
          ? dernierEtudiantFaculte.classes?.nom_classe || dernierEtudiantFaculte.classes_id
          : '');

      // Charger les classes pour le niveau
      if (formEtudiant.value.niveau_id) {
        getClassesByNiveau(formEtudiant.value.niveau_id);
      }
    }
  } catch (error) {
    console.error('Erreur lors du chargement des détails:', error);
  }
};

const fetchInitialData = async () => {
  try {
    console.log(route.params.etudiantId);
    
    // Charger les années académiques
    // const anneesResponse = await axios.get(`${url}/anneeAcademique`);
    // annee_academique.value = anneesResponse.data.data || anneesResponse.data;

    // // Charger les niveaux
    // const niveauxResponse = await axios.get(`${url}/niveau`);
    // niveau_et.value = niveauxResponse.data.data || niveauxResponse.data;

    // Si on a un ID dans l'URL, charger les détails de l'étudiant
    if (route.params.etudiantId) {
      await fetchStudentDetails(route.params.etudiantId);
    }
  } catch (error) {
    console.error('Erreur lors du chargement des données initiales:', error);
  }
};

// Lifecycle
onMounted(async () => {   
  await fetchInitialData()
  initializeTabs();
});

const initializeTabs = () => {
  // Code pour initialiser les tabs (simplifié)
  const tabs = document.querySelectorAll('[data-tab-target]');
  const tabContents = document.querySelectorAll('[role="tabpanel"]');
  
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => {
      // Cacher tous les contenus
      tabContents.forEach(content => {
        content.classList.add('hidden', 'opacity-0');
        content.classList.remove('block', 'opacity-100');
      });
      
      // Désactiver tous les tabs
      tabs.forEach(t => {
        t.setAttribute('aria-selected', 'false');
      });
      
      // Activer le tab cliqué
      tab.setAttribute('aria-selected', 'true');
      
      // Afficher le contenu correspondant
      const targetId = tab.getAttribute('aria-controls');
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.remove('hidden', 'opacity-0');
        targetContent.classList.add('block', 'opacity-100');
      }
    });
  });
};

 

const getClassesByNiveau = (niveauId) => {   
  if (!niveauId || !classes.value) return [];  
  return classes.value.filter(c => c.niveau_id === niveauId);
};

const navigateToStudentDetails = (studentId) => {
  router.push(`/students/${studentId}`);
  searchForDetailsClose();
};
</script>

<template> 
    <div class="max-w-7xl px-2 mx-auto sm:px-6 lg:px-8 pt-4 pb-14">
      <div class="w-full">
        <p 
          v-if="formEtudiant.errors && Object.keys(formEtudiant.errors).length > 0"
          class="p-2 mb-2 bg-red-100 text-red-500"
        >
          Veuillez bien vérifier le formulaire, certains champs ne sont pas corrects.
        </p>

        <div class="relative right-0">
          <!-- Tabs Navigation -->
          <ul 
            class="relative flex flex-col md:flex-row flex-wrap w-full px-2 list-none border-b bg-purple-100 z-0"
            data-tabs="tabs"
            role="list"
          >
            <li class="z-30 flex-auto text-center">
              <a 
                class="z-30 flex items-center justify-center w-full px-0 text-lg mb-0 transition-all ease-in-out border-0 bg-transparent border-t cursor-pointer text-slate-600"
                data-tab-target=""
                role="tab"
                aria-selected="true"
                aria-controls="inscription_parcours"
              >
                Inscription / Parcours
              </a>
            </li>

            <li class="z-30 flex-auto text-center">
              <a 
                class="z-30 flex items-center justify-center w-full px-0 mb-0 text-lg transition-all ease-in-out border-0 border-t bg-transparent cursor-pointer text-slate-600"
                data-tab-target=""
                role="tab"
                aria-selected="false"
                aria-controls="personnes_responsable"
              >
                Personnes Responsable
              </a>
            </li>

            <li class="z-30 flex-auto text-center">
              <a 
                class="z-30 flex items-center justify-center w-full px-0 py-1 text-lg mb-0 transition-all ease-in-out border-0 bg-transparent border-t cursor-pointer text-slate-700"
                data-tab-target=""
                role="tab"
                aria-selected="false"
                aria-controls="pieces_soumise"
              >
                Pieces Soumises
              </a>
            </li>

            <li v-if="studentDetailsShow" class="z-30 flex-auto text-center">
              <a 
                class="z-30 flex items-center justify-center w-full px-0 py-1 text-lg mb-0 transition-all ease-in-out border-0 rounded-b-lg border-t cursor-pointer text-slate-600 active:text-sky-500 focus:text-sky-500"
                data-tab-target=""
                role="tab"
                aria-selected="false"
                aria-controls="details"
              >
                Details
              </a>
            </li>
          </ul>

          <!-- Tabs Content -->
          <div data-tab-content="" class="p-2">
            <form @submit.prevent="submitEtudiant" enctype="multipart/form-data">
              
              <!-- TAB 1: Inscription/Parcours -->
              <div 
                class="transition-all duration-700 ease-in-out" 
                id="inscription_parcours" 
                role="tabpanel"
              >
                <div class="md:max-w-7xl md:mx-auto w-full sm:px-6 lg:px-8 transition-all duration-700 ease-in-out">
                  <!--  -->
                  <div class="flex flex-col md:flex-row md:gap-4">
                    <div class="mb-4 w-full">
                      <InputLabel for="niveau_id" value="Niveau / Section" />
                      <select 
                      
                        class="select" 
                        v-model="formEtudiant.niveau_id" 
                        id="niveau_id"
                        @change="actionOnRadionButton"
                      >
                        <option value="" disabled>Cycle</option>
                        <option 
                          v-for="niv in niveau_global" 
                          :key="niv.id"
                          :value="niv.id"
                        >
                          {{ niv.name }}
                        </option>
                      </select>
                      <InputError 
                        v-if="formEtudiant.errors" 
                        class="mt-2"
                        :message="formEtudiant.errors?.niveau_e" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="dernier_etablissement" value="Dernier établissement fréquenté" />
                      <TextInput 
                        id="dernier_etablissement" 
                        v-model="formEtudiant.dernier_etablissement" 
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.dernier_etablissement?.[0]" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="nisu" value="NISU" />
                      <TextInput 
                        id="nisu" 
                        v-model="formEtudiant.nisu" 
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.nisu?.[0]" 
                      />
                    </div>
                  </div>

                  <div class="flex flex-col md:flex-row md:gap-4">
                    <div class="pb-2 w-full">
                      <InputLabel for="nom" value="Nom" />
                      <TextInput 
                        id="nom" 
                        v-model="formEtudiant.nom" 
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.nom?.[0]" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="prenom" value="Prénom" />
                      <TextInput 
                        id="prenom" 
                        v-model="formEtudiant.prenom" 
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.prenom?.[0]" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="sexe" value="Sexe" />
                      <select class="select" v-model="formEtudiant.sexe" id="sexe">
                        <option value="" disabled>Sexe</option>
                        <option value="F">F</option>
                        <option value="M">M</option>
                      </select>
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.sexe?.[0]" 
                      />
                    </div>
                  </div>

                  <div class="flex flex-col md:flex-row md:gap-4">
                    <div class="pb-2 w-full">
                      <InputLabel for="date_de_naissance" value="Date de Naissance" />
                      <TextInput 
                        id="date_de_naissance" 
                        v-model="formEtudiant.date_de_naissance"
                        type="date" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.date_de_naissance?.[0]" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="lieu_de_naissance" value="Lieu de Naissance" />
                      <TextInput 
                        id="lieu_de_naissance" 
                        v-model="formEtudiant.lieu_de_naissance"
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.lieu_de_naissance?.[0]" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="religion" value="Religion" />
                      <TextInput 
                        id="religion" 
                        v-model="formEtudiant.religion" 
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.religion?.[0]" 
                      />
                    </div>
                  </div>

                  <div class="flex flex-col md:flex-row md:gap-6">
                    <div class="pb-2 w-full">
                      <InputLabel for="adresse" value="Adresse" />
                      <TextInput 
                        id="adresse" 
                        v-model="formEtudiant.adresse" 
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.adresse?.[0]" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="telephone" value="Téléphone" />
                      <TextInput 
                        id="telephone" 
                        v-model="formEtudiant.telephone" 
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.telephone?.[0]" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="email" value="Courriel" />
                      <TextInput 
                        id="email" 
                        v-model="formEtudiant.email" 
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.email?.[0]" 
                      />
                    </div>
                  </div>

                  <div class="flex flex-col md:flex-row md:gap-6">
                    <div class="pb-2 w-full">
                      <InputLabel for="annee_academique_id" value="Année Académique" />
                      <select 
                        class="select" 
                        v-model="formEtudiant.annee_academique_id"
                        id="annee_academique_id"
                      >
                        <option value="" disabled>Année Académique</option>
                        <option 
                          v-for="annee in annee_global" 
                          :key="annee.id" 
                          :value="annee.id"
                        >
                          {{ annee.annee_academique }}
                        </option>
                      </select>
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.annee_academique_id?.[0]" 
                      />
                    </div>

                    <div 
                      v-if="choseNiveau.name === 'Universitaire' || choseNiveau.name === 'Technique'" 
                      class="mb-4 w-full"
                    >
                      <InputLabel for="faculte_id" value="Domaine d'étude" />
                      <select 
                        class="select" 
                        v-model="formEtudiant.faculte_id" 
                        id="faculte_id"
                      >
                        <option value="" disabled>Faculté / Option</option>
                        <option 
                          v-for="fac in faculte" 
                          :key="fac.id"
                          :value="fac.id"
                        >
                          {{ fac.nom }}
                        </option>
                      </select>
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.faculte_id?.[0]" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="classe_actuelle_id" value="Classe" />
                      <select 
                        class="select" 
                        v-model="formEtudiant.classe_actuelle_id"
                        id="classe_actuelle_id"
                      >
                        <option value="" disabled>Classe</option>
                        <option 
                          v-for="classe in getClassesByNiveau(formEtudiant.niveau_id)"
                          :key="classe.id" 
                          :value="classe.id"
                        >
                          {{ classe.nom_classe }}
                        </option>
                      </select>
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.classe_actuelle_id?.[0]" 
                      />
                    </div>

                    <div class="mb-4 w-full">
                      <InputLabel for="aide_financiere" value="Aide financière" />
                      <select 
                        class="select" 
                        v-model="formEtudiant.aide_financiere" 
                        id="aide_financiere"
                      >
                        <option value="" disabled>Aide financière</option>
                        <option value="Aucune">Aucune</option>
                        <option value="1/4 Bourse">1/4 Bourse</option>
                        <option value="Démie Bourse">Démie Bourse</option>
                        <option value="Bourse">Bourse</option>
                      </select>
                      <InputError 
                        class="mt-2"
                        :message="formEtudiant.errors?.aide_financiere" 
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- TAB 2: Personnes Responsable -->
              <div class="hidden opacity-0" id="personnes_responsable" role="tabpanel">
                <div class="max-w-5xl mx-auto md:py-8 px-2 sm:px-6 lg:px-8 transition-all duration-700 ease-in-out">
                  <div class="flex flex-col md:flex-row md:gap-4">
                    <div class="pb-2 w-full">
                      <InputLabel for="nom_responsable" value="Nom" />
                      <TextInput 
                        id="nom_responsable" 
                        v-model="formEtudiant.nom_responsable"
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.nom_responsable" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="prenom_responsable" value="Prénom" />
                      <TextInput 
                        id="prenom_responsable" 
                        v-model="formEtudiant.prenom_responsable"
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.prenom_responsable" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="sexe_responsable" value="Sexe" />
                      <select 
                        class="select" 
                        v-model="formEtudiant.sexe_responsable"
                        id="sexe_responsable"
                      >
                        <option value="" disabled>Sexe</option>
                        <option value="F">F</option>
                        <option value="M">M</option>
                      </select>
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.sexe_responsable" 
                      />
                    </div>
                  </div>

                  <div class="flex flex-col md:flex-row md:gap-4">
                    <div class="pb-2 w-full">
                      <InputLabel for="adresse_responsable" value="Adresse" />
                      <TextInput 
                        id="adresse_responsable" 
                        v-model="formEtudiant.adresse_responsable"
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.adresse_responsable" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="telephone_responsable" value="Téléphone" />
                      <TextInput 
                        id="telephone_responsable"
                        v-model="formEtudiant.telephone_responsable" 
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.telephone_responsable" 
                      />
                    </div>

                    <div class="pb-2 w-full">
                      <InputLabel for="email_responsable" value="Courriel" />
                      <TextInput 
                        id="email_responsable" 
                        v-model="formEtudiant.email_responsable"
                        type="text" 
                        class=""
                      />
                      <InputError 
                        class="mt-2" 
                        :message="formEtudiant.errors?.email_responsable" 
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- TAB 3: Pieces Soumises -->
              <div 
                class="hidden opacity-0 transition-all duration-300 ease-in-out" 
                id="pieces_soumise"
                role="tabpanel"
              >
                <div class="max-w-7xl mx-auto px-2 md:py-8 sm:px-6 lg:px-8 transition-all duration-300 ease-in-out">
                  <div class="py-4 transition-all duration-300 ease-in-out">
                    <h2 class="text-lg  mb-4 text-gray-700">Ajouter des Documents</h2>

                    <div 
                      v-for="(document, index) in documents" 
                      :key="index"
                      class="mb-4 transition-all duration-300 ease-in-out"
                    >
                      <span 
                        class="text-red-500 text-sm block mb-2"
                        v-if="formEtudiant.errors && formEtudiant.errors[`documentss.${index}.type_de_document`]"
                      >
                        {{ formEtudiant.errors[`documentss.${index}.type_de_document`] }}
                      </span>

                      <div class="flex flex-col md:flex-row justify-between md:gap-4 items-center">
                        <div class="w-full mb-2">
                          <select 
                            v-model="document.type_de_document"
                            class="border rounded select"
                          >
                            <option value="" disabled>Type de document</option>
                            <option 
                              v-for="type in documentTypes" 
                              :key="type" 
                              :value="type"
                            >
                              {{ type }}
                            </option>
                          </select>
                        </div>

                        <div class="w-full mb-2">
                          <input 
                            v-model="document.document_numero" 
                            type="text"
                            placeholder="Numéro de document" 
                            class="input-normal" 
                          />
                        </div>

                        <div class="w-full mb-2">
                          <input 
                            v-model="document.document_date_dexpiration" 
                            type="date"
                            class="input-normal" 
                          />
                        </div>

                        <div class="w-full mb-2">
                          <label class="block border rounded-md">
                            <span class="sr-only">Choisir un fichier</span>
                            <input 
                              type="file" 
                              @change="handleFileChange($event, index)"
                              class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100 hover:cursor-pointer input-normal"
                            />
                          </label>
                        </div>

                        <div class="flex justify-end">
                          <button 
                            type="button" 
                            @click="removeDocument(index)"
                            class="text-red-500 px-4 py-1 rounded hover:text-red-600 transition-all duration-300 hover:border"
                          >
                            Supprimer
                          </button>
                        </div>
                      </div>
                    </div>

                    <button 
                      type="button" 
                      @click="addDocument"
                      class="text-blue-500  px-4 py-2 rounded text-lg hover:text-blue-600 transition-all duration-300 hover:border"
                    >
                      <span class="inline-flex text-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
                          <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
                        </svg>
                      </span>
                      Ajouter un Document
                    </button>
                  </div>

                  <div class="flex justify-end mt-2">
                    <PrimaryButton 
                      type="submit" 
                      class=""
                      :disabled="false"
                    >
                      <span v-if="studentDetails !== null">Modifier</span>
                      <span v-else>Enregistrer</span>
                    </PrimaryButton>
                  </div>
                </div>
              </div>
            </form>

            <!-- TAB 4: Details (si mode édition) -->
            <div 
              v-if="studentDetailsShow" 
              class="hidden opacity-0" 
              id="details" 
              role="tabpanel"
            >
              <div class="pb-4 flex justify-between w-full md:w-6/12">
                <div class="w-full">
                  <input 
                    type="text" 
                    class="input-normal border-sky-500"
                    placeholder="Identifiant de l'etudiant" 
                    v-model="searhStudent" 
                    @keyup="fetchStudent"
                    autofocus
                  >
                </div>
              </div>

              <div class="flex flex-col md:flex-row gap-24">
                <!-- Informations personnelles -->
                <div class="text-slate-500 w-full md:w-6/12">
                  <h1 class="text-sky-500 text-lg  text-center py-1 border-y border-sky-300 bg-sky-100">
                    Informations personnelles
                  </h1>
                  <div class="px-4" v-if="studentDetails">
                    <p class="py-1.5 flex justify-between">
                      Identifiant: 
                      <span class="">{{ studentDetails.identifiant }}</span>
                    </p>
                    <p class="py-1.5 flex justify-between">
                      Nom: 
                      <span class="">{{ studentDetails.nom }}</span>
                    </p>
                    <p class="py-1.5 flex justify-between">
                      Prénom: 
                      <span class="">{{ studentDetails.prenom }}</span>
                    </p>
                    <p class="py-1.5 flex justify-between">
                      Sexe: 
                      <span class="">{{ studentDetails.sexe }}</span>
                    </p>
                    <p class="py-1.5 flex justify-between">
                      Date de naissance: 
                      <span class="">{{ studentDetails.date_de_naissance }}</span>
                    </p>
                    <p class="py-1.5 flex justify-between">
                      Lieu de naissance: 
                      <span class="">{{ studentDetails.lieu_de_naissance }}</span>
                    </p>
                    <p class="py-1.5 flex justify-between">
                      Adresse: 
                      <span class="">{{ studentDetails.adresse }}</span>
                    </p>
                    <p class="py-1.5 flex justify-between">
                      Courriel: 
                      <span class="">{{ studentDetails.email }}</span>
                    </p>
                    <p class="py-1.5 flex justify-between">
                      Téléphone: 
                      <span class="">{{ studentDetails.telephone }}</span>
                    </p>
                    <p class="py-1.5 flex justify-between">
                      Classe actuelle: 
                      <span class="">{{ classe_actuelle_ }}</span>
                    </p>
                  </div>
                </div>

                <!-- Responsable & Pièces -->
                <div class="text-slate-500 w-full md:w-6/12 flex flex-col gap-4">
                  <!-- Responsable -->
                  <div>
                    <h1 class="text-yellow-500 text-lg  text-center py-1 border-y border-yellow-200 bg-yellow-100">
                      Informations sur le responsable
                    </h1>
                    <div class="px-4" v-if="studentDetails?.responsable">
                      <p class="py-1 flex justify-between">
                        Nom: 
                        <span class="">{{ studentDetails.responsable.nom_responsable }}</span>
                      </p>
                      <p class="py-1 flex justify-between">
                        Prénom: 
                        <span class="">{{ studentDetails.responsable.prenom_responsable }}</span>
                      </p>
                      <p class="py-1 flex justify-between">
                        Adresse: 
                        <span class="">{{ studentDetails.responsable.adresse_responsable }}</span>
                      </p>
                      <p class="py-1 flex justify-between">
                        Courriel: 
                        <span class="">{{ studentDetails.responsable.email_responsable }}</span>
                      </p>
                      <p class="py-1 flex justify-between">
                        Téléphone: 
                        <span class="">{{ studentDetails.responsable.telephone_responsable }}</span>
                      </p>
                    </div>
                  </div>

                  <!-- Pièces soumises -->
                  <div>
                    <h1 class="text-blue-500 text-lg  text-center py-1 border-y border-blue-300 bg-blue-100">
                      Pieces Soumises
                    </h1>
                    <div 
                      class="px-4 py-1"
                      v-if="studentDetails?.pieces_soumise"
                    >
                      <div 
                        v-for="(piece, index) in studentDetails.pieces_soumise" 
                        :key="piece.id"
                        class="w-full mt-2 gap-4"
                      >
                        <div class="items-start">
                          <p 
                            class="inline-flex rounded-md px-2 text-slate-500 text-lg items-center gap-2 hover:text-slate-600 cursor-pointer hover:bg-slate-200 py-1"
                            @click="toggleAccordionForPieces(1 + index)"
                          >
                            {{ piece.type_de_document }}
                            <span :id="'icon-' + (1 + index)" class="text-slate-800 ms-4">
                              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
                                <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
                              </svg>
                            </span>
                          </p>

                          <div 
                            :id="'content-' + (1 + index)"
                            class="max-h-0 overflow-hidden transition-all duration-300 ease-in-out ps-4"
                          >
                            <div class="grid grid-cols-3 items-center pb-1 border-b">
                              <div>
                                <a 
                                  :href="piece.document_image_url" 
                                  target="_blank"
                                  rel="noopener noreferrer"
                                >
                                  <img 
                                    :src="piece.document_image_url" 
                                    alt=""
                                    class="h-24 w-20 object-cover rounded-lg"
                                  >
                                </a>
                              </div>
                              <div class="col-span-2">
                                <p class="flex justify-between">
                                  Type: 
                                  <span class="">{{ piece.type_de_document }}</span>
                                </p>
                                <p class="flex justify-between">
                                  Nummero: 
                                  <span class="">{{ piece.document_numero }}</span>
                                </p>
                                <p class="flex justify-between">
                                  Expiration: 
                                  <span class="">{{ piece.document_date_dexpiration }}</span>
                                </p>
                                <p class="flex justify-between">
                                  Status: 
                                  <span class="">{{ piece.document_status }}</span>
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Parcours -->
              <div v-if="studentDetailsShow" class="pt-4">
                <h1 class="text-xl text-center  border-y border-green-300 py-1 bg-green-100 text-green-600">
                  Parcours
                </h1>

                <!-- Parcours Classique -->
                <div v-if="studentDetails?.classe_etudiant">
                  <div 
                    v-for="(parcours, index) in studentDetails.classe_etudiant"
                    :key="index"
                    class="w-full mt-2"
                  >
                    <p 
                      class="inline-flex rounded-md px-2 text-slate-500 text-lg items-center gap-2 hover:text-slate-600 cursor-pointer hover:bg-slate-200 my-1 py-1"
                      @click="toggleAccordionForParcours(1 + index, parcours.classes_id, parcours.niveau_id, parcours.annee_academique_id, studentDetails.id)"
                    >
                      {{ parcours.annee_academiques?.annee_academique }}
                      <span :id="'icon_Par-' + (1 + index)" class="text-slate-800 ms-4">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
                          <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
                        </svg>
                      </span>
                    </p>

                    <div 
                      :id="'content_Par-' + (1 + index)"
                      class="max-h-0 overflow-hidden transition-all duration-300 ease-in-out ps-4"
                    >
                      <div class="flex justify-between items-center px-8 mb-2 border-b">
                        <p class="text-slate-600 text-lg">{{ parcours.classes?.nom_classe }}</p>
                      </div>
                      
                      <div class="ms-2">
                        <div class="mt-4">
                          <p class="text-lg  text-slate-700">
                            🏫 Informations académiques
                          </p>
                        </div>
                        
                        <p class="py-1 ms-4">
                          Classes fréquentées 
                          <span class="ms-4">{{ parcours.classes?.nom_classe }}</span>
                        </p>

                        <div class="ms-4">
                          <p class="text-lg font-medium text-slate-700">- Cours suivis</p>
                          <div class="ms-4 grid grid-cols-2 md:grid-cols-5 gap-2 py-2">
                            <p 
                              class="text-md text-slate-700 underline underline-offset-2 text-nowrap" 
                              v-for="cours in parcours_cours" 
                              :key="cours.id"
                            >
                              {{ cours.cours_nom }}
                            </p>
                          </div>
                        </div>

                        <div class="ms-4">
                          <p class="text-lg font-medium text-slate-700">- Notes et moyennes</p>
                        </div>

                        <div class="mt-4">
                          <p class="text-lg  text-slate-700">📊 Suivi pédagogique</p>
                        </div>

                        <div class="mt-4">
                          <p class="text-lg  text-slate-700">💰 Suivi financier</p>
                        </div>

                        <div class="mt-4">
                          <p class="text-lg  text-slate-700">🧾 Vie scolaire</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Parcours Universitaire -->
                <div v-if="studentDetails?.etudiant_facultes">
                  <div 
                    v-for="(parcours, index) in studentDetails.etudiant_facultes"
                    :key="'fac-' + index"
                    class="w-full mt-2"
                  >
                    <p 
                      class="inline-flex rounded-md px-2 text-slate-500 text-lg items-center gap-2 hover:text-slate-600 cursor-pointer hover:bg-slate-200 my-1 py-1"
                      @click="toggleAccordionForParcours(100 + index, parcours.classes_id, parcours.niveau_id, parcours.annee_academique_id, studentDetails.id)"
                    >
                      {{ parcours.annee_academiques?.annee_academique }}
                      <span :id="'icon_Par-' + (100 + index)" class="text-slate-800 ms-4">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
                          <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
                        </svg>
                      </span>
                    </p>

                    <div 
                      :id="'content_Par-' + (100 + index)"
                      class="max-h-0 overflow-hidden transition-all duration-300 ease-in-out ps-4"
                    >
                      <div class="flex justify-between items-center px-8 mb-2 border-b">
                        <p class="text-slate-600 text-lg">{{ parcours.classes?.nom_classe }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Search -->
      <DialogModal :show="searchForDetails" @close="searchForDetailsClose">
        <template #title>
          <span 
            class="flex justify-end text-red-500 text-lg cursor-pointer" 
            @click="searchForDetailsClose"
          >
            <i class="ri-close-large-line"></i>X
          </span>
        </template>
        <template #content>
          <div class="p-4 flex w-full">
            <input 
              type="text" 
              class="input-normal flex justify-end"
              placeholder="Identifiant de l'etudiant" 
              v-model="searhStudent" 
              @keyup="fetchStudent" 
              autofocus
            >
          </div>
          <div v-if="showPayment">
            <table class="w-full text-center text-gray-500">
              <tr 
                v-for="studentD in studentData" 
                :key="studentD.id" 
                class="border-b py-2"
              >
                <td class="td py-1">{{ studentD.identifiant }}</td>
                <td class="td">{{ studentD.nom }}</td>
                <td class="td">{{ studentD.prenom }}</td>
                <td class="td">
                  <span 
                    class="my-2 text-sky-500  text-lg cursor-pointer hover:text-sky-600"
                    @click="navigateToStudentDetails(studentD.id)"
                  >
                    Details
                  </span>
                </td>
              </tr>
            </table>
          </div>
        </template>
      </DialogModal>
    </div> 
</template>

 
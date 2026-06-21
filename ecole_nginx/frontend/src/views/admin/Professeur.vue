
<script setup>
import { onMounted, ref, watch, reactive } from "vue";
import axios from "axios";
// Importations de tes composants UI existants
import DialogModal from "@/components/DialogModal.vue";
import StyleModal from "@/components/StyleModal.vue";
import PrimaryButton from "@/components/PrimaryButton.vue";
import DangerButton from "@/components/DangerButton.vue";
import InputError from "@/components/InputError.vue";
import InputLabel from "@/components/InputLabel.vue";
import TextInput from "@/components/TextInput.vue";
import DataTable from "@/components/DataTable.vue";

const url = import.meta.env.VITE_APP_BASE_URL;
const dataLoading = ref(false);
const activatingId = ref(null)
const errors = ref({})

// On remplace props d'Inertia par des valeurs locales par défaut
const props = defineProps({
  filters: { type: Object, default: () => ({ search: "" }) }
});

const registerProfesseur = ref(false);
const processing = ref(false);  

const changeButton = ref(false);
const pages = ref(1);
const search = ref(props.filters.search || "");
const professeurData = ref({ data: [], meta: { links: [] } });

// Remplacement de useForm par un objet reactive standard
const formProfesseur = reactive({
  id: "",
  nom: "",
  prenom: "",
  sexe: "",
  telephone: "",
  notification: false,
  email: "",
  adresse: "",
  matiere_enseignee: "",
  // processing: false, // Manuel
  // errors: {}        // Manuel
});

const resetForm = () => {
  Object.assign(formProfesseur, {
    id: "", nom: "", prenom: "", sexe: "", telephone: "",
    notification: false, email: "", adresse: "", matiere_enseignee: "",
    processing: false, errors: {}
  });
};

const professeurModalShow = () => {
  registerProfesseur.value = true;
};

const professeurModalClose = () => {
  registerProfesseur.value = false;
  resetForm();
  changeButton.value = false;
};

// Logique de soumission avec Axios pur
// const submitProfesseur = async () => {
//   processing.value = true;
//   errors.value = {};

//   try {
//     const endpoint = changeButton.value 
//       ? `${url}/professeur` 
//       : `${url}/professeur`;
    
//     // Utiliser PUT si on modifie, POST sinon
//     const method = changeButton.value ? 'post' : 'post';
    
//     const response = await axios[method](endpoint, formProfesseur);

//     if (response.status === 200 || response.status === 201) {
//       professeurModalClose();
//       fetchPersonData(); // Recharger la liste
//     }
//   } catch (error) {
//       if (error.response?.data?.detail) {
//         showSwalInfo(e.response.data.detail, 'red');
//       }
//     if (error.response && error.response.status === 422) {
//       errors.value = error.response.data.errors;
//     } else {
//       // console.error("Erreur technique:", error);
//     }
//   } finally {
//     processing.value = false;
//   }
// };

const submitProfesseur = async () => {
  processing.value = true;
  errors.value = {};

  try {
    // Fix: use correct endpoint and method for create vs update
    const endpoint = changeButton.value 
      ? `${url}/professeur/${formProfesseur.id}`  // update: include ID
      : `${url}/professeur`;                       // create
    
    const method = changeButton.value ? 'put' : 'post';  // Fix: use PUT for update
    
    const response = await axios[method](endpoint, formProfesseur);

    if (response.status === 200 || response.status === 201) {
      professeurModalClose();
      fetchPersonData();
    }
  } catch (error) {
    if (error.response?.data?.detail) {
      showSwalInfo(error.response.data.detail, 'red');  // Fix: was "e.response" (undefined variable)
    }

    if (error.response?.status === 422) {
      const rawErrors = error.response.data.errors;

      // Fix: normalize errors to arrays for InputError component
      if (rawErrors) {
        errors.value = Object.fromEntries(
          Object.entries(rawErrors).map(([key, val]) => [
            key,
            Array.isArray(val) ? val : [val]
          ])
        );
      }
    }
  } finally {
    processing.value = false;
  }
};

const fetchPersonData = async (page=1) => {
  dataLoading.value=true
  try {
    const response = await axios.get(`${url}/professeur`, {
      params: {
        search: search.value,
        page: page,
      },
    });
    professeurData.value = response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération :", error);
  }finally{dataLoading.value=false}
};

onMounted(() => {
  fetchPersonData();
});

// Surveiller la recherche et réinitialiser la page
watch(search, () => {
  pages.value = 1;
  fetchPersonData();
});

// Surveiller le changement de page
watch(pages, () => {
  fetchPersonData();
});

const editProf = (dataProfesseur) => {
  formProfesseur.id = dataProfesseur.id;
  formProfesseur.nom = dataProfesseur.nom;
  formProfesseur.prenom = dataProfesseur.prenom;
  formProfesseur.sexe = dataProfesseur.sexe;
  formProfesseur.telephone = dataProfesseur.telephone;
  formProfesseur.email = dataProfesseur.email;
  formProfesseur.adresse = dataProfesseur.adresse;
  formProfesseur.matiere_enseignee = dataProfesseur.matiere_enseignee;
  formProfesseur.notification = !!dataProfesseur.notification;
  
  changeButton.value = true;
  professeurModalShow();
};

const activeProf = async (id) => {
  activatingId.value=id
  try {
    // Remplacement de router.post par axios
    await axios.patch(`${url}/active-teacher`,{
      id:id
    });
    fetchPersonData();
    activatingId.value=null
  } catch (error) {
    activatingId.value=null
    console.error("Erreur d'activation:", error);
  }
};


const columns = [ 
  { key: 'nom',       label: 'Nom',    badge: true, nowrap: false},
  { key: 'prenom',       label: 'Prénom', nowrap: true },
  { key: 'telephone',       label: 'Téléphone', nowrap: true },
  { key: 'sexe',       label: 'Sexe', nowrap: true ,    badge: true},
  { key: 'adresse',       label: 'Adresse', nowrap: true ,    badge: true},
  { key: 'email',  label: "Courriel" },
  // { key: 'matierre',  label: "Matiere Ens." },
  { key: 'status_',        label: 'Status' , badge: true }
]

const actions = [
  {
    key: 'edit',
    type: 'slot',
    icon: 'ri-edit-box-line text-sky-500 hover:text-sky-700 cursor-pointer',
    onClick: async (row, selection, index) => {
        console.log(row); 
    },
  },

  // {
  //   key: 'view',
  //   type: 'slot',
  //   icon: 'ri-eye-line text-emerald-500 hover:text-emerald-700',
  //   onClick: async (row, selection, index) => {
  //       console.log(row); 
  //   },
  // },

  {
    key: 'delete',
    type: 'button',
    icon: 'ri-delete-bin-6-line text-rose-400/75 hover:text-rose-600',
    onClick: async (row, selection, index) => {
        console.log(row); 
    },
  },
]
</script>

<template>
  <div class="max-w-7xl px-4 mx-auto sm:px-2 lg:px-4 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex items-center gap-3 mb-5">
  <div class="w-9 h-9 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center shrink-0">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6" class="w-5 h-5 text-violet-400">
      <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
    </svg>
  </div>
  <div>
    <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Professeurs</h1>
    <p class="text-[12px] text-[#7c83a0]">Gestion du corps enseignant</p>
  </div>
</div>

    <!-- <PrimaryButton type="button" @click="professeurModalShow" class=" ms-3 pb-2 md:pb-0">
      Ajouter Professeur
    </PrimaryButton> -->
      <button type="button" @click="professeurModalShow"
    class="btn-violet">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
    </svg>
    Ajouter Professeur
  </button>
    <div class="flex justify-end me-4 pb-2">
      <div class="w-full md:w-5/12">
          <div class="relative flex-1">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
        class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#3d4d62] pointer-events-none">
        <path fill-rule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clip-rule="evenodd" />
      </svg>
          <input type="text" class="field-search" name="" v-model="search"
              placeholder="Rechercher un professeur.." id="" />
      </div>
      </div>
  </div>
 

  <DataTable
    :columns="columns"
    :rows="professeurData.data"
    row-key="id"
    :loading="dataLoading"
    :skeleton-rows="10"
    :meta="professeurData.meta"
    :actions="actions"  
    @change-page="fetchPersonData"
    @update:selections="selections = $event"
  > 
      <template #cell-email="{value }">
      <span class="text-[13px] text-[#7c83a0]">{{ value ?? 'Non definie' }}</span>
       </template>

    <template #cell-adresse="{value }">
      <span class="text-[13px] text-[#7c83a0]">{{ value.substring(0, 20) }}</span>
    </template>

    <template #cell-nom="{ row, value }">
  <button
    v-if="activatingId !== row.id"
    @click="activeProf(row.id)"
    :disabled="activatingId !== null"
    class="font-mono hover:underline cursor-pointer text-sm"
    :class="{
      'text-green-400 bg-green-500/10 border border-green-500/20 px-2.5 rounded-full': row?.user?.status == '1',
      'text-orange-400 bg-orange-500/10 border border-orange-500/20 px-2.5 rounded-full': row?.user?.status == '0',
      'text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2.5 rounded-full': row?.user?.status != '1' && row?.user?.status != '0'
    }"
  >
    {{ value }}
  </button>

  <span v-else class="inline-flex items-center gap-1.5 text-sky-500 text-sm">
    <svg class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10"
        stroke="currentColor" stroke-width="4"/>
      <path class="opacity-75" fill="currentColor"
        d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
    </svg>
    Waiting…
  </span>

</template>

 <template #cell-status_="{ row, value }">
  <p
    class="font-mono hover:underline cursor-pointer text-sm flex justify-center items-center mr-6"
    :class="{
      'text-green-400 bg-green-500/10 border border-green-500/20 px-2 rounded-full': row?.user?.status == '1',
      'text-orange-400 bg-orange-500/10 border border-orange-500/20 px-2 rounded-full': row?.user?.status == '0',
      'text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 rounded-full': row?.user?.status != '1' && row?.user?.status != '0'
    }"
  >
    {{ value }}
  </p>
 </template>

    <!-- <template #cell-nom="{row, value }">
          <button
          v-if="activatingId !== row.id"
          @click="activeProf(row.id)"
          :disabled="activatingId !== null"
          class="font-mono hover:underline cursor-pointer"
          :class="row?.user?.status == '1' ? 'text-green-600 bg-green-300' : 'text-rose-500 bg-rose-300'">
          {{ value }}
        </button>

        <span v-else class="inline-flex items-center gap-1.5 text-sky-500 text-sm">
          <svg class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10"
              stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
          </svg>
          Waiting…
        </span>
    </template> -->

      <!-- <template #action-view="{row}">
        <router-link :to="'/etudiants/voir/' + row.id" title="Détails">
          <i class="ri-eye-line text-emerald-500 hover:text-emerald-700"></i>
        </router-link>
      </template> -->

      <template #action-edit="{row}">
          <i class="ri-edit-circle-fill text-yellow-500/75 hover:border-yellow-500/20 me-3 cursor-pointer text-xs" @click="editProf(row)"></i>  
      </template>
 
        <template #empty>
        Aucun étudiant trouvé pour cette recherche.
    </template>
    </DataTable> 

   
    <StyleModal :show="registerProfesseur" @close="professeurModalClose" max-width="'3xl'">
      <template #title>
       <div class="flex flex-col md:flex-row justify-between items-center">
         <h5 class="text-center text-xl text-slate-500" id="professeurLabel">
           Ajouter un Professeur
          </h5>
       </div>

      </template>
      <template #content>
        <form id="prof-form" @submit.prevent="submitProfesseur">
          <div class="modal-body">
            <div class="flex flex-col md:flex-row justify-between items-center gap-2">
              <div class="pb-2 w-full">
                <InputLabel for="nom" value="Nom" />
                <TextInput id="nom" v-model="formProfesseur.nom" type="text" class="py-0" autofocus autocomplete="nom" />
                <InputError class="mt-2" :message="errors.nom" />
              </div>

              <div class="pb-2 w-full">
                <InputLabel for="prenom" value="Prénom" />
                <TextInput id="prenom" v-model="formProfesseur.prenom" type="text" class="py-0" autofocus
                  autocomplete="prenom" />
                <InputError class="mt-2" :message="errors.prenom" />
              </div>
           </div>

           <div class="flex flex-col md:flex-row justify-between items-center gap-2">
            <div class="pb-2 w-full">
              <InputLabel for="sexe" value="Sexe" />
              <select class="select" name="" id="sexe" v-model="formProfesseur.sexe">
                <option value="" aria-selected="true">Sexe</option>
                <option value="F">Femme</option>
                <option value="M">Homme</option>
              </select>
              <InputError class="mt-2" :message="errors.sexe" />
            </div>

            <div class="pb-2 w-full">
              <InputLabel for="telephone" value="Téléphone" />
              <TextInput id="telephone" v-model="formProfesseur.telephone" type="text" class="py-0" autofocus
                autocomplete="telephone" />
              <InputError class="mt-2" :message="errors.telephone" />
            </div>
            </div>
          <div class="flex flex-col md:flex-row justify-between items-center gap-2">
              <div class="pb-2 w-full">
                <InputLabel for="email" value="Courriel" />
                <TextInput id="email" v-model="formProfesseur.email" type="email" class="py-0" autofocus
                  autocomplete="email" />
                <InputError class="mt-2" :message="errors.email" />
              </div>

              <div class="pb-2 w-full">
                <InputLabel for="adresse" value="Adresse" />
                <TextInput id="adresse" v-model="formProfesseur.adresse" type="text" class="py-0" autofocus
                  autocomplete="adresse" />
                <InputError class="mt-2" :message="errors.adresse" />
              </div>
            </div>
          <div class="flex flex-col md:flex-row justify-between items-center gap-2">
            <div class="pb-2 w-full">
              <InputLabel for="matiere_enseignee" value="Matière enseignée" />
              <TextInput id="matiere_enseignee" v-model="formProfesseur.matiere_enseignee" type="text" class="py-0"
                autofocus autocomplete="matiere_enseignee" />
              <InputError class="mt-2" :message="errors.matiere_enseignee" />
            </div>

            <!-- <div class="flex justify-end items-center me-4 my-2">
              <InputLabel value="Notifier Le Prof" />
              <input type="checkbox" name="" class="ms-2" id="notifier" v-model="formProfesseur.notification">
            </div> -->
            <div class="pb-2 w-full flex justify-end items-center">
             <label class="flex items-center gap-2.5 cursor-pointer group">
                <div class="relative">
                  <input type="checkbox" id="notifier" v-model="formProfesseur.notification" class="sr-only peer" />
                  <div class="w-9 h-5 bg-white/[0.07] peer-checked:bg-[#4f8ef7]/70 rounded-full transition-colors duration-200 border border-white/[0.1] peer-checked:border-[#4f8ef7]/40"></div>
                  <div class="absolute top-0.5 left-0.5 w-4 h-4 bg-[#7c83a0] peer-checked:bg-white rounded-full transition-all duration-200 peer-checked:translate-x-4"></div>
                </div>
                <span class="text-[12px] text-[#7c83a0] group-hover:text-[#c0c7d8] transition-colors">Notifier Le Prof</span>
              </label>
            </div>
            </div>
          </div>
          <div class="flex justify-end gap-4">
            <DangerButton type="button" class="" @click="professeurModalClose">
              Close
            </DangerButton>
            <PrimaryButton id="button" type="submit"  data-bs-ripple-init
              :class="{ 'opacity-25': formProfesseur.processing }" :disabled="formProfesseur.processing">
              <span v-if="changeButton == true">
                Modifier
              </span>
              <span v-else>
                Enregistrer
              </span>
            </PrimaryButton>
          </div>
        </form>
      </template>
  <!-- <template #footer>
    <button class="btn-secondary" @click="open = false">Annuler</button>
    <button class="btn-primary" form="prof-form">Confirmer</button>
  </template> -->
</StyleModal>
  </div>
</template>
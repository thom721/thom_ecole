
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
const submitProfesseur = async () => {
  processing.value = true;
  errors.value = {};

  try {
    const endpoint = changeButton.value 
      ? `${url}/professeur` 
      : `${url}/professeur`;
    
    // Utiliser PUT si on modifie, POST sinon
    const method = changeButton.value ? 'post' : 'post';
    
    const response = await axios[method](endpoint, formProfesseur);

    if (response.status === 200 || response.status === 201) {
      professeurModalClose();
      fetchPersonData(); // Recharger la liste
    }
  } catch (error) {
    console.log(error.response);
    
    if (error.response && error.response.status === 422) {
      errors.value = error.response.data.errors;
    } else {
      console.error("Erreur technique:", error);
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
    await axios.post(`${url}/active-prof/${id}`);
    fetchPersonData();
    activatingId.value=null
  } catch (error) {
    activatingId.value=null
    console.error("Erreur d'activation:", error);
  }
};


const columns = [ 
  { key: 'nom',       label: 'Nom',    badge: true, nowrap: true},
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
    icon: 'ri-delete-bin-6-line text-rose-400 hover:text-rose-600',
    onClick: async (row, selection, index) => {
        console.log(row); 
    },
  },
]
</script>

<template>
  <div class="max-w-7xl px-4 mx-auto sm:px-2 lg:px-4 pt-4">
    <PrimaryButton type="button" @click="professeurModalShow" class=" ms-3 pb-2">
      Ajouter Professeur
    </PrimaryButton>
          <div class="flex justify-end me-4 pb-3">
            <div class="w-full md:w-5/12">
                <input type="text" class="input-normal" name="" v-model="search"
                    placeholder="Rechercher un professeur.." id="" />
            </div>
        </div>

    <!-- <DialogModal :show="registerProfesseur2" @close="professeurModalClose">
      <template #title>
       <div class="flex justify-between items-center">
         <h5 class="text-center text-xl text-slate-500" id="professeurLabel">
           Ajouter un Professeur
          </h5>
          <button type="button" class="text-xl text-red-500 cursor-pointer flex justify-end" @click="professeurModalClose"
           aria-label="Close"><i class="ri-close-line"></i></button>
       </div>

      </template>
      <template #content>
        <form @submit.prevent="submitProfesseur">
          <div class="modal-body">
            <div class="pb-2">
              <InputLabel for="nom" value="Nom" />
              <TextInput id="nom" v-model="formProfesseur.nom" type="text" class="py-0" autofocus autocomplete="nom" />
              <InputError class="mt-2" :message="formProfesseur.errors.nom" />
            </div>

            <div class="pb-2">
              <InputLabel for="prenom" value="Prénom" />
              <TextInput id="prenom" v-model="formProfesseur.prenom" type="text" class="py-0" autofocus
                autocomplete="prenom" />
              <InputError class="mt-2" :message="formProfesseur.errors.prenom" />
            </div>

            <div class="pb-2">
              <InputLabel for="sexe" value="Sexe" />
              <select class="select" name="" id="sexe" v-model="formProfesseur.sexe">
                <option value="" aria-selected="true">Sexe</option>
                <option value="F">Femme</option>
                <option value="M">Homme</option>
              </select>
              <InputError class="mt-2" :message="formProfesseur.errors.sexe" />
            </div>

            <div class="pb-2">
              <InputLabel for="telephone" value="Téléphone" />
              <TextInput id="telephone" v-model="formProfesseur.telephone" type="text" class="py-0" autofocus
                autocomplete="telephone" />
              <InputError class="mt-2" :message="formProfesseur.errors.telephone" />
            </div>

            <div class="pb-2">
              <InputLabel for="email" value="Courriel" />
              <TextInput id="email" v-model="formProfesseur.email" type="email" class="py-0" autofocus
                autocomplete="email" />
              <InputError class="mt-2" :message="formProfesseur.errors.email" />
            </div>

            <div class="pb-2">
              <InputLabel for="adresse" value="Adresse" />
              <TextInput id="adresse" v-model="formProfesseur.adresse" type="text" class="py-0" autofocus
                autocomplete="adresse" />
              <InputError class="mt-2" :message="formProfesseur.errors.adresse" />
            </div>

            <div class="pb-2">
              <InputLabel for="matiere_enseignee" value="Matière enseignée" />
              <TextInput id="matiere_enseignee" v-model="formProfesseur.matiere_enseignee" type="text" class="py-0"
                autofocus autocomplete="matiere_enseignee" />
              <InputError class="mt-2" :message="formProfesseur.errors.matiere_enseignee" />
            </div>

            <div class="flex justify-end items-center me-4 my-2">
              <InputLabel value="Notifier Le Prof" />
              <input type="checkbox" name="" class="ms-2" id="notifier" v-model="formProfesseur.notification">
            </div>
          </div>
          <div class="flex justify-end gap-4">
            <DangerButton type="button" class="" @click="professeurModalClose">
              Close
            </DangerButton>
            <PrimaryButton id="button" type="submit" class="btn btn-primary btn-sm" data-bs-ripple-init
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
    </DialogModal> -->

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

    <template #cell-nom="{row, value }">
          <button
          v-if="activatingId !== row.id"
          @click="activeProf(row.id)"
          :disabled="activatingId !== null"
          class="font-mono hover:underline cursor-pointer"
          :class="row?.user?.status == '1' ? 'text-green-600' : 'text-rose-500'">
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

      <!-- <template #action-view="{row}">
        <router-link :to="'/etudiants/voir/' + row.id" title="Détails">
          <i class="ri-eye-line text-emerald-500 hover:text-emerald-700"></i>
        </router-link>
      </template> -->

      <template #action-edit="{row}">
          <i class="ri-edit-circle-fill text-yellow-500 me-3 cursor-pointer" @click="editProf(row)"></i> <i
                class="fa fa-trash text-red-500 cursor-pointer"></i>
      </template>
 
        <template #empty>
        Aucun étudiant trouvé pour cette recherche.
    </template>
    </DataTable> 

       
    <!-- <div class=" overflow-x-auto mt-2">
      <table class="w-full text-sm text-center text-gray-500  ">
        <thead class="text-md text-slate-100 uppercase bg-gray-600  dark:text-gray-100 px-2">
          <tr>
            <th class="th p-2">Nom</th>
            <th class="th p-2">Pr&eacute;nom</th>
            <th class="th p-2">T&eacute;l&eacute;phone</th>
            <th class="th p-2">Courriel</th>
            <th class="th p-2">Adresse</th> 
            <th class="th p-2">Status</th>
            <th class="th p-2">Action</th>
          </tr>



        </thead>
        <tbody>
          <tr class="cursor-pointer hover:bg-sky-100" :class="{ 'bg-slate-200': index % 2 == 1 }"
            v-for="(dataProfesseur, index) in professeurData.data" :key="dataProfesseur.id">

            <td class="td" @click="activeProf(dataProfesseur.id)" style="cursor: pointer;">
              <span v-if="dataProfesseur.user" :class="[dataProfesseur.user.status == '0' ? 'text-yellow-500' : 'text-green-500'
              ]">{{ dataProfesseur.nom }} </span>
              <span v-else class="text-red-500">{{ dataProfesseur.nom }}</span>
            </td>

            <td class="td">{{ dataProfesseur.prenom }} </td>
            <td class="td">{{ dataProfesseur.telephone }}</td>
            <td class="td">{{ dataProfesseur.email }}</td>
            <td class="td">{{ dataProfesseur.adresse.substring(0, 20) }}</td> 
            <td class="td">
               {{dataProfesseur.status_}}
               
            </td>
            <td class="td">
              <i class="ri-edit-circle-fill text-yellow-500 me-3 cursor-pointer" @click="editProf(dataProfesseur)"></i> <i
                class="fa fa-trash text-red-500 cursor-pointer"></i>
            </td>
          </tr>
        </tbody>
      </table>
     

    </div> -->

    <StyleModal :show="registerProfesseur" @close="professeurModalClose" max-width="xl">
      <template #title>
       <div class="flex justify-between items-center">
         <h5 class="text-center text-xl text-slate-500" id="professeurLabel">
           Ajouter un Professeur
          </h5>
       </div>

      </template>
      <template #content>
        <form id="prof-form" @submit.prevent="submitProfesseur">
          <div class="modal-body">
            <div class="pb-2">
              <InputLabel for="nom" value="Nom" />
              <TextInput id="nom" v-model="formProfesseur.nom" type="text" class="py-0" autofocus autocomplete="nom" />
              <InputError class="mt-2" :message="errors.nom" />
            </div>

            <div class="pb-2">
              <InputLabel for="prenom" value="Prénom" />
              <TextInput id="prenom" v-model="formProfesseur.prenom" type="text" class="py-0" autofocus
                autocomplete="prenom" />
              <InputError class="mt-2" :message="errors.prenom" />
            </div>

            <div class="pb-2">
              <InputLabel for="sexe" value="Sexe" />
              <select class="select" name="" id="sexe" v-model="formProfesseur.sexe">
                <option value="" aria-selected="true">Sexe</option>
                <option value="F">Femme</option>
                <option value="M">Homme</option>
              </select>
              <InputError class="mt-2" :message="errors.sexe" />
            </div>

            <div class="pb-2">
              <InputLabel for="telephone" value="Téléphone" />
              <TextInput id="telephone" v-model="formProfesseur.telephone" type="text" class="py-0" autofocus
                autocomplete="telephone" />
              <InputError class="mt-2" :message="errors.telephone" />
            </div>

            <div class="pb-2">
              <InputLabel for="email" value="Courriel" />
              <TextInput id="email" v-model="formProfesseur.email" type="email" class="py-0" autofocus
                autocomplete="email" />
              <InputError class="mt-2" :message="errors.email" />
            </div>

            <div class="pb-2">
              <InputLabel for="adresse" value="Adresse" />
              <TextInput id="adresse" v-model="formProfesseur.adresse" type="text" class="py-0" autofocus
                autocomplete="adresse" />
              <InputError class="mt-2" :message="errors.adresse" />
            </div>

            <div class="pb-2">
              <InputLabel for="matiere_enseignee" value="Matière enseignée" />
              <TextInput id="matiere_enseignee" v-model="formProfesseur.matiere_enseignee" type="text" class="py-0"
                autofocus autocomplete="matiere_enseignee" />
              <InputError class="mt-2" :message="errors.matiere_enseignee" />
            </div>

            <div class="flex justify-end items-center me-4 my-2">
              <InputLabel value="Notifier Le Prof" />
              <input type="checkbox" name="" class="ms-2" id="notifier" v-model="formProfesseur.notification">
            </div>
          </div>
          <!-- <div class="flex justify-end gap-4">
            <DangerButton type="button" class="" @click="professeurModalClose">
              Close
            </DangerButton>
            <PrimaryButton id="button" type="submit" class="btn btn-primary btn-sm" data-bs-ripple-init
              :class="{ 'opacity-25': formProfesseur.processing }" :disabled="formProfesseur.processing">
              <span v-if="changeButton == true">
                Modifier
              </span>
              <span v-else>
                Enregistrer
              </span>
            </PrimaryButton>
          </div> -->
        </form>
      </template>
  <template #footer>
    <button class="btn-secondary" @click="open = false">Annuler</button>
    <button class="btn-primary" form="prof-form">Confirmer</button>
  </template>
</StyleModal>
  </div>
</template>
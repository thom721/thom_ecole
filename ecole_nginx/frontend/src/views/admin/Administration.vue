<script setup>
import { onMounted, ref, watch, reactive } from "vue";
import axios from "axios";
 
import InputError from "@/components/InputError.vue";
import InputLabel from "@/components/InputLabel.vue";
import TextInput from "@/components/TextInput.vue";
import PrimaryButton from "@/components/PrimaryButton.vue";
import StyleModal from "@/components/StyleModal.vue";
import DangerButton from "@/components/DangerButton.vue";
import { useSchoolStoreInfo } from '@/stores/schoolStore';
import DataTable from "@/components/DataTable.vue";
const {role_global} =useSchoolStoreInfo()
 
// import AuthorisationComponents from '@/Components/AuthorisationComponents.vue';

const url = import.meta.env.VITE_APP_BASE_URL;

 
const props = defineProps({
    filters: { type: Object, default: () => ({ search: "" }) }
});

// États réactifs
const openModal = ref(false);
const changeButton = ref(false);
const authorization = ref(true);
const message = ref('');
const pages = ref(1);
const search = ref(props.filters.search || "");
const personnelData = ref({ data: [], meta: { links: [] } });

// Remplacement de useForm par reactive
const formPersonnel = reactive({
    id: "",
    nom: "",
    prenom: "",
    sexe: "",
    telephone: "",
    email: "",
    adresse: "",
    role: "",
    processing: false,
    errors: {}
});

const resetForm = () => {
    Object.assign(formPersonnel, {
        id: "", nom: "", prenom: "", sexe: "", telephone: "",
        email: "", adresse: "", role: "", processing: false, errors: {}
    });
};

const PersonnelModalShow = () => {
    openModal.value = true;
};

const PersonnelModalClose = () => {
    changeButton.value = false;
    resetForm();
    openModal.value = false;
};

// Soumission avec Axios
const submitPersonnel = async () => {
    formPersonnel.processing = true;
    formPersonnel.errors = {};

    try {
        const endpoint = changeButton.value 
            ? `${url}/personnel` 
            : `${url}/personnel`;
        
        const method = changeButton.value ? 'post' : 'post';
        const response = await axios[method](endpoint, formPersonnel);

        if (response.status === 200 || response.status === 201) {
            PersonnelModalClose();
            searchPersonnel(); // Rafraîchir la liste
        }
    } catch (error) {
        console.log(error.response);
        
        if (error.response) {
            if (error.response.status === 403) {
                authorization.value = error.response.data.Authorization;
                message.value = error.response.data.message;
            } else if (error.response.status === 422 || error.response.status === 202) {
                formPersonnel.errors = error.response.data.errors;
            }
        }
        console.error("Erreur lors de la soumission :", error);
    } finally {
        formPersonnel.processing = false;
    }
};

const editPerso = (personnel) => {
    
    formPersonnel.id = personnel.id;
    formPersonnel.nom = personnel.nom;
    formPersonnel.prenom = personnel.prenom;
    formPersonnel.sexe = personnel.sexe;
    formPersonnel.email = personnel.email;
    formPersonnel.telephone = personnel.telephone;
    formPersonnel.adresse = personnel.adresse;
    
    // Extraction sécurisée du rôle
    if (personnel.user && personnel.user.roles && personnel.user.roles.length > 0) {
        formPersonnel.role = personnel.user.roles[0].id;
    } else {
        formPersonnel.role = '';
    }
    
    changeButton.value = true;
    PersonnelModalShow();
};

const dataLoading = ref(false)

const searchPersonnel = async (page=1) => {
    dataLoading.value=true
    try {
        const response = await axios.get(`${url}/personnel`, {
            params: {
                search: search.value,
                page: page,
            },
        });
        console.log(response.data);
        
        personnelData.value = response.data;
    } catch (error) {
        console.error('Erreur lors de la récupération :', error);
    }finally{
        dataLoading.value=false
    }
};

// Observateurs
watch(search, () => {
    pages.value = 1;
    searchPersonnel();
});

watch(pages, () => {
    searchPersonnel();
});

onMounted(() => {
    searchPersonnel();
});

const close_autorisation_close = () => {
    authorization.value = true;
};

 

 const columns = [ 
  { key: 'nom',       label: 'Nom',    badge: true },
  { key: 'prenom',       label: 'Prénom', nowrap: true },
  { key: 'sexe',       label: 'Sexe', nowrap: true },
  { key: 'telephone',  label: "T&eacute;l&eacute;phone" },
  { key: 'email',        label: 'Courriel' },
  { key: 'status_', label: 'Statut', badge: true  },
]
 


const actions = [
  {
    key: 'edit',
    type: 'button',
    icon: 'ri-edit-circle-fill text-yellow-500/75 me-3 cursor-pointer',
    onClick: async (row, selection, index) => {
        editPerso(row)
    },
  },

  {
    key: 'delete',
    type: 'button',
    icon: 'ri-delete-bin-6-line text-rose-400 text-red-500/50 cursor-pointer',
    onClick: async (row, selection, index) => {
        // console.log(row); 
    },
  },
]
const activatingId = ref(null)
const activePersonnel = async (id) => {
  activatingId.value=id
  try {
    // Remplacement de router.post par axios
    await axios.patch(`${url}/active-personnel`,{
      id:id
    });
    searchPersonnel();
    activatingId.value=null
  } catch (error) {
    activatingId.value=null
    console.error("Erreur d'activation:", error);
  }
};

</script>


<template>
    <div class="max-w-7xl px-2 mx-auto sm:px-4 lg:px-4 pb-16 animate-[fadeUp_0.4s_ease_both]">
        <div class="flex items-center gap-3 mb-5">
    <div class="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shrink-0">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6" class="w-5 h-5 text-amber-400">
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3.75h.008v.008h-.008v-.008zm0 3h.008v.008h-.008v-.008zm0 3h.008v.008h-.008v-.008z"/>
        </svg>
    </div>
  <div>
    <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Administration</h1>
    <p class="text-[12px] text-[#7c83a0]">Gestion du personnel administratif</p>
  </div>
</div>
     <div class="flex flex-col md:flex-row">
        <!-- <PrimaryButton type="button" @click="PersonnelModalShow" class=" mb-2">
            Ajouter Personnel
        </PrimaryButton> -->
          <button type="button" @click="PersonnelModalShow"
    class="btn-amber">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
    </svg>
    Ajouter Personnel
  </button>
     </div>
        <div class="flex justify-end md:me-4 pb-2">
            <div class="w-full md:w-5/12">
                   <div class="relative flex-1">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
              class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#3d4d62] pointer-events-none">
              <path fill-rule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clip-rule="evenodd" />
            </svg>
                <input type="text" class="field-search" name="" v-model="search"
                    placeholder="Rechercher un Personnel..." id="" />
            </div>
            </div>
        </div>

        <StyleModal :show="openModal" :max-width="'2xl'" @close="PersonnelModalClose">
            <template #title>
                <h5 class="modal-title text-center text-slate-300" id="PersonnelLabel">
                    Ajouter un Personnel
                </h5>
            </template>

            <template #content>
                <div>
                    <form @submit.prevent="submitPersonnel">
                        <div class="modal-body">
                            <div class="flex flex-col md:flex-row justify-between items-center gap-2">
                                <div class="pb-2 w-full">
                                    <InputLabel for="nom" value="Nom" />
                                    <TextInput id="nom" v-model="formPersonnel.nom" type="text" class="py-0" autofocus
                                        autocomplete="nom" />
                                    <InputError v-if="formPersonnel.errors" class="mt-2"
                                        :message="formPersonnel.errors.nom" />
                                </div>

                                <div class="pb-2 w-full">
                                    <InputLabel for="prenom" value="Prénom" />
                                    <TextInput id="prenom" v-model="formPersonnel.prenom" type="text" class="py-0" autofocus
                                        autocomplete="prenom" />
                                    <InputError class="mt-2" :message="formPersonnel.errors.prenom" />
                                </div>
                            </div>

                            <div class="flex flex-col md:flex-row justify-between items-center gap-2">
                                <div class="pb-2 w-full">
                                    <InputLabel for="sexe" value="Sexe" />
                                    <select
                                        class="border-gray-300 focus:border-sky-600 focus:ring-sky-600 py-1 rounded-md shadow-sm  text-lg text-gray-600 w-full"
                                        name="" id="sexe" v-model="formPersonnel.sexe">
                                        <option value="" aria-selected="true">Sexe</option>
                                        <option value="F">Femme</option>
                                        <option value="M">Homme</option>
                                    </select>
                                    <InputError class="mt-2" :message="formPersonnel.errors.sexe" />
                                </div>

                                <div class="pb-2 w-full">
                                    <InputLabel for="telephone" value="Téléphone" />
                                    <TextInput id="telephone" v-model="formPersonnel.telephone" type="text" class="py-0"
                                        autofocus autocomplete="telephone" />
                                    <InputError class="mt-2" :message="formPersonnel.errors.telephone" />
                                </div>
                            </div>

                            <div class="flex flex-col md:flex-row justify-between items-center gap-2">
                                <div class="pb-2 w-full">
                                    <InputLabel for="email" value="Courriel" />
                                    <TextInput id="email" v-model="formPersonnel.email" type="email" class="py-0" autofocus
                                        autocomplete="email" />
                                    <InputError class="mt-2" :message="formPersonnel.errors.email" />
                                </div>

                                <div class="pb-2 w-full">
                                    <InputLabel for="role" value="Role" /> 
                                    <select
                                        class="input-select"
                                        name="" id="role" v-model="formPersonnel.role">
                                        <option disabled value="">role</option>
                                        <option :selected="formPersonnel.role == role.id" v-for="role in role_global"
                                            :key="role.id" :value="role.id">{{ role.name }}
                                        </option>
                                    </select>
                                    <InputError class="mt-2" :message="formPersonnel.errors.role" />
                                </div>
                            </div>


                            <div class="pb-2">
                                <InputLabel for="adresse" value="Adresse" />
                                <TextInput id="adresse" v-model="formPersonnel.adresse" type="text" class="py-0"
                                    autofocus autocomplete="adresse" />
                                <InputError class="mt-2" :message="formPersonnel.errors.adresse" />
                            </div>


                        </div>
                        <div class="flex justify-end gap-4 py-1">
                            <DangerButton type="button" class="" @click="PersonnelModalClose">
                                Close
                            </DangerButton>
                            <PrimaryButton type="submit" class="" :class="{ 'opacity-25': formPersonnel.processing }"
                                :disabled="formPersonnel.processing" data-bs-ripple-init>
                                <span v-if="changeButton">Modifier</span>
                                <span v-else>Enregistrer</span>
                            </PrimaryButton>
                        </div>
                    </form>
                </div>
            </template>

        </StyleModal>


    <DataTable
    :columns="columns"
    :rows="personnelData.data"
    row-key="id"
    :loading="dataLoading"
    :skeleton-rows="10"
    :meta="personnelData.meta"
    :actions="actions"  
    @change-page="searchPersonnel"
    @update:selections="selections = $event"
  > 
<template #cell-nom="{ row, value }">
  <button
    v-if="activatingId !== row.id"
    @click="activePersonnel(row.id)"
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
  <button 
    class="font-mono hover:underline cursor-pointer text-sm"
    :class="{
      'text-green-400 bg-green-500/10 border border-green-500/20 px-2.5 rounded-full': row?.user?.status == '1',
      'text-orange-400 bg-orange-500/10 border border-orange-500/20 px-2.5 rounded-full': row?.user?.status == '0',
      'text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2.5 rounded-full': row?.user?.status != '1' && row?.user?.status != '0'
    }"
  >
    {{ value }}
  </button>
  
 </template>

        <template #empty>
        Aucune donnée trouvée pour cette recherche.
    </template>
    </DataTable>   
    
    </div>

    <!-- <AuthorisationComponents :status="authorization" :permission="['Modifier personnel']" :message="message" @autorisation_close="close_autorisation_close"/> -->
</template>

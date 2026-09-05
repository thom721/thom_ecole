<script setup>
import { onMounted, ref, watch, reactive } from "vue";
import axios from "axios";
 
import InputError from "@/components/InputError.vue";
import InputLabel from "@/components/InputLabel.vue";
import TextInput from "@/components/TextInput.vue";
import PrimaryButton from "@/components/PrimaryButton.vue";
import DialogModal from "@/components/DialogModal.vue";
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
    console.log(personnel);
    
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

// watch(pages, () => {
//     searchPersonnel();
// });

onMounted(() => {
    searchPersonnel();
});

const close_autorisation_close = () => {
    authorization.value = true;
};

const changePageForPayments = (link) => {
    if (!link.url || link.active) return;
    const urlObj = new URL(link.url);
    pages.value = urlObj.searchParams.get("page") || 1;
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
    icon: 'ri-edit-circle-fill text-yellow-500 me-3 cursor-pointer',
    onClick: async (row, selection, index) => {
        console.log(row); 
    },
  },

  {
    key: 'delete',
    type: 'button',
    icon: 'fa fa-trash text-red-500 cursor-pointer',
    onClick: async (row, selection, index) => {
        console.log(row); 
    },
  },
]
</script>


<template>
    <div class="max-w-7xl px-4 mx-auto sm:px-6 lg:px-8 pt-4 pb-16">
     
        <PrimaryButton type="button" @click="PersonnelModalShow" class=" pb-2">
            Ajouter Personnel
        </PrimaryButton>
        <div class="flex justify-end me-4 pb-3">
            <div class="w-full md:w-5/12">
                <input type="text" class="input-normal" name="" v-model="search"
                    placeholder="Rechercher un Personnel..." id="" />
            </div>
        </div>

        <DialogModal :show="openModal" :max-width="'xl'" @close="PersonnelModalClose">
            <template #title>
                <h5 class="modal-title text-center" id="PersonnelLabel">
                    Ajouter un Personnel
                </h5>
            </template>

            <template #content>
                <div>
                    <form @submit.prevent="submitPersonnel">
                        <div class="modal-body">
                            <div class="pb-2">
                                <InputLabel for="nom" value="Nom" />
                                <TextInput id="nom" v-model="formPersonnel.nom" type="text" class="py-0" autofocus
                                    autocomplete="nom" />
                                <InputError v-if="formPersonnel.errors" class="mt-2"
                                    :message="formPersonnel.errors.nom" />
                            </div>

                            <div class="pb-2">
                                <InputLabel for="prenom" value="Prénom" />
                                <TextInput id="prenom" v-model="formPersonnel.prenom" type="text" class="py-0" autofocus
                                    autocomplete="prenom" />
                                <InputError class="mt-2" :message="formPersonnel.errors.prenom" />
                            </div>

                            <div class="pb-2">
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

                            <div class="pb-2">
                                <InputLabel for="telephone" value="Téléphone" />
                                <TextInput id="telephone" v-model="formPersonnel.telephone" type="text" class="py-0"
                                    autofocus autocomplete="telephone" />
                                <InputError class="mt-2" :message="formPersonnel.errors.telephone" />
                            </div>

                            <div class="pb-2">
                                <InputLabel for="email" value="Courriel" />
                                <TextInput id="email" v-model="formPersonnel.email" type="email" class="py-0" autofocus
                                    autocomplete="email" />
                                <InputError class="mt-2" :message="formPersonnel.errors.email" />
                            </div>

                            <div class="pb-2">
                                <InputLabel for="role" value="Role" />
                                <!-- {{ formPersonnel.role }} -->
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

        </DialogModal>


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
    <template #cell-nom_classe="{ value }">
      <span class="text-[12px] font-semibold text-sky-400">{{ value }}</span>
    </template>
 
        <template #empty>
        Aucune donnée trouvée pour cette recherche.
    </template>
    </DataTable>   
        <!-- <div class=" overflow-x-auto mt-2 gap-4">
            <table class="w-full text-sm text-center text-gray-500 dark:text-gray-400">
                <thead class="text-md text-slate-100 uppercase bg-gray-600 dark:bg-gray-700 dark:text-gray-100 px-2">
                    <tr>
                        <th class="p-2">Nom</th>
                        <th class="py-1">Pr&eacute;nom</th>
                        <th class="py-1">T&eacute;l&eacute;phone</th>
                        <th class="py-1">Courriel</th>
                        <th class="py-1">Statut</th>
                        <th class="py-1 text-nowrap">Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="fs-6" :class="{ 'bg-gray-200': index % 2 == 1 }"
                        v-for="(dataPerso, index) in personnelData.data" :key="dataPerso.id">

                        <td class="td" style="cursor: pointer;">
                            <span v-if="dataPerso.user" :class="[dataPerso.user.status == '0' ? 'text-yellow-500' : 'text-green-500'
                            ]">{{ dataPerso.nom }}</span>
                            <span v-else class="text-red-500">{{ dataPerso.nom }}</span>
                        </td>
                        <td class="td">{{ dataPerso.prenom }}</td>
                        <td class="td">{{ dataPerso.telephone }}</td>
                        
                        <td class="td">{{ dataPerso.email }}</td>
                        
                        <td class="text-green-500 td">
                            {{dataPerso.status_}}
                        </td>
                        <td class="td text-nowrap"> <i class="ri-edit-circle-fill text-yellow-500 me-3 cursor-pointer"
                                @click="editPerso(dataPerso)"></i> <i
                                class="fa fa-trash text-red-500 cursor-pointer"></i>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div> -->

    </div>

    <!-- <AuthorisationComponents :status="authorization" :permission="['Modifier personnel']" :message="message" @autorisation_close="close_autorisation_close"/> -->
</template>

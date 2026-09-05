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
    salaire_fixe: "",
    processing: false,
    errors: {}
});

const resetForm = () => {
    Object.assign(formPersonnel, {
        id: "", nom: "", prenom: "", sexe: "", telephone: "",
        email: "", adresse: "", role: "", salaire_fixe: "", processing: false, errors: {}
    });
};

const PersonnelModalShow = () => {
    openModal.value = true;
};

// Statut actif/inactif affiché et bascule dans le modal — équivalent de
// admin_status/admin_change_status (flutter_version, administration_screen.
// dart:_toggleStatus), même endpoint PATCH v1/active-personnel que le badge
// "Nom" de la liste (activePersonnel ci-dessous).
const personnelUserStatus = ref(null);
const togglingModalStatus = ref(false);

const toggleModalStatus = async () => {
    if (!formPersonnel.id) return;
    togglingModalStatus.value = true;
    try {
        const { data } = await axios.patch(`${url}/active-personnel`, { id: formPersonnel.id });
        personnelUserStatus.value = typeof data.status === 'boolean' ? (data.status ? 1 : 0) : data.status;
        searchPersonnel(pages.value);
    } catch (error) {
        console.error("Erreur d'activation:", error);
    } finally {
        togglingModalStatus.value = false;
    }
};

// Réinitialisation du mot de passe — équivalent de reset_password_personnel()
// (school_client) / PersonnelState.resetPassword (flutter_version) → PATCH
// v1/change-password-personnel, absente du web jusqu'ici.
const newPassword = ref("");
const confirmPassword = ref("");
const passwordError = ref("");
const passwordSuccess = ref("");
const resettingPassword = ref(false);

const resetPasswordPersonnel = async () => {
    passwordError.value = "";
    passwordSuccess.value = "";
    if (newPassword.value.length < 8) {
        passwordError.value = "Le mot de passe doit contenir au moins 8 caractères.";
        return;
    }
    if (newPassword.value !== confirmPassword.value) {
        passwordError.value = "Les mots de passe ne correspondent pas.";
        return;
    }
    resettingPassword.value = true;
    try {
        await axios.patch(`${url}/change-password-personnel`, {
            personnel_id: formPersonnel.id,
            password: newPassword.value,
            password_confirm: confirmPassword.value,
        });
        passwordSuccess.value = "Mot de passe réinitialisé.";
        newPassword.value = "";
        confirmPassword.value = "";
    } catch (error) {
        passwordError.value = error.response?.data?.detail ?? "Impossible de réinitialiser le mot de passe.";
    } finally {
        resettingPassword.value = false;
    }
};

const PersonnelModalClose = () => {
    changeButton.value = false;
    resetForm();
    personnelUserStatus.value = null;
    newPassword.value = "";
    confirmPassword.value = "";
    passwordError.value = "";
    passwordSuccess.value = "";
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
        const payload = {
            ...formPersonnel,
            salaire_fixe: formPersonnel.salaire_fixe === "" ? null : Number(formPersonnel.salaire_fixe),
        };
        const response = await axios[method](endpoint, payload);

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
    formPersonnel.salaire_fixe = personnel.salaire_fixe ?? "";

    // Extraction sécurisée du rôle
    if (personnel.user && personnel.user.roles && personnel.user.roles.length > 0) {
        formPersonnel.role = personnel.user.roles[0].id;
    } else {
        formPersonnel.role = '';
    }

    personnelUserStatus.value = personnel.user?.status ?? null;
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
                    {{ changeButton ? 'Modifier un Personnel' : 'Ajouter un Personnel' }}
                </h5>
            </template>

            <template #content>
                <div>
                    <form @submit.prevent="submitPersonnel">
                        <div class="modal-body">
                            <!-- Actif/Inactif — équivalent de admin_status (flutter_version,
                                 administration_screen.dart), visible seulement en modification. -->
                            <div v-if="changeButton" class="flex items-center gap-3 mb-3 px-3.5 py-2.5 rounded-lg bg-white/[0.03] border border-white/[0.07]">
                                <span class="text-sm font-bold" :class="personnelUserStatus == 1 ? 'text-emerald-400' : 'text-rose-400'">
                                    {{ personnelUserStatus == 1 ? 'Active' : 'Inactive' }}
                                </span>
                                <span class="flex-1"></span>
                                <button type="button" @click="toggleModalStatus" :disabled="togglingModalStatus"
                                    class="px-3 py-1 rounded-md text-xs font-medium border disabled:opacity-50 transition-colors"
                                    :class="personnelUserStatus == 1
                                        ? 'text-rose-400 border-rose-400/40 hover:bg-rose-400/10'
                                        : 'text-emerald-400 border-emerald-400/40 hover:bg-emerald-400/10'">
                                    {{ togglingModalStatus ? '…' : (personnelUserStatus == 1 ? 'Desactiver' : 'Activer') }}
                                </button>
                            </div>

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

                            <div class="pb-2">
                                <InputLabel for="salaire_fixe" value="Salaire fixe (mensuel)" />
                                <TextInput id="salaire_fixe" v-model="formPersonnel.salaire_fixe" type="number" step="0.01" class="py-0" />
                                <InputError class="mt-2" :message="formPersonnel.errors.salaire_fixe" />
                            </div>

                            <!-- Réinitialiser le mot de passe — équivalent de
                                 PersonnelState.resetPassword (flutter_version), absente du web
                                 jusqu'ici. -->
                            <div v-if="changeButton" class="pt-3 mt-2 border-t border-white/[0.07]">
                                <p class="text-[10.5px] tracking-wide font-semibold text-[#7c83a0] uppercase mb-2">
                                    Réinitialiser le mot de passe
                                </p>
                                <div class="flex flex-col md:flex-row gap-2 items-start">
                                    <div class="w-full">
                                        <TextInput v-model="newPassword" type="password" class="py-0" placeholder="Nouveau mot de passe" />
                                    </div>
                                    <div class="w-full">
                                        <TextInput v-model="confirmPassword" type="password" class="py-0" placeholder="Confirmation" />
                                    </div>
                                    <button type="button" @click="resetPasswordPersonnel" :disabled="resettingPassword"
                                        class="shrink-0 px-3.5 py-1.5 rounded-lg text-[12.5px] font-medium text-[#c9d1d9] border border-white/[0.12] hover:bg-white/[0.06] disabled:opacity-50 transition-colors">
                                        {{ resettingPassword ? '…' : 'Réinitialiser' }}
                                    </button>
                                </div>
                                <p v-if="passwordError" class="text-xs text-rose-400 mt-1.5">{{ passwordError }}</p>
                                <p v-if="passwordSuccess" class="text-xs text-emerald-400 mt-1.5">{{ passwordSuccess }}</p>
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
 <span class="inline-flex items-center gap-1.5">
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

  <!-- "Casquette administrative" d'un Professeur avec un rôle non-enseignant
       (RAcademic.py:_sync_shadow_personnel) — aucun compte de connexion
       propre pour cette fiche, symétrique du badge "via Personnel" côté
       Professeur (voir aussi flutter_version, administration_screen.dart). -->
  <span v-if="row.professeur_id" title="Casquette administrative d'un Professeur — pas de compte de connexion propre."
    class="inline-flex items-center px-2 py-0.5 rounded-full text-[10.5px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20 whitespace-nowrap">
    via Professeur
  </span>
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

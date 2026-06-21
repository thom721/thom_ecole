<script setup>
import { onMounted, ref, watch, computed } from "vue";
import axios from "axios";
import PrimaryButton from '@/components/PrimaryButton.vue';
import AdminLayout from '@/layouts/AdminLayout.vue';
import StyleModal from '@/components/StyleModal.vue';
import { useRouter } from 'vue-router';
import DataTable from "@/components/DataTable.vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const canCreatePayment = computed(() => authStore.canAccessPaiement);

// URL de base définie dans ton .env
const url = import.meta.env.VITE_APP_BASE_URL;

defineOptions({
    layout: AdminLayout
});

// --- ÉTATS ---
const searhStudent = ref('');
const studentData = ref([]);
const paiements = ref({ data: [], meta: { links: [] } });
const search = ref('');
const dataLoading = ref(false)
const pages = ref(1);

// Modaux et visibilité
const showPayment = ref(false);
const searchForPay = ref(false);

// --- LOGIQUE DE RECHERCHE D'ÉTUDIANT (LIVE SEARCH) ---
const fetchStudent = async () => {
    if (searhStudent.value.length < 2) {
        studentData.value = [];
        return;
    }
    try {
        const response = await axios.post(`${url}/live-student`, { 
            val: searhStudent.value 
        });
        if (response.status === 200) {
            showPayment.value = true;
            studentData.value = response.data.data;
        }
    } catch (error) {
        console.error("Erreur live search:", error);
    }
};

// --- LOGIQUE DES PAIEMENTS (LISTE) ---
const searchPayments = async (page=1) => {
    dataLoading.value = true
    try {
        const response = await axios.get(`${url}/paiement`, {
            params: {
                search: search.value,
                page: page,
            },
        });
            paiements.value = response.data;
     
    } catch (error) {
        console.error('Erreur chargement paiements:', error);
    }finally{
        dataLoading.value = false
    }
};

// --- NAVIGATION (REDIRECTIONS SANS INERTIA) ---
const goToDetail = (id) => {
    // Redirection classique vers la page de détails
    window.location.href = `/paiement-detail/${id}`;
};

 
const router = useRouter();

const goToPaiementIndex = (student) => {
    // On utilise router.push pour une navigation fluide sans rechargement
    router.push({ 
        name: 'add-paiement', // Utilise le nom défini dans vos routes
        params: { etudiantId: student.id } 
    });
};

// --- LIFECYCLE & WATCHERS ---
onMounted(() => {
    searchPayments();
});

watch(search, () => {
    pages.value = 1;
    searchPayments();
});

watch(pages, searchPayments);

const closeModal = () => {
    searchForPay.value = false;
    searhStudent.value = '';
    studentData.value = [];
};

const columns = [
  { key: 'identifiant', label: 'Identifiant' },
  { key: 'nom',label: 'Nom', nowrap: true },
  { key: 'prenom', label: 'Prénom', nowrap: true },
  { key: 'annee', label: 'Année' },
  { key: 'classes',  label: 'Classe' }
]
const actions = [
  {
    key: 'view',
    type: 'slot',
    icon: 'ri-edit-box-line text-sky-500 hover:text-sky-700 cursor-pointer',
    onClick: async (row, selection, index) => {
        console.log(row); 
    },
  },
 
]
</script>

<template>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-4 pb-10 min-h-screen animate-[fadeUp_0.4s_ease_both] overflow-x-auto">

<div class="flex items-center gap-3 mb-5">
  <div class="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6" class="w-5 h-5 text-emerald-400">
      <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z"/>
    </svg>
  </div>
  <div>
    <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Paiements</h1>
    <p class="text-[12px] text-[#7c83a0]">Suivi des versements et échéances</p>
  </div>
</div>

<!-- Finance -->
<!-- <div class="flex items-center gap-3 mb-5">
  <div class="w-9 h-9 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center shrink-0">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6" class="w-5 h-5 text-sky-400">
      <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
    </svg>
  </div>
  <div>
    <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Finance</h1>
    <p class="text-[12px] text-[#7c83a0]">Recettes, dépenses et bilans financiers</p>
  </div>
</div> -->

        <div class="flex flex-col md:flex-row justify-between pb-2 gap-4">
       <div>
        <button v-if="canCreatePayment" type="button" @click="searchForPay = true"
            class="btn-custum-sky">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-3.5 h-3.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z"/>
            </svg>
            Nouveau Paiement
            </button>

         <!-- <PrimaryButton @click="searchForPay = true" class="py-1 cursor-pointer">
            Nouveau Paiement            
        </PrimaryButton>  -->
       </div>

      <div class="w-full md:w-5/12 mb-2 md:mr-4">
          <div class="relative flex-1">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor"
              class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#3d4d62] pointer-events-none">
              <path fill-rule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clip-rule="evenodd" />
            </svg>
        <input 
          v-model="search" 
          type="text" 
          placeholder="Filtrer un paiement..." 
          class="field-search"
        />
      </div> 
      </div> 
    </div>


    <DataTable
        :columns="columns"
        :rows="paiements.data"
        row-key="id"
        :loading="dataLoading"
        :skeleton-rows="12"
        :meta="paiements.meta"
        :actions="actions" 
        @change-page="searchPayments"
        @update:selections="selections = $event"
    >
            <template #action-view="{row}">
            <router-link class="text-sky-500 hover:text-slate-600" :to="'/paiement-detail/' + row.id" title="Voir">
            Voir détail
            </router-link>
        </template>

            <!-- Optional: empty state override -->
            <template #empty>
            Aucun étudiant trouvé pour cette recherche.
            </template>
    </DataTable>

    
    </div>

    <StyleModal :show="searchForPay" max-width="2xl" @close="closeModal">
        <template #title>
            <div class="flex justify-between items-center py-2">
                <p class="text-lg  text-gray-800">Chercher l'étudiant</p>
                <p class="far fa-circle-xmark text-xl text-red-500 cursor-pointer hover:scale-110 transition flex justify-end" @click="closeModal"></p>
            </div>

        </template>
        <template #content>
            <div class="p-4 w-full py-2">
                <input 
                    type="text" 
                     placeholder="Rechercher un Paiement (Nom, ID...)" 
                class="field-input w-full"
                    v-model="searhStudent" 
                    @keyup="fetchStudent" 
                    autofocus
                >
            </div>
            <div v-if="studentData.length > 0" class="bg-[#171b26] border rounded-lg mx-4 mb-4 overflow-hidden divide-y">
                <div 
                    v-for="studentD in studentData" 
                    :key="studentD.id"
                    @click="goToPaiementIndex(studentD)"
                    class="grid grid-cols-3 p-3 hover:bg-gray-800 cursor-pointer transition text-sm text-gray-700 items-center"
                >
                    <p class="font-mono text-xs ">{{ studentD.identifiant }}</p>
                    <p class="uppercase text-right px-2">{{ studentD.nom }}</p>
                    <p class="capitalize text-right">{{ studentD.prenom }}</p>
                </div>
            </div>
            <div v-else-if="searhStudent.length > 1" class="text-center py-4 text-gray-400 text-sm">
                Aucun étudiant trouvé...
            </div>
        </template>
    </StyleModal>
</template>

<style scoped>
/* Tu peux ajouter ici tes styles personnalisés si nécessaire */
</style>
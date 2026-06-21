<script setup>
import { onMounted, ref, watch } from "vue";
import axios from "axios";
import PrimaryButton from '@/components/PrimaryButton.vue';
import AdminLayout from '@/layouts/AdminLayout.vue';
import DialogModal from '@/components/DialogModal.vue';
import { useRouter } from 'vue-router';

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
const searchPayments = async () => {
    try {
        const response = await axios.get(`${url}/paiement`, {
            params: {
                search: search.value,
                page: pages.value,
            },
        });
        if (response.data) {
            paiements.value = response.data;
        }
    } catch (error) {
        console.error('Erreur chargement paiements:', error);
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

// --- PAGINATION ---
const changePage = (link) => {
    if (!link.url || link.active) return;
    const urlParams = new URLSearchParams(link.url.split('?')[1]);
    pages.value = parseInt(urlParams.get('page')) || 1;
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
</script>

<template>
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 pb-10 min-h-screen">
        <div class="flex justify-between pt-4 pb-2">
        <PrimaryButton @click="searchForPay = true">
            Nouveau Paiement            
        </PrimaryButton>
                  <!-- <div class="flex justify-end pt-4 pb-2"> -->
      <div class="w-full md:w-5/12">
        <input 
          v-model="search" 
          type="text" 
          placeholder="Filtrer un paiement..." 
          class="w-full px-4 py-2 border rounded-lg focus:ring-0 focus:border-sky-500 outline-none border-slate-200 mb-2"
        />
      </div>
    <!-- </div>  -->
    </div>

    

        <div class="overflow-x-auto bg-white rounded-lg shadow border border-gray-200">
            <table class="w-full text-sm text-center text-gray-500">
                <thead class="text-xs text-white uppercase bg-gray-700 ">
                    <tr>
                        <th class="px-4 py-3">Identifiant</th>
                        <th class="px-4 py-3">Nom</th>
                        <th class="px-4 py-3">Prénom</th>
                        <th class="px-4 py-3">Année</th>
                        <th class="px-4 py-3">Classe</th>
                        <th class="px-4 py-3">Action</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                    <tr 
                        v-for="(paiement, index) in paiements.data" 
                        :key="paiement.id"
                        class="hover:bg-sky-50 transition-colors cursor-default"
                        :class="{ 'bg-gray-50': index % 2 == 1 }"
                    >
                        <td class="px-4 py-3 font-mono text-xs text-gray-600">{{ paiement.identifiant }}</td>
                        <td class="px-4 py-3 font-semibold text-gray-800 uppercase">{{ paiement.nom }}</td>
                        <td class="px-4 py-3 capitalize">{{ paiement.prenom }}</td>
                        <td class="px-4 py-3 text-xs">{{ paiement.annee }}</td>
                        <td class="px-4 py-3 text-xs">{{ paiement.classes }}</td>
                        <td class="px-4 py-3">
                            <button 
                                @click="goToDetail(paiement.id)"
                                class="px-3 py-1 bg-green-100 text-green-700 rounded-md hover:bg-green-200 font-medium transition"
                            >
                                Voir
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div v-if="paiements.meta" class="px-6 py-4 flex justify-end gap-2 bg-gray-50 border-t">
                <button 
                    v-for="link in paiements.meta.links" 
                    :key="link.label"
                    @click="changePage(link)"
                    v-html="link.label"
                    :disabled="!link.url"
                    class="px-3 py-1 text-xs rounded transition"
                    :class="[
                        link.active ? 'bg-sky-600 text-white shadow-sm ' : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-100',
                        !link.url ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'
                    ]"
                ></button>
            </div>
        </div>
    </div>

    <DialogModal :show="searchForPay" max-width="2xl" @close="closeModal">
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
                class="input-field w-full"
                    v-model="searhStudent" 
                    @keyup="fetchStudent" 
                    autofocus
                >
            </div>
            <div v-if="studentData.length > 0" class="bg-white border rounded-lg mx-4 mb-4 overflow-hidden divide-y">
                <div 
                    v-for="studentD in studentData" 
                    :key="studentD.id"
                    @click="goToPaiementIndex(studentD)"
                    class="grid grid-cols-3 p-3 hover:bg-sky-50 cursor-pointer transition text-sm text-gray-700 items-center"
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
    </DialogModal>
</template>

<style scoped>
/* Tu peux ajouter ici tes styles personnalisés si nécessaire */
</style>
<script setup>
import { onMounted, ref, watch, computed, reactive } from "vue";
import axios from "axios";
import Swal from 'sweetalert2';
import PrimaryButton from '@/components/PrimaryButton.vue';
import AdminLayout from '@/layouts/AdminLayout.vue';
import StyleModal from '@/components/StyleModal.vue';
import { useRouter } from 'vue-router';
import DataTable from "@/components/DataTable.vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const canCreatePayment = computed(() => authStore.canAccessPaiement);
const canManageArrears = computed(() => authStore.hasPermission('Annuler arriéré'));
const executantName = computed(() => authStore.user?.name || authStore.user?.email || '');

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
  { key: 'classes',  label: "Session / Année d'étude" }
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
  {
    key: 'annulation',
    type: 'slot',
    icon: 'ri-shield-cross-line text-rose-500 hover:text-rose-700 cursor-pointer',
    onClick: () => {},
  },
]

// --- DÉROGATION D'ARRIÉRÉ (annulation manuelle et réversible) ------------
const derogationModal = ref(false);
const derogationRow = ref(null);
const derogationLoading = ref(false);
const derogationSubmitting = ref(false);
const derogationExisting = ref(null);
const derogationSoldeRestant = ref(null);
const derogationDevise = ref('');
const derogationError = ref('');
const derogationForm = reactive({
  accepteContrat: false,
  ordonnePar: '',
  ordonneParFonction: '',
  typeAnnulation: 'total',
  montant: '',
  raison: '',
});

const roles = ref([]);
const fetchRoles = async () => {
  if (roles.value.length > 0) return;
  try {
    const { data } = await axios.get(`${url}/role`);
    roles.value = data.data;
  } catch (e) {
    console.error('Erreur chargement rôles:', e);
  }
};

const openDerogationModal = async (row) => {
  derogationRow.value = row;
  derogationError.value = '';
  derogationExisting.value = null;
  derogationSoldeRestant.value = null;
  derogationDevise.value = '';
  Object.assign(derogationForm, {
    accepteContrat: false, ordonnePar: '', ordonneParFonction: '',
    typeAnnulation: 'total', montant: '', raison: '',
  });
  derogationModal.value = true;
  derogationLoading.value = true;
  fetchRoles();
  try {
    const { data } = await axios.get(`${url}/annulation-arriere`, { params: { paiement_id: row.id } });
    derogationExisting.value = data.derogations.find(d => d.statut === 'actif') || null;
    derogationSoldeRestant.value = data.solde_restant;
    derogationDevise.value = data.devise || '';
  } catch (e) {
    console.error('Erreur chargement dérogation:', e);
  } finally {
    derogationLoading.value = false;
  }
};

const closeDerogationModal = () => {
  derogationModal.value = false;
  derogationRow.value = null;
};

const submitDerogation = async () => {
  if (!derogationForm.accepteContrat) return;
  const confirm = await Swal.fire({
    icon: 'warning',
    title: 'Confirmer la dérogation',
    text: "Cette action lève le blocage d'arriéré pour cet étudiant sur cette année. Elle reste réversible.",
    showCancelButton: true,
    confirmButtonText: 'Oui, accorder la dérogation',
    cancelButtonText: 'Annuler',
    background: '#0f1117', color: '#e8eaf0',
  });
  if (!confirm.isConfirmed) return;

  derogationSubmitting.value = true;
  derogationError.value = '';
  try {
    await axios.post(`${url}/annulation-arriere`, {
      paiement_id: derogationRow.value.id,
      type_annulation: derogationForm.typeAnnulation,
      montant_annule: derogationForm.typeAnnulation === 'partiel' ? Number(derogationForm.montant) : null,
      ordonne_par: derogationForm.ordonnePar,
      ordonne_par_fonction: derogationForm.ordonneParFonction,
      raison: derogationForm.raison,
      contrat_accepte: derogationForm.accepteContrat,
    });
    Swal.fire({ icon: 'success', title: 'Dérogation accordée', timer: 2000, showConfirmButton: false, background: '#0f1117', color: '#e8eaf0' });
    closeDerogationModal();
  } catch (e) {
    derogationError.value = e.response?.data?.detail?.errors || 'Erreur lors de la création de la dérogation.';
  } finally {
    derogationSubmitting.value = false;
  }
};

const revokeDerogation = async () => {
  const { value: raison } = await Swal.fire({
    icon: 'warning',
    title: 'Révoquer cette dérogation ?',
    text: "Le blocage d'arriéré sera rétabli pour cet étudiant sur cette année.",
    input: 'textarea',
    inputPlaceholder: 'Raison de la révocation (20 à 150 caractères)',
    showCancelButton: true,
    confirmButtonText: 'Oui, révoquer',
    cancelButtonText: 'Annuler',
    background: '#0f1117', color: '#e8eaf0',
    inputValidator: (value) => {
      if (!value || value.trim().length < 20 || value.trim().length > 150) {
        return 'La raison doit contenir entre 20 et 150 caractères.';
      }
    },
  });
  if (!raison) return;

  derogationSubmitting.value = true;
  try {
    await axios.post(`${url}/annulation-arriere/${derogationExisting.value.id}/annuler`, { raison });
    Swal.fire({ icon: 'success', title: 'Dérogation révoquée', timer: 2000, showConfirmButton: false, background: '#0f1117', color: '#e8eaf0' });
    closeDerogationModal();
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Erreur', text: e.response?.data?.detail?.errors || 'Erreur lors de la révocation.', background: '#0f1117', color: '#e8eaf0' });
  } finally {
    derogationSubmitting.value = false;
  }
};
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

            <template #action-annulation="{row}">
            <button v-if="canManageArrears" type="button" class="text-rose-500 hover:text-rose-700"
                title="Dérogation d'arriéré" @click="openDerogationModal(row)">
                Dérogation
            </button>
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

    <StyleModal :show="derogationModal" max-width="2xl" @close="closeDerogationModal">
        <template #title>
            <div class="flex justify-between items-center py-2">
                <p class="text-lg text-gray-800">
                    Dérogation d'arriéré — {{ derogationRow?.nom }} {{ derogationRow?.prenom }} ({{ derogationRow?.annee }})
                </p>
                <p class="far fa-circle-xmark text-xl text-red-500 cursor-pointer hover:scale-110 transition flex justify-end" @click="closeDerogationModal"></p>
            </div>
        </template>
        <template #content>
            <div v-if="derogationLoading" class="text-center py-8 text-sm text-gray-400">Chargement...</div>

            <div v-else-if="derogationExisting" class="space-y-4">
                <div class="bg-amber-500/10 border border-amber-500/25 rounded-xl p-4 text-sm space-y-1.5">
                    <p><strong>Dérogation active</strong> pour {{ derogationExisting.annee_academique }}</p>
                    <p>Montant annulé : <strong>{{ derogationExisting.montant_annule }} GDES</strong> ({{ derogationExisting.type_annulation }})</p>
                    <p>Ordonné par : {{ derogationExisting.ordonne_par }} ({{ derogationExisting.ordonne_par_fonction }})</p>
                    <p>Exécuté par : {{ derogationExisting.executant_nom }}<span v-if="derogationExisting.executant_role"> — {{ derogationExisting.executant_role }}</span></p>
                    <p>Motif : {{ derogationExisting.raison }}</p>
                </div>
                <div class="flex justify-end">
                    <button type="button" class="btn-red disabled:opacity-40" :disabled="derogationSubmitting" @click="revokeDerogation">
                        {{ derogationSubmitting ? 'Révocation…' : 'Révoquer la dérogation' }}
                    </button>
                </div>
            </div>

            <div v-else class="space-y-4">
                <div class="bg-rose-500/10 border border-rose-500/25 rounded-xl p-3 text-sm">
                    <span v-if="derogationSoldeRestant !== null">
                        Solde restant dû pour {{ derogationRow?.annee }} :
                        <strong>{{ derogationSoldeRestant }} {{ derogationDevise }}</strong>
                    </span>
                    <span v-else class="text-gray-400">
                        Solde restant non déterminable automatiquement — utilisez un montant précis.
                    </span>
                </div>

                <div class="bg-slate-500/10 border border-slate-500/20 rounded-xl p-4 text-[12.5px] leading-relaxed max-h-56 overflow-y-auto">
                    <p class="font-semibold mb-2">ATTESTATION D'ANNULATION D'ARRIÉRÉ DE PAIEMENT</p>
                    <p class="mb-2">
                        Je soussigné(e) <strong>{{ executantName }}</strong>, certifie procéder à l'annulation du solde impayé
                        de l'année académique <strong>{{ derogationRow?.annee }}</strong> pour l'étudiant
                        <strong>{{ derogationRow?.nom }} {{ derogationRow?.prenom }}</strong>, sur instruction expresse de
                        <strong>{{ derogationForm.ordonnePar || '…' }}</strong>, en sa qualité de
                        <strong>{{ derogationForm.ordonneParFonction || '…' }}</strong>.
                    </p>
                    <p class="mb-1">Je reconnais que cette action :</p>
                    <ul class="list-disc pl-5 space-y-0.5">
                        <li>permet à l'étudiant de régler ses paiements de l'année en cours sans que le solde de l'année précédente ne soit exigé au préalable ;</li>
                        <li>n'efface pas la dette dans les registres : elle est enregistrée comme une dérogation, horodatée et nominative ;</li>
                        <li>reste réversible à tout moment par une personne autorisée, ce qui rétablira l'obligation de règlement ;</li>
                        <li>sera intégrée au rapport financier (personne ayant ordonné, personne ayant exécuté, montant, motif).</li>
                    </ul>
                    <p class="mt-2">En cochant la case ci-dessous, je confirme avoir pris connaissance de ces termes et j'atteste de l'exactitude des informations saisies.</p>
                </div>

                <label class="flex items-start gap-2 text-sm">
                    <input type="checkbox" v-model="derogationForm.accepteContrat" class="mt-1">
                    <span>J'ai lu et j'accepte les termes de cette attestation.</span>
                </label>

                <fieldset :disabled="!derogationForm.accepteContrat" class="space-y-3" :class="{ 'opacity-40': !derogationForm.accepteContrat }">
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="text-sm">Ordonné par</label>
                            <input type="text" v-model="derogationForm.ordonnePar" placeholder="Nom du responsable" class="input-select">
                        </div>
                        <div>
                            <label class="text-sm">Fonction</label>
                            <select v-model="derogationForm.ordonneParFonction" class="input-select">
                                <option value="" disabled>Choisir une fonction</option>
                                <option v-for="r in roles" :key="r.id" :value="r.name">{{ r.name }}</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label class="text-sm block mb-1">Montant à annuler</label>
                        <div class="flex items-center gap-4 text-sm mb-2">
                            <label class="flex items-center gap-1.5">
                                <input type="radio" value="total" v-model="derogationForm.typeAnnulation"> Tout le reste (calculé automatiquement)
                            </label>
                            <label class="flex items-center gap-1.5">
                                <input type="radio" value="partiel" v-model="derogationForm.typeAnnulation"> Montant précis
                            </label>
                        </div>
                        <input v-if="derogationForm.typeAnnulation === 'partiel'" type="number" min="0" step="0.01"
                            v-model="derogationForm.montant" placeholder="Montant en GDES" class="input-select">
                    </div>

                    <div>
                        <label class="text-sm">Raison (20 à 150 caractères)</label>
                        <textarea v-model="derogationForm.raison" rows="3" maxlength="150" class="input-select"
                            placeholder="Motif de cette dérogation"></textarea>
                        <p class="text-[11px] text-gray-400 text-right">{{ derogationForm.raison.length }}/150</p>
                    </div>
                </fieldset>

                <p v-if="derogationError" class="text-red-500 text-sm">{{ derogationError }}</p>

                <div class="flex justify-end gap-2 pt-2">
                    <button type="button" class="btn-outline-sky" @click="closeDerogationModal">Annuler</button>
                    <button type="button" class="btn-red disabled:opacity-40"
                        :disabled="!derogationForm.accepteContrat || !derogationForm.ordonnePar || !derogationForm.ordonneParFonction || derogationForm.raison.length < 20 || (derogationForm.typeAnnulation === 'partiel' && !derogationForm.montant) || derogationSubmitting"
                        @click="submitDerogation">
                        {{ derogationSubmitting ? 'Envoi…' : 'Accorder la dérogation' }}
                    </button>
                </div>
            </div>
        </template>
    </StyleModal>
</template>

<style scoped>
/* Tu peux ajouter ici tes styles personnalisés si nécessaire */
</style>
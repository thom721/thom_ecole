<script setup>
import { onMounted, ref, computed } from "vue";
import axios from "axios";
import AdminDashComposante from "@/components/AdminDashComposante.vue";
import DashboardStudentStats from "@/components/DashboardStudentStats.vue";
import PaiementsStats from "@/components/PaiementsStats.vue";
import StyleModal from "@/components/StyleModal.vue";
import DataTable from "@/components/DataTable.vue";
import { useAuthStore } from "@/stores/auth";
import { useSchoolStore } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';

const authStore = useAuthStore();
const showFinancials = computed(() => !authStore.shouldMaskFinancials);
const canSeeSubTab = (subId) => authStore.canSeeSubTab(subId);

const schoolStore = useSchoolStore();
const { niveau, professeur, annee, classes, faculte, cours, loading } = storeToRefs(schoolStore);



const dataLoading = ref(false)
const url = import.meta.env.VITE_APP_BASE_URL;

// États des données
const stats = ref({
  etudiant: 0,
  personnel: 0,
  professeur: 0,
  faculte: 0,
  classes: 0,
  classeDetails: [],
  paiement: 0,
  devise: ""
});

const classListeStudent = ref([]);
const isModalOpen = ref(false);
const openAccordionIndex = ref(null); 

// Chargement des données au montage
onMounted(() => {
  fetchDashboardData();
  openAccordionIndex.value=3
});

const fetchDashboardData = async () => {
  try {
    const response = await axios.get('/dashboard');
    if (response.status === 200) {
      stats.value = response.data;
    }
  } catch (error) {
    console.error("Erreur Dashboard:", error);
  }
};

const getStudentList = async (classe_id, annee_academique_id) => {
  try {
    const response = await axios.get(`${url}/student-with-classe`, {
      params: { classe_id, annee_id: annee_academique_id }
    });
    classListeStudent.value = response.data.data;
    isModalOpen.value = true;
  } catch (error) {
    console.error("Erreur Liste Étudiants:", error);
  }
};

// Logique simplifiée de l'accordéon (sans manipulation directe du DOM si possible)
const toggleAccordion = (index) => {
  openAccordionIndex.value = openAccordionIndex.value === index ? null : index;
};

const toggleStudentChart= (index) => {
  //  console.log(index);
  openAccordionIndex.value = openAccordionIndex.value === index ? null : index;
};
const togglePaymentChart= (index) => { 
  openAccordionIndex.value = openAccordionIndex.value === index ? null : index;
};

const actions = [
  {
    key: 'view',
    type: 'slot',
    icon: 'ri-edit-box-line text-sky-500 hover:text-sky-700 cursor-pointer',
    onClick: async (row, selection, index) => {
        // console.log(row); 
    },
  },
 
]
      const columns = [
  { key: 'niveau_name', label: 'Cycle / Niveau' , nowrap: true},
  { key: 'nom_classe',label: 'Classe', nowrap: true },
  { key: 'etudiant_count', label: 'Effectif', nowrap: true }, 
]
</script>

<template>
  <div class="px-4 animate-[fadeUp_0.4s_ease_both]"> 
<div class="flex items-center gap-3 mb-5">
  <div class="w-9 h-9 rounded-xl bg-[#4f8ef7]/10 border border-[#4f8ef7]/20 flex items-center justify-center shrink-0">
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6" class="w-5 h-5 text-[#7aaeff]">
      <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z"/>
    </svg>
  </div>
  <div>
    <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Tableau de bord</h1>
    <p class="text-[12px] text-[#7c83a0]">Vue d'ensemble de l'établissement</p>
  </div>
</div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <AdminDashComposante title="Total Étudiants"  icon="ri-group-line"        :value="stats.etudiant"      color="blue"    @show-details="canSeeSubTab('home.stats_etudiant') && toggleStudentChart(2)" />
      <AdminDashComposante v-if="showFinancials && canSeeSubTab('home.suivi_paiement')" title="Paiements reçus" icon="ri-bank-card-line" :value="stats.paiement" color="emerald" devise="HTG" @show-details="togglePaymentChart(3)" />
      <AdminDashComposante title="Professeurs"     icon="ri-user-star-line"     :value="stats.professeur"        color="violet"  @show-details="" />
      <AdminDashComposante title="Personnel"       icon="ri-user-star-line"     :value="stats.personnel"         color="cian"    @show-details="" />
      <AdminDashComposante title="Classes actives" icon="ri-building-line"      :value="stats.classes"           color="amber"   @show-details="canSeeSubTab('home.classes') && toggleAccordion(1)" />
      <AdminDashComposante title="Absences"        icon="ri-calendar-close-line" :value="7"                     color="rose"    @show-details="" />
      <AdminDashComposante title="Cours"           icon="ri-book-open-line"     :value="stats.cours"             color="sky"     @show-details="" />
      <AdminDashComposante title="Cours programmés" icon="ri-book-open-line"   :value="94"                      color="purple"  @show-details="" />

    </div>
    <PaiementsStats v-if="openAccordionIndex===3 && showFinancials && canSeeSubTab('home.suivi_paiement')" :annee="annee" />

    <DashboardStudentStats v-if="openAccordionIndex===2 && canSeeSubTab('home.stats_etudiant')" />

<div v-if="openAccordionIndex === 1 && canSeeSubTab('home.classes')" class="mt-4">
 <!-- <h3 class=" text-gray-300 text-xl ml-4P">Détails des Classes</h3> -->
         <div class="px-4 mt-2 flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center border transition-colors border-amber-500/20 bg-amber-500/10 shrink-0">
            <i class="text-[16px] ri-building-line text-amber-400"></i>
          </div>
          <div>
            <h1 class="text-[17px] font-semibold text-[#e8eaf0] tracking-tight">Détails des Classes</h1>
            <p class="text-[12px] text-[#7c83a0]">Répartition des étudiants par classe.</p>
          </div>
        </div>

    <DataTable 
        :columns="columns"
        :rows="stats.classeDetails"
        row-key="id"
        :loading="dataLoading"
        :skeleton-rows="12" 
        :actions="actions" 
        @update:selections="selections = $event"
    >
            <template #action-view="{row}">
           <button @click="getStudentList(row.classe_id, row.annee_academique_id)" class="text-sky-600 hover:underline ">
                  Gérer
                </button>
        </template>

            <!-- Optional: empty state override -->
            <template #empty>
            Aucun étudiant trouvé pour cette recherche.
            </template>
    </DataTable>
</div>



    <StyleModal :show="isModalOpen" @close="isModalOpen = false" :maxWidth="'3xl'">
      <template #title>
        <span class="text-slate-300">Liste des élèves</span>
      </template>
      <template #content>
        <div class="max-h-[60vh] overflow-y-auto">
          <table class="w-full text-sm">
            <thead class="sticky top-0 bg-white shadow-sm  border-b">
              <tr>
                <th class="py-2 text-left">ID</th>
                <th class="py-2 text-left">Nom Complet</th>
                <th class="py-2 text-left">Sexe</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in classListeStudent" :key="student.id" class="border-b last:border-0">
                <td class="py-3">{{ student.identifiant }}</td>
                <td class="py-3">{{ student.nom }} {{ student.prenom }}</td>
                <td class="py-3">{{ student.sexe }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </StyleModal>
  </div>
</template>
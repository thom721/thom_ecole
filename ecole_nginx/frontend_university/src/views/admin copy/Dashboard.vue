<script setup>
import { onMounted, ref } from "vue";
import axios from "axios";
import AdminDashComposante from "@/components/AdminDashComposante.vue";
import DialogModal from "@/components/DialogModal.vue"; // Assure-toi qu'il est créé

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
    const response = await axios.get(`${url}/api/student-with-classe`, {
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
</script>

<template>
  <div class="p-4">
    <!-- <h1 class="text-2xl  text-gray-800 mb-6">Tableau de Bord Administratif</h1> -->

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <AdminDashComposante 
        title="Étudiants" 
        colors="border-sky-500" 
        colorsText="sky-500" 
        icon="fa-users" 
        :value="stats.etudiant" 
      />

      <AdminDashComposante 
        title="Professeurs" 
        colors="border-orange-500" 
        colorsText="orange-500" 
        icon="fa-user-tie" 
        :value="stats.professeur" 
      />

      <AdminDashComposante 
        title="Classes" 
        colors="border-red-500" 
        colorsText="red-500" 
        icon="fa-graduation-cap" 
        :value="stats.classes" 
        @show-details="toggleAccordion(1)"
      />

      <AdminDashComposante 
        title="Paiements" 
        colors="border-green-500" 
        colorsText="green-500" 
        icon="fa-hand-holding-dollar" 
        :value="stats.paiement" 
        :devise="stats.devise"
      />
    </div>

    <div v-if="openAccordionIndex === 1" class="mt-6 bg-white rounded-xl shadow-sm border animate__animated animate__fadeIn">
      <div class="p-4 border-b bg-gray-50 flex justify-between items-center">
        <h3 class=" text-gray-700">Détails des Classes</h3>
        <button @click="openAccordionIndex = null" class="text-gray-400 hover:text-red-500">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-gray-100 text-xs uppercase text-gray-600">
            <tr>
              <th class="px-6 py-3">Cycle / Niveau</th>
              <th class="px-6 py-3">Classe</th>
              <th class="px-6 py-3">Effectif</th>
              <th class="px-6 py-3">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="detail in stats.classeDetails" :key="detail.classe_id" class="hover:bg-sky-50 transition-colors">
              <td class="px-6 py-4">{{ detail.niveau_name }}</td>
              <td class="px-6 py-4 font-medium">{{ detail.nom_classe }}</td>
              <td class="px-6 py-4">{{ detail.etudiant_count }} élèves</td>
              <td class="px-6 py-4">
                <button @click="getStudentList(detail.classe_id, detail.annee_academique_id)" class="text-sky-600 hover:underline ">
                  Voir la liste
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <DialogModal :show="isModalOpen" @close="isModalOpen = false">
      <template #title>Liste des élèves</template>
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
    </DialogModal>
  </div>
</template>
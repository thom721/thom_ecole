<template>
  <div class="text-slate-500 bg-gray-100 pb-10 min-h-screen font-sans">
    <div class="max-w-7xl mx-auto p-4 sm:px-6 lg:px-8">
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 mt-6">
        <div class="bg-white rounded-lg shadow-sm">
          <h2 class="text-xl font-bold text-center mb-6">📊 Rapport Global</h2> 
          
          <div class="grid grid-cols-1 gap-4 p-4 bg-gray-50">
            <div>
              <label class="block text-sm font-medium text-gray-700">Type de rapport</label>
              <select v-model="formGlobal.type" class="select">
                <option value="" disabled>Choisir le type</option>
                <option value="Global">Global</option>
                <option value="Livres">Livres</option>
                <option value="Tissus">Tissus</option>
                <option value="Fournitures">Fournitures</option>
                <option value="Arriéré">Arriéré</option>
                <option value="Dépense">Dépense</option>
              </select>
            </div>

            <!-- <div class="flex gap-4"> -->
              <div class="w-full">
                <label class="block text-sm font-medium text-gray-700">Début</label>
                <input type="date" v-model="formGlobal.date_debut" class="border-gray-300 focus:border-sky-600 focus:ring-sky-600 py-1 rounded-md shadow-sm text-lg text-gray-600 w-full" />
              </div>
              <div class="w-full">
                <label class="block text-sm font-medium text-gray-700">Fin</label>
                <input type="date" v-model="formGlobal.date_fin" class="border-gray-300 focus:border-sky-600 focus:ring-sky-600 py-1 rounded-md shadow-sm text-lg text-gray-600 w-full" />
              </div>
            <!-- </div> -->

            <div class="flex justify-end mt-4">
              <PrimaryButton @click="printPDF('/print-global-repport', formGlobal)" class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 font-bold transition">
                Imprimer
              </PrimaryButton>
            </div>
          </div>
        </div>

        <div class="rounded-lg shadow-sm bg-white">
          <h2 class="text-xl font-bold text-center mb-6">Rapports Financiers 💰</h2>
          <div class="flex flex-col space-y-6">
            <div class="bg-gray-50 p-4 rounded-md ga-20">
              <p class="text-lg font-medium text-slate-700 mb-3 border-b">Paiements des élèves</p>
              
              <div class="mt-4">
                <label class="block text-sm text-gray-600">Classe</label>
                <select v-model="formPayment.classe" class="w-full select">
                  <option value="All">Toutes les classes</option>
                  <option v-for="c in classes" :key="c.id" :value="c.nom_classe">{{ c.nom_classe }}</option>
                </select>
              </div>

               <div class="mt-4">
                <label class="block text-sm text-gray-600">Année Académique</label>
                <select v-model="formPayment.classe" class="w-full select">
                  <option value="All">Toutes les classes</option>
                  <option v-for="c in classes" :key="c.id" :value="c.nom_classe">{{ c.nom_classe }}</option>
                </select>
              </div>
              
              <!-- <div class="grid grid-cols-2 gap-2 mb-3">
                <input type="date" v-model="formPayment.date_debut" class="border-gray-300 rounded text-sm select" />
                <input type="date" v-model="formPayment.date_fin" class="border-gray-300 rounded text-sm select" />
              </div> -->

              <div class="mt-4">
               <label class="block text-sm text-gray-600">Versement</label>
                <select v-model="formPayment.versement" class="w-full border-gray-300 rounded text-sm select">
                  <option v-for="v in versements" :key="v" :value="v">{{ v }}</option>
                </select>
              </div>

              <div class="flex justify-end mt-4">
                <PrimaryButton @click="printPDF('/print-rapport-paiement', formPayment)" class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
                  Générer PDF
                </PrimaryButton>
              </div>
          </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';
import AdminLayout from '@/layouts/AdminLayout.vue'; 
import InputLabel from "@/components/InputLabel.vue";
import TextInput from "@/components/TextInput.vue";
import PrimaryButton from "@/components/PrimaryButton.vue";
defineOptions({ layout: AdminLayout });

const props = defineProps({
  classes: Array,
  annees: Array,
  niveaux_cycles: Array
});

// URL de base depuis les variables d'environnement
const baseUrl = import.meta.env.VITE_APP_BASE_URL || '';

// États réactifs simples (sans Inertia)
const formGlobal = reactive({
  type: '',
  date_debut: '',
  date_fin: '',
});

const formPayment = reactive({
  classe: 'All',
  date_debut: '',
  date_fin: '',
  versement: 'tous les Versements'
});

const versements = ["tous les Versements", "1er Versement", "2ème Versement", "3ème Versement", "4ème Versement"];


const printPDF = async (endpoint, data) => {
  try {
    const token = localStorage.getItem("auth-token");
    
    const response = await axios.post(`${baseUrl}${endpoint}`, data, {
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/pdf",
      },
      responseType: "blob" // Indique à Axios que la réponse est un fichier
    });

    // Création du lien temporaire pour ouvrir le PDF
    const blob = new Blob([response.data], { type: "application/pdf" });
    const fileUrl = URL.createObjectURL(blob);
    
    // Ouvre le PDF dans un nouvel onglet
    window.open(fileUrl, "_blank");
    
    // Nettoyage de la mémoire après un court délai
    setTimeout(() => URL.revokeObjectURL(fileUrl), 100);
    
  } catch (error) {
    console.error("Erreur lors de la génération du PDF:", error);
    alert("Impossible de générer le rapport. Vérifiez votre connexion ou vos accès.");
  }
};
</script>

 
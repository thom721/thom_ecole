<template>
  <div class="text-slate-500 min-h-screen">
    <div class="max-w-7xl mx-auto p-2 sm:px-6 lg:px-8 gap-8">
      
      <div class="flex flex-col md:flex-row w-full gap-8 mt-4">
        <div class="p-4 bg-white rounded-lg border w-full shadow-sm">
          <h2 class="text-xl  text-center border-b pb-2 mb-4">📊 Rapport Global</h2> 
          <div class="flex items-center gap-12 mb-4">
            <p class="text-xl ">- Rapport</p>
            <div class="flex-1">
              <label class="block text-sm">Type</label>
              <select v-model="forms.global.type" class="input-select">
                <option value="" disabled>Choisir le type</option>
                <option value="Global">Global</option>
                <option value="Livres">Livres</option>
                <option value="Tissus">Tissus</option>
                <option value="Fournitures">Fournitures</option>
                <option value="Arriéré">Arriéré</option>
                <option value="Dépense">Dépense</option>
              </select>
            </div>
          </div> 
            <div class="w-full mt-2">
              <label class="block text-sm">Début</label>
              <input type="date" v-model="forms.global.date_debut" class="input-field" />
            </div>

            <div class="w-full mt-2">
              <label class="block text-sm">Fin</label>
              <input type="date" v-model="forms.global.date_fin" class="input-field" />
            </div>
          <!-- </div> -->
          <div class="mt-4 flex justify-end">
            <button @click="submitPdf('/print-global-repport', forms.global)" class="bg-slate-800 text-white px-4 py-1 rounded">Imprimer</button>
          </div>
        </div>
      
       <div class="w-full p-4 border rounded shadow-sm bg-white">
          <h1 class="text-xl  text-center border-b pb-2 mb-4">Rapports Financiers 💰</h1>
          <p class="py-2 text-lg">- Rapport des paiements des élèves</p>
          <div class="px-4 space-y-3">
            <div>
              <label class="text-sm">Classe</label>
              <select v-model="forms.payment.classe" class="input-select">
                <option value="All">Toutes les classes</option>
                <option v-for="c in classes" :key="c.id" :value="c.nom_classe">{{ c.nom_classe }}</option>
              </select>
            </div> 
            <div> 
            <label class="text-sm">Année Académique</label>
             <select v-model="forms.payment.date_debut" class="input-select">
              <option value="" disabled>Choisir une Année</option>
              <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
            </select>
            </div>

            <div>
              <label class="text-sm">Versement</label>
              <select v-model="forms.payment.versement" class="input-select">
                <option value="tous les Versements">Tous les Versements</option>
                <option v-for="v in versements" :key="v" :value="v">{{ v }}</option>
              </select>
            </div>
            <div class="flex justify-end">
              <button @click="submitPdf('/print-rapport-paiement', forms.payment)" class="bg-slate-800 text-white px-4 py-1 rounded">Imprimer</button>
            </div>
          </div>
         
        </div>
      </div>

      <div class="flex flex-col md:flex-row justify-between gap-8 mt-4"> 
        <div class="w-full p-4 border rounded shadow-sm bg-white">
          <h1 class="text-xl  text-center border-b pb-2 mb-4">Rapports pédagogique 🎓</h1>
          <p class="py-2 text-lg">- Évaluation Mensuel / Annuel</p>
          <div class="space-y-3">
            <div class="flex gap-2">
              <select v-model="forms.pedago.cycle" class="input-select">
                <option value="All">Tous les Cycles</option>
                <option v-for="n in niveau" :key="n.id" :value="n.id">{{ n.name }}</option>
              </select>
              <select v-model="forms.pedago.classe" class="input-select">
                   <option value="" disabled>Choisir Classe</option>
                <option value="Toutes les classes">Toutes les classes</option>
                 
               <option v-for="cls in getClassesByNiveau(forms.pedago.cycle)" 
                         :key="cls.id" 
                         :value="cls.id">
               {{ cls.nom_classe }}
               </option>
              </select>
            </div>
        
            <div class="flex jutify-between items-center">
                  <select v-model="forms.pedago.annee_ac" class="input-select">
                    <option value="" disabled>Choisir une Année</option>
                    <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
                  </select>
              <select v-model="forms.pedago.mois" class="input-select">
                   <option value="" disabled>Choisir le mois</option>
                <option value="Tous les mois">Tous les mois</option>
                 
               <option v-for="cls in mois_" 
                         :key="cls" 
                         :value="cls">
               {{ cls }}
               </option>
              </select>
            </div>
            <div class="flex justify-end items-center gap-2">
              <span class="text-sm">Avec Identifiant</span>
              <input type="checkbox" v-model="forms.pedago.identifiant">
              <button @click="submitPdf('/print-repport-pedagogique', forms.pedago)" class="bg-slate-800 text-white px-4 py-1 rounded ml-4">Imprimer</button>
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col md:flex-row justify-between gap-8 mt-4">
        
        <div class="w-full p-4 border rounded shadow-sm bg-white">
          <h1 class="text-xl  text-center border-b pb-2 mb-4">Rapports Administratifs 📂</h1>
          <p class=" text-sm mb-2">- Inscription des élèves</p>
          <div class="space-y-3 mb-6 bg-gray-50 p-2 rounded">
             <div class="flex gap-2">
               <select v-model="forms.admin.cycle" class="input-select text-xs">
                 <option value="All">Tous Cycles</option>
                 <option v-for="n in niveau" :key="n.id" :value="n.id">{{ n.name }}</option>
               </select>
               <select v-model="forms.admin.classe" class="input-select text-xs">
                 <option value="All">Toutes classes</option>
                  <option v-for="cls in getClassesByNiveau(forms.admin.cycle)" 
                         :key="cls.id" 
                         :value="cls.id">
               {{ cls.nom_classe }}</option>
                 
               </select>
             </div>
                  <div> 
            <label class="text-sm">Année Académique</label>
             <select v-model="forms.admin.annee_ac" class="input-select">
              <option value="" disabled>Choisir une Année</option>
              <option v-for="a in annee" :key="a.id" :value="a.id">{{ a.annee_academique }}</option>
            </select>
            </div>
             <button @click="submitPdf('/print-repport-register', forms.admin)" class="w-full bg-slate-700 text-white py-1 rounded text-sm">Imprimer Registre</button>
          </div>

          <p class=" text-sm mb-2">- Présence des élèves</p>
          <div class="flex flex-col gap-2 bg-gray-50 p-2 rounded">
            <div class="flex gap-2">
              <input type="date" v-model="forms.presence.date_debut" class="input-select text-xs" />
              <input type="date" v-model="forms.presence.date_fin" class="input-select text-xs" />
            </div>
            <button @click="submitPdf('/print-present-repport', forms.presence)" class="w-full bg-slate-700 text-white py-1 rounded text-sm">Imprimer Présences</button>
          </div>
        </div>

        <div class="w-full p-4 border rounded shadow-sm bg-white">
          <h1 class="text-xl  text-center border-b pb-2 mb-4">Rapports Disciplinaires 🚨</h1>
          <div class="space-y-4 py-4 text-center">
            <p class="text-slate-400">- Rapport des incidents et sanctions</p>
            <p class="text-slate-400">- Rapport du comportement des élèves</p>
            <div class="mt-4 p-4 border border-yellow-200 bg-yellow-50 rounded text-yellow-700 text-xs">
              Ces modules sont en attente de données disciplinaires.
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue';
import axios from 'axios';
  
const baseUrl = import.meta.env.VITE_APP_BASE_URL || '';

// Tous les formulaires regroupés
const forms = reactive({
  global: { type: '', date_debut: '', date_fin: '' },
  payment: { classe: 'All', date_debut: '', date_fin: '', versement: 'tous les Versements' },
  pedago: { cycle: 'All', classe: 'Toutes les classes', annee_ac: '', identifiant: false },
  admin: { cycle: 'All', classe: 'All', annee_ac: '', identifiant: false },
  presence: { date_debut: '', date_fin: '', classe: 'All' }
});

const versements = ["1er Versement", "2ème Versement", "3ème Versement", "4ème Versement"];
const mois_ =["Septembre", "Octobre", "Novembre", "Décembre", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août"]

import { useSchoolStore } from '@/stores/schoolStore';
import { storeToRefs } from 'pinia';

const schoolStore = useSchoolStore();
// storeToRefs permet de garder la réactivité
const { niveau, professeur, annee,classes,faculte,cours, loading } = storeToRefs(schoolStore);

onMounted(() => {
  schoolStore.fetchAllDependencies();
}); 
const getClassesByNiveau = (niveauId) => { 
  if (!niveauId || !classes.value) return [];  
  return classes.value.filter(c => c.niveau_id === niveauId);
};

/**
 * Fonction de soumission AXIOS pour PDF
 */
const submitPdf = async (endpoint, data) => {
  try {
    const token = localStorage.getItem("auth-token");
    const response = await axios.post(`${baseUrl}${endpoint}`, data, {
      headers: { 
        "Authorization": `Bearer ${token}`,
        "Accept": "application/pdf" 
      },
      responseType: 'blob'
    });

    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    window.open(url, '_blank');
    
    setTimeout(() => window.URL.revokeObjectURL(url), 100);
  } catch (error) {
    console.error("Erreur Impression:", error);
    alert("Erreur lors de la génération du document.");
  }
};
</script>
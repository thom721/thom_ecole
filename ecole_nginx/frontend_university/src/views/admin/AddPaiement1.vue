<template>
  <div class="p-6 bg-white rounded-lg shadow-sm">
    <div v-if="firstInfo" class="flex items-center gap-10 mb-6"> 
      <div class="flex-shrink-0">
        <img :src="profilePic" class="h-24 w-24 rounded-full border-2 border-gray-200 object-cover shadow-sm" />
      </div>
      
      <div class="flex flex-col gap-1"> <h2 class="text-2xl font-bold text-gray-800 tracking-tight leading-none">
          {{ firstInfo.identifiant }}
        </h2>
        <div class="text-lg text-gray-600 capitalize">
          {{ firstInfo.nom }} {{ firstInfo.prenom }}
        </div>
        <div class="text-sm font-semibold text-blue-700 bg-blue-50 px-3 py-1 rounded-full w-fit mt-1">
          {{ firstInfo.nom_classe }}
        </div>
      </div>
    </div>

    <hr class="border-gray-200 mb-8" />

    <div class="flex flex-row gap-8">
      <aside class="w-2/5 max-h-[500px] overflow-y-auto pr-4 flex flex-col gap-4 border-r border-gray-100">
        <button
          v-for="(data, index) in studentDataList"
          :key="index"
          @click="showInfoToPay(data, index)"
          :class="[
            'w-full py-4 px-4 rounded-xl font-bold transition-all duration-200 text-center border shadow-sm',
            selectedIndex === index 
              ? 'bg-blue-600 border-blue-600 text-white transform scale-[1.02]' 
              : 'bg-white border-gray-200 text-gray-500 hover:border-blue-300 hover:bg-blue-50'
          ]"
        >
          {{ data.annee_academique }}
        </button>
      </aside>

      <main class="w-3/5 bg-gray-50 rounded-2xl p-8 min-h-[400px] border border-gray-100">
        <div v-if="selectedIndex !== null">
          <h3 class="text-xl text-gray-700 font-bold mb-6 border-b pb-2">
            Paiement : {{ studentDataList[selectedIndex].annee_academique }}
          </h3>
          
          <div class="space-y-6">
             <div class="flex flex-col gap-2">
                <label class="text-sm font-bold text-gray-600 uppercase tracking-wide">Montant à verser</label>
                <input 
                  id="montant_verser"
                  type="number" 
                  class="w-full p-4 text-lg border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-0 outline-none transition-colors"
                  placeholder="0.00"
                />
             </div>
             </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center h-full text-gray-400 gap-4">
          <span class="text-5xl">💳</span>
          <p class="italic text-lg">Sélectionnez une année pour continuer</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import profileImage from '@/assets/icons/profile.png';

const profilePic = ref(profileImage);

// Props pour l'ID de l'étudiant
const props = defineProps(['etudiantId']);

// État
const studentDataList = ref([]);
const firstInfo = ref(null);
const selectedIndex = ref(null); 

// Fonction pour récupérer les données au chargement
const loadData = async () => {
  try {
    const response = await axios.get(`/fetch-data-with-payment-params/${props.etudiantId}`);
    const data = response.data.data;

    if (data && data.length > 0) {
      studentDataList.value = data;
      
      // Similaire à self.show_student_for_payment = response_data['data'][-1]
      const lastIndex = data.length - 1;
      firstInfo.value = data[lastIndex];

      // Déclenche le clic sur le dernier bouton automatiquement
      showInfoToPay(data[lastIndex], lastIndex);
    }
  } catch (error) {
    console.error("Erreur de chargement:", error);
  }
};

const showInfoToPay = (data, index) => {
  selectedIndex.value = index;
  console.log("Chargement des détails de paiement pour:", data.annee_academique);
  
  // Équivalent du setFocus sur montant_verser
  // On attend un cycle de rendu pour cibler l'input si présent
  setTimeout(() => {
    const input = document.querySelector('#montant_verser');
    if (input) input.focus();
  }, 50);
};

// Cycle de vie : chargement automatique
onMounted(() => {
     console.log("ID de l'étudiant reçu :", props.etudiantId);
  loadData();
});
 
</script>

<style scoped>
.identifiant { color: #555; font-weight: bold; }
.text-gray { color: #555; margin: 2px 0; }

.scroll-area {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  max-width: 150px;
}

.button-list { display: flex; flex-direction: column; gap: 10px; }

.year-btn {
  padding: 5px;
  text-align: center;
  border-radius: 5px;
  font-size: 14pt;
  font-weight: bold;
  border: 1px solid #ccc;
  background: white;
  color: #999;
  cursor: pointer;
  transition: all 0.2s;
}

.year-btn:hover {
  background: #00a7ee;
  border-color: #00a7ee;
  color: white;
}

.year-btn.active {
  background: #4385f5;
  border-color: #4385f5;
  color: white;
}


</style>
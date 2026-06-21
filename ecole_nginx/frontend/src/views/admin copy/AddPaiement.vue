<template>
  <div class="p-6 bg-white rounded-lg shadow-sm">
    <div v-if="firstInfo" class="flex items-center gap-10 mb-6"> 
      <div class="flex-shrink-0">
        <img :src="profilePic" class="h-24 w-24 rounded-full border-2 border-gray-200 object-cover shadow-sm" />
      </div>
      
      <div class="flex flex-col gap-1"> <h2 class="text-2xl  text-gray-800 tracking-tight leading-none">
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

    <div class="flex flex-row gap-8 mt-4">
      <aside class="w-2/5 max-h-[500px] overflow-y-auto pr-4 flex flex-col gap-4 border-r border-gray-100">
        <button
          v-for="(data, index) in studentDataList"
          :key="index"
          @click="showInfoToPay(data, index)"
          :class="[
            'w-full py-2 px-4 rounded-xl  transition-all duration-200 text-center border shadow-sm',
            selectedIndex === index 
              ? 'bg-blue-600 border-blue-600 text-white transform scale-[1.02] my-2 cursor-pointer' 
              : 'bg-white border-gray-200 text-gray-500 hover:border-blue-300 hover:bg-blue-50 my-2 cursor-pointer'
          ]"
        >
          {{ data.annee_academique }}
        </button>
      </aside>

      <main class="w-3/5 bg-gray-50 rounded-2xl p-8 min-h-[400px] border border-gray-100">
        <div v-if="selectedIndex !== null">
          <h3 class="text-xl text-gray-700  mb-4 pb-2">
            Paiement : {{ studentDataList[selectedIndex].annee_academique }}
          </h3>
           
             <PaymentDetails :details="dataFromBackend" :key="selectedIndex" />
             
        </div>
        <div v-else class="flex flex-col items-center justify-center h-full text-gray-400 gap-4">
          <span class="text-5xl">💳</span>
          <p class="italic text-lg">Sélectionnez une année pour continuer</p>
        </div>
      </main>
    </div>
  </div> 
  <!-- <div class="max-w-6xl mx-auto p-6 bg-slate-50 min-h-screen">
    
    <div class="bg-white rounded-3xl p-8 shadow-sm flex items-center gap-8 mb-10 border border-slate-100">
      <div class="h-24 w-24 bg-sky-100 rounded-full flex items-center justify-center text-sky-600">
        <i class="ri-user-3-fill text-5xl"></i>
      </div>
      <div>
        <h1 class="text-3xl font-black text-slate-800 tracking-tight">
          {{ dataForPayment[0]?.nom }} {{ dataForPayment[0]?.prenom }}
        </h1>
        <p class="text-slate-500 font-medium text-lg italic">{{ dataForPayment[0]?.identifiant }}</p>
      </div>
    </div> -->

    <!-- <div class="flex flex-col lg:flex-row gap-8">
      
      <div class="w-full lg:w-1/3 space-y-4">
        <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Années Académiques</h2>
        <button 
          v-for="(year, index) in dataForPayment" :key="index"
          @click="fetchPaymentDetails(index, year)"
          :class="[
            'w-full p-5 rounded-2xl  transition-all text-left flex justify-between items-center shadow-sm',
            openAccordionIndex === index ? 'bg-sky-600 text-white ring-4 ring-sky-100' : 'bg-white text-slate-600 hover:bg-slate-50'
          ]"
        >
          {{ year.annee_academique }}
          <i :class="openAccordionIndex === index ? 'ri-arrow-down-s-line' : 'ri-arrow-right-s-line'"></i>
        </button>
      </div>

 
    </div> -->
  <!-- </div> -->
</template>

<script setup>
import { ref, computed, reactive,onMounted } from 'vue';
import axios from 'axios'; 
import Swal from 'sweetalert2';
import profileImage from '@/assets/icons/profile.png';
import PaymentDetails from '@/components/PaymentDetails.vue';

const profilePic = ref(profileImage);

// --- PROPS ---
const props = defineProps({
    etudiantId: {
        type: [String, Number],
        required: true
    },
    dataForPay: {
        type: Object,
        default: () => ({})
    },
    paiements: {
        type: Object,
        default: () => ({})
    }
});
// État
const studentDataList = ref([]);
const firstInfo = ref(null);
const selectedIndex = ref(null); 
const dataFromBackend = ref([])

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

      showInfoToPay(data[lastIndex], lastIndex);
    }
  } catch (error) {
    console.error("Erreur de chargement:", error);
  }
};

const showInfoToPay = (data, index) => {
  if (selectedIndex.value === index) {
    selectedIndex.value = null;
    return;
  }
  selectedIndex.value = index;
  
  console.log("Chargement des détails de paiement pour:", data);
      const [startYear, endYear] = data.annee_academique.split('/');

    const anneFormat = startYear + '-' + endYear
    axios.get('/next-payment-step', {
        params: {
            niveau: data.niveauId,
            classe: data.classeId,
            annee_a: data.anneeId,
            etudiant: props.etudiantId, // Utilisation de la prop fusionnée
            annee_academique: anneFormat,
            faculte: data.faculte_id
        }
    })        .then((response) => { 
            if (response.status == 200) {
              console.log(response.data.data);
              // openAccordionIndex.value = index;
              dataFromBackend.value=response.data.data
              console.log(dataFromBackend.value);
              
            }
        })
        .catch((error) => {
            // Gère les erreurs ici
            if (error.response) {
                console.error("Erreur API :", error.response.data);
            } else {
                console.error("Erreur réseau ou autre :", error.message);
            }
        });
 
  setTimeout(() => {
    const input = document.querySelector('#montant_verser');
    if (input) input.focus();
  }, 50);
};

// Cycle de vie : chargement automatique
onMounted(() => { 
  console.log('chargement automatique');
  
  loadData();
});


 

// --- FORMULAIRE PRINCIPAL ---
const payDetail = reactive({
    identifiant: '',
    nom: '',
    prenom: '',
    etudiant_id: '',
    classe: '',
    annee_academique: '',
    devise: '',
    echeance: '',
    annee_academiquesId: '',
    paiement_details: {
        depot: '',           // Saisie utilisateur
        depot_et_avance: 0,  // Somme disponible (Dépôt + Avance précédente)
        montant: 0,          // Montant de l'échéance en cours
        total_verse: 0,
        total_annuel: 0,
        balance: 0,          // Ce qu'il reste à payer pour l'échéance cochée
        avance: 0,           // Le surplus qui restera pour la prochaine fois
    },
    mois: {},           // Stocke { "Janvier": true, "Février": false }
    accessoires: {}     // Stocke { "Uniforme": true }
});

 
const submitPayment = () => {
    payDetail.post('/post-payment-save', {
        onSuccess: (page) => {
            Swal.fire("Succès", "Paiement enregistré", "success");
          
        },
        onError: () => Swal.fire("Erreur", "Veuillez vérifier les champs", "error")
    });
};
 
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
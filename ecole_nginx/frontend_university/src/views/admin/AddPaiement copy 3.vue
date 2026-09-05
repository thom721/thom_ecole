<template>
  <div class="p-6 bg-[#161b22] rounded-lg shadow-sm">
    <div v-if="firstInfo" class="flex items-center gap-10 mb-6"> 
      <div class="flex-shrink-0">
        <img :src="profilePic" class="h-24 w-24 rounded-full border-2 border-gray-200 object-cover shadow-sm" />
      </div>
      
      <div class="flex flex-col gap-1"> <h2 class="text-2xl  text-gray-200 tracking-tight leading-none">
          {{ firstInfo.identifiant }}
        </h2>
        <div class="text-lg text-gray-400 capitalize">
          {{ firstInfo.nom }} {{ firstInfo.prenom }}
        </div>
        <div class="text-sm font-semibold text-blue-700 bg-blue-100 px-3 py-1 rounded-full w-fit mt-1">
          {{ firstInfo.nom_classe }}
        </div>
      </div>
    </div>

    <hr class="border-gray-600 mb-8 hidden md:block" />

    <div class="flex flex-col md:flex-row gap-8 mt-4">
      <!-- <aside class="w-2/5 max-h-[500px] overflow-y-auto pr-4 flex flex-col gap-4 border-r border-gray-600">
        <template v-for="(data, index) in studentDataList" :key="index">

          <button v-if="load_data_paiement != index"  
            @click="showInfoToPay(data, index)"
          class="w-full py-2 px-8 rounded-md  transition-all duration-200 text-center border shadow-sm cursor-pointer"
          :class="selectedIndex === index 
            ? 'text-[var(--accent)] border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_12%,transparent)]'
            : 'bg-[#1e2335] border-white/[0.07] text-[#7c83a0] hover:text-[#e8eaf0]'"
          :style="selectedIndex === index  ? { borderColor: 'var(--accent,#4f8ef7)', color: 'var(--accent,#4f8ef7)', background: 'rgba(79,142,247,0.1)' } : {}"
        >
            {{ data.annee_academique }} --{{ load_data_paiement }} + {{ index }}
          </button>
          <button v-else  
          class="w-full py-2 px-8 rounded-md  transition-all duration-200 text-center border shadow-sm cursor-pointer"
          :class="selectedIndex === index 
            ? 'text-[var(--accent)] border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_12%,transparent)]'
            : 'bg-[#1e2335] border-white/[0.07] text-[#7c83a0] hover:text-[#e8eaf0]'"
          :style="selectedIndex === index  ? { borderColor: 'var(--accent,#4f8ef7)', color: 'var(--accent,#4f8ef7)', background: 'rgba(79,142,247,0.1)' } : {}"
        >
            <span class="spin">{{ data.annee_academique }} --{{ load_data_paiement }} == {{ index }}</span>
          </button>
        </template>
      </aside> -->
 
      <aside class="w-2/5 max-h-[500px] overflow-y-auto pr-4 flex flex-col gap-4 border-r border-white/[0.07]">
        <button
          v-for="(data, index) in studentDataList"
          :key="index"
          @click="showInfoToPay(data, index)"
          class="w-full py-2.5 px-6 rounded-lg transition-all duration-200 text-center border
                shadow-sm cursor-pointer flex items-center justify-center gap-2"
          :class="selectedIndex === index
            ? 'border-[#4f8ef7] text-[#4f8ef7] bg-[#4f8ef7]/10'
            : 'bg-[#1e2335] border-white/[0.07] text-[#7c83a0] hover:text-[#e8eaf0] hover:border-white/20'"
        >
          <!-- Spinner visible uniquement pendant le chargement de CE bouton -->
          <svg
            v-if="load_data_paiement === index"
            class="w-3.5 h-3.5 animate-spin shrink-0"
            fill="none" viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>

          <span>{{ data.annee_academique }}</span>
        </button>
      </aside>
      <main class="w-3/5 bg-gray-750 rounded-2xl p-8 min-h-[400px] border border-gray-700 w-full" >
        <div v-if="selectedIndex !== null">
          <h3 class="text-xl text-gray-300  mb-4 pb-2">
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
const load_data_paiement = ref(null)

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
  }finally{load_data_paiement.value=null}
};

const showInfoToPay = (data, index) => {
  // if (selectedIndex.value === index) {
  //   selectedIndex.value = null;
  //   return;
  // }
  print(index)
  load_data_paiement.value=index
  selectedIndex.value = index;
  
      // console.log("Chargement des détails de paiement pour:", data);
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
            // console.log(response);
       load_data_paiement.value=null
            if (response.statusText == 'OK') {
              // console.log(response.data.data);?
              // openAccordionIndex.value = index;
              dataFromBackend.value=response.data.data
              console.log(dataFromBackend.value);
              
            }
           
        })
        .catch((error) => {
          load_data_paiement.value=null
            if (error.response) {
                console.error("Erreur API :", error.response.data);
            } else {
                console.error("Erreur réseau ou autre :", error.message);
            }
        })
        ;
 
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
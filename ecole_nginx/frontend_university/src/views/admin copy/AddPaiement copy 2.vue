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
             <!-- <div class="flex flex-col gap-2">
                <label class="text-sm font-bold text-gray-600 uppercase tracking-wide">Montant à verser</label>
                <input 
                  id="montant_verser"
                  type="number" 
                  class="w-full p-4 text-lg border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-0 outline-none transition-colors"
                  placeholder="0.00"
                />
             </div> -->
             <PaymentDetails :details="dataFromBackend" :key="openAccordionIndex" />
             </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center h-full text-gray-400 gap-4">
          <span class="text-5xl">💳</span>
          <p class="italic text-lg">Sélectionnez une année pour continuer</p>
        </div>
      </main>
    </div>
  </div> 
  <div class="max-w-6xl mx-auto p-6 bg-slate-50 min-h-screen">
    
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
    </div>

    <div class="flex flex-col lg:flex-row gap-8">
      
      <div class="w-full lg:w-1/3 space-y-4">
        <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Années Académiques</h2>
        <button 
          v-for="(year, index) in dataForPayment" :key="index"
          @click="fetchPaymentDetails(index, year)"
          :class="[
            'w-full p-5 rounded-2xl font-bold transition-all text-left flex justify-between items-center shadow-sm',
            openAccordionIndex === index ? 'bg-sky-600 text-white ring-4 ring-sky-100' : 'bg-white text-slate-600 hover:bg-slate-50'
          ]"
        >
          {{ year.annee_academique }}
          <i :class="openAccordionIndex === index ? 'ri-arrow-down-s-line' : 'ri-arrow-right-s-line'"></i>
        </button>
      </div>

      <div class="w-full lg:w-2/3">
        

        <!-- <div v-if="openAccordionIndex !== null" class="bg-white rounded-3xl p-8 shadow-xl border border-slate-100 animate-in fade-in slide-in-from-bottom-4">
          
          <form @submit.prevent="submitPayment" class="space-y-8">
            
            <div class="bg-slate-50 p-6 rounded-2xl border-2 border-dashed border-slate-200">
              <label class="block text-sm font-bold text-slate-500 uppercase mb-2">Montant du versement ({{ payDetail.devise }})</label>
              <input 
                v-model="payDetail.paiement_details.depot"
                @input="handleDepotInput"
                type="number"
                class="w-full bg-transparent text-4xl font-black text-sky-600 outline-none placeholder:text-slate-300"
                placeholder="0.00"
              />
              <div v-if="lastAvance > 0" class="mt-2 text-amber-600 font-bold flex items-center gap-2">
                <i class="ri-information-fill"></i> Avance disponible : {{ lastAvance }} {{ payDetail.devise }}
              </div>
            </div>

            <div v-if="accessoiresList.length > 0">
              <h3 class="text-slate-800 font-bold mb-4 flex items-center gap-2 text-lg">
                <i class="ri-shopping-bag-3-line text-sky-500"></i> Accessoires
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <label v-for="acc in accessoiresList" :key="acc.type_daccessoire"
                  class="flex items-center justify-between p-4 rounded-xl border-2 cursor-pointer transition-all hover:bg-slate-50"
                  :class="payDetail.accessoires[acc.type_daccessoire] ? 'border-sky-500 bg-sky-50' : 'border-slate-100'"
                >
                  <div class="flex items-center gap-3">
                    <input type="checkbox" v-model="payDetail.accessoires[acc.type_daccessoire]" class="w-5 h-5 rounded text-sky-600" />
                    <span class="font-bold text-slate-700">{{ acc.type_daccessoire }}</span>
                  </div>
                  <span class="text-sky-600 font-black">{{ acc.prix }}</span>
                </label>
              </div>
            </div>

            <div v-if="montant_par[payDetail.echeance]">
              <h3 class="text-slate-800 font-bold mb-4 flex items-center gap-2 text-lg">
                <i class="ri-calendar-check-line text-sky-500"></i> Échéances ({{ payDetail.echeance }})
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div v-for="(key, idx) in Object.keys(montant_par[payDetail.echeance])" :key="key"
                  class="relative p-4 rounded-xl border-2 flex items-center justify-between"
                  :class="[
                    indexPayMont.includes(key) ? 'bg-slate-100 border-transparent opacity-50' : 
                    (payDetail.mois[key] ? 'border-green-500 bg-green-50' : 'border-slate-100')
                  ]"
                >
                  <div>
                    <p class="font-bold text-slate-700 capitalize">{{ key.replace('_', ' ') }}</p>
                    <p class="text-xs text-slate-400">{{ montant_par[payDetail.echeance][key] }} {{ payDetail.devise }}</p>
                  </div>
                  
                  <i v-if="indexPayMont.includes(key)" class="ri-checkbox-circle-fill text-green-500 text-2xl"></i>
                  <input 
                    v-else
                    type="checkbox"
                    v-model="payDetail.mois[key]"
                    @change="handleEcheanceCheck(key, idx, payDetail.echeance)"
                    :disabled="idx > chekedIndex"
                    class="w-6 h-6 rounded-full text-green-600 border-slate-300 disabled:bg-slate-200"
                  />
                </div>
              </div>
            </div>

            <div class="pt-6 border-t border-slate-100 flex justify-between items-center">
              <div>
                <p class="text-sm text-slate-400 font-bold uppercase tracking-widest">Reste à payer (Balance)</p>
                <p class="text-2xl font-black" :class="payDetail.paiement_details.balance > 0 ? 'text-rose-500' : 'text-slate-800'">
                  {{ payDetail.paiement_details.balance }} {{ payDetail.devise }}
                </p>
              </div>
              <button 
                type="submit" 
                class="bg-sky-600 text-white px-10 py-4 rounded-2xl font-black text-lg hover:bg-sky-700 hover:-translate-y-1 transition-all shadow-lg shadow-sky-200 active:scale-95"
              >
                Valider le Paiement
              </button>
            </div>

          </form>
        </div>

        <div v-else class="h-full flex flex-col items-center justify-center text-slate-300 border-4 border-dashed border-slate-100 rounded-3xl p-20 text-center">
          <i class="ri-bank-card-line text-8xl mb-4"></i>
          <p class="text-xl font-bold">Sélectionnez une année académique<br>pour gérer les paiements</p>
        </div> -->
      </div>
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
  selectedIndex.value = index;
  console.log("Chargement des détails de paiement pour:", data);
      const [startYear, endYear] = data.annee_academique.split('/');

    const anneFormat = startYear + '-' + endYear
    axios.get(`${url}/next-payment-step`, {
        params: {
            niveau: data.niveauId,
            classe: data.classeId,
            annee_a: data.anneeId,
            etudiant: props.etudiantId, // Utilisation de la prop fusionnée
            annee_academique: anneFormat,
            faculte: data.faculte_id
        }
    })        .then((response) => {
            // indexPayMont.value = ''
            // chekedIndex.value = 0
            // lastAvance.value = 0
            // balances.value = 0
            // console.log(response.data.data);
            // infoDataForPayment.value = null;
            if (response.status == 200) {
              console.log(response.data.data);
              dataFromBackend.value=response.data.data
              console.log(dataFromBackend.value);
              
                // dataNotFount.value = response.data.data
                
                // if (response.data.data !== 'null') {


                //     infoDataForPayment.value = response.data.data
                //     payDetail.niveau_id = infoDataForPayment.value.id_niveau
                //     payDetail.etudiant_id = infoDataForPayment.value.studentId
                //     payDetail.studentId = infoDataForPayment.value.studentId
                //     payDetail.identifiant = infoDataForPayment.value.identifiant
                //     payDetail.classe = infoDataForPayment.value.classeId
                //     payDetail.nom = infoDataForPayment.value.nom
                //     payDetail.prenom = infoDataForPayment.value.prenom

                //     payDetail.echeance = infoDataForPayment.value.echeance
                //     nbecheance.value = Array.from({ length: parseInt(infoDataForPayment.value.nb_echeance, 10) || 0 }, () => "");
                //     payDetail.paiement_details.montant = infoDataForPayment.value.montant

                //     payDetail.devise = infoDataForPayment.value.devise
                //     annee_aca.value = infoDataForPayment.value.annee_academique
                //     payDetail.annee_academique = infoDataForPayment.value.annee_academique
                //     payDetail.annee_academiquesId = infoDataForPayment.value.annee_academiquesId
                //     payDetail.annee_detude = infoDataForPayment.value.classe_actuelle

                //     dataPayementAfterFetc.value = infoDataForPayment.value.paiement_details
                //     payedMonth.value = infoDataForPayment.value.mois

                //     montant_par.value = JSON.parse(infoDataForPayment.value.montant_par)
                //     paying.value = infoDataForPayment.value.montant_par
                //     accessoiresValue.value = JSON.parse(infoDataForPayment.value.accessoires)

                //     // if (payedMonth.value != '' && infoDataForPayment.value.mois != null) {

                //     //     const pay = JSON.parse(payedMonth.value)

                //     //     const entries = Object.entries(pay.mois);


                //     //     const entries1 = Object.keys(pay.mois);

                //     //     const details = JSON.parse(infoDataForPayment.value.paiement_details)

                //     //     const payment_info = Object.entries(details.paiement_details.info_paiement)
                //     //     const payment_info_keys = Object.keys(details.paiement_details.info_paiement)

                //     //     const checkPayFor = JSON.parse(paying.value)


                //     //     lastIndex.value = entries1.length
                //     //     nb_echeance.value = infoDataForPayment.value.nb_echeance

                //     //     indexPayMont.value = entries1

                //     //     if (payedMonth.value != null) {
                //     //         const details = JSON.parse(dataPayementAfterFetc.value)

                //     //         const payment_info = Object.entries(details.paiement_details.info_paiement)
                //     //         // const payment_info = Object.entries(details.paiement_details.info_paiement)
                //     //         let avance_pay = 0;

                //     //         const payment_info_accessoire = Object.values(details.paiement_details.accessoires)
                //     //         //   console.log(payment_info_accessoire[0], payAccessoires.value, selectedKeys,);

                //     //         // console.log(JSON.stringify(payment_info_accessoire));
                //     //         payAccessoires.value = payment_info_accessoire[0]
                //     //         for (const element of payment_info[payment_info.length - 1]) {
                //     //             avance_pay = element.avance
                //     //             lastAvance.value = avance_pay
                //     //             balances.value = element.balance
                //     //             balances_montant.value = element.montant
                //     //         }
                //     //         // payDetail.paiement_details.depot_et_avance = avance_pay + parseFloat(payDetail.paiement_details.depot)
                //     //     } else {
                //     //         // payDetail.paiement_details.depot_et_avance = parseFloat(payDetail.paiement_details.depot)
                //     //     }



                //     // }
                // }
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
     console.log("ID de l'étudiant reçu :", props.etudiantId);
  loadData();
});




const url = import.meta.env.VITE_APP_BASE_URL;
const dataForPayment = ref(props.dataForPay);
const openAccordionIndex = ref(null);
const infoDataForPayment = ref(null);

// Données calculées après le fetch
const montant_par = ref({});
const indexPayMont = ref([]); // Liste des mois déjà payés (venant du serveur)
const chekedIndex = ref(0);   // Index de la prochaine échéance cochable
const lastAvance = ref(0);    // Reliquat du paiement précédent
const accessoiresList = ref([]);

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

// --- LOGIQUE DE CALCUL ---

// 1. Quand l'utilisateur saisit un montant
const handleDepotInput = () => {
    const depot = parseFloat(payDetail.paiement_details.depot) || 0;
    // La somme disponible est le nouveau dépôt + l'avance stockée en base de données
    payDetail.paiement_details.depot_et_avance = depot + lastAvance.value;
    
    // Reset des sélections si le montant change pour éviter les erreurs
    payDetail.mois = {};
    chekedIndex.value = indexPayMont.value.length; 
};

// 2. Quand on coche une échéance
const handleEcheanceCheck = (key, index, type) => {
    const montantEcheance = parseFloat(montant_par.value[type][key]);

    if (payDetail.mois[key]) {
        // Si on coche
        if (payDetail.paiement_details.depot_et_avance >= montantEcheance) {
            payDetail.paiement_details.depot_et_avance -= montantEcheance;
            payDetail.paiement_details.avance = payDetail.paiement_details.depot_et_avance;
            payDetail.paiement_details.balance = 0;
            chekedIndex.value = index + 1;
        } else {
            // Pas assez de fonds pour couvrir l'échéance complète
            const fondsRestants = payDetail.paiement_details.depot_et_avance;
            payDetail.paiement_details.balance = montantEcheance - fondsRestants;
            payDetail.paiement_details.avance = 0;
            payDetail.paiement_details.depot_et_avance = 0;
            chekedIndex.value = 999; // Bloquer les suivantes
        }
    } else {
        // Si on décoche (Logique simplifiée : on reset pour recalculer proprement)
        handleDepotInput();
    }
};

// --- ACTIONS API ---

const fetchPaymentDetails = (index, data) => {
    if (openAccordionIndex.value === index) {
        openAccordionIndex.value = null;
        return;
    }

    const anneFormat = data.annee_academique.replace('/', '-');
    
    axios.get(`${url}/api/next-payment-step`, {
        params: {
            niveau: data.niveauId,
            classe: data.classeId,
            annee_a: data.anneeId,
            etudiant: data.studentId,
            annee_academique: anneFormat,
        }
    }).then(res => {
        const d = res.data.data;
        infoDataForPayment.value = d;
        openAccordionIndex.value = index;

        // Hydratation du formulaire
        payDetail.identifiant = d.identifiant;
        payDetail.etudiant_id = d.studentId;
        payDetail.devise = d.devise;
        payDetail.echeance = d.echeance;
        payDetail.annee_academiquesId = d.annee_academiquesId;

        // Parsing des données JSON
        montant_par.value = JSON.parse(d.montant_par);
        accessoiresList.value = JSON.parse(d.accessoires);
        
        // Calcul des mois déjà réglés
        if (d.mois) {
            const paye = JSON.parse(d.mois);
            indexPayMont.value = Object.keys(paye.mois);
            chekedIndex.value = indexPayMont.value.length;
        }

        // Récupération de l'avance historique
        const details = JSON.parse(d.paiement_details);
        const info = details.paiement_details.info_paiement;
        const lastRecord = info[info.length - 1];
        lastAvance.value = lastRecord ? parseFloat(lastRecord.avance) : 0;
    });
};

const submitPayment = () => {
    payDetail.post(`${url}/api/post-payment-save`, {
        onSuccess: (page) => {
            Swal.fire("Succès", "Paiement enregistré", "success");
            openAccordionIndex.value = null;
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
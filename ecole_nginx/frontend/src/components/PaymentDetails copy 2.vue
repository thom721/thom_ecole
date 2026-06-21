<template>
  <div class="" v-if="details">
    
    <div class="frame-1">
      <span class="flex justify-end text-[18px] text-slate-400">
        {{ details.nom_classe }} {{ displayAide }}
      </span>
    </div>

    <div class="frame-2">
      <div v-if="!status" class="text-slate-400 text-[18x]">
        {{ avance_sur }}
      </div>
      <div v-else class="text-green-500 text-md">
        Acquitté
      </div>

      <InputLabel >Montant</InputLabel>
      <input 
        ref="montantInput"
        type="number" 
        v-model="montant_verser"
        class="field-input w-full"
        :class="{ 'hidden': details === 'null' }"
        @keyup.enter="handleEnter"
      />
      
      <div v-if="details === 'null'" class="error-msg">
        Les paramètres de paiement ne sont pas définis pour cette classe.
      </div>
    </div>

    <div v-for="(check, name) in accessoire_checkboxes" :key="'acc-' + name" class="frame-accessoire">
      <label class="label-acc">{{ name }} ({{ check.prix }})</label>
      <input 
        type="checkbox" 
        v-model="check.selected"
        :disabled="check.alreadyPaid"
        :class="{ 'qcheckbox-paid': check.alreadyPaid }"
      />
    </div>

    <div v-for="(item, key) in sortedEcheances" :key="'ech-' + key" class="flex flex-col space-y-6">
    <div class="flex justify-between items-center m-6">
       <label class="rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500 text-md -4">
        {{ formatEcheanceLabel(item, key) }}
      </label>
      <input 
        type="checkbox" 
        v-model="item.selected"
        :disabled="item.alreadyPaid"
        :class="{ 'qcheckbox-paid': item.alreadyPaid }"
      />
    </div>
    </div>

    <div class="flex justify-end mt-4">
      <button 
        class="btn-outline-green"
        :disabled="status"
        @click="validerPaiement"
      >
        Valider
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import InputLabel from "@/components/InputLabel.vue";
const props = defineProps({
  details: Object // Reçoit l'objet JSON que tu m'as montré au début
});

// États internes (équivalents aux variables self.xxx de PySide)
const status = ref(false);
const balanse = ref(0);
const avance = ref(0);
const avance_sur = ref('');
const montant_verser = ref('');
const must_refresh_paiement = ref(false);
const accessoire_checkboxes = ref({});
const echeance_checkboxes = ref({});
const montantInput = ref(null);

// -- LOGIQUE INITIALE (show_last_payment_and_details_if_exist) --

const initPaymentLogic = () => {
     console.log('props.details');
     console.log(props.details);
     if (!props.details && props.details.length < 1)return
  const d = typeof props.details.paiement_details === 'string' 
            ? JSON.parse(props.details.paiement_details) 
            : props.details.paiement_details;


  const info_paiement = d?.paiement_details?.info_paiement || {};
  const details_etudiant = d?.paiement_details?.details_etudiant || {};
  const aide = props.details.aide_financiere !== 'Aucune' ? props.details.aide_financiere : '';
  
  let latest_entry = null;

  // Tri des dates à l'identique (DD-MM-YYYY HH:mm)
  const dates = Object.keys(info_paiement);
  if (dates.length > 0) {
    const sortedDates = dates.sort((a, b) => {
        const parseDate = (s) => {
            const [d, t] = s.split(' ');
            const [day, month, year] = d.split('-');
            return new Date(`${year}-${month}-${day}T${t}`);
        };
        return parseDate(a) - parseDate(b);
    });

    for (let i = sortedDates.length - 1; i >= 0; i--) {
      const entry = info_paiement[sortedDates[i]];
      if (entry.status !== 'retourné') {
        latest_entry = entry;
        break;
      }
    }
  }

  // Calcul Avance/Balance
  if (latest_entry && (latest_entry.total_verse || 0) < (latest_entry.total_annuel || 0)) {
    avance.value = latest_entry.depot_et_avance;
    balanse.value = latest_entry.balance;

    const month_pays = d.paiement_details.mois || {};
    if (Object.keys(month_pays).length > 0) {
      const latest_pay = Object.keys(month_pays).sort().pop();
      const idx = parseInt(latest_pay.split('_')[1]);
      const type = latest_pay.split('_')[0];
      avance_sur.value = `Avance de ${avance.value}${props.details.devise} sur le ${idx + 2}${idx === -1 ? 're' : 'ème'} ${type}`;
    } else {
      avance_sur.value = `Avance de ${avance.value}${props.details.devise} sur le 1re Versement`;
    }
  } else if (latest_entry && latest_entry.total_verse >= latest_entry.total_annuel) {
    status.value = true;
  }

  // Initialisation Accessoires
  const accessoiresData = props.details.accessoires || [];
  const accPayes = d.paiement_details?.accessoires?.accessoire || [];
  
  accessoiresData.forEach(acc => {
    accessoire_checkboxes.value[acc.type_daccessoire] = {
      prix: acc.prix,
      selected: accPayes.includes(acc.type_daccessoire),
      alreadyPaid: accPayes.includes(acc.type_daccessoire)
    };
  });

  // Initialisation Échéances (Triées par index split('_')[1])
  const echeancesConfig = props.details.montant_par?.[props.details.echeance] || {};
  const moisPayes = d.paiement_details.mois || {};

  Object.keys(echeancesConfig).forEach(key => {
    echeance_checkboxes.value[key] = {
      montant: echeancesConfig[key],
      selected: moisPayes.hasOwnProperty(key),
      alreadyPaid: moisPayes.hasOwnProperty(key),
      index: parseInt(key.split('_')[1])
    };
  });
};

// -- COMPUTED & HELPERS --

const displayAide = computed(() => {
    return props.details.aide_financiere !== 'Aucune' ? `(${props.details.aide_financiere})` : '';
});

const sortedEcheances = computed(() => {
  return Object.fromEntries(
    Object.entries(echeance_checkboxes.value).sort((a, b) => a[1].index - b[1].index)
  );
});

const formatEcheanceLabel = (item, key) => {
  const name = key.split('_')[0];
  if (props.details.echeance !== 'mois') {
    return `${item.index}${item.index === 1 ? 'er' : 'ème'} ${props.details.echeance} - (${item.montant} ${props.details.devise})`;
  }
  return `${name} - (${item.montant} ${props.details.devise})`;
};

const validerPaiement = () => {
    // Collecte les données pour l'envoi (équivalent de self.valider_paiement)
    const payload = {
        montant: montant_verser.value,
        accessoires: Object.fromEntries(Object.entries(accessoire_checkboxes.value).map(([k,v]) => [k, v.selected])),
        mois: Object.fromEntries(Object.entries(echeance_checkboxes.value).map(([k,v]) => [k, v.selected])),
    };
    console.log("Validation du paiement...", payload);
};

onMounted(() => {
  initPaymentLogic();
  if (montantInput.value) montantInput.value.focus();
});
</script>

<style scoped>
/* Mimic du StyleSheet PySide */
/* .main-container { padding: 10px 10px 60px 10px; max-width: 650px; }
.frame-1 { border-bottom: 1px solid #aaa; text-align: right; margin-bottom: 10px; }
.label-value { color: #777; font-size: 15pt; }

.frame-2 { padding: 20px 20px 20px 20px; }
.label-avance { font-size: 12pt; margin-bottom: 5px; }
.label-montant { color: #777; display: block; }
.qline-edit { width: 100%; border: 1px solid #ccc; padding: 5px; }

.frame-accessoire, .frame-echeance { 
    display: flex; 
    justify-content: space-between; 
    padding: 10px 60px 10px 20px; 
}
.label-acc, .label-echeance { color: #777; }

.btn-valider {
    float: right;
    color: #007bff; border: 1px solid #007bff; border-radius: 5px;
    padding: 5px 10px; font-size: 14pt; font-weight: bold; cursor: pointer;
}
.btn-valider:hover { background-color: #007bff; color: white; }
.btn-valider:disabled { opacity: 0.5; cursor: not-allowed; }
*/
.qcheckbox-paid { accent-color: #40C057; }
.error-msg { color: red; word-wrap: break-word; }
.status-acquitte { color: #40C057; font-weight: bold; } 
</style>
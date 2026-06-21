<template>
  <div class="payment-container" v-if="details">
    <div class="header-frame">
      <h2 class="text-gray">
        {{ details.nom_classe }} 
        <span v-if="details.aide_financiere && details.aide_financiere !== 'Aucune'">
          ({{ details.aide_financiere }})
        </span>
      </h2>
    </div>

    <div class="amount-frame">
      <div v-if="!isAcquitte" class="avance-label">
        {{ labelAvanceSur }}
      </div>
      <div v-else class="status-acquitte">Acquitté</div>

      <label class="text-gray">Montant à verser</label>
      <input 
        type="number" 
        v-model="form.montant" 
        class="payment-input"
        :disabled="isAcquitte"
        placeholder="Saisir le montant..."
      />
    </div>

    <div class="accessoires-section" v-if="accessoiresList.length > 0">
      <div v-for="acc in accessoiresList" :key="acc.type_daccessoire" class="checkbox-item">
        <label :class="{ 'text-gray': true, 'disabled': isAccessoirePaye(acc.type_daccessoire) }">
          <input 
            type="checkbox" 
            :value="acc.type_daccessoire"
            v-model="form.selectedAccessoires"
            :disabled="isAccessoirePaye(acc.type_daccessoire)"
          />
          {{ acc.type_daccessoire }} ({{ acc.prix }} {{ details.devise }})
        </label>
      </div>
    </div>

    <div class="echeance-section">
      <div v-for="(montant, key, index) in sortedEcheances" :key="key" class="checkbox-item">
        <label :class="{ 'text-gray': true, 'disabled': isEcheancePayee(key) }">
          <input 
            type="checkbox" 
            :value="key"
            v-model="form.selectedEcheances"
            :disabled="isEcheancePayee(key)"
          />
          <span v-if="details.echeance !== 'mois'">
            {{ index + 1 }}{{ index === 0 ? 'er' : 'ème' }} {{ details.echeance }} - ({{ montant }} {{ details.devise }})
          </span>
          <span v-else>
            {{ key.split('_')[0] }} - ({{ montant }} {{ details.devise }})
          </span>
        </label>
      </div>
    </div>

    <div class="button-frame">
      <button 
        @click="validerPaiement" 
        class="btn-valider"
        :disabled="isAcquitte || loading"
      >
        {{ loading ? 'Enregistrement...' : 'Valider' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const props = defineProps({
  details: Object // Vos données JSON reçues de l'API
});

const loading = ref(false);
const form = ref({
  montant: '',
  selectedAccessoires: [],
  selectedEcheances: []
});

// --- LOGIQUE DE CALCUL (équivalent Python) ---

// 1. Extraire le dernier paiement valide (status != 'retourné')
const latestEntry = computed(() => {
  const info = props.details.paiement_details?.info_paiement;
  if (!info || Object.keys(info).length === 0) return null;

  const sortedDates = Object.keys(info).sort((a, b) => {
    return new Date(a.split(' ').reverse().join(' ')) - new Date(b.split(' ').reverse().join(' '));
  });

  for (let i = sortedDates.length - 1; i >= 0; i--) {
    const entry = info[sortedDates[i]];
    if (entry.status !== 'retourné') return entry;
  }
  return null;
});

// 2. Vérifier si c'est acquitté
const isAcquitte = computed(() => {
  if (!latestEntry.computed) return false;
  return latestEntry.value.total_verse >= latestEntry.value.total_annuel;
});

// 3. Formater le label d'avance (Logic de `self.avance_sur`)
const labelAvanceSur = computed(() => {
  if (isAcquitte.value) return "Acquitté";
  
  const avance = latestEntry.value?.depot_et_avance || 0;
  const dev = props.details.devise;
  const paysPresents = props.details.paiement_details?.mois || {};
  const keys = Object.keys(paysPresents);

  if (keys.length > 0) {
    const latestPayKey = keys.sort().pop();
    const nextIndex = parseInt(latestPayKey.split('_')[1]) + 2; // +1 pour l'index, +1 pour le suivant
    return `Avance de ${avance} ${dev} sur le ${nextIndex}${nextIndex === 1 ? 're' : 'ème'} versement`;
  } else {
    return `Avance de ${avance} ${dev} sur le 1er Versement`;
  }
});

// 4. Trier les échéances par index (Logic `key=lambda x: int(x[0].split('_')[1])`)
const sortedEcheances = computed(() => {
  const type = props.details.echeance; // 'Versement' ou 'mois'
  const source = props.details.montant_par?.[type] || {};
  
  return Object.fromEntries(
    Object.entries(source).sort((a, b) => {
      return parseInt(a[0].split('_')[1]) - parseInt(b[0].split('_')[1]);
    })
  );
});

// 5. Helpers pour désactiver les cases déjà payées
const isAccessoirePaye = (name) => {
  return props.details.paiement_details?.accessoires?.accessoire?.includes(name);
};

const isEcheancePayee = (key) => {
  return props.details.paiement_details?.mois?.hasOwnProperty(key);
};

// --- ACTION ---
const validerPaiement = () => {
  loading.value = true;
  // Simuler l'envoi à l'API (api_handler_.enregistrer_paiement)
  const payload = {
    montant: form.value.montant,
    studentId: props.details.studentId,
    accessoires: form.value.selectedAccessoires,
    echeances: form.value.selectedEcheances
  };
  console.log("Envoi du paiement:", payload);
};
</script>

<style scoped>
.payment-container { padding: 20px; max-width: 650px; border: 1px solid #ddd; }
.text-gray { color: #777; }
.header-frame { border-bottom: 1px solid #aaa; margin-bottom: 15px; }
.payment-input { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; }
.checkbox-item { display: flex; align-items: center; margin: 10px 0; }
.disabled { color: #40C057; text-decoration: line-through; opacity: 0.7; }
.btn-valider { 
  background: white; color: #007bff; border: 1px solid #007bff; 
  padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;
}
.btn-valider:hover { background: #007bff; color: white; }
</style>
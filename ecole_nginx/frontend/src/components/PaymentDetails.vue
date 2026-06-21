<template>
  <div v-if="details">

    <!-- En-tête -->
    <div class="flex justify-end text-[14px] text-[#7d8590] pb-3 border-b border-white/[0.06] mb-4">
      {{ details.nom_classe }}
      <span v-if="displayAide" class="ml-1.5 text-[#7aaeff]">{{ displayAide }}</span>
    </div>

    <!-- Statut / Avance / Erreur -->
    <div class="mb-4">
      <div v-if="details === 'null'"
        class="text-[13px] text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
        ⚠ Les paramètres de paiement ne sont pas définis pour cette classe.
      </div>
      <div v-else-if="status"
        class="text-[13px] text-green-400 bg-green-500/10 border border-green-500/20 rounded-lg px-3 py-2 font-medium">
        ✓ Acquitté — paiement complet
      </div>
      <div v-else-if="avance_sur"
        class="text-[13px] text-[#d29922] bg-yellow-500/10 border border-yellow-500/20 rounded-lg px-3 py-2">
        {{ avance_sur }}
      </div>
    </div>

    <!-- Champ montant -->
    <div v-if="details !== 'null'" class="mb-5">
      <label class="text-[11px] font-medium uppercase tracking-[0.06em] text-[#3d4d62] block mb-1.5">
        Montant à verser
      </label>
      <input
        id="montant_verser"
        ref="montantInput"
        type="number"
        v-model="montant_verser"
        min="0"
        placeholder="0"
        :disabled="status"
        @keyup.enter="validerPaiement"
        class="w-full bg-[#0d1017] border border-white/[0.08] rounded-lg px-3 py-2
               text-[13px] text-[#c9d1d9] placeholder-[#2e3a4a] outline-none
               focus:border-[#4a7cff]/40 focus:ring-2 focus:ring-[#4a7cff]/[0.08]
               disabled:opacity-50 disabled:cursor-not-allowed
               transition-all duration-150
               [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
      />
    </div>

    <!-- Accessoires -->
    <div v-if="Object.keys(accessoire_checkboxes).length" class="mb-4">
      <p class="text-[11px] font-medium uppercase tracking-[0.06em] text-[#3d4d62] mb-2">Accessoires</p>
      <div class="bg-[#161b22] border border-white/[0.06] rounded-lg overflow-hidden divide-y divide-white/[0.04]">
        <div
          v-for="(check, name) in accessoire_checkboxes" :key="'acc-' + name"
          class="flex items-center justify-between px-4 py-2.5 transition-colors"
          :class="check.alreadyPaid ? 'opacity-55' : 'hover:bg-white/[0.02]'"
        >
          <label :for="'acc-' + name" class="text-[13px] text-[#8a95a8] cursor-pointer select-none">
            {{ name }}
            <span class="text-[11px] text-[#3d4d62] ml-1">({{ check.prix }} {{ details.devise }})</span>
            <span v-if="check.alreadyPaid" class="ml-1.5 text-[11px] text-green-500">✓ payé</span>
          </label>
          <input
            :id="'acc-' + name"
            type="checkbox"
            v-model="check.selected"
            :disabled="check.alreadyPaid"
            class="w-4 h-4 rounded accent-[#4a7cff] cursor-pointer disabled:cursor-not-allowed"
          />
        </div>
      </div>
    </div>

    <!-- Échéances -->
    <div v-if="Object.keys(sortedEcheances).length" class="mb-5">
      <p class="text-[11px] font-medium uppercase tracking-[0.06em] text-[#3d4d62] mb-2">Échéances</p>
      <div class="bg-[#161b22] border border-white/[0.06] rounded-lg overflow-hidden divide-y divide-white/[0.04]">
        <div
          v-for="(item, key) in sortedEcheances" :key="'ech-' + key"
          class="flex items-center justify-between px-4 py-2.5 transition-colors"
          :class="item.alreadyPaid ? 'opacity-55' : 'hover:bg-white/[0.02]'"
        >
          <label :for="'ech-' + key" class="text-[13px] cursor-pointer select-none"
            :class="item.alreadyPaid ? 'text-green-400' : 'text-[#8a95a8]'">
            {{ formatEcheanceLabel(item, key) }}
            <span v-if="item.alreadyPaid" class="ml-1.5 text-[11px] text-green-500">✓ payé</span>
          </label>
          <input
            :id="'ech-' + key"
            type="checkbox"
            v-model="item.selected"
            :disabled="item.alreadyPaid"
            class="w-4 h-4 rounded accent-[#4a7cff] cursor-pointer disabled:cursor-not-allowed"
          />
        </div>
      </div>
    </div>

    <!-- Bouton valider -->
    <!-- <div class="flex justify-end pt-1">
      <button
        :disabled="status || details === 'null' || !montant_verser"
        @click="validerPaiement"
        class="inline-flex items-center gap-1.5 px-5 py-2 rounded-lg text-[13px] font-medium
               text-white bg-gradient-to-r from-[#2d5dd4] to-[#4a7cff]
               border border-white/10 shadow-[0_2px_10px_rgba(45,93,212,.28)]
               hover:from-[#3568e8] hover:to-[#5a8cff] hover:-translate-y-px
               transition-all duration-150
               disabled:opacity-40 disabled:cursor-not-allowed disabled:translate-y-0 disabled:shadow-none cursor-pointer"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
          <path d="M12.78 5.22a.749.749 0 0 1 0 1.06l-4.25 4.25a.749.749 0 0 1-1.06 0L5.22 8.28a.749.749 0 1 1 1.06-1.06L8 8.94l3.72-3.72a.749.749 0 0 1 1.06 0Z" />
        </svg>
        Valider le paiement
      </button>
    </div> -->
    <button
  :disabled="status || details === 'null' || !montant_verser || props.waiting"
  @click="validerPaiement"
  class="inline-flex items-center gap-1.5 px-5 py-2 rounded-lg text-[13px] font-medium
         text-white bg-gradient-to-r from-[#2d5dd4] to-[#4a7cff]
         border border-white/10 shadow-[0_2px_10px_rgba(45,93,212,.28)]
         hover:from-[#3568e8] hover:to-[#5a8cff] hover:-translate-y-px
         transition-all duration-150
         disabled:opacity-40 disabled:cursor-not-allowed disabled:translate-y-0 disabled:shadow-none cursor-pointer"
>
  <!-- Spinner pendant le chargement -->
  <svg v-if="props.waiting" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" class="opacity-25"/>
    <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" class="opacity-75"/>
  </svg>
  <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
    <path d="M12.78 5.22a.749.749 0 0 1 0 1.06l-4.25 4.25a.749.749 0 0 1-1.06 0L5.22 8.28a.749.749 0 1 1 1.06-1.06L8 8.94l3.72-3.72a.749.749 0 0 1 1.06 0Z" />
  </svg>
  {{ props.waiting ? 'Traitement…' : 'Valider le paiement' }}
</button>

  </div>

  <!-- Fallback si pas de données -->
  <div v-else class="flex flex-col items-center justify-center py-12 text-[#3d4d62] text-[13px]">
    <span class="text-3xl mb-2">📭</span>
    Aucune donnée disponible
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';

const props = defineProps({
  details: {
    type: [Object, String],
    default: null,
  },
  waiting: { type: Boolean, default: false }  // ← ajouter
});


const emit = defineEmits(['paiement-valide']);

// ── State ──────────────────────────────────────────────────────────────────────
const status                = ref(false);
const balanse               = ref(0);
const avance                = ref(0);
const avance_sur            = ref('');
const montant_verser        = ref('');
const accessoire_checkboxes = ref({});
const echeance_checkboxes   = ref({});
const montantInput          = ref(null);

// ── Helpers ────────────────────────────────────────────────────────────────────

/** Parse paiement_details : string JSON ou objet déjà parsé */
const parsePaiementDetails = (details) => {
  if (!details || details === 'null') return null;
  try {
    return typeof details.paiement_details === 'string'
      ? JSON.parse(details.paiement_details)
      : (details.paiement_details ?? null);
  } catch (e) {
    console.error('[PaymentDetails] Erreur parsing paiement_details:', e);
    return null;
  }
};

/** Parse une date "DD-MM-YYYY HH:mm" en objet Date */
const parseDate = (s) => {
  if (!s) return new Date(0);
  const [datePart, timePart = '00:00'] = s.split(' ');
  const [day, month, year] = (datePart || '').split('-');
  if (!day || !month || !year) return new Date(0);
  return new Date(`${year}-${month}-${day}T${timePart}`);
};

// ── Init ───────────────────────────────────────────────────────────────────────
const initPaymentLogic = () => {
  // Reset complet à chaque init (changement d'année, ré-ouverture…)
  status.value               = false;
  balanse.value              = 0;
  avance.value               = 0;
  avance_sur.value           = '';
  montant_verser.value       = '';
  accessoire_checkboxes.value = {};
  echeance_checkboxes.value  = {};

  if (!props.details || props.details === 'null') return;

  const d = parsePaiementDetails(props.details);
  if (!d) return;

  const info_paiement = d?.paiement_details?.info_paiement ?? {};
  const devise        = props.details.devise ?? '';

  // ── Trouver la dernière entrée non retournée ──
  let latest_entry = null;
  const dates = Object.keys(info_paiement);

  if (dates.length > 0) {
    const sortedDates = [...dates].sort((a, b) => parseDate(a) - parseDate(b));
    for (let i = sortedDates.length - 1; i >= 0; i--) {
      if (info_paiement[sortedDates[i]]?.status !== 'retourné') {
        latest_entry = info_paiement[sortedDates[i]];
        break;
      }
    }
  }

  // ── Calcul avance / balance / status ──
  if (latest_entry) {
    const total_verse  = Number(latest_entry.total_verse  ?? 0);
    const total_annuel = Number(latest_entry.total_annuel ?? 0);

    if (total_annuel > 0 && total_verse >= total_annuel) {
      status.value = true;
    } else {
      avance.value  = Number(latest_entry.depot_et_avance ?? 0);
      balanse.value = Number(latest_entry.balance         ?? 0);

      const month_pays = d.paiement_details?.mois ?? {};
      const moisKeys   = Object.keys(month_pays);

      if (moisKeys.length > 0) {
        const latest_pay = [...moisKeys].sort().pop() ?? '';
        const parts  = latest_pay.split('_');
        const type   = parts[0] || 'Versement';
        const idx    = parseInt(parts[1] ?? '0') + 2;
        const suffix = idx === 1 ? 'er' : 'ème';
        avance_sur.value = `Avance de ${avance.value} ${devise} sur le ${idx}${suffix} ${type}`;
      } else {
        avance_sur.value = `Avance de ${avance.value} ${devise} sur le 1er Versement`;
      }
    }
  }

  // ── Accessoires ──
  const accessoiresData = Array.isArray(props.details.accessoires)
    ? props.details.accessoires
    : [];
  const accPayes = Array.isArray(d.paiement_details?.accessoires?.accessoire)
    ? d.paiement_details.accessoires.accessoire
    : [];

  accessoiresData.forEach(acc => {
    const nom = acc?.type_daccessoire;
    if (!nom) return;
    accessoire_checkboxes.value[nom] = {
      prix:        acc.prix   ?? 0,
      selected:    accPayes.includes(nom),
      alreadyPaid: accPayes.includes(nom),
    };
  });

  // ── Échéances ──
  const echeancesConfig = props.details.montant_par?.[props.details.echeance] ?? {};
  const moisPayes       = d.paiement_details?.mois ?? {};

  Object.keys(echeancesConfig).forEach(key => {
    const parts = key.split('_');
    echeance_checkboxes.value[key] = {
      montant:    echeancesConfig[key] ?? 0,
      selected:   Object.prototype.hasOwnProperty.call(moisPayes, key),
      alreadyPaid: Object.prototype.hasOwnProperty.call(moisPayes, key),
      index:      parseInt(parts[1] ?? '0'),
    };
  });
};

// ── Computed ───────────────────────────────────────────────────────────────────
const displayAide = computed(() => {
  if (!props.details || props.details === 'null') return '';
  return props.details.aide_financiere && props.details.aide_financiere !== 'Aucune'
    ? `(${props.details.aide_financiere})`
    : '';
});

const sortedEcheances = computed(() =>
  Object.fromEntries(
    Object.entries(echeance_checkboxes.value)
      .sort((a, b) => a[1].index - b[1].index)
  )
);

const formatEcheanceLabel = (item, key) => {
  if (!props.details || props.details === 'null') return key;
  const name   = key.split('_')[0] || key;
  const devise = props.details.devise ?? '';

  if (props.details.echeance !== 'mois') {
    const suffix = item.index === 1 ? 'er' : 'ème';
    return `${item.index}${suffix} ${props.details.echeance} — ${item.montant} ${devise}`;
  }
  return `${name} — ${item.montant} ${devise}`;
};

// ── Actions ────────────────────────────────────────────────────────────────────
const validerPaiement = () => {
  if (status.value || props.details === 'null' || !montant_verser.value) return;

  const payload = {
    montant: Number(montant_verser.value),
    accessoires: Object.fromEntries(
      Object.entries(accessoire_checkboxes.value).map(([k, v]) => [k, v.selected])
    ),
    mois: Object.fromEntries(
      Object.entries(echeance_checkboxes.value).map(([k, v]) => [k, v.selected])
    ),
  };

  emit('paiement-valide', props.details,payload);
  emit('waiting', false)
};

// ── Lifecycle ──────────────────────────────────────────────────────────────────

// Re-init à chaque changement de details (nouvelle année cliquée)
watch(
  () => props.details,
  (newVal) => { if (newVal) initPaymentLogic(); },
  { deep: false }
);

onMounted(() => {
  initPaymentLogic();
  setTimeout(() => montantInput.value?.focus(), 80);
});
</script>
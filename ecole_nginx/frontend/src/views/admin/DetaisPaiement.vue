<script setup>
import { usePdfWithLoading } from "@/stores/usePdf";
import axios from "axios";
import Swal from "sweetalert2";
import { onMounted, ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const canRetourner = computed(() =>
  authStore.roleNames.some(r => ['admin', 'Comptable'].includes(r))
);

const { submitPdf, loading, error, loadingMap } = usePdfWithLoading()

const url = import.meta.env.VITE_APP_BASE_URL;

const props = defineProps({
  DetailsData: Object,
  paiement_id: {
    type: [String, Number],
    required: true,
  },
});

const dataLoading = ref(false);
const DetailsData = ref(null);
const token = ref(null);
const printing = ref(null);

// ── Computed ──────────────────────────────────────────────────
const paiement_details = computed(
  () => DetailsData.value?.paiement_details?.paiement_details ?? null
);
const etudiant = computed(() => paiement_details.value?.details_etudiant ?? {});
const check_echeance = computed(() => paiement_details.value?.check_echeance ?? {});
const info_paiement = computed(() => paiement_details.value?.info_paiement ?? {});
const echeances = computed(() => check_echeance.value ?? {});
const mois = computed(() => paiement_details.value?.mois ?? {});

// ── Helpers ───────────────────────────────────────────────────
const ordinal = (n) => (n === 1 ? `${n}er` : `${n}ème`);
const formatAmount = (val) => Number(val || 0).toLocaleString("fr-FR");

function getNumFromLabel(label) {
  const m = label.match(/^(\d+)/);
  return m ? parseInt(m[1]) : null;
}

// ── Tableau enrichi des versements ───────────────────────────
const versementsInfo = computed(() => {
  return Object.entries(info_paiement.value).map(([dateKey, details], index) => {
    const versementKey = Object.keys(details).find((k) => k.startsWith("Versement_"));
    const versementNum = versementKey ? parseInt(versementKey.split("_")[1]) : index + 1;
    const versementLabel = `${ordinal(versementNum)} Versement`;
    const montantDu = echeances.value[versementLabel] ?? 0;

    let avanceVal = 0;
    if (details.avance !== undefined) {
      if (typeof details.avance === "string") {
        avanceVal = details.avance.split("+").reduce((s, p) => s + (parseInt(p.trim()) || 0), 0);
      } else {
        avanceVal = Number(details.avance) || 0;
      }
    }

    return {
      dateKey, details, index, versementNum, versementLabel, montantDu, avanceVal,
      statusPaiement: Array.isArray(details.status_paiement) ? details.status_paiement : [],
      isRetourne: !!(details.return_by && details.return_by !== ""),
      isFinalAcquitte: details.status === "Acquitte",
      depot: details.depot ?? 0,
      totalVerse: details.total_verse ?? 0,
      balance: details.balance ?? 0,
      devise: details.devise ?? "GDES",
      remise: details.remise ?? 0,
      employer: details.employer ?? "",
      editBy: details.edit_by ?? "",
      aideFinanciere: details.aide_financiere ?? "",
      totalAnnuel: details.total_annuel ?? 0,
    };
  });
});

const globalInfo = computed(() => versementsInfo.value[0] ?? {});
 
const versementsAcquitesFromMois = computed(() => {
  const map = {}
  for (const key of Object.keys(mois.value)) {
    // "Versement_1_8ef65c55-..." → numéro 1
    const parts = key.split('_')
    const numero = parseInt(parts[1])
    if (!isNaN(numero)) {
      const label = numero === 1 ? '1er Versement' : `${numero}ème Versement`
      map[numero] = 'acquitte'  // présent dans mois = acquitté
    }
  }
  return map
})

// Fusionne avec versementStatusMap existant
const versementStatusMap = computed(() => {
  const map = { ...versementsAcquitesFromMois.value } 
  
  for (const v of versementsInfo.value) {
    for (const sp of v.statusPaiement) {
      if (sp.startsWith("Acqt:")) {
        const num = getNumFromLabel(sp.replace("Acqt: ", ""));
        if (num) map[num] = v.isRetourne ? "retourne" : "acquitte";
      }
      if (sp.startsWith("Avns:")) {
        const num = getNumFromLabel(sp.replace("Avns: ", ""));
        if (num && !map[num]) map[num] = "avance";
      }
    }
  }
  return map
})
// const versementStatusMap = computed(() => {
//   const map = {};
//   for (const v of versementsInfo.value) {
//     for (const sp of v.statusPaiement) {
//       if (sp.startsWith("Acqt:")) {
//         const num = getNumFromLabel(sp.replace("Acqt: ", ""));
//         if (num) map[num] = v.isRetourne ? "retourne" : "acquitte";
//       }
//       if (sp.startsWith("Avns:")) {
//         const num = getNumFromLabel(sp.replace("Avns: ", ""));
//         if (num && !map[num]) map[num] = "avance";
//       }
//     }
//   }
//   return map;
// });

const isVersementAcquitte = (num) => versementStatusMap.value[num] === "acquitte";
const isVersementAvance = (num) => versementStatusMap.value[num] === "avance";
const isVersementRetourne = (num) => versementStatusMap.value[num] === "retourne";

function getVersementStatus(num) {
  const s = versementStatusMap.value[num];
  if (s === "acquitte") return "Acquitte";
  if (s === "avance") return "Avance";
  if (s === "retourne") return "Retourne";
  return "En attente";
}

// ── API ───────────────────────────────────────────────────────
const payments = async () => {
  dataLoading.value = true;
  try {
    const response = await axios.get(`${url}/paiement/${props.paiement_id}`);
    DetailsData.value = response.data?.show_paiement;
    console.log(DetailsData.value);
    
  } catch (error) {
    console.error("Erreur chargement paiements:", error);
  } finally {
    dataLoading.value = false;
  }
};

onMounted(() => {
  token.value = localStorage.getItem("auth-token");
  payments();
});

const printRecu = async (id, key) => {
  try {
    printing.value = key;
    const t = localStorage.getItem("auth-token");
    const res = await fetch(`${url}/print-recu`, {
      method: "POST",
      headers: { Authorization: `Bearer ${t}`, Accept: "application/pdf", "Content-Type": "application/json" },
      body: JSON.stringify({ id, key }),
    });
    if (!res.ok) throw new Error(`Erreur ${res.status}`);
    window.open(URL.createObjectURL(await res.blob()), "_blank");
  } catch (e) {
    console.error("[printRecu]", e);
  } finally {
    printing.value = null;
  }
};

const hasVersementKey = (details, num) => {
  return Object.keys(details).some(key => {
    const parts = key.split('_')
    return parts[0] === 'Versement' && parseInt(parts[1]) === num
  })
}

// ── Retour de paiement ────────────────────────────────────────
const returningKey = ref(null);

const lastNonReturnedKey = computed(() => {
  const keys = Object.keys(info_paiement.value);
  for (let i = keys.length - 1; i >= 0; i--) {
    const entry = info_paiement.value[keys[i]];
    if (entry?.status !== 'retourné') return keys[i];
  }
  return null;
});

const isLastPayment = (dateKey) => dateKey === lastNonReturnedKey.value;

const retournerPaiement = async (dateKey) => {
  const confirm = await Swal.fire({
    title: 'Retourner ce paiement ?',
    text: 'Cette action est irréversible. Le paiement sera marqué comme retourné.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#ef4444',
    cancelButtonColor: '#374151',
    confirmButtonText: 'Oui, retourner',
    cancelButtonText: 'Annuler',
    background: '#0f1117',
    color: '#e8eaf0',
  });
  if (!confirm.isConfirmed) return;

  returningKey.value = dateKey;
  try {
    await axios.post(`${url}/delete-paiement`, {
      id: DetailsData.value?.id,
      index: dateKey,
    });
    // Recharger les données AVANT d'afficher la notification
    await payments();
    Swal.fire({
      icon: 'success',
      title: 'Paiement retourné',
      text: 'Le paiement a été marqué comme retourné avec succès.',
      timer: 2000,
      showConfirmButton: false,
      background: '#0f1117',
      color: '#e8eaf0',
    });
  } catch (err) {
    // S'assurer que le loading s'arrête même en cas d'erreur
    dataLoading.value = false;
    const status = err.response?.status;
    const detail = err.response?.data?.detail;
    if (status === 202) {
      Swal.fire({
        icon: 'warning',
        title: 'Autorisation requise',
        text: "Vous n'avez pas la permission. Un administrateur doit approuver cette action.",
        background: '#0f1117',
        color: '#e8eaf0',
      });
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Erreur',
        text: detail || 'Une erreur est survenue.',
        background: '#0f1117',
        color: '#e8eaf0',
      });
    }
  } finally {
    returningKey.value = null;
  }
};

const getVersementValue = (details, num) => {
  const key = Object.keys(details).find(k => {
    const parts = k.split('_')
    return parts[0] === 'Versement' && parseInt(parts[1]) === num
  })
  return key ? details[key] : null
}

// Utilisation
// getVersementValue(details, 1) // 25000
// getVersementValue(details, 2) // null
</script>

<template>
  <div class="max-w-6xl mx-auto pb-10 px-4 sm:px-6 min-h-screen" style="font-family:'DM Sans','Segoe UI',sans-serif">

    <!-- Loading -->
    <div v-if="dataLoading" class="flex items-center justify-center py-24">
      <div class="flex flex-col items-center gap-3">
        <svg class="w-8 h-8 animate-spin text-[#1f6feb]" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"/>
          <path class="opacity-80" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        <span class="text-[12px] text-[#3d4d62]">Chargement du dossier...</span>
      </div>
    </div>

    <template v-else>

      <!-- En-tete etudiant -->
      <div class="bg-[#161b22] border border-white/[0.06] rounded-xl px-5 py-4 mb-5 flex items-center gap-4">
        <div class="w-10 h-10 rounded-xl bg-[#1f6feb]/10 border border-[#1f6feb]/20 flex items-center justify-center text-lg shrink-0">
          <span>&#x1F4B3;</span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#3d4d62] mb-1">Dossier de paiement</p>
          <div class="flex items-center gap-2 flex-wrap">
            <span class="font-mono text-[12px] text-[#7aaeff] bg-[#1f6feb]/10 border border-[#1f6feb]/15 px-2 py-0.5 rounded">
              {{ etudiant.identifiant }}
            </span>
            <span class="text-[15px] font-semibold text-[#e2e8f5] tracking-tight">
              {{ etudiant.prenom }} {{ etudiant.nom }}
            </span>
          </div>
        </div>
        <div v-if="globalInfo.totalAnnuel" class="hidden sm:flex flex-col items-end gap-1 shrink-0">
          <span class="text-[10px] uppercase tracking-widest text-[#3d4d62]">Total annuel</span>
          <span class="text-[15px] font-bold text-[#e2e8f5] font-mono">
            {{ formatAmount(globalInfo.totalAnnuel) }}
            <span class="text-[11px] font-normal text-[#3d4d62] ml-0.5">{{ globalInfo.devise }}</span>
          </span>
          <span v-if="globalInfo.aideFinanciere" class="text-[10px] text-purple-400 font-medium bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded-full">
            {{ globalInfo.aideFinanciere }}
          </span>
        </div>
      </div>

      <!-- Recapitulatif echeancier -->
      <div v-if="Object.keys(echeances).length" class="mb-5 bg-[#0d1117] border border-white/[0.05] rounded-xl p-4">
        <p class="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#3d4d62] mb-3">Recapitulatif des versements</p>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-2">
          <div
            v-for="(montant, label, idx) in echeances"
            :key="label"
            class="border rounded-lg px-3 py-2.5"
            :class="{
              'bg-[#3fb950]/5 border-[#3fb950]/25': isVersementAcquitte(idx + 1),
              'bg-yellow-500/5 border-yellow-500/20': isVersementAvance(idx + 1),
              'bg-red-500/5 border-red-500/20': isVersementRetourne(idx + 1),
              'bg-[#161b22] border-white/[0.05]': !isVersementAcquitte(idx + 1) && !isVersementAvance(idx + 1) && !isVersementRetourne(idx + 1),
            }"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-[10px] font-semibold text-[#3d4d62] uppercase tracking-wide">{{ label }}</span>
              <span
                class="text-[9px] font-bold px-1.5 py-0.5 rounded-full border"
                :class="{
                  'bg-[#3fb950]/15 text-[#3fb950] border-[#3fb950]/25': isVersementAcquitte(idx + 1),
                  'bg-yellow-500/15 text-yellow-400 border-yellow-500/25': isVersementAvance(idx + 1),
                  'bg-red-500/15 text-red-400 border-red-500/20': isVersementRetourne(idx + 1),
                  'bg-white/5 text-[#3d4d62] border-white/[0.06]': !isVersementAcquitte(idx + 1) && !isVersementAvance(idx + 1) && !isVersementRetourne(idx + 1),
                }"
              >{{ getVersementStatus(idx + 1) }}</span>
            </div>
            <div
              class="text-[15px] font-bold font-mono"
              :class="{
                'text-[#3fb950]': isVersementAcquitte(idx + 1),
                'text-yellow-400': isVersementAvance(idx + 1),
                'text-red-400': isVersementRetourne(idx + 1),
                'text-[#7d8590]': !isVersementAcquitte(idx + 1) && !isVersementAvance(idx + 1) && !isVersementRetourne(idx + 1),
              }"
            >
              {{ formatAmount(montant) }}
              <span class="text-[10px] font-normal text-[#3d4d62] ml-0.5">{{ globalInfo.devise }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Historique des versements -->
       <!-- {{versementsInfo}}
       {{echeances}} -->
      <div v-if="versementsInfo.length" class="space-y-3">
        <p class="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#3d4d62] px-1 mb-2">Historique des versements</p>

        <div
          v-for="(v,i) in versementsInfo"
          :key="v.dateKey"
          class="bg-[#161b22] border rounded-xl overflow-hidden"
          :class="{
            'border-red-500/20': v.isRetourne,
            'border-[#3fb950]/15': v.isFinalAcquitte,
            'border-white/[0.06]': !v.isRetourne && !v.isFinalAcquitte,
          }"
        >
          <!-- Header --> 
          <div class="flex items-center justify-between px-5 py-3 bg-[#0d1117] border-b border-white/[0.05]">
            <div class="flex items-center gap-3 flex-wrap">
              <span
                class="w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold shrink-0"
                :class="{
                  'bg-red-500/15 border border-red-500/25 text-red-400': v.isRetourne,
                  'bg-[#3fb950]/15 border border-[#3fb950]/25 text-[#3fb950]': !v.isRetourne,
                }"
              >{{ v.index + 1 }}</span>
              <span class="text-[12px] font-medium text-[#7d8590] font-mono">{{ v.dateKey }}</span>
              <span class="text-[11px] font-semibold text-[#7aaeff] bg-[#1f6feb]/10 border border-[#1f6feb]/15 px-2 py-0.5 rounded">
                {{ v.versementLabel }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span v-if="v.aideFinanciere" class="hidden sm:inline text-[10px] font-medium px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
                {{ v.aideFinanciere }}
              </span>
              <span v-if="v.isRetourne" class="text-[11px] font-medium px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">Retourne</span>
              <span v-else-if="v.isFinalAcquitte" class="text-[11px] font-medium px-2 py-0.5 rounded-full bg-[#3fb950]/10 text-[#3fb950] border border-[#3fb950]/20">Acquitte</span>
              <span v-else class="text-[11px] font-medium px-2 py-0.5 rounded-full bg-[#3fb950]/10 text-[#3fb950] border border-[#3fb950]/20">Valide</span>
            </div>
          </div>

          <div class="p-5 space-y-4">
            <!-- Infos caissier + cumul -->
            <div class="flex items-center gap-4 flex-wrap text-[12px]">
              <div v-if="v.employer" class="flex items-center gap-1.5">
                <span class="text-[#3d4d62]">Caissier</span>
                <span class="font-medium text-[#c9d1d9]">{{ v.employer }}</span>
              </div>
              <div v-if="v.editBy && v.editBy !== v.employer" class="flex items-center gap-1.5">
                <span class="text-[#3d4d62]">Modifie par</span>
                <span class="font-medium text-[#c9d1d9]">{{ v.editBy }}</span>
              </div>
              <div class="ml-auto flex items-center gap-1.5">
                <span class="text-[#3d4d62]">Cumul verse</span>
                <span class="font-bold text-[#7aaeff] font-mono">{{ formatAmount(v.totalVerse) }} <span class="font-normal text-[#3d4d62]">{{ v.devise }}</span></span>
              </div>
            </div>

            <!-- Tableau financier -->
            <div class="bg-[#0d1017] border border-white/[0.05] rounded-lg overflow-x-auto">
              <table class="w-full border-collapse text-[12.5px] min-w-[500px]">
                <thead>
                  <tr class="border-b border-white/[0.05]">
                    <th class="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Versement</th>
                    <th class="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Montant du</th>
                    <th class="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Depose</th>
                    <th class="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Avance</th>
                    <th class="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Balance</th>
                    <th v-if="v.remise" class="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Remise</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="px-3 py-3">
                      <span class="text-[11px] font-semibold text-[#7aaeff] bg-[#1f6feb]/10 border border-[#1f6feb]/15 px-2 py-0.5 rounded">
                        {{ v.versementLabel }}
                      </span>
                    </td>
                    <td class="px-3 py-3">
                      <span class="font-bold text-[#e2e8f5] font-mono">{{ formatAmount(v.montantDu) }}</span>
                      <span class="text-[#3d4d62] text-[11px] ml-0.5">{{ v.devise }}</span>
                    </td>
                    <td class="px-3 py-3">
                      <span class="font-semibold text-[#c9d1d9] font-mono">{{ formatAmount(v.depot) }}</span>
                      <span class="text-[#3d4d62] text-[11px] ml-0.5">{{ v.devise }}</span>
                    </td>
                    <td class="px-3 py-3">
                      <span v-if="v.avanceVal > 0 && !hasVersementKey(v.details, v.versementNum) && !isVersementAcquitte(v.versementNum)" class="font-semibold text-[#d29922] font-mono">
                        {{ formatAmount(v.avanceVal) }}
                        <span class="text-[#3d4d62] font-normal text-[11px] ml-0.5">{{ v.devise }}</span>
                      </span>
                      <span v-else class="text-[#3d4d62]">--</span>
                    </td>
                    <td class="px-3 py-3">
                      <span
                        class="font-semibold font-mono"
                        :class="{
                          'text-[#f85149]': v.balance > 0,
                          'text-[#3fb950]': v.balance === 0 && v.isFinalAcquitte,
                          'text-[#3d4d62]': v.balance === 0 && !v.isFinalAcquitte,
                        }"
                      >
                        {{hasVersementKey(v.details, i+1) ? 0 : formatAmount(v.balance) }}
                        <span class="text-[#3d4d62] font-normal text-[11px] ml-0.5">{{ v.devise }}</span>
                      </span>
                    </td>
                    <td v-if="v.remise" class="px-3 py-3">
                      <span class="font-semibold text-purple-400 font-mono">
                        {{ formatAmount(v.remise) }}
                        <span class="text-[#3d4d62] font-normal text-[11px] ml-0.5">{{ v.devise }}</span>
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Status badges --> 
            <div v-if="v.statusPaiement.length" class="flex flex-wrap gap-2">
              <span
                v-for="sp in v.statusPaiement"
                :key="sp"
                class="inline-flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-1 rounded-full border"
                :class="{
                  'bg-[#3fb950]/10 text-[#3fb950] border-[#3fb950]/20': sp.startsWith('Acqt:'),
                  'bg-yellow-500/10 text-yellow-400 border-yellow-500/20': sp.startsWith('Avns:'),
                }"
              >
                <svg v-if="sp.startsWith('Acqt:')" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3 shrink-0">
                  <path d="M12.78 5.22a.749.749 0 0 1 0 1.06l-4.25 4.25a.749.749 0 0 1-1.06 0L5.22 8.28a.749.749 0 1 1 1.06-1.06L8 8.94l3.72-3.72a.749.749 0 0 1 1.06 0Z"/>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3 shrink-0">
                  <path fill-rule="evenodd" d="M1 8a7 7 0 1 1 14 0A7 7 0 0 1 1 8Zm7.75-4.25a.75.75 0 0 0-1.5 0V8c0 .198.079.389.22.53l2.25 2.25a.75.75 0 1 0 1.06-1.06l-2.03-2.03V3.75Z" clip-rule="evenodd"/>
                </svg>
                <span>
                  <span class="opacity-50 mr-0.5 text-[10px]">{{ sp.startsWith('Acqt:') ? 'Acquitte :' : 'Avance sur :' }}</span>
                  {{ sp.replace('Acqt: ', '').replace('Avns: ', '') }}
                </span>
              </span>
            </div>
            <div v-else class="flex flex-wrap gap-2">
              <span
                v-if="hasVersementKey(v.details, i+1) && !v.statusPaiement.length" 
                class="inline-flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-1 rounded-full border"
                :class="{
                  'bg-[#3fb950]/10 text-[#3fb950] border-[#3fb950]/20': hasVersementKey(v.details, i+1)
                }"
              >v.statusPaiement.length{{v.statusPaiement.length}}
                <svg v-if="hasVersementKey(v.details, i+1)" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3 shrink-0">
                  <path d="M12.78 5.22a.749.749 0 0 1 0 1.06l-4.25 4.25a.749.749 0 0 1-1.06 0L5.22 8.28a.749.749 0 1 1 1.06-1.06L8 8.94l3.72-3.72a.749.749 0 0 1 1.06 0Z"/>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3 shrink-0">
                  <path fill-rule="evenodd" d="M1 8a7 7 0 1 1 14 0A7 7 0 0 1 1 8Zm7.75-4.25a.75.75 0 0 0-1.5 0V8c0 .198.079.389.22.53l2.25 2.25a.75.75 0 1 0 1.06-1.06l-2.03-2.03V3.75Z" clip-rule="evenodd"/>
                </svg>
                <span>
                  <span class="opacity-50 mr-0.5 text-[10px]">{{ hasVersementKey(v.details, i+1) ? 'Acquitte :' : 'Avance sur:' }}</span>
                  {{ v.versementLabel }}
                </span>
              </span>
            </div>
            

            <!-- Alerte balance -->
            <div v-if="v.avanceVal > 0 && !hasVersementKey(v.details, v.versementNum) && !isVersementAcquitte(v.versementNum)"
              class="flex items-start gap-2 text-[12px] text-yellow-400 bg-yellow-500/8 border border-yellow-500/20 rounded-lg px-3 py-2.5">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 shrink-0 mt-px">
                <path d="M6.457 1.047c.659-1.234 2.427-1.234 3.086 0l6.082 11.378A1.75 1.75 0 0 1 14.082 15H1.918a1.75 1.75 0 0 1-1.543-2.575Zm1.763 2.453a.75.75 0 0 0-1.44 0l-.613 3.51a.75.75 0 0 0 .737.89h1.226a.75.75 0 0 0 .737-.89l-.647-3.51Zm.53 7a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"/>
              </svg>
              <span>Avance de <strong>{{ formatAmount(v.avanceVal) }} {{ v.devise }}</strong> — reportee comme avance sur {{ v.versementLabel }}.</span>
            </div>

            <!-- Retourne -->
            <div v-if="v.isRetourne && v.details.return_by"
              class="flex items-center gap-2 text-[12px] text-red-400 bg-red-500/8 border border-red-500/20 rounded-lg px-3 py-2">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 shrink-0">
                <path d="M1.22 6.22a.75.75 0 0 1 1.06 0L4 7.94V4.5a5.5 5.5 0 0 1 10.007-3.152.75.75 0 0 1-1.321.704A4 4 0 0 0 5.5 4.5v3.44l1.72-1.72a.75.75 0 1 1 1.06 1.06l-3 3a.75.75 0 0 1-1.06 0l-3-3a.75.75 0 0 1 0-1.06Z"/>
              </svg>
              Retourne par <strong class="ml-0.5">{{ v.details.return_by }}</strong>
            </div>

            <!-- Remise -->
            <div v-if="v.remise"
              class="flex items-center gap-2 text-[12px] text-purple-400 bg-purple-500/8 border border-purple-500/20 rounded-lg px-3 py-2">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5 shrink-0">
                <path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.749.749 0 1 1 1.06-1.06L6 10.939l6.72-6.719a.75.75 0 0 1 1.06 0Z"/>
              </svg>
              Remise accordee de <strong class="ml-0.5">{{ formatAmount(v.remise) }} {{ v.devise }}</strong>
            </div>
          </div>

          <!-- Footer actions -->
          <div class="flex items-center justify-end gap-2 px-5 py-3 border-t border-white/[0.05] bg-[#0d1117]/50">

            <!-- Bouton Retourner — uniquement sur le dernier paiement non retourné -->
            <button
              v-if="isLastPayment(v.dateKey) && !v.isRetourne && canRetourner"
              @click="retournerPaiement(v.dateKey)"
              :disabled="returningKey === v.dateKey"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium bg-red-500/8 text-red-400 border border-red-500/20 hover:bg-red-500/15 hover:text-red-300 hover:border-red-500/40 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150"
              title="Retourner ce paiement"
            >
              <svg v-if="returningKey === v.dateKey" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
                <path d="M1.22 6.22a.75.75 0 0 1 1.06 0L4 7.94V4.5a5.5 5.5 0 0 1 10.007-3.152.75.75 0 0 1-1.321.704A4 4 0 0 0 5.5 4.5v3.44l1.72-1.72a.75.75 0 1 1 1.06 1.06l-3 3a.75.75 0 0 1-1.06 0l-3-3a.75.75 0 0 1 0-1.06Z"/>
              </svg>
              Retourner
            </button>


            <button
              @click="submitPdf('/print-recu', { id: DetailsData?.id, key: i }, i)"
              :disabled="loadingMap[i] === true"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium bg-white/[0.04] text-[#6b7a90] border border-white/[0.07] hover:bg-[#4a7cff]/10 hover:text-[#7aaeff] hover:border-[#4a7cff]/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150"
            >
              <svg v-if="loadingMap[i] === true" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
                <path fill-rule="evenodd" d="M4 2a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2h.5A2.5 2.5 0 0 1 15 6.5v4A2.5 2.5 0 0 1 12.5 13H12v1a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-1h-.5A2.5 2.5 0 0 1 1 10.5v-4A2.5 2.5 0 0 1 3.5 4H4V2Zm2 0v2h4V2H6Zm-1 9v3h6v-3H5Zm8-4.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0Z" clip-rule="evenodd"/>
              </svg>
              Recu
            </button>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="flex flex-col items-center justify-center py-20 text-[#3d4d62] text-[13px]">
        <span class="text-4xl mb-3">&#x1F4ED;</span>
        Aucun paiement enregistre
      </div>

    </template>
  </div>
</template>
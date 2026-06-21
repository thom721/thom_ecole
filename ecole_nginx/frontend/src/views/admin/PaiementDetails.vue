<script setup>
import { useForm } from '@inertiajs/vue3';
import { onMounted, ref, computed } from "vue";

const url = import.meta.env.VITE_APP_BASE_URL;


const props = defineProps({
  DetailsData: Object
});

// ── State ──────────────────────────────────────────────────────
const token           = ref(null);
const printing        = ref(null); // index du reçu en cours d'impression

const paiement_details = computed(() =>
  props.DetailsData?.paiement_details?.paiement_details ?? null
);

const etudiant = computed(() =>
  paiement_details.value?.details_etudiant ?? {}
);

const info_paiement = computed(() =>
  paiement_details.value?.info_paiement ?? {}
);

const mois = computed(() =>
  props.DetailsData?.paiement_details?.mois ?? {}
);

// ── Lifecycle ──────────────────────────────────────────────────
onMounted(() => {
  token.value = localStorage.getItem('auth-token');
});

// ── Helpers ────────────────────────────────────────────────────

/** Dernier champ de l'objet details pour détecter si avance présente */
const hasAvance = (details) =>
  Object.keys(details).slice(-1)[0] === 'avance';

const ordinal = (n) => n === 1 ? `${n}er` : `${n}ème`;

// ── Actions ────────────────────────────────────────────────────
const printRecu = async (id, key) => {
  try {
    printing.value = key;
    const t = localStorage.getItem('auth-token');
    const response = await fetch(`${url}/print-recu`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${t}`,
        'Accept': 'application/pdf',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id, key }),
    });

    if (!response.ok) throw new Error(`Erreur ${response.status}`);

    const blob = await response.blob();
    const blobUrl = URL.createObjectURL(blob);
    window.open(blobUrl, '_blank');
  } catch (e) {
    console.error('[printRecu]', e);
  } finally {
    printing.value = null;
  }
};
</script>

<template>
  <div
    class="max-w-4xl mx-auto py-8 px-4 sm:px-6 min-h-screen  animate-[fadeUp_0.4s_ease_both]"
    style="font-family:'DM Sans','Segoe UI',sans-serif"
  >

    <!-- ── En-tête étudiant ──────────────────────────────────── -->
    <div class="bg-[#161b22] border border-white/[0.06] rounded-xl px-6 py-4 mb-6 flex items-center gap-4">
      <div class="w-10 h-10 rounded-xl bg-[#1f6feb]/10 border border-[#1f6feb]/20 flex items-center justify-center text-lg shrink-0">
        💳
      </div>
      <div>
        <p class="text-[11px] font-medium uppercase tracking-[0.06em] text-[#3d4d62] mb-0.5">Dossier de paiement</p>
        <div class="flex items-center gap-3 flex-wrap">
          <span class="font-mono text-[13px] text-[#7aaeff] bg-[#1f6feb]/10 border border-[#1f6feb]/15 px-2 py-0.5 rounded">
            {{ etudiant.identifiant }}
          </span>
          <span class="text-[15px] font-semibold text-[#e2e8f5] tracking-tight">
            {{ etudiant.prenom }} {{ etudiant.nom }}
          </span>
        </div>
      </div>
    </div>

    <!-- ── Versements ─────────────────────────────────────────── -->
    <div v-if="Object.keys(info_paiement).length" class="space-y-4">

      <div
        v-for="(details, dateKey, loopIndex) in info_paiement"
        :key="dateKey"
        class="bg-[#161b22] border border-white/[0.06] rounded-xl overflow-hidden"
      >

        <!-- Header du versement -->
        <div class="flex items-center justify-between px-5 py-3 bg-[#0d1117] border-b border-white/[0.05]">
          <div class="flex items-center gap-3">
            <span class="w-6 h-6 rounded-full bg-[#3fb950]/15 border border-[#3fb950]/25 flex items-center justify-center text-[11px] font-bold text-[#3fb950]">
              {{ loopIndex + 1 }}
            </span>
            <span class="text-[12px] font-medium text-[#7d8590] font-mono">{{ dateKey }}</span>
          </div>
          <!-- Statut -->
          <span v-if="details.status === 'retourné'"
            class="text-[11px] font-medium px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
            Retourné
          </span>
          <span v-else
            class="text-[11px] font-medium px-2 py-0.5 rounded-full bg-[#3fb950]/10 text-[#3fb950] border border-[#3fb950]/20">
            Validé
          </span>
        </div>

        <div class="p-5 space-y-4">

          <!-- Employé -->
          <div v-if="loopIndex === 0" class="flex items-center gap-2">
            <span class="text-[11px] uppercase tracking-[0.06em] text-[#3d4d62]">Caissier</span>
            <span class="text-[13px] font-medium text-[#c9d1d9]">{{ details.employer }}</span>
          </div>

          <!-- Tableau financier -->
          <div class="bg-[#0d1017] border border-white/[0.05] rounded-lg overflow-hidden">
            <table class="w-full border-collapse text-[12.5px]">
              <thead>
                <tr class="border-b border-white/[0.05]">
                  <th class="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Versé</th>
                  <th class="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">À payer</th>
                  <th class="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Avance</th>
                  <th class="px-3 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.07em] text-[#3d4d62]">Balance</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="px-3 py-2.5 font-semibold text-[#c9d1d9]">
                    {{ details.depot }} <span class="text-[#3d4d62]">{{ details.devise }}</span>
                  </td>
                  <td class="px-3 py-2.5 font-semibold text-[#c9d1d9]">
                    {{ details.montant }} <span class="text-[#3d4d62]">{{ details.devise }}</span>
                  </td>
                  <td class="px-3 py-2.5 font-semibold text-[#d29922]">
                    {{ details.avance ?? 0 }} <span class="text-[#3d4d62]">{{ details.devise }}</span>
                  </td>
                  <td class="px-3 py-2.5 font-semibold"
                    :class="hasAvance(details) && details.balance > 0 ? 'text-[#f85149]' : 'text-[#3fb950]'">
                    {{ hasAvance(details) ? details.balance : 0 }}
                    <span class="text-[#3d4d62]">{{ details.devise }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Versements acquittés -->
          <div v-if="Object.keys(mois).length" class="flex flex-wrap gap-2">
            <span
              v-for="(_, moisKey, moisIndex) in mois" :key="moisKey"
              class="inline-flex items-center gap-1 text-[11px] font-medium px-2.5 py-1 rounded-full
                     bg-[#1f6feb]/10 text-[#7aaeff] border border-[#1f6feb]/15"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3 text-[#3fb950]">
                <path d="M12.78 5.22a.749.749 0 0 1 0 1.06l-4.25 4.25a.749.749 0 0 1-1.06 0L5.22 8.28a.749.749 0 1 1 1.06-1.06L8 8.94l3.72-3.72a.749.749 0 0 1 1.06 0Z" />
              </svg>
              {{ ordinal(moisIndex + 1) }} versement acquitté
            </span>
          </div>

          <!-- Message balance -->
          <div v-if="hasAvance(details)"
            class="text-[12px] text-[#d29922] bg-yellow-500/10 border border-yellow-500/20 rounded-lg px-3 py-2">
            Balance de <strong>{{ details.balance }} {{ details.devise }}</strong> sur ce versement
          </div>

        </div>

        <!-- Footer actions -->
        <div class="flex items-center justify-end gap-2 px-5 py-3 border-t border-white/[0.05] bg-[#0d1117]/50">

          <!-- Modifier -->
          <button
            class="w-7 h-7 rounded-lg flex items-center justify-center text-[#3d4d62]
                   border border-transparent hover:bg-[#4a7cff]/10 hover:border-[#4a7cff]/20
                   hover:text-[#7aaeff] transition-all duration-150"
            title="Modifier"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
              <path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z" />
              <path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z" />
            </svg>
          </button>

          <!-- Supprimer -->
          <button
            class="w-7 h-7 rounded-lg flex items-center justify-center text-[#3d4d62]
                   border border-transparent hover:bg-red-500/10 hover:border-red-500/20
                   hover:text-red-400 transition-all duration-150"
            title="Supprimer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
              <path fill-rule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5Z" clip-rule="evenodd" />
            </svg>
          </button>

          <!-- Imprimer reçu -->
          <button
            @click="printRecu(props.DetailsData.id, dateKey)"
            :disabled="printing === dateKey"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium
                   bg-white/[0.04] text-[#6b7a90] border border-white/[0.07]
                   hover:bg-[#4a7cff]/10 hover:text-[#7aaeff] hover:border-[#4a7cff]/20
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-all duration-150"
            title="Imprimer le reçu"
          >
            <!-- Spinner pendant l'impression -->
            <svg v-if="printing === dateKey"
              class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
              <path fill-rule="evenodd" d="M4 2a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2h.5A2.5 2.5 0 0 1 15 6.5v4A2.5 2.5 0 0 1 12.5 13H12v1a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-1h-.5A2.5 2.5 0 0 1 1 10.5v-4A2.5 2.5 0 0 1 3.5 4H4V2Zm2 0v2h4V2H6Zm-1 9v3h6v-3H5Zm8-4.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0Z" clip-rule="evenodd" />
            </svg>
            Reçu
          </button>

        </div>
      </div>

    </div>

    <!-- Empty state -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-[#3d4d62] text-[13px]">
      <span class="text-4xl mb-3">📭</span>
      Aucun paiement enregistré
    </div>

  </div>
</template>

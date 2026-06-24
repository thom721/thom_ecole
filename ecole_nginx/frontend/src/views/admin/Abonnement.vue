<template>
  <div class="animate-[fadeUp_0.4s_ease_both]">

    <!-- Statut -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
        <p class="text-xs text-[#7c83a0] mb-2">Statut</p>
        <p class="text-[22px] font-semibold" :class="abonnement.actif ? 'text-emerald-400' : 'text-rose-400'">
          {{ abonnement.actif ? 'Actif' : 'Expiré / invalide' }}
        </p>
      </div>
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
        <p class="text-xs text-[#7c83a0] mb-2">Clé actuelle</p>
        <p class="text-[15px] font-mono text-[#e8eaf0]">{{ abonnement.cle_actuelle || '—' }}</p>
      </div>
      <div class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5">
        <p class="text-xs text-[#7c83a0] mb-2">Expire le</p>
        <p class="text-[15px] text-[#e8eaf0]">{{ abonnement.date_expiration || '—' }}</p>
        <p v-if="abonnement.jours_restants !== null" class="text-xs mt-2"
           :class="abonnement.actif ? 'text-emerald-400' : 'text-rose-400'">
          {{ abonnement.jours_restants >= 0
            ? `${abonnement.jours_restants} jour(s) restant(s)`
            : `Expiré depuis ${Math.abs(abonnement.jours_restants)} jour(s)` }}
        </p>
      </div>
    </div>

    <!-- Historique -->
    <div class="bg-[#171b26] border border-white/[0.07] rounded-xl overflow-hidden">
      <div class="px-5 py-3 border-b border-white/[0.07]">
        <span class="text-[13.5px] font-medium text-[#e8eaf0]">Historique des activations</span>
      </div>

      <div v-if="loading" class="animate-pulse px-5 py-4 space-y-3">
        <div v-for="i in 4" :key="i" class="h-8 bg-white/[0.04] rounded"></div>
      </div>

      <table v-else class="w-full">
        <thead>
          <tr class="bg-[#13161f]">
            <th v-for="h in ['Activé le', 'Expire le', 'Statut']" :key="h"
                class="px-4 py-2.5 text-left text-[11px] font-semibold text-[#7c83a0] uppercase tracking-wider">{{ h }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="historique.length === 0">
            <td colspan="3" class="px-4 py-8 text-center text-[#7c83a0] text-sm">Aucune activation trouvée</td>
          </tr>
          <tr v-for="h in historique" :key="h.id" class="border-t border-white/[0.05] hover:bg-white/[0.03] transition-colors">
            <td class="px-4 py-3 text-xs text-[#7c83a0]">{{ formatDate(h.date_activation) }}</td>
            <td class="px-4 py-3 text-xs text-[#7c83a0]">{{ h.date_expiration || '—' }}</td>
            <td class="px-4 py-3 text-xs font-semibold" :class="isEntryActif(h.date_expiration) ? 'text-emerald-400' : 'text-rose-400'">
              {{ isEntryActif(h.date_expiration) ? 'Actif' : 'Expiré' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const url = import.meta.env.VITE_APP_BASE_URL

const abonnement = ref({ actif: false, cle_actuelle: null, date_expiration: null, jours_restants: null })
const historique = ref([])
const loading = ref(false)

const formatDate = (value) => {
  if (!value) return '—'
  try { return new Date(value).toLocaleString('fr-FR') } catch { return value }
}

const isEntryActif = (dateExpiration) => {
  if (!dateExpiration) return false
  const expiration = new Date(dateExpiration)
  if (Number.isNaN(expiration.getTime())) return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  expiration.setHours(0, 0, 0, 0)
  return expiration >= today
}

const fetchAbonnement = async () => {
  loading.value = true
  try {
    const { data } = await axios.get(`${url}/abonnement`)
    abonnement.value = data
    historique.value = data.historique || []
  } catch (e) {
    console.error("Erreur lors du chargement de l'abonnement", e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchAbonnement)
</script>

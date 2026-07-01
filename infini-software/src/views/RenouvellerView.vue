<template>
  <main class="pt-28 pb-24 min-h-screen">
    <div class="max-w-xl mx-auto px-6">
      <h1 class="font-syne text-3xl font-extrabold mb-2 text-center">Renouveler ma licence</h1>
      <p class="text-[#64748b] text-sm text-center mb-10">
        Prix de base : {{ tarif.monthly_price }} {{ tarif.currency }} / mois
      </p>

      <div class="card p-8">
        <!-- Vérification en cours (mac fourni par le lien Lekol360, ou par l'utilisateur) -->
        <div v-if="macStatus === 'verifying'" class="text-center py-6">
          <p class="text-sm text-[#64748b]">Vérification de votre installation...</p>
        </div>

        <!-- Mac inconnu -->
        <div v-else-if="macStatus === 'introuvable'" class="text-center py-6 space-y-4">
          <p class="text-sm text-red-400">
            Cette adresse MAC n'est pas enregistrée sur notre serveur. Votre installation Lekol360 doit d'abord
            créer son premier compte administrateur (qui l'enregistre automatiquement) avant de pouvoir renouveler.
          </p>
          <button v-if="!macLocked" class="btn-outline" @click="macStatus = null">Réessayer avec une autre adresse</button>
        </div>

        <!-- Mac suspendu -->
        <div v-else-if="macStatus === 'suspendu'" class="text-center py-6">
          <p class="text-sm text-red-400">
            Ce client a été suspendu par un administrateur. Contactez le support pour réactiver votre licence.
          </p>
        </div>

        <!-- Identification manuelle : utilisateur arrivé sans lien Lekol360 (ex: depuis un téléphone) -->
        <div v-else-if="!macLocked && macStatus !== 'ok'" class="space-y-4">
          <p class="text-sm text-[#64748b]">
            Vous renouvelez depuis un autre appareil que votre serveur ? Indiquez l'adresse MAC de votre
            installation Lekol360 pour identifier votre licence.
          </p>
          <div>
            <label class="block text-xs text-[#64748b] mb-1">Adresse MAC de votre serveur</label>
            <input v-model="mac" type="text" placeholder="AA:BB:CC:DD:EE:FF"
                   class="w-full bg-[#080c10] border border-[#1e2a38] rounded-lg px-4 py-2.5 text-sm font-mono focus:outline-none focus:border-[#06b6d4]" />
            <p class="text-xs text-[#64748b] mt-1">
              Visible sur le serveur, dans Lekol360 → Gestion du serveur → Licence (champ « MAC »).
            </p>
          </div>
          <button class="btn-primary w-full justify-center" :disabled="!mac" @click="verifierMac">
            Vérifier
          </button>
        </div>

        <!-- Étape 1 : formulaire de paiement (mac vérifié) -->
        <form v-else-if="!paymentId" @submit.prevent="payer" class="space-y-5">
          <div>
            <label class="block text-xs text-[#64748b] mb-1">Adresse MAC de votre installation</label>
            <input :value="mac" type="text" readonly disabled
                   class="w-full bg-[#080c10]/60 border border-[#1e2a38] rounded-lg px-4 py-2.5 text-sm font-mono text-[#64748b] cursor-not-allowed" />
            <div class="flex items-center justify-between mt-1">
              <p class="text-xs text-[#64748b]">
                {{ macLocked ? 'Détectée automatiquement depuis Lekol360.' : 'Vérifiée.' }}
              </p>
              <button v-if="!macLocked" type="button" class="text-xs text-[#06b6d4] hover:underline" @click="macStatus = null">
                Changer
              </button>
            </div>
          </div>

          <div>
            <label class="block text-xs text-[#64748b] mb-1">Durée</label>
            <select v-model.number="months" class="w-full bg-[#080c10] border border-[#1e2a38] rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#06b6d4]">
              <option :value="1">1 mois</option>
              <option :value="2">2 mois</option>
              <option :value="3">3 mois</option>
              <option :value="6">6 mois</option>
              <option :value="12">12 mois</option>
            </select>
          </div>

          <div>
            <label class="block text-xs text-[#64748b] mb-2">Moyen de paiement</label>
            <div class="grid grid-cols-3 gap-3">
              <button type="button" @click="provider = 'moncash'"
                      :class="provider === 'moncash' ? 'border-[#06b6d4] bg-[#06b6d4]/10' : 'border-[#1e2a38]'"
                      class="border rounded-lg py-3 text-sm font-semibold">MonCash</button>
              <button type="button" @click="provider = 'natcash'"
                      :class="provider === 'natcash' ? 'border-[#06b6d4] bg-[#06b6d4]/10' : 'border-[#1e2a38]'"
                      class="border rounded-lg py-3 text-sm font-semibold">NatCash</button>
              <button type="button" disabled title="Bientôt disponible"
                      class="border border-[#1e2a38] rounded-lg py-3 text-sm font-semibold opacity-40 cursor-not-allowed">
                Carte<br /><span class="text-[10px] text-[#64748b]">Bientôt disponible</span>
              </button>
            </div>
          </div>

          <div class="bg-[#080c10] border border-[#1e2a38] rounded-lg px-4 py-3 flex items-center justify-between">
            <span class="text-sm text-[#64748b]">Total à payer</span>
            <span class="font-syne font-bold text-lg">{{ totalAffiche }}</span>
          </div>

          <p v-if="error" class="text-sm text-red-400">{{ error }}</p>

          <button type="submit" class="btn-primary w-full justify-center" :disabled="loading">
            {{ loading ? 'Démarrage du paiement...' : 'Payer' }}
          </button>
        </form>

        <!-- Étape 2 : redirection envoyée, en attente de confirmation -->
        <div v-else class="text-center space-y-5">
          <p v-if="!resultKey" class="text-sm text-[#64748b]">
            Une fenêtre de paiement {{ provider }} a été ouverte. Une fois le paiement terminé, cliquez ci-dessous
            pour récupérer votre nouvelle clé.
          </p>

          <button v-if="redirectUrl && !resultKey" class="btn-outline w-full justify-center" @click="ouvrirPaiement">
            Rouvrir la page de paiement
          </button>

          <button v-if="!resultKey" class="btn-gold w-full justify-center" :disabled="confirming" @click="confirmer">
            {{ confirming ? 'Vérification...' : 'J\'ai terminé le paiement' }}
          </button>

          <p v-if="confirmError" class="text-sm text-red-400">{{ confirmError }}</p>

          <div v-if="resultPending" class="bg-amber-500/10 border border-amber-500/30 rounded-lg p-5 text-left">
            <p class="text-amber-400 font-semibold mb-2">Paiement reçu — activation en attente</p>
            <p class="text-sm text-[#cbd5e1]">
              Votre paiement a bien été enregistré. La clé d'activation sera générée par un administrateur.
              Contactez le support pour finaliser l'activation de votre licence.
            </p>
          </div>

          <div v-if="resultKey" class="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-5 text-left">
            <p class="text-emerald-400 font-semibold mb-2">✅ Licence renouvelée</p>
            <p class="text-sm">Clé : <span class="font-mono">{{ resultKey }}</span></p>
            <p class="text-sm text-[#64748b]">Expire le : {{ resultExpiration }}</p>
            <p class="text-xs text-[#64748b] mt-2">
              Saisissez cette clé dans Lekol360 si une activation manuelle est demandée.
            </p>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const route = useRoute()

// true si le mac vient d'un lien de confiance (bouton Renouveler de Lekol360) :
// dans ce cas il est verrouillé. Sinon (accès direct, ex: depuis un téléphone),
// l'utilisateur doit le saisir lui-même puis le faire vérifier.
const macLocked = ref(!!route.query.mac)
const mac = ref(route.query.mac || '')
const months = ref(1)
const provider = ref('moncash')
const tarif = ref({ monthly_price: 0, currency: 'USD', exchange_rate_usd_htg: 0 })

// null (pas encore vérifié) | 'verifying' | 'ok' | 'introuvable' | 'suspendu'
const macStatus = ref(macLocked.value ? 'verifying' : null)

const loading = ref(false)
const error = ref('')
const paymentId = ref(null)
const redirectUrl = ref('')
const confirming = ref(false)
const confirmError = ref('')
const resultKey = ref('')
const resultExpiration = ref('')
const resultPending = ref(false)

const totalAffiche = computed(() => {
  const base = tarif.value.monthly_price * months.value
  if (provider.value === 'stripe') return `${base.toFixed(2)} ${tarif.value.currency}`
  return `${(base * tarif.value.exchange_rate_usd_htg).toFixed(2)} HTG`
})

const fetchTarif = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/licence/tarif`)
    if (res.ok) tarif.value = await res.json()
  } catch {
    // le formulaire reste utilisable, juste sans aperçu de prix fiable
  }
}

const verifierMac = async () => {
  if (!mac.value) return
  macStatus.value = 'verifying'
  try {
    const res = await fetch(`${API_BASE}/api/licence/verifier-mac?mac=${encodeURIComponent(mac.value)}`)
    const data = await res.json()
    if (!data.exists) macStatus.value = 'introuvable'
    else if (data.suspended) macStatus.value = 'suspendu'
    else macStatus.value = 'ok'
  } catch {
    macStatus.value = 'introuvable'
  }
}

const payer = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/licence/payer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mac: mac.value, provider: provider.value, months: months.value }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Paiement impossible')
    paymentId.value = data.payment_id
    redirectUrl.value = data.redirect_url
    if (data.status === 'paid') {
      resultPending.value = true
    } else if (data.status === 'success') {
      // Mode test (PAYMENT_TEST_MODE) : le paiement est déjà confirmé, pas besoin de redirection.
      resultKey.value = data.key
      resultExpiration.value = data.expiration_date
    } else if (data.redirect_url) {
      window.location.href = data.redirect_url
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const ouvrirPaiement = () => {
  if (redirectUrl.value) window.location.href = redirectUrl.value
}

const confirmer = async () => {
  confirming.value = true
  confirmError.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/licence/payer/confirmer?payment_id=${paymentId.value}`)
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Paiement non confirmé')
    if (data.status === 'paid') {
      resultPending.value = true
    } else {
      resultKey.value = data.key
      resultExpiration.value = data.expiration_date
    }
  } catch (e) {
    confirmError.value = e.message
  } finally {
    confirming.value = false
  }
}

onMounted(() => {
  fetchTarif()
  if (macLocked.value) verifierMac()
})
</script>

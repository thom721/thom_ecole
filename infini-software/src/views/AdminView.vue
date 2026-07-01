<template>
  <main class="pt-28 pb-24 min-h-screen">
    <div class="max-w-5xl mx-auto px-6">

      <!-- Connexion -->
      <div v-if="!token" class="max-w-md mx-auto card p-10">
        <h1 class="font-syne text-2xl font-extrabold mb-6 text-center">Connexion administrateur</h1>
        <form @submit.prevent="login" class="space-y-4">
          <input v-model="loginForm.email" type="email" placeholder="Email" required
                 class="w-full bg-[#080c10] border border-[#1e2a38] rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#06b6d4]" />
          <input v-model="loginForm.password" type="password" placeholder="Mot de passe" required
                 class="w-full bg-[#080c10] border border-[#1e2a38] rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[#06b6d4]" />
          <p v-if="loginError" class="text-sm text-red-400">{{ loginError }}</p>
          <button type="submit" class="btn-primary w-full justify-center" :disabled="loading">
            {{ loading ? 'Connexion...' : 'Se connecter' }}
          </button>
        </form>
      </div>

      <!-- Dashboard -->
      <div v-else>
        <div class="flex items-center justify-between mb-8">
          <h1 class="font-syne text-3xl font-extrabold">Administration</h1>
          <button class="btn-outline" @click="logout">Déconnexion</button>
        </div>

        <!-- Configuration tarifaire -->
        <div class="card p-6 mb-8">
          <h2 class="font-syne text-lg font-bold mb-4">Configuration tarifaire</h2>
          <p class="text-xs text-[#64748b] mb-4">
            Le prix mensuel est toujours en devise de base. Pour un paiement par carte, le montant facturé reste dans
            cette devise. Pour MonCash/NatCash, il est converti en HTG au taux du jour ci-dessous.
          </p>
          <form @submit.prevent="saveConfig" class="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
            <div>
              <label class="block text-xs text-[#64748b] mb-1">Prix mensuel</label>
              <input v-model.number="configForm.monthly_price" type="number" min="0" step="0.01" required
                     class="w-full bg-[#080c10] border border-[#1e2a38] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#06b6d4]" />
            </div>
            <div>
              <label class="block text-xs text-[#64748b] mb-1">Devise de base</label>
              <input v-model="configForm.currency" type="text" maxlength="3" required
                     class="w-full bg-[#080c10] border border-[#1e2a38] rounded-lg px-3 py-2 text-sm uppercase focus:outline-none focus:border-[#06b6d4]" />
            </div>
            <div>
              <label class="block text-xs text-[#64748b] mb-1">Taux du jour (1 {{ configForm.currency }} = ? HTG)</label>
              <input v-model.number="configForm.exchange_rate_usd_htg" type="number" min="0" step="0.01" required
                     class="w-full bg-[#080c10] border border-[#1e2a38] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#06b6d4]" />
            </div>
            <div class="sm:col-span-3">
              <label class="flex items-center gap-3 cursor-pointer select-none">
                <span class="relative inline-flex">
                  <input type="checkbox" v-model="configForm.auto_release" class="sr-only peer" />
                  <div class="w-10 h-6 bg-[#1e2a38] rounded-full peer peer-checked:bg-[#06b6d4] transition-colors"></div>
                  <div class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-4"></div>
                </span>
                <span class="text-sm font-medium">Livraison automatique de la clé</span>
              </label>
              <p class="text-xs text-[#64748b] mt-1 ml-13">
                <template v-if="configForm.auto_release">
                  Activé — la clé est générée et affichée dès que le paiement est confirmé par le fournisseur.
                </template>
                <template v-else>
                  Désactivé — après paiement, le client voit "contactez l'admin". Un admin doit cliquer "Activer" pour générer la clé.
                </template>
              </p>
            </div>
            <div class="sm:col-span-3 flex items-center gap-3">
              <button type="submit" class="btn-gold" :disabled="configSaving">
                {{ configSaving ? 'Enregistrement...' : 'Enregistrer' }}
              </button>
              <span v-if="configSaved" class="text-sm text-emerald-400">Enregistré ✓</span>
              <span class="text-xs text-[#64748b]">
                Exemple, 2 mois : carte = {{ (configForm.monthly_price * 2).toFixed(2) }} {{ configForm.currency }} ·
                MonCash/NatCash = {{ (configForm.monthly_price * 2 * configForm.exchange_rate_usd_htg).toFixed(2) }} HTG
              </span>
            </div>
          </form>
        </div>

        <!-- Activation manuelle d'un plan -->
        <div class="card p-6 mb-8">
          <h2 class="font-syne text-lg font-bold mb-4">Activer un plan manuellement</h2>
          <p class="text-xs text-[#64748b] mb-4">
            Pour un paiement reçu hors-ligne (cash, chèque, virement...). L'adresse MAC et l'email doivent
            correspondre à un client déjà enregistré.
          </p>
          <form @submit.prevent="activerPlan" class="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
            <div>
              <label class="block text-xs text-[#64748b] mb-1">Adresse MAC du serveur</label>
              <input v-model="activerForm.mac" type="text" placeholder="AA:BB:CC:DD:EE:FF" required
                     class="w-full bg-[#080c10] border border-[#1e2a38] rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:border-[#06b6d4]" />
            </div>
            <div>
              <label class="block text-xs text-[#64748b] mb-1">Email du client</label>
              <input v-model="activerForm.email" type="email" required
                     class="w-full bg-[#080c10] border border-[#1e2a38] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#06b6d4]" />
            </div>
            <div>
              <label class="block text-xs text-[#64748b] mb-1">Nombre de mois</label>
              <input v-model.number="activerForm.months" type="number" min="1" required
                     class="w-full bg-[#080c10] border border-[#1e2a38] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#06b6d4]" />
            </div>
            <button type="submit" class="btn-gold" :disabled="activerLoading">
              {{ activerLoading ? 'Activation...' : 'Activer' }}
            </button>
          </form>
          <p v-if="activerError" class="text-sm text-red-400 mt-3">{{ activerError }}</p>
          <p v-if="activerSuccess" class="text-sm text-emerald-400 mt-3">
            Clé générée : <span class="font-mono">{{ activerSuccess.key }}</span> — expire le {{ activerSuccess.expiration_date }}
          </p>
        </div>

        <!-- Paiements en attente d'activation (auto_release=false) -->
        <div v-if="paiementsEnAttente.length" class="card p-6 mb-8">
          <h2 class="font-syne text-lg font-bold mb-1">Paiements en attente d'activation</h2>
          <p class="text-xs text-[#64748b] mb-4">
            Ces paiements ont été confirmés par le fournisseur mais la clé n'a pas encore été générée (livraison manuelle activée).
          </p>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-[#080c10] text-left text-[11px] uppercase tracking-wider text-[#64748b]">
                  <th class="px-4 py-3">Client</th>
                  <th class="px-4 py-3">MAC</th>
                  <th class="px-4 py-3">Fournisseur</th>
                  <th class="px-4 py-3">Montant</th>
                  <th class="px-4 py-3">Durée</th>
                  <th class="px-4 py-3">Date</th>
                  <th class="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in paiementsEnAttente" :key="p.id" class="border-t border-[#1e2a38]">
                  <td class="px-4 py-3">
                    <div>{{ p.client_prenom }} {{ p.client_nom }}</div>
                    <div class="text-xs text-[#64748b]">{{ p.client_email }}</div>
                  </td>
                  <td class="px-4 py-3 font-mono text-xs text-[#64748b]">{{ p.client_mac }}</td>
                  <td class="px-4 py-3">{{ p.provider }}</td>
                  <td class="px-4 py-3">{{ p.amount }} {{ p.currency }}</td>
                  <td class="px-4 py-3">{{ p.days_valid }} jours</td>
                  <td class="px-4 py-3 text-[#64748b]">{{ formatDate(p.created_at) }}</td>
                  <td class="px-4 py-3 text-right">
                    <button class="btn-gold !px-3 !py-1.5 !text-xs" :disabled="activatingPayment === p.id"
                            @click="activerPaiement(p)">
                      {{ activatingPayment === p.id ? '...' : 'Activer' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-if="activerPaiementError" class="text-sm text-red-400 mt-3">{{ activerPaiementError }}</p>
          <p v-if="activerPaiementSuccess" class="text-sm text-emerald-400 mt-3">
            Clé générée : <span class="font-mono">{{ activerPaiementSuccess.key }}</span> — expire le {{ activerPaiementSuccess.expiration_date }}
          </p>
        </div>

        <h2 class="font-syne text-xl font-bold mb-4">Clients</h2>
        <p v-if="error" class="text-sm text-red-400 mb-4">{{ error }}</p>

        <div class="card overflow-hidden">
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-[#080c10] text-left text-[11px] uppercase tracking-wider text-[#64748b]">
                <th class="px-4 py-3">Nom</th>
                <th class="px-4 py-3">Email</th>
                <th class="px-4 py-3">MAC</th>
                <th class="px-4 py-3">Licence</th>
                <th class="px-4 py-3">Compte</th>
                <th class="px-4 py-3">Inscrit le</th>
                <th class="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              <template v-for="c in clients" :key="c.id">
                <tr class="border-t border-[#1e2a38] cursor-pointer hover:bg-[#06b6d4]/5" @click="toggleHistorique(c)">
                  <td class="px-4 py-3">{{ c.prenom }} {{ c.nom }}</td>
                  <td class="px-4 py-3">{{ c.email }}</td>
                  <td class="px-4 py-3 font-mono text-xs text-[#64748b]">{{ c.mac }}</td>
                  <td class="px-4 py-3">
                    <span v-if="c.licence_active === null" class="text-[#64748b]">—</span>
                    <span v-else :class="c.licence_active ? 'text-emerald-400' : 'text-red-400'" class="font-semibold">
                      {{ c.licence_active ? 'Active' : 'Expirée' }}
                    </span>
                    <span v-if="c.licence_expiration" class="text-xs text-[#64748b] ml-1">({{ c.licence_expiration }})</span>
                  </td>
                  <td class="px-4 py-3">
                    <span :class="c.suspended ? 'text-red-400' : 'text-emerald-400'" class="font-semibold">
                      {{ c.suspended ? 'Suspendu' : 'Actif' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-[#64748b]">{{ formatDate(c.created_at) }}</td>
                  <td class="px-4 py-3 text-right" @click.stop>
                    <button v-if="c.suspended" class="btn-gold !px-3 !py-1.5 !text-xs" @click="activer(c)">Activer</button>
                    <button v-else class="bg-red-500/10 text-red-400 border border-red-500/30 rounded-full px-3 py-1.5 text-xs font-semibold hover:bg-red-500/20"
                            @click="suspendre(c)">Suspendre</button>
                  </td>
                </tr>
                <tr v-if="ouvert === c.id" class="border-t border-[#1e2a38] bg-[#080c10]/60">
                  <td colspan="7" class="px-4 py-4">
                    <p class="text-xs uppercase tracking-wider text-[#64748b] mb-2">Historique des clés</p>
                    <p v-if="!historiqueDetail?.licence_keys?.length" class="text-sm text-[#64748b]">Aucune clé générée</p>
                    <ul v-else class="space-y-1 text-sm mb-3">
                      <li v-for="k in historiqueDetail.licence_keys" :key="k.id" class="flex gap-4 items-center">
                        <span class="text-[#64748b]">{{ formatDate(k.created_at) }}</span>
                        <span>expire le {{ k.expiration_date }}</span>
                        <span class="text-[#64748b]">({{ k.days_valid }} jours)</span>
                        <button
                          class="ml-auto text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded p-1 transition-colors"
                          title="Supprimer cette clé et le paiement associé"
                          @click.stop="supprimerHistorique(k.id, ouvert)"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </li>
                    </ul>
                    <p class="text-xs uppercase tracking-wider text-[#64748b] mb-2">Paiements</p>
                    <p v-if="!historiqueDetail?.payments?.length" class="text-sm text-[#64748b]">Aucun paiement</p>
                    <ul v-else class="space-y-1 text-sm">
                      <li v-for="p in historiqueDetail.payments" :key="p.id" class="flex gap-4">
                        <span class="text-[#64748b]">{{ formatDate(p.created_at) }}</span>
                        <span>{{ p.provider }}</span>
                        <span>{{ p.amount }} {{ p.currency }}</span>
                        <span :class="p.status === 'success' ? 'text-emerald-400' : p.status === 'failed' ? 'text-red-400' : 'text-amber-400'">
                          {{ p.status }}
                        </span>
                      </li>
                    </ul>
                  </td>
                </tr>
              </template>
              <tr v-if="!loading && clients.length === 0">
                <td colspan="7" class="px-4 py-10 text-center text-[#64748b]">Aucun client enregistré</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const token = ref(localStorage.getItem('infini_admin_token') || '')
const loginForm = ref({ email: '', password: '' })
const loginError = ref('')
const loading = ref(false)
const error = ref('')
const clients = ref([])
const ouvert = ref(null)
const historiqueDetail = ref(null)

const configForm = ref({ monthly_price: 0, currency: 'USD', exchange_rate_usd_htg: 0, auto_release: false })
const configSaving = ref(false)
const configSaved = ref(false)

const activerForm = ref({ mac: '', email: '', months: 1 })
const activerLoading = ref(false)
const activerError = ref('')
const activerSuccess = ref(null)

const paiementsEnAttente = ref([])
const activatingPayment = ref(null)
const activerPaiementError = ref('')
const activerPaiementSuccess = ref(null)

const authHeaders = () => ({ Authorization: `Bearer ${token.value}` })

const formatDate = (value) => {
  if (!value) return '-'
  try { return new Date(value).toLocaleString('fr-FR') } catch { return value }
}

const login = async () => {
  loading.value = true
  loginError.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginForm.value),
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || 'Connexion impossible')
    }
    const data = await res.json()
    token.value = data.access_token
    localStorage.setItem('infini_admin_token', token.value)
    await Promise.all([fetchClients(), fetchConfig(), fetchPaiementsEnAttente()])
  } catch (e) {
    loginError.value = e.message
  } finally {
    loading.value = false
  }
}

const logout = () => {
  token.value = ''
  clients.value = []
  localStorage.removeItem('infini_admin_token')
}

const fetchClients = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/admin/clients`, { headers: authHeaders() })
    if (res.status === 401 || res.status === 403) {
      logout()
      return
    }
    if (!res.ok) throw new Error('Impossible de charger les clients')
    clients.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const toggleHistorique = async (c) => {
  if (ouvert.value === c.id) {
    ouvert.value = null
    return
  }
  ouvert.value = c.id
  try {
    const res = await fetch(`${API_BASE}/api/admin/clients/${c.id}`, { headers: authHeaders() })
    historiqueDetail.value = await res.json()
  } catch {
    historiqueDetail.value = null
  }
}

const activer = async (c) => {
  const res = await fetch(`${API_BASE}/api/admin/clients/${c.id}/activer`, { method: 'POST', headers: authHeaders() })
  if (res.ok) c.suspended = false
}

const suspendre = async (c) => {
  const res = await fetch(`${API_BASE}/api/admin/clients/${c.id}/suspendre`, { method: 'POST', headers: authHeaders() })
  if (res.ok) c.suspended = true
}

const supprimerHistorique = async (keyId, clientId) => {
  if (!confirm('Supprimer cette clé et le paiement associé ? Cette action est irréversible.')) return
  const res = await fetch(`${API_BASE}/api/admin/historique/${keyId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (res.ok || res.status === 204) {
    const detail = await fetch(`${API_BASE}/api/admin/clients/${clientId}`, { headers: authHeaders() })
    historiqueDetail.value = detail.ok ? await detail.json() : null
    await fetchClients()
  }
}

const fetchConfig = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/admin/config`, { headers: authHeaders() })
    if (!res.ok) return
    const data = await res.json()
    configForm.value = {
      monthly_price: data.monthly_price,
      currency: data.currency,
      exchange_rate_usd_htg: data.exchange_rate_usd_htg,
      auto_release: data.auto_release ?? false,
    }
  } catch {
    // silencieux : la config par défaut s'affiche dans le formulaire
  }
}

const fetchPaiementsEnAttente = async () => {
  try {
    const res = await fetch(`${API_BASE}/api/admin/paiements/en-attente`, { headers: authHeaders() })
    if (res.ok) paiementsEnAttente.value = await res.json()
  } catch {
    // silencieux
  }
}

const activerPaiement = async (p) => {
  activatingPayment.value = p.id
  activerPaiementError.value = ''
  activerPaiementSuccess.value = null
  try {
    const res = await fetch(`${API_BASE}/api/admin/paiements/${p.id}/activer`, {
      method: 'POST',
      headers: authHeaders(),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Activation impossible')
    activerPaiementSuccess.value = data
    paiementsEnAttente.value = paiementsEnAttente.value.filter(x => x.id !== p.id)
    await fetchClients()
  } catch (e) {
    activerPaiementError.value = e.message
  } finally {
    activatingPayment.value = null
  }
}

const activerPlan = async () => {
  activerLoading.value = true
  activerError.value = ''
  activerSuccess.value = null
  try {
    const res = await fetch(`${API_BASE}/api/admin/clients/activer-plan`, {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(activerForm.value),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Activation impossible')
    activerSuccess.value = data
    await fetchClients()
  } catch (e) {
    activerError.value = e.message
  } finally {
    activerLoading.value = false
  }
}

const saveConfig = async () => {
  configSaving.value = true
  configSaved.value = false
  try {
    const res = await fetch(`${API_BASE}/api/admin/config`, {
      method: 'PUT',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(configForm.value),
    })
    if (res.ok) {
      configSaved.value = true
      setTimeout(() => { configSaved.value = false }, 2000)
    }
  } finally {
    configSaving.value = false
  }
}

onMounted(() => {
  if (token.value) {
    fetchClients()
    fetchConfig()
    fetchPaiementsEnAttente()
  }
})
</script>

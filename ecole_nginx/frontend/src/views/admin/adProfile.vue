<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore(); 

const props = defineProps({
  profilesData: Object,
  details: Boolean,
})

const BASE_URL = import.meta.env.VITE_APP_BASE_URL ?? ''

const allPermissions = ref([])
const allRole        = ref([])
const dataProfile    = ref({})

const userPermissions = ref([])
const hasPermission   = (name) => userPermissions.value.includes(name)

const toast = ref({ show: false, msg: '', ok: true })
const notify = (msg, ok = true) => {
  toast.value = { show: true, msg, ok }
  setTimeout(() => (toast.value.show = false), 3000)
}

const isEditing    = ref(false)
const profileLoad  = ref(false)
const logoPreview  = ref(null)
const profileErrors = ref({})

const profileForm = ref({
  nom: '', email: '', ligne1: '', ligne2: '', adresse: '', logo_image_path: null,
  is_receive_arriere: false,
})

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    logoPreview.value = ev.target.result
    profileForm.value.logo_image_path = ev.target.result
  }
  reader.readAsDataURL(file)
}

const getProfile = async () => {
  try {
    const { data } = await axios.get(BASE_URL + '/get-profile')
    const d = data.data
    dataProfile.value = d
    Object.assign(profileForm.value, {
      nom: d.nom, email: d.email,
      ligne1: d.ligne1, ligne2: d.ligne2, adresse: d.adresse,
      is_receive_arriere: d.is_receive_arriere ?? false,
    })
    if (d.logo_image_base64) logoPreview.value = d.logo_image_base64
    isEditing.value = true
  } catch { /* silencieux */ }
}

const submitProfile = async () => {
  profileErrors.value = {}
  if (!profileForm.value.nom)   { profileErrors.value.nom = 'Le nom est requis.'; return }
  if (!profileForm.value.email) { profileErrors.value.email = "L'email est requis."; return }
  profileLoad.value = true
  try {
    await axios.post('/profile', profileForm.value)
    notify(isEditing.value ? 'Profil mis à jour !' : 'Profil enregistré !')
    isEditing.value = true
  } catch (err) {
    console.log(err.response);
    
    if (err.response?.data?.errors) profileErrors.value = err.response.data.errors
    else notify('Erreur lors de la sauvegarde.', false)
  } finally {
    profileLoad.value = false
  }
}

/* ── RÔLES ── */
const roleLoad = ref(false)
const formRole = ref({ user_id: '', role: [], searchLabel: '' })

const assignRoleToUser = async () => {
  if (!formRole.value.user_id) { notify('Sélectionnez un utilisateur.', false); return }
  roleLoad.value = true
  try {
    await axios.post(BASE_URL + '/assign-role-to-user', formRole.value)
    notify('Rôle assigné avec succès !')
  } catch {
    notify("Erreur lors de l'assignation.", false)
  } finally {
    roleLoad.value = false
  }
}

/* ── PERMISSIONS ── */
const permLoad = ref(false)
const formPermission = ref({ role: '', user_id: '', permission: [], searchLabel: '' })

const getPermissionByRole = async () => {
  formPermission.value.user_id = ''
  formPermission.value.searchLabel = ''
  formPermission.value.permission = []
  if (!formPermission.value.role) return
  try {
    const { data } = await axios.get(BASE_URL + `/get-permission-by-role/${formPermission.value.role}`)
    formPermission.value.permission = (data.permis ?? []).map(p => p.id)
  } catch { /* silencieux */ }
}

const assignPermission = async () => {
  if (!formPermission.value.role && !formPermission.value.user_id) {
    notify('Choisissez un rôle ou un utilisateur.', false); return
  }
  permLoad.value = true
  try {
    await axios.post(BASE_URL + '/assign-permission-to-role', formPermission.value)
    notify('Permissions mises à jour !')
  } catch {
    notify('Erreur lors de la mise à jour.', false)
  } finally {
    permLoad.value = false
  }
}

/* ── VUES PAR RÔLE ── */
const ALL_NAV = [
  { id: 'home',      label: 'Dashboard',     subs: [
    { id: 'home.suivi_paiement', label: 'Suivi de paiement' },
    { id: 'home.stats_etudiant', label: 'Statistiques étudiants' },
    { id: 'home.classes',        label: 'Détail des classes' },
  ]},
  { id: 'admin',     label: 'Administration', subs: [] },
  { id: 'etudiant',  label: 'Étudiant',       subs: [
    { id: 'etudiant.badge', label: 'Générer badge' },
  ]},
  { id: 'promus',    label: 'Promus',         subs: [] },
  { id: 'prof',      label: 'Professeur',     subs: [] },
  { id: 'cours',     label: 'Cours',          subs: [] },
  { id: 'notes',     label: 'Notes',          subs: [] },
  { id: 'presences', label: 'Présences',      subs: [] },
  { id: 'paiement',  label: 'Paiement',       subs: [] },
  { id: 'vente',     label: 'Finances',       subs: [
    { id: 'vente.vente',         label: 'Vente' },
    { id: 'vente.produits',      label: 'Produits' },
    { id: 'vente.depenses',      label: 'Dépenses' },
    { id: 'vente.prets',         label: 'Prêts' },
    { id: 'vente.payroll',       label: 'Payroll' },
    { id: 'vente.transactions',  label: 'Autre transaction' },
  ]},
  { id: 'rapport',   label: 'Rapport',        subs: [] },
  { id: 'settings',  label: 'Paramètres',     subs: [
    { id: 'settings.exams',        label: 'Examens' },
    { id: 'settings.facultes',     label: 'Facultés' },
    { id: 'settings.annees',       label: 'Années' },
    { id: 'settings.classes',      label: 'Classes' },
    { id: 'settings.paiements',    label: 'Paiements' },
    { id: 'settings.frais',        label: 'Frais' },
    { id: 'settings.frais_divers', label: 'Frais Divers' },
  ]},
  { id: 'log',        label: 'Log',           subs: [] },
  { id: 'abonnement', label: 'Abonnement',    subs: [] },
]

const vuesRoleId   = ref('')
const vuesAllTabs  = ref(true)
const vuesChecked  = ref([])
const vuesLoad     = ref(false)

const selectRoleForVues = () => {
  const role = allRole.value.find(r => r.id === vuesRoleId.value)
  if (!role || role.accessible_tabs == null) {
    vuesAllTabs.value = true
    vuesChecked.value = []
  } else {
    vuesAllTabs.value = false
    vuesChecked.value = [...role.accessible_tabs]
  }
}

const toggleTab = (id, subs) => {
  if (vuesChecked.value.includes(id)) {
    const subIds = subs.map(s => s.id)
    vuesChecked.value = vuesChecked.value.filter(t => t !== id && !subIds.includes(t))
  } else {
    vuesChecked.value = [...vuesChecked.value, id]
  }
}

const toggleSub = (subId) => {
  if (vuesChecked.value.includes(subId))
    vuesChecked.value = vuesChecked.value.filter(t => t !== subId)
  else
    vuesChecked.value = [...vuesChecked.value, subId]
}

const submitVues = async () => {
  if (!vuesRoleId.value) return
  vuesLoad.value = true
  try {
    const tabs = vuesAllTabs.value ? null : vuesChecked.value
    await axios.patch(BASE_URL + `/roles/${vuesRoleId.value}/tabs`, { accessible_tabs: tabs })
    const idx = allRole.value.findIndex(r => r.id === vuesRoleId.value)
    if (idx >= 0) allRole.value[idx].accessible_tabs = tabs
    notify('Vues du rôle mises à jour !')
  } catch {
    notify('Erreur lors de la mise à jour.', false)
  } finally {
    vuesLoad.value = false
  }
}

/* ── MODAL RECHERCHE ── */
const showModal    = ref(false)
const activeModal  = ref('role')
const modalSearch  = ref('')
const modalResults = ref([])
const modalInput   = ref(null)
let   searchTimer  = null

const openModal = (type) => {
  activeModal.value  = type
  modalSearch.value  = ''
  modalResults.value = []
  showModal.value    = true
  nextTick(() => modalInput.value?.focus())
}
const closeModal = () => { showModal.value = false }

const onModalSearch = () => {
  clearTimeout(searchTimer)
  if (!modalSearch.value || modalSearch.value.length < 2) { modalResults.value = []; return }
  searchTimer = setTimeout(async () => {
    const ep = activeModal.value === 'role' ? '/fetch-data-with-role' : '/fetch-data-with-permission'
    try {
      const { data } = await axios.get(BASE_URL + ep, { params: { q: modalSearch.value } })
      modalResults.value = data.data ?? []
    } catch { modalResults.value = [] }
  }, 300)
}

const selectPerson = (person) => {
  if (activeModal.value === 'permission') {
    formPermission.value.user_id     = person.id
    formPermission.value.searchLabel = `${person.prenom} ${person.nom}`
    formPermission.value.role        = ''
    formPermission.value.permission  = person.permissions ?? []
  } else {
    formRole.value.user_id     = person.id
    formRole.value.searchLabel = `${person.prenom} ${person.nom}`
    formRole.value.role        = person.roles ?? []
  }
  closeModal()
}

/* ── MON PROFIL UTILISATEUR ── */
const userForm = ref({ id:'', prenom: '', nom: '', email: '', username: '',process:false })
const updateUserProfile = async () => {
  userForm.value.process=true
  try {
    await axios.patch('/user/profile', userForm.value)
    notify('Profil utilisateur mis à jour !')
    get_my_profile()
    userForm.value.id=''
  } catch(error) { 
    console.log(error);
    
    notify('Erreur.', false) 
  }finally{
    userForm.value.process = false
  }
}
 
const passwordForm = ref({ current: '', newPw: '', confirm: '', processing: false })
const pwMismatch   = computed(() =>
  passwordForm.value.confirm && passwordForm.value.newPw !== passwordForm.value.confirm
)

const updatePassword = async () => {
  if (pwMismatch.value || !passwordForm.value.current || !passwordForm.value.newPw) {
    notify('Vérifiez les champs mot de passe.', false); return
  }
  passwordForm.value.processing = true
  try {
    await axios.put('/password-change-user-global', {
      current_password: passwordForm.value.current,
      password: passwordForm.value.newPw,
      password_confirmation: passwordForm.value.confirm,
    })
    notify('Mot de passe changé !')
    
    passwordForm.value.current = ''
    passwordForm.value.newPw = ''
    passwordForm.value.confirm = ''
    authStore.logout()
  } catch (error) {
    notify(error.response?.data?.detail ?? error.response?.data?.message ?? 'Erreur.', false)
  } finally {
    passwordForm.value.processing = false
  }
}

const get_my_profile = async ()=>{
  const { data } = await axios.get(`/personnel/${authStore?.user.user?.userable_id}`)
  userForm.value ={ 
    id: authStore?.user.user?.userable_id,
    prenom: data?.data?.prenom,
    nom: data?.data?.nom,
    email: data?.data?.email,
    username: data?.data?.user?.username
  } 
  
}

onMounted(async () => {
  const [permRes, roleRes] = await Promise.allSettled([
    axios.get(BASE_URL + '/permission'),
    axios.get(BASE_URL + '/role'),
  ])
  if (permRes.status === 'fulfilled') {
    allPermissions.value  = permRes.value.data.data
    userPermissions.value = permRes.value.data.data.map(p => p.name)
  }
  if (roleRes.status === 'fulfilled') allRole.value = roleRes.value.data.data
  await getProfile()
  await get_my_profile()
})


</script>

<template>
  <div
    class="min-h-screen animate-[fadeUp_0.4s_ease_both]"
    style="background: #0f1117; font-family: 'DM Sans', 'Segoe UI', sans-serif;"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 px-6 pb-20">

      <!-- ════════════════════════════════════════
           MESSAGE POUR UTILISATEUR AVEC RÔLE "USER"
      ════════════════════════════════════════ -->
      <div v-if="authStore.isBaseUser" class="bg-amber-500/10 border border-amber-500/25 rounded-2xl p-5 mb-6">
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-[20px] shrink-0">ℹ️</div>
          <div class="flex-1">
            <h3 class="text-[14px] font-bold text-amber-300 mb-2">Accès limité</h3>
            <p class="text-[13px] text-amber-200/90 leading-relaxed mb-3">
              Votre compte n'a actuellement que le rôle <span class="font-semibold">"User"</span> de base.
              Pour accéder aux autres fonctionnalités du système, veuillez contacter l'administrateur pour qu'il vous attribue un rôle approprié :
            </p>
            <ul class="text-[12px] text-amber-200/80 space-y-1.5 ml-4">
              <li class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400/60 shrink-0"></span>
                <span><strong class="text-amber-300">Caissier</strong> - pour la gestion des paiements</span>
              </li>
              <li class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400/60 shrink-0"></span>
                <span><strong class="text-amber-300">Responsable financier</strong> - pour la trésorerie</span>
              </li>
              <li class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400/60 shrink-0"></span>
                <span><strong class="text-amber-300">Responsable des admissions</strong> - pour la gestion des étudiants</span>
              </li>
              <li class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400/60 shrink-0"></span>
                <span><strong class="text-amber-300">Responsable pédagogique</strong> - pour les notes et cours</span>
              </li>
              <li class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400/60 shrink-0"></span>
                <span><strong class="text-amber-300">Comptable</strong> - pour la comptabilité complète</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- ════════════════════════════════════════
           SECTION : PROFIL DE L'ÉCOLE
      ════════════════════════════════════════ -->
      <div v-if="!authStore.isBaseUser" class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 rounded-xl bg-[#4f8ef7]/10 border border-[#4f8ef7]/20 flex items-center justify-center text-[16px] shrink-0">🏫</div>
        <div>
          <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Profil de l'école</h1>
          <p class="text-[12px] text-[#7c83a0]">Informations générales et coordonnées</p>
        </div>
      </div>

      <div v-if="!authStore.isBaseUser" class="bg-[#161b26] rounded-2xl border border-white/[0.07] p-6 mb-6">
        <form @submit.prevent="submitProfile">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

            <div class="flex flex-col gap-1.5">
              <label class="field-label">Nom de l'école</label>
              <input v-model="profileForm.nom" type="text" placeholder="Ex : Lycée Victor Hugo" class="field-input" />
              <span v-if="profileErrors.nom" class="error-msg">⚠ {{ profileErrors.nom }}</span>
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="field-label">Email</label>
              <input v-model="profileForm.email" type="email" placeholder="contact@ecole.fr" class="field-input" />
              <span v-if="profileErrors.email" class="error-msg">⚠ {{ profileErrors.email }}</span>
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="field-label">Téléphone principal</label>
              <input v-model="profileForm.ligne1" type="tel" placeholder="+509 00 00 00 00" class="field-input" />
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="field-label">Téléphone secondaire</label>
              <input v-model="profileForm.ligne2" type="tel" placeholder="+509 00 00 00 00" class="field-input" />
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="field-label">Adresse</label>
              <input v-model="profileForm.adresse" type="text" placeholder="12 rue des Écoles, Port-au-Prince" class="field-input" />
            </div>

            <!-- Toggle arriérés -->
            <div class="md:col-span-2 flex items-start gap-3 p-3 rounded-xl bg-[#0d1117] border border-white/[0.06]">
              <button type="button"
                @click="profileForm.is_receive_arriere = !profileForm.is_receive_arriere"
                class="relative w-9 h-5 rounded-full transition-colors shrink-0 mt-0.5"
                :class="profileForm.is_receive_arriere ? 'bg-[#4f8ef7]' : 'bg-white/[0.08]'">
                <span class="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all"
                  :class="profileForm.is_receive_arriere ? 'left-[18px]' : 'left-0.5'"></span>
              </button>
              <div>
                <p class="text-[12px] font-semibold text-[#c9d1d9]">Vérifier les arriérés de l'année précédente</p>
                <p class="text-[11px] text-[#7c83a0] mt-0.5">Si activé, un paiement pour l'année en cours est refusé si l'étudiant a des versements impayés de l'année précédente.</p>
              </div>
            </div>

            <!-- Logo upload -->
            <div class="flex flex-col gap-1.5">
              <label class="field-label">Logo de l'école</label>
              <div class="flex items-center gap-3">
                <label class="flex-1 flex items-center gap-2.5 bg-[#0d1117] border border-white/[0.08] rounded-xl px-3 py-2 cursor-pointer hover:border-[#4f8ef7]/40 transition-colors group">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" class="w-4 h-4 text-[#7c83a0] group-hover:text-[#7aaeff] transition-colors shrink-0"><path d="M4 16l4-4a2 2 0 012.83 0L14 15m-2-3l1.59-1.59A2 2 0 0116 10l4 4m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                  <span class="text-[12px] text-[#7c83a0] group-hover:text-[#c0c7d8] transition-colors">Choisir un fichier…</span>
                  <input type="file" accept="image/*" @change="handleFileChange" class="sr-only" />
                </label>
                <div class="w-11 h-11 rounded-xl overflow-hidden border border-white/[0.08] shrink-0 bg-[#0d1117] flex items-center justify-center">
                  <img v-if="logoPreview" :src="logoPreview" alt="Logo" class="w-full h-full object-cover" />
                  <span v-else class="text-[18px] opacity-30">🏫</span>
                </div>
              </div>
            </div>

          </div>

          <div class="flex justify-end mt-5 pt-4 border-t border-white/[0.05]">
            <button type="submit" class="action-btn action-btn--blue" :disabled="profileLoad">
              <svg v-if="profileLoad" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/></svg>
              <span>{{ isEditing ? 'Mettre à jour' : 'Enregistrer' }}</span>
            </button>
          </div>
        </form>
      </div>

      <!-- ════════════════════════════════════════
           SECTION : RÔLES & PERMISSIONS
      ════════════════════════════════════════ -->
      <div v-if="!authStore.isBaseUser" class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-[16px] shrink-0">🔐</div>
        <div>
          <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Rôles &amp; Permissions</h1>
          <p class="text-[12px] text-[#7c83a0]">Gérer les accès par rôle et par utilisateur</p>
        </div>
      </div>

      <div v-if="!authStore.isBaseUser && hasPermission('Voir role')" class="bg-[#161b26] rounded-2xl border border-white/[0.07] p-6 mb-6 space-y-6">

        <!-- ── Assigner rôle ── -->
        <form @submit.prevent="assignRoleToUser">
          <div class="flex items-center gap-2 mb-4">
            <span class="w-6 h-6 rounded-lg bg-violet-500/10 border border-violet-500/15 text-violet-400 flex items-center justify-center text-[12px]">👤</span>
            <h2 class="text-[13px] font-semibold text-[#c9d1d9]">Assigner un rôle à un utilisateur</h2>
          </div>

          <div class="mb-4 max-w-sm">
            <label class="field-label">Personnel / Professeur</label>
            <button type="button" @click="openModal('role')"
              class="w-full flex items-center gap-2.5 bg-[#0d1117] border border-white/[0.08] rounded-xl px-3 py-2.5 text-[13px] text-left hover:border-violet-500/30 transition-colors group mt-1.5">
              <svg class="w-4 h-4 text-[#7c83a0] group-hover:text-violet-400 transition-colors shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
              <span :class="formRole.searchLabel ? 'text-[#c9d1d9]' : 'text-[#7c83a0]'">
                {{ formRole.searchLabel || 'Rechercher un personnel…' }}
              </span>
            </button>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2.5">
            <label v-for="role in allRole" :key="role.id"
              class="flex items-center gap-2.5 p-2.5 rounded-xl border cursor-pointer transition-all"
              :class="formRole.role.includes(role.id)
                ? 'border-violet-500/35 bg-violet-500/8 shadow-sm'
                : 'border-white/[0.06] hover:border-violet-500/20 hover:bg-violet-500/5 bg-[#0d1117]/50'">
              <input type="checkbox" :value="role.id" v-model="formRole.role" class="sr-only" />
              <span class="relative w-8 h-4 rounded-full transition-colors shrink-0"
                :class="formRole.role.includes(role.id) ? 'bg-violet-500' : 'bg-white/[0.08]'">
                <span class="absolute top-0.5 w-3 h-3 bg-white rounded-full shadow transition-all"
                  :class="formRole.role.includes(role.id) ? 'left-[18px]' : 'left-0.5'"></span>
              </span>
              <span class="text-[12px] font-medium text-[#c9d1d9] leading-tight">{{ role.name }}</span>
            </label>
          </div>

          <div v-if="hasPermission('Ajouter role') || hasPermission('Modifier role')"
            class="flex justify-end mt-5 pt-4 border-t border-white/[0.05]">
            <button type="submit" class="action-btn action-btn--violet" :disabled="roleLoad">
              <svg v-if="roleLoad" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/></svg>
              <span>Sauvegarder</span>
            </button>
          </div>
        </form>

        <!-- ── Permissions ── -->
        <div v-if="hasPermission('Voir permission')" class="border-t border-white/[0.05] pt-5">
          <div class="flex items-center gap-2 mb-4">
            <span class="w-6 h-6 rounded-lg bg-emerald-500/10 border border-emerald-500/15 text-emerald-400 flex items-center justify-center text-[12px]">🛡</span>
            <h2 class="text-[13px] font-semibold text-[#c9d1d9]">Gérer les permissions</h2>
          </div>

          <form @submit.prevent="assignPermission">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
              <div class="flex flex-col gap-1.5">
                <label class="field-label">Rôle cible</label>
                <div class="relative">
                  <select v-model="formPermission.role" @change="getPermissionByRole" class="dark-select pr-8">
                    <option value="" disabled>Choisir un rôle…</option>
                    <option v-for="role in allRole" :key="role.id" :value="role.id">{{ role.name }}</option>
                  </select>
                </div>
              </div>
              <div v-if="hasPermission('Modifier permission')" class="flex flex-col gap-1.5">
                <label class="field-label">Personnel / Professeur</label>
                <button type="button" @click="openModal('permission')"
                  class="w-full flex items-center gap-2.5 bg-[#0d1117] border border-white/[0.08] rounded-xl px-3 py-2.5 text-[13px] text-left hover:border-emerald-500/30 transition-colors group">
                  <svg class="w-4 h-4 text-[#7c83a0] group-hover:text-emerald-400 transition-colors shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
                  <span :class="formPermission.searchLabel ? 'text-[#c9d1d9]' : 'text-[#7c83a0]'">
                    {{ formPermission.searchLabel || 'Rechercher un personnel…' }}
                  </span>
                </button>
              </div>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2.5">
              <label v-for="perm in allPermissions" :key="perm.id"
                class="flex items-center gap-2.5 p-2.5 rounded-xl border cursor-pointer transition-all"
                :class="formPermission.permission.includes(perm.id)
                  ? 'border-emerald-500/35 bg-emerald-500/8 shadow-sm'
                  : 'border-white/[0.06] hover:border-emerald-500/20 hover:bg-emerald-500/5 bg-[#0d1117]/50'">
                <input type="checkbox" :value="perm.id" v-model="formPermission.permission" class="sr-only" />
                <span class="relative w-8 h-4 rounded-full transition-colors shrink-0"
                  :class="formPermission.permission.includes(perm.id) ? 'bg-emerald-500' : 'bg-white/[0.08]'">
                  <span class="absolute top-0.5 w-3 h-3 bg-white rounded-full shadow transition-all"
                    :class="formPermission.permission.includes(perm.id) ? 'left-[18px]' : 'left-0.5'"></span>
                </span>
                <span class="text-[12px] font-medium text-[#c9d1d9] leading-tight">{{ perm.name }}</span>
              </label>
            </div>

            <div v-if="hasPermission('Modifier permission')"
              class="flex justify-end mt-5 pt-4 border-t border-white/[0.05]">
              <button type="submit" class="action-btn action-btn--emerald" :disabled="permLoad">
                <svg v-if="permLoad" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/></svg>
                <span>Sauvegarder permissions</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- ════════════════════════════════════════
           SECTION : VUES PAR RÔLE
      ════════════════════════════════════════ -->
      <div v-if="!authStore.isBaseUser && hasPermission('Voir role')" class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-[16px] shrink-0">👁</div>
        <div>
          <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Vues par rôle</h1>
          <p class="text-[12px] text-[#7c83a0]">Choisissez quels onglets chaque rôle peut voir</p>
        </div>
      </div>

      <div v-if="!authStore.isBaseUser && hasPermission('Voir role')" class="bg-[#161b26] rounded-2xl border border-white/[0.07] p-6 mb-6">
        <!-- Sélecteur de rôle -->
        <div class="mb-5 max-w-xs">
          <label class="field-label">Rôle</label>
          <div class="relative mt-1.5">
            <select v-model="vuesRoleId" @change="selectRoleForVues" class="dark-select">
              <option value="" disabled>Choisir un rôle…</option>
              <option v-for="role in allRole" :key="role.id" :value="role.id">{{ role.name }}</option>
            </select>
          </div>
        </div>

        <template v-if="vuesRoleId">
          <!-- Accès total -->
          <label class="flex items-center gap-2.5 p-2.5 rounded-xl border cursor-pointer mb-4 transition-all"
            :class="vuesAllTabs ? 'border-sky-500/35 bg-sky-500/[0.08]' : 'border-white/[0.06] bg-[#0d1117]/50'">
            <input type="checkbox" v-model="vuesAllTabs" @change="vuesAllTabs && (vuesChecked = [])" class="sr-only" />
            <span class="relative w-8 h-4 rounded-full transition-colors shrink-0"
              :class="vuesAllTabs ? 'bg-sky-500' : 'bg-white/[0.08]'">
              <span class="absolute top-0.5 w-3 h-3 bg-white rounded-full shadow transition-all"
                :class="vuesAllTabs ? 'left-[18px]' : 'left-0.5'"></span>
            </span>
            <span class="text-[13px] font-semibold text-[#c9d1d9]">Accès total (tous les onglets)</span>
          </label>

          <template v-if="!vuesAllTabs">
            <p class="text-[11px] font-semibold tracking-widest text-[#7c83a0] uppercase mb-3">Onglets autorisés</p>
            <div class="space-y-0.5">
              <template v-for="item in ALL_NAV" :key="item.id">
                <!-- Onglet parent -->
                <label class="flex items-center gap-2.5 px-2.5 py-2 rounded-lg cursor-pointer hover:bg-white/[0.02] transition-colors">
                  <input type="checkbox" :checked="vuesChecked.includes(item.id)" @change="toggleTab(item.id, item.subs)" class="sr-only" />
                  <span class="relative w-8 h-4 rounded-full transition-colors shrink-0"
                    :class="vuesChecked.includes(item.id) ? 'bg-sky-500' : 'bg-white/[0.06]'">
                    <span class="absolute top-0.5 w-3 h-3 bg-white rounded-full shadow transition-all"
                      :class="vuesChecked.includes(item.id) ? 'left-[18px]' : 'left-0.5'"></span>
                  </span>
                  <span class="text-[12px] font-medium text-[#c9d1d9]">{{ item.label }}</span>
                </label>

                <!-- Sous-onglets (si parent coché et a des sous-items) -->
                <div v-if="vuesChecked.includes(item.id) && item.subs.length"
                  class="ml-8 pl-3 border-l border-white/[0.05] mb-1">
                  <div class="flex flex-wrap gap-2 py-2">
                    <label v-for="sub in item.subs" :key="sub.id"
                      class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border cursor-pointer transition-all text-[11px]"
                      :class="vuesChecked.includes(sub.id)
                        ? 'border-sky-500/35 bg-sky-500/[0.08] text-sky-300'
                        : 'border-white/[0.06] bg-[#0d1117]/50 text-[#7c83a0] hover:border-sky-500/20'">
                      <input type="checkbox" :checked="vuesChecked.includes(sub.id)" @change="toggleSub(sub.id)" class="sr-only" />
                      <span class="relative w-6 h-3 rounded-full transition-colors shrink-0"
                        :class="vuesChecked.includes(sub.id) ? 'bg-sky-500' : 'bg-white/[0.08]'">
                        <span class="absolute top-[1px] w-[10px] h-[10px] bg-white rounded-full shadow transition-all"
                          :class="vuesChecked.includes(sub.id) ? 'left-[13px]' : 'left-[1px]'"></span>
                      </span>
                      {{ sub.label }}
                    </label>
                  </div>
                </div>
              </template>
            </div>
          </template>

          <div class="flex justify-end mt-5 pt-4 border-t border-white/[0.05]">
            <button type="button" @click="submitVues" class="action-btn action-btn--blue" :disabled="vuesLoad">
              <svg v-if="vuesLoad" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/></svg>
              <span>Enregistrer</span>
            </button>
          </div>
        </template>
      </div>

      <!-- ════════════════════════════════════════
           SECTION : MON PROFIL UTILISATEUR
      ════════════════════════════════════════ -->
      <div class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-[16px] shrink-0">🧑</div>
        <div>
          <h1 class="text-[15px] font-bold text-[#e8eaf0] leading-tight">Mon profil</h1>
          <p class="text-[12px] text-[#7c83a0]">Vos informations personnelles</p>
        </div>
      </div>

      <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] p-6 mb-4">
        <form @submit.prevent="updateUserProfile">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-1.5">
              <label class="field-label">Prénom</label>
              <input v-model="userForm.prenom" type="text" placeholder="Votre prénom" class="field-input" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="field-label">Nom</label>
              <input v-model="userForm.nom" type="text" placeholder="Votre nom" class="field-input" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="field-label">Email</label>
              <input v-model="userForm.email" type="email" placeholder="vous@ecole.fr" class="field-input" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="field-label">Nom d'utilisateur</label>
              <input v-model="userForm.username" type="text" placeholder="@username" class="field-input" />
            </div>
          </div>
          <div class="flex justify-end mt-5 pt-4 border-t border-white/[0.05]">
            <!-- <button type="submit" class="">
              <span></span>
            </button> -->

             <button type="submit" class="action-btn action-btn--blue" :disabled="userForm.process">
              <svg v-if="userForm.process" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              <span>{{ userForm.process ? 'En cours…' : 'Mettre à jour' }}</span>
            </button>
          </div>
        </form>
      </div>

      <!-- ── Mot de passe ── -->
      <div class="bg-[#161b26] rounded-2xl border border-white/[0.07] p-6 mb-6">
        <div class="flex items-center gap-2 mb-5">
          <span class="w-6 h-6 rounded-lg bg-white/[0.05] border border-white/[0.07] text-[#7c83a0] flex items-center justify-center text-[13px]">🔑</span>
          <h2 class="text-[13px] font-semibold text-[#c9d1d9]">Changer le mot de passe</h2>
        </div>
        <form @submit.prevent="updatePassword">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="flex flex-col gap-1.5">
              <label class="field-label">Mot de passe actuel</label>
              <input v-model="passwordForm.current" type="password" placeholder="••••••••" class="field-input" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="field-label">Nouveau mot de passe</label>
              <input v-model="passwordForm.newPw" type="password" placeholder="••••••••" class="field-input" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="field-label">Confirmer</label>
              <input v-model="passwordForm.confirm" type="password" placeholder="••••••••"
                class="field-input"
                :class="pwMismatch ? '!border-red-500/40 focus:!border-red-500/60' : ''" />
              <span v-if="pwMismatch" class="error-msg">⚠ Les mots de passe ne correspondent pas.</span>
            </div>
          </div>
          <div class="flex justify-end mt-5 pt-4 border-t border-white/[0.05]">
            <button type="submit" class="action-btn action-btn--default" :disabled="passwordForm.processing">
              <svg v-if="passwordForm.processing" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              <span>{{ passwordForm.processing ? 'En cours…' : 'Changer le mot de passe' }}</span>
            </button>
          </div>
        </form>
      </div>

    </div>

    <!-- ════════════ MODAL RECHERCHE ════════════ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0">
        <div v-if="showModal"
          class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          @click.self="closeModal">
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 scale-95 translate-y-2"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95">
            <div v-if="showModal" class="bg-[#161b26] rounded-2xl border border-white/[0.09] shadow-2xl w-full max-w-md overflow-hidden">

              <div class="flex items-center justify-between px-5 py-4 border-b border-white/[0.07]">
                <h3 class="text-[13px] font-semibold text-[#e8eaf0]">
                  {{ activeModal === 'role' ? '👤 Assigner un rôle' : '🛡 Assigner une permission' }}
                </h3>
                <button @click="closeModal"
                  class="w-7 h-7 rounded-lg bg-white/[0.05] hover:bg-red-500/15 hover:text-red-400 text-[#7c83a0] flex items-center justify-center text-[13px] transition-colors">
                  ✕
                </button>
              </div>

              <div class="p-5">
                <div class="relative">
                  <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7c83a0]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
                  <input ref="modalInput" v-model="modalSearch" @input="onModalSearch" type="text"
                    placeholder="Tapez un nom pour rechercher…"
                    class="w-full bg-[#0d1117] border border-white/[0.08] rounded-xl pl-9 pr-3 py-2.5 text-[13px] text-[#c9d1d9] placeholder-[#7c83a0] focus:outline-none focus:border-[#4f8ef7]/40 transition" />
                </div>

                <div v-if="modalResults.length" class="mt-3 border border-white/[0.07] rounded-xl overflow-hidden divide-y divide-white/[0.04]">
                  <div v-for="person in modalResults" :key="person.id"
                    class="flex items-center justify-between px-4 py-2.5 cursor-pointer hover:bg-white/[0.03] transition-colors"
                    @click="selectPerson(person)">
                    <span class="font-semibold text-[13px] text-[#7aaeff]">{{ person.nom }}</span>
                    <span class="text-[13px] text-[#7c83a0]">{{ person.prenom }}</span>
                  </div>
                </div>
                <div v-else class="mt-3 text-center text-[12px] text-[#7c83a0] py-6">
                  {{ modalSearch ? `Aucun résultat pour « ${modalSearch} »` : 'Tapez au moins 2 caractères pour rechercher.' }}
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <!-- ════════════ TOAST ════════════ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0 translate-y-4">
        <div v-if="toast.show"
          class="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-xl text-[13px] font-medium"
          :class="toast.ok
            ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/25'
            : 'bg-red-500/15 text-red-300 border border-red-500/25'">
          <span>{{ toast.ok ? '✅' : '❌' }}</span>
          <span>{{ toast.msg }}</span>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.field-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #7c83a0;
}

.field-input {
  width: 100%;
  background: #0d1117;
  border: 1px solid rgba(255,255,255,0.08);
  color: #c9d1d9;
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}
.field-input::placeholder { color: #3d4d62; }
.field-input:focus { border-color: rgba(79,142,247,0.35); }

.dark-select {
  width: 100%;
  background: #0d1117;
  border: 1px solid rgba(255,255,255,0.08);
  color: #c9d1d9;
  border-radius: 10px;
  padding: 8px 30px 8px 12px;
  font-size: 13px;
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%237c83a0' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19.5 8.25l-7.5 7.5-7.5-7.5'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 14px;
  transition: border-color 0.15s;
}
.dark-select:focus { border-color: rgba(79,142,247,0.35); }
.dark-select option { background: #161b26; color: #c9d1d9; }

.error-msg { font-size: 11px; color: #f87171; }

/* ── Action buttons ── */


</style>

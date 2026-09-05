<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'

const props = defineProps({
  profilesData: Object,
  details: Boolean,
})

const BASE_URL = import.meta.env.VITE_APP_BASE_URL ?? ''

const allPermissions = ref([])
const allRole       = ref([])
const dataProfile   = ref({})

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
    })
    
    if (d.logo_image_base64) logoPreview.value = d.logo_image_base64
    isEditing.value = true
  } catch {
    /* silencieux en démo */
  }
}

const submitProfile = async () => {
  profileErrors.value = {}
  if (!profileForm.value.nom)   { profileErrors.value.nom = 'Le nom est requis.'; return }
  if (!profileForm.value.email) { profileErrors.value.email = "L'email est requis."; return }
  profileLoad.value = true
  try {
    await axios.post(BASE_URL + '/profile', profileForm.value)
    // , {
    //   headers: { 'Content-Type': 'multipart/form-data' },
    // }
    notify(isEditing.value ? 'Profil mis à jour !' : 'Profil enregistré !')
    isEditing.value = true
  } catch (err) {
    if (err.response?.data?.errors) profileErrors.value = err.response.data.errors
    else notify('Erreur lors de la sauvegarde.', false)
  } finally {
    profileLoad.value = false
  }
}

/* ─────────────────────────── RÔLES ─────────────────────────── */
const roleLoad = ref(false)
const formRole = ref({ user_id: '', role: [], searchLabel: '' })

const assignRoleToUser = async () => {
  if (!formRole.value.user_id) { notify('Sélectionnez un utilisateur.', false); return }
  roleLoad.value = true 
  
  try {
    await axios.post(BASE_URL + '/assign-role-to-user', formRole.value)
    notify('Rôle assigné avec succès !')
  } catch {
    notify('Erreur lors de l\'assignation.', false)
  } finally {
    roleLoad.value = false
  }
}

/* ─────────────────────────── PERMISSIONS ─────────────────────────── */
const permLoad = ref(false)
const formPermission = ref({ role: '', user_id: '', permission: [], searchLabel: '' })

const getPermissionByRole = async () => {
  formPermission.value.user_id = ''
  formPermission.value.searchLabel = ''
  formPermission.value.permission = []
  if (!formPermission.value.role) return
  try {
    const { data } = await axios.get(BASE_URL + `/get-permission-by-role/${formPermission.value.role}`)
    console.log(data);
    
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

/* ─────────────────────────── MODAL RECHERCHE ─────────────────────────── */
const showModal   = ref(false)
const activeModal = ref('role')   // 'role' | 'permission'
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
    const ep = activeModal.value === 'role'
      ? '/fetch-data-with-role'
      : '/fetch-data-with-permission'
    try {
      const { data } = await axios.get(BASE_URL + ep, { params: { q: modalSearch.value } })
      modalResults.value = data.data ?? []
    } catch { modalResults.value = [] }
  }, 300)
}

const selectPerson = (person) => {
  console.log(person,activeModal.value);
  
  if (activeModal.value === 'permission') {
    formPermission.value.user_id     = person.id
    formPermission.value.searchLabel = `${person.prenom} ${person.nom}`
    formPermission.value.role        = ''
    formPermission.value.permission = person.permissions ?? [] //(person.permissions ?? []).map(p => p.id)
    
  } else {
    formRole.value.user_id     = person.id
    formRole.value.searchLabel = `${person.prenom} ${person.nom}`
    formRole.value.role       = person.roles ?? [] //(person.roles ?? []).map(r => r.id)
  }
  closeModal()
}

/* ─────────────────────────── MON PROFIL UTILISATEUR ─────────────────────────── */
const userForm = ref({ prenom: '', nom: '', email: '' , username: ''})
const updateUserProfile = async () => {
  try {
    await axios.put(BASE_URL + '/user/profile', userForm.value)
    notify('Profil utilisateur mis à jour !')
  } catch { notify('Erreur.', false) }
}

/* ─────────────────────────── MOT DE PASSE ─────────────────────────── */
const passwordForm = ref({ current: '', newPw: '', confirm: '',processing:false })
const pwMismatch   = computed(() =>
  passwordForm.value.confirm && passwordForm.value.newPw !== passwordForm.value.confirm
)

const updatePassword = async () => {
  if (pwMismatch.value || !passwordForm.value.current || !passwordForm.value.newPw) {
    notify('Vérifiez les champs mot de passe.', false)
    return
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
passwordForm.value.processing = false
    // passwordForm.value = { current: '', newPw: '', confirm: '', processing: false }
  } catch (error) {
    if(error.response?.data?.detail){
      notify(error.response?.data?.detail, false)
    }else{

      notify(error.response?.data?.message, false)
    }
  } finally {
    passwordForm.value.processing = false
  }
}
 

/* ─── init ─── */
onMounted(async () => {
  const [permRes, roleRes] = await Promise.allSettled([
    axios.get(BASE_URL + '/permission'),
    axios.get(BASE_URL + '/role'),
  ])
  if (permRes.status === 'fulfilled') {
    allPermissions.value  = permRes.value.data.data
    userPermissions.value = permRes.value.data.data.map(p => p.name) // adapter selon l'API réelle
  }
  if (roleRes.status === 'fulfilled') allRole.value = roleRes.value.data.data
  await getProfile()
})
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 py-8 pb-20 text-slate-700 font-sans animate-[fadeUp_0.4s_ease_both]">

    <div class="flex items-center gap-3 mb-4">
      <div class="w-9 h-9 rounded-lg bg-sky-100 flex items-center justify-center text-sky-600 text-lg shrink-0">🏫</div>
      <div>
        <h1 class="text-lg font-bold text-slate-300 leading-tight">Profil de l'école</h1>
        <p class="text-xs text-slate-400">Informations générales et coordonnées</p>
      </div>
    </div>

    <div class="bg-[#161b22] rounded-2xl border border-slate-200 shadow-sm p-6 mb-8">
      <form @submit.prevent="submitProfile">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">

          <!-- Nom -->
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Nom de l'école</label>
            <input v-model="profileForm.nom" type="text" placeholder="Ex : Lycée Victor Hugo"
              class="field-input" />
            <span v-if="profileErrors.nom" class="text-xs text-red-500 flex items-center gap-1">⚠ {{ profileErrors.nom }}</span>
          </div>

          <!-- Email -->
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Email</label>
            <input v-model="profileForm.email" type="email" placeholder="contact@ecole.fr"
              class="field-input" />
            <span v-if="profileErrors.email" class="text-xs text-red-500 flex items-center gap-1">⚠ {{ profileErrors.email }}</span>
          </div>

          <!-- Téléphone 1 -->
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Téléphone principal</label>
            <input v-model="profileForm.ligne1" type="tel" placeholder="+221 77 000 00 00"
              class="field-input" />
          </div>

          <!-- Téléphone 2 -->
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Téléphone secondaire</label>
            <input v-model="profileForm.ligne2" type="tel" placeholder="+221 33 000 00 00"
              class="field-input" />
          </div>

          <!-- Adresse -->
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Adresse</label>
            <input v-model="profileForm.adresse" type="text" placeholder="12 rue des Écoles, Dakar"
              class="field-input" />
          </div>

          <!-- Logo -->
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Logo de l'école</label>
            <div class="flex items-center gap-3">
              <input type="file" accept="image/*" @change="handleFileChange"
                class="flex-1 border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-slate-50 text-slate-600 file:mr-3 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-sky-50 file:text-sky-600 hover:file:bg-sky-100 cursor-pointer focus:outline-none" />
              <img v-if="logoPreview" :src="logoPreview" alt="Logo"
                class="w-12 h-12 rounded-full object-cover border-2 border-slate-200 shadow-sm shrink-0" />
              <div v-else class="w-12 h-12 rounded-full bg-slate-100 border-2 border-dashed border-slate-300 flex items-center justify-center text-slate-500 text-xl shrink-0">🏫</div>
            </div>
          </div>

        </div>

        <!-- Footer -->
        <div class="flex justify-end mt-6 pt-5 border-t border-slate-100">
          <button type="submit"
            class="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-sky-600 hover:bg-sky-700 active:scale-95 text-white text-sm font-semibold shadow-sm shadow-sky-200 transition-all disabled:opacity-60 cursor-pointer"
            :disabled="profileLoad">
            <svg v-if="profileLoad" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
            </svg>
            <span>{{ isEditing ? '✏️ Mettre à jour' : '💾 Enregistrer' }}</span>
          </button>
        </div>
      </form>
    </div>

 
    <div class="flex items-center gap-3 mb-4">
      <div class="w-9 h-9 rounded-lg bg-violet-100 flex items-center justify-center text-violet-600 text-lg shrink-0">🔐</div>
      <div>
        <h1 class="text-lg font-bold text-slate-300 leading-tight">Rôles &amp; Permissions</h1>
        <p class="text-xs text-slate-400">Gérer les accès par rôle et par utilisateur</p>
      </div>
    </div>

    <div v-if="hasPermission('Voir role')" class="bg-[#161b22] rounded-2xl border border-slate-900 shadow-sm p-6 mb-8 space-y-8">

      <!-- ── ASSIGNER RÔLE ── -->
      <form @submit.prevent="assignRoleToUser">
        <h2 class="text-sm font-bold text-slate-700 mb-4 flex items-center gap-2">
          <span class="w-6 h-6 rounded-md bg-violet-100 text-violet-600 flex items-center justify-center text-xs">👤</span>
          Assigner un rôle à un utilisateur
        </h2>

        <div class="mb-5 max-w-sm">
          <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500 block mb-1">Personnel / Professeur</label>
          <button type="button" @click="openModal('role')"
            class="w-full flex items-center gap-2 border border-slate-800 rounded-lg px-3 py-2 text-sm bg-slate-900 text-slate-500 hover:border-sky-400 hover:bg-sky-50 transition text-left cursor-pointer">
            <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            <span :class="formRole.searchLabel ? 'text-slate-800 font-medium' : 'text-slate-500'">
              {{ formRole.searchLabel || 'Rechercher un personnel…' }}
            </span>
          </button>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
          <label v-for="role in allRole" :key="role.id"
            class="flex items-center gap-2.5 p-2.5 rounded-xl border cursor-pointer transition-all"
            :class="formRole.role.includes(role.id)
              ? 'border-violet-300 bg-violet-50 shadow-sm'
              : 'border-slate-200 hover:border-violet-200 hover:bg-violet-50/50'">
            <input type="checkbox" :value="role.id" v-model="formRole.role" class="sr-only " />
            <!-- custom toggle -->
            <span class="relative w-9 h-5 rounded-full transition-colors shrink-0"
              :class="formRole.role.includes(role.id) ? 'bg-violet-500' : 'bg-slate-200'">
              <span class="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all"
                :class="formRole.role.includes(role.id) ? 'left-[18px]' : 'left-0.5'"></span>
            </span>
            <span class="text-xs font-medium text-slate-600 leading-tight">{{ role.name }}</span>
          </label>
        </div>

        <div v-if="hasPermission('Ajouter role') || hasPermission('Modifier role')"
          class="flex justify-end mt-5 pt-4 border-t border-slate-100">
          <button type="submit"
            class="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-violet-600 hover:bg-violet-700 active:scale-95 text-white text-sm font-semibold shadow-sm shadow-violet-200 transition-all disabled:opacity-60 cursor-pointer"
            :disabled="roleLoad">
            <svg v-if="roleLoad" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
            </svg>
            <span>💾 Sauvegarder</span>
          </button>
        </div>
      </form>

      <!-- ── PERMISSIONS ── -->
      <div v-if="hasPermission('Voir permission')" class="border-t border-slate-800 pt-6">
        <h2 class="text-sm font-bold text-slate-400 mb-4 flex items-center gap-2">
          <span class="w-6 h-6 rounded-md bg-emerald-100 text-emerald-600 flex items-center justify-center text-xs">🛡</span>
          Gérer les permissions
        </h2>

        <form @submit.prevent="assignPermission">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">

            <!-- Select rôle -->
            <div class="flex flex-col gap-1">
              <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-400">Rôle cible</label>
              <div class="relative">
                <select v-model="formPermission.role" @change="getPermissionByRole"
                  class="w-full field-select">
                  <option value="" disabled>Choisir un rôle…</option>
                  <option v-for="role in allRole" :key="role.id" :value="role.id">{{ role.name }}</option>
                </select>
                <svg class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500"
                  fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
              </div>
            </div>

            <!-- Recherche personnel pour permission -->
            <div v-if="hasPermission('Modifier permission')" class="flex flex-col gap-1">
              <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Personnel / Professeur</label>
              <button type="button" @click="openModal('permission')"
                class="w-full flex items-center gap-2 border border-slate-200 rounded-lg px-3 py-2 text-sm bg-slate-50 text-slate-500 hover:border-sky-400 hover:bg-sky-50 transition text-left cursor-pointer">
                <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
                <span :class="formPermission.searchLabel ? 'text-slate-800 font-medium' : 'text-slate-500'">
                  {{ formPermission.searchLabel || 'Rechercher un personnel…' }}
                </span>
              </button>
            </div>
          </div>

          <!-- Toggles permissions -->
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            <label v-for="perm in allPermissions" :key="perm.id"
              class="flex items-center gap-2.5 p-2.5 rounded-xl border cursor-pointer transition-all"
              :class="formPermission.permission.includes(perm.id)
                ? 'border-emerald-300 bg-emerald-50 shadow-sm'
                : 'border-slate-200 hover:border-emerald-200 hover:bg-emerald-50/50'">
              <input type="checkbox" :value="perm.id" v-model="formPermission.permission" class="sr-only" />
              <span class="relative w-9 h-5 rounded-full transition-colors shrink-0"
                :class="formPermission.permission.includes(perm.id) ? 'bg-emerald-500' : 'bg-slate-200'">
                <span class="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all"
                  :class="formPermission.permission.includes(perm.id) ? 'left-[18px]' : 'left-0.5'"></span>
              </span>
              <span class="text-xs font-medium text-slate-600 leading-tight">{{ perm.name }}</span>
            </label>
          </div>

          <div v-if="hasPermission('Modifier permission')"
            class="flex justify-end mt-5 pt-4 border-t border-slate-100">
            <button type="submit"
              class="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white text-sm font-semibold shadow-sm shadow-emerald-200 transition-all disabled:opacity-60 cursor-pointer"
              :disabled="permLoad">
              <svg v-if="permLoad" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
              </svg>
              <span>✅ Sauvegarder permissions</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ══════════ MON PROFIL UTILISATEUR ══════════ -->
    <div class="flex items-center gap-3 mb-4">
      <div class="w-9 h-9 rounded-lg bg-amber-100 flex items-center justify-center text-amber-600 text-lg shrink-0">🧑</div>
      <div>
        <h1 class="text-lg font-bold text-slate-300 leading-tight">Mon profil</h1>
        <p class="text-xs text-slate-400">Vos informations personnelles</p>
      </div>
    </div>

    <div class="bg-[#161b22] rounded-2xl border border-slate-800 shadow-sm p-6 mb-6">
      <form @submit.prevent="updateUserProfile">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Prénom</label>
            <input v-model="userForm.prenom" type="text" placeholder="Votre prénom"
              class="field-input" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Nom</label>
            <input v-model="userForm.nom" type="text" placeholder="Votre nom"
              class="field-input" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Email</label>
            <input v-model="userForm.email" type="email" placeholder="vous@ecole.fr"
              class="field-input" />
          </div>

           <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Nom d'utilisateur</label>
            <input v-model="userForm.username" type="email" placeholder="Thom"
              class="field-input" />
          </div>
        </div>
        <div class="flex justify-end mt-5 pt-4 border-t border-slate-100">
          <button type="submit"
            class="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-sky-600 hover:bg-sky-700 active:scale-95 text-white text-sm font-semibold shadow-sm shadow-sky-200 transition-all cursor-pointer">
            ✏️ Mettre à jour
          </button>
        </div>
      </form>
    </div>

    <!-- ── MOT DE PASSE ── -->
    <div class="bg-[#161b22] rounded-2xl border border-slate-200 shadow-sm p-6 mb-8">
      <h2 class="text-sm font-bold text-slate-400 mb-5 flex items-center gap-2">
        <span class="w-6 h-6 rounded-md  text-slate-400 flex items-center justify-center text-xs">🔑</span>
        Changer le mot de passe
      </h2>
      <form @submit.prevent="updatePassword">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Mot de passe actuel</label>
            <input v-model="passwordForm.current" type="password" placeholder="••••••••"
              class="field-input" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Nouveau mot de passe</label>
            <input v-model="passwordForm.newPw" type="password" placeholder="••••••••"
              class="field-input" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Confirmer</label>
            <input v-model="passwordForm.confirm" type="password" placeholder="••••••••"
              class="field-input"
              :class="pwMismatch
                ? 'border-red-300 focus:border-red-400 focus:ring-2 focus:ring-red-100 text-red-700'
                : 'border-slate-200 focus:border-sky-500 focus:ring-2 focus:ring-sky-100 text-slate-800'" />
            <span v-if="pwMismatch" class="text-xs text-red-500">⚠ Les mots de passe ne correspondent pas.</span>
          </div>
        </div>
        <div class="flex justify-end mt-5 pt-4 border-t border-slate-100"> 
          <button type="submit"
            class="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-slate-800 hover:bg-slate-900 active:scale-95 text-white text-sm font-semibold shadow-sm transition-all cursor-pointer" :disabled="passwordForm.processing">
            <svg v-if="passwordForm.processing" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg> 
            <span>{{ passwordForm.processing ? 'Changement...' : '🔒 Changer le mot de passe' }}</span>
            
          </button>
        </div>
      </form>
    </div>

    <!-- ══════════ MODAL RECHERCHE ══════════ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0">
        <div v-if="showModal"
          class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          @click.self="closeModal">
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 scale-95 translate-y-2"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95">
            <div v-if="showModal" class="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">

              <!-- header -->
              <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100">
                <h3 class="text-sm font-bold text-slate-800">
                  {{ activeModal === 'role' ? '👤 Assigner un rôle' : '🛡 Assigner une permission' }}
                </h3>
                <button @click="closeModal"
                  class="w-7 h-7 rounded-full bg-slate-100 hover:bg-red-50 hover:text-red-500 text-slate-500 flex items-center justify-center text-sm transition-colors">
                  ✕
                </button>
              </div>

              <!-- body -->
              <div class="p-5">
                <div class="relative">
                  <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
                  <input ref="modalInput" v-model="modalSearch" @input="onModalSearch" type="text"
                    placeholder="Tapez un nom pour rechercher…"
                    class="w-full border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-sm text-slate-800 bg-slate-50 focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100 transition" />
                </div>

                <!-- résultats -->
                <div v-if="modalResults.length" class="mt-3 border border-slate-200 rounded-xl overflow-hidden divide-y divide-slate-100">
                  <div v-for="person in modalResults" :key="person.id"
                    class="flex items-center justify-between px-4 py-2.5 cursor-pointer hover:bg-sky-50 transition-colors"
                    @click="selectPerson(person)">
                    <span class="font-semibold text-sm text-sky-600">{{ person.nom }}</span>
                    <span class="text-sm text-slate-500">{{ person.prenom }}</span>
                  </div>
                </div>
                <div v-else-if="modalSearch" class="mt-3 text-center text-sm text-slate-500 py-6">
                  Aucun résultat pour « {{ modalSearch }} »
                </div>
                <div v-else class="mt-3 text-center text-sm text-slate-500 py-6">
                  Tapez au moins 2 caractères pour rechercher.
                </div>
              </div>

            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <!-- ══════════ TOAST ══════════ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0 translate-y-4">
        <div v-if="toast.show"
          class="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-lg text-sm font-medium text-white"
          :class="toast.ok ? 'bg-emerald-600' : 'bg-red-600'">
          <span>{{ toast.ok ? '✅' : '❌' }}</span>
          <span>{{ toast.msg }}</span>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>
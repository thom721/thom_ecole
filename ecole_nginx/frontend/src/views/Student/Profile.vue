<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const url = import.meta.env.VITE_APP_BASE_URL ?? ''

/* ══════════════════════════════════════════════════════════════════
   ÉTAT
══════════════════════════════════════════════════════════════════ */
const editMode = ref(false)
const saving = ref(false)
const uploadingAvatar = ref(false)

const toast = ref({ show: false, msg: '', type: 'success' })
const notify = (msg, type = 'success') => {
  toast.value = { show: true, msg, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}
const originalData = ref({})

/* ── Avatar preview ── */
const avatarPreview = ref(null)
const avatarFile = ref(null)

/* ── Données étudiant ── */
const student = ref({
  id: '',
  identifiant: '',
  nom: '',
  prenom: '',
  date_de_naissance: '',
  lieu_de_naissance: '',
  username:'',
  sexe: '',
  adresse: '',
  telephone: '',
  email: '',
  photo_url: null,
  classe: '',
  niveau: '',
  annee_admission: '',
  nom_responsable: '',
  telephone_responsable: '',
  prenom_responsable:'',
  email_responsable: '',
  adresse_responsable:'',
  statut: 'actif',
})
 

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    avatarPreview.value = ev.target.result
    student.value.photo_url = ev.target.result
  }
  reader.readAsDataURL(file)
}


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
    notify(error.response?.data?.message, false)
  } finally {
    passwordForm.value.processing = false
  }
}


const initials = computed(() => {
  if (!student.value.prenom || !student.value.nom) return '?'
  return `${student.value.prenom.charAt(0)}${student.value.nom.charAt(0)}`.toUpperCase()
})

/* ── Validation ── */
const errors = ref({})
const validate = () => {
  errors.value = {}
  
  if (!student.value.nom?.trim()) errors.value.nom = 'Le nom est requis'
  if (!student.value.prenom?.trim()) errors.value.prenom = 'Le prénom est requis'
  
  if (student.value.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(student.value.email)) {
    errors.value.email = 'Email invalide'
  }
  
  if (student.value.telephone && !/^[\d\s\-\+\(\)]+$/.test(student.value.telephone)) {
    errors.value.telephone = 'Numéro de téléphone invalide'
  }
  
  return Object.keys(errors.value).length === 0
}

/* ══════════════════════════════════════════════════════════════════
   API
══════════════════════════════════════════════════════════════════ */
const loadProfile = async () => {
  try {
    const { data } = await axios.get(`${url}/etudiant/${authStore.user?.user?.userable_id}`
  )
    console.log(data);
    const dernierClasseEtudiant = data?.data?.classes_etudiant?.at(-1); 
    student.value = {
      ...data?.data,
      lieu_de_naissance: data?.data?.lieu_de_naissance,
      date_de_naissance: data?.data.date_de_naissance?.split(' ')[0] || '',
      classe:dernierClasseEtudiant?.classes?.nom_classe,
      niveau:dernierClasseEtudiant?.niveaux?.name,
      annee_admission:data?.data.created_at?.split('T')[0] || '',

      username:data?.data?.user?.username || '',
      nom_responsable: data?.data?.responsable?.nom_responsable,
      telephone_responsable: data?.data?.responsable?.telephone_responsable,
      prenom_responsable:data?.data?.responsable?.prenom_responsable,
      email_responsable: data?.data?.responsable?.email_responsable,
      adresse_responsable:data?.data?.responsable?.adresse_responsable,
      

    }
    originalData.value = { ...student.value }
    
    if (data?.data?.user) avatarPreview.value = data?.data?.user?.profile_image_url
    
  } catch (error) {
    console.error('Erreur chargement profil:', error.response?.data || error.message)
    notify('Erreur lors du chargement du profil', 'error')
  }
}

const saveProfile = async () => {
  if (!validate()) {
    notify('Veuillez corriger les erreurs', 'error')
    return
  }
  
  saving.value = true
  
  try {
    let payload = { ...student.value }
    await axios.put(`${url}/student/profile`, payload)
    
    notify('✅ Profil mis à jour avec succès !')
    editMode.value = false
    originalData.value = { ...student.value }
    avatarFile.value = null
    
    await loadProfile()
    
  } catch (error) {
    console.error('Erreur sauvegarde:', error.response?.data || error.message)
    notify(error.response?.data?.detail || 'Erreur lors de la sauvegarde', 'error')
  } finally {
    saving.value = false
  }
}

const cancelEdit = () => {
  student.value = { ...originalData.value }
  avatarPreview.value = originalData.value.photo_url
  avatarFile.value = null
  errors.value = {}
  editMode.value = false
}

/* ── Upload avatar ── */
const handleAvatarChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  // Validation
  if (!file.type.startsWith('image/')) {
    notify('Veuillez sélectionner une image', 'error')
    return
  }
  
  if (file.size > 5 * 1024 * 1024) {
    notify('Image trop volumineuse (max 5 Mo)', 'error')
    return
  }
  
  avatarFile.value = file
  
  const reader = new FileReader()
  reader.onload = (ev) => { 
    student.value.photo_url = ev.target.result
    avatarPreview.value = ev.target.result 
  }
  reader.readAsDataURL(file)
}

const triggerAvatarUpload = () => {
  document.getElementById('avatar-input').click()
}

/* ── Sections ── */
const sections = [
  { id: 'info', label: 'Informations personnelles', icon: '👤' },
  { id: 'contact', label: 'Contact', icon: '📞' },
  { id: 'scolarite', label: 'Scolarité', icon: '🎓' },
  { id: 'tuteur', label: 'Tuteur légal', icon: '👨‍👩‍👦' },
]

const activeSection = ref('info')

/* ── Init ── */
onMounted(() => {
  loadProfile()
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-sky-50 to-emerald-50 pb-12 -mt-8 animate-[fadeUp_0.4s_ease_both]">
    
    <!-- ══════════════════════ HERO ══════════════════════ -->
    <div class="relative bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 overflow-hidden">
      <!-- Pattern décoratif -->
      <div class="absolute inset-0 opacity-10">
        <svg width="100%" height="100%">
          <defs>
            <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1.5" fill="white"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dots)"/>
        </svg>
      </div>
      
      <div class="relative max-w-5xl mx-auto px-4 sm:px-6 py-10">
        <div class="flex flex-col sm:flex-row items-center gap-6">
          
          <!-- Avatar -->
          <div class="relative group">
            <div class="w-24 h-24 rounded-full overflow-hidden ring-4 ring-white/30 shadow-2xl transition-all duration-300 group-hover:ring-white/50">
              <img v-if="avatarPreview" :src="avatarPreview" alt="Avatar" class="w-full h-full object-contain" />
              <div v-else class="w-full h-full bg-white/20 backdrop-blur flex items-center justify-center text-5xl font-bold text-white">
                {{ initials }}
              </div>
            </div>
            
            <!-- Bouton upload (mode édition) -->
            <button v-if="editMode" @click="triggerAvatarUpload"
              class="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
              <div class="text-center text-white">
                <svg class="w-8 h-8 mx-auto mb-1" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
                </svg>
                <span class="text-xs font-semibold">Changer</span>
              </div>
            </button>
            
            <input id="avatar-input" type="file" accept="image/*" @change="handleAvatarChange" class="hidden" />
            
            <!-- Badge statut -->
            <span class="absolute -bottom-2 -right-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-lg"
              :class="student.statut === 'actif' ? 'bg-emerald-400 text-emerald-900' : 'bg-slate-400 text-slate-900'">
              Actif
            </span>
          </div>
          
          <!-- Infos -->
          <div class="flex-1 text-center sm:text-left">
            <h1 class="text-3xl sm:text-4xl font-bold text-white leading-tight mb-2">
              {{ student.prenom }} <span class="text-emerald-200">{{ student.nom }}</span>
            </h1>
            <div class="flex flex-wrap items-center justify-center sm:justify-start gap-2 mb-3">
              <span class="inline-flex items-center gap-1.5 bg-white/10 backdrop-blur text-white text-xs px-3 py-1.5 rounded-full font-medium">
                🪪 {{ student.identifiant || '—' }}
              </span>
              <span class="inline-flex items-center gap-1.5 bg-white/10 backdrop-blur text-white text-xs px-3 py-1.5 rounded-full font-medium">
                🏫 {{ student.classe || '—' }}
              </span>
              <span class="inline-flex items-center gap-1.5 bg-white/10 backdrop-blur text-white text-xs px-3 py-1.5 rounded-full font-medium">
                📚 {{ student.niveau || '—' }}
              </span>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center justify-center sm:justify-start gap-3 mt-4">
              <button v-if="!editMode" @click="editMode = true"
                class="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-emerald-600 rounded-xl font-semibold text-sm shadow-lg hover:shadow-xl hover:scale-105 active:scale-100 transition-all">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"/>
                </svg>
                Modifier mon profil
              </button>
              
              <template v-else>
                <button @click="saveProfile" :disabled="saving"
                  class="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-emerald-600 rounded-xl font-semibold text-sm shadow-lg hover:shadow-xl hover:scale-105 active:scale-100 transition-all disabled:opacity-60 disabled:cursor-not-allowed">
                  <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"/>
                  </svg>
                  <span v-else>💾</span>
                  {{ saving ? 'Sauvegarde...' : 'Enregistrer' }}
                </button>
                
                <button @click="cancelEdit" :disabled="saving"
                  class="inline-flex items-center gap-2 px-5 py-2.5 bg-white/10 backdrop-blur text-white border-2 border-white/30 rounded-xl font-semibold text-sm hover:bg-white/20 transition-all disabled:opacity-60">
                  ✕ Annuler
                </button>
              </template>
            </div>
          </div>
          
        </div>
      </div>
    </div>
    
    <!-- ══════════════════════ NAVIGATION SECTIONS ══════════════════════ -->
    <div class="max-w-5xl mx-auto px-4 sm:px-6 -mt-6">
      <div class="bg-white rounded-2xl shadow-md border border-slate-100 p-4 flex gap-2 overflow-x-auto scrollbar-hide flex items-center justify-between px-2 md:px-8">
        <button v-for="sec in sections" :key="sec.id" @click="activeSection = sec.id"
          class="flex items-center justify-between gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all"
          :class="activeSection === sec.id
            ? 'bg-emerald-100 text-emerald-700 shadow-sm'
            : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'">
          <span>{{ sec.icon }}</span>
          <span>{{ sec.label }}</span>
        </button>
      </div>
    </div>
    
    <!-- ══════════════════════ CONTENU ══════════════════════ -->
    <div class="p-2 md:px-6 mt-6 w-full">
      
      <!-- ████ INFORMATIONS PERSONNELLES ████ -->
      <div v-show="activeSection === 'info'"
        class="bg-white rounded-2xl shadow-lg border border-slate-100 p-6 space-y-5">
        
        <div class="flex items-center gap-3 pb-4 border-b border-slate-100">
          <div class="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-xl">👤</div>
          <div>
            <h2 class="text-lg font-bold text-slate-800">Informations personnelles</h2>
            <p class="text-xs text-slate-400">Données d'identité</p>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          
          <!-- Prénom -->
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Prénom</label>
            <input v-model="student.prenom" :disabled="!editMode" type="text"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'" />
            <span v-if="errors.prenom" class="text-xs text-red-500">{{ errors.prenom }}</span>
          </div>
          
          <!-- Nom -->
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Nom</label>
            <input v-model="student.nom" :disabled="!editMode" type="text"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'" />
            <span v-if="errors.nom" class="text-xs text-red-500">{{ errors.nom }}</span>
          </div>
          
          <!-- Date de naissance -->
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Date de naissance</label>
            <input v-model="student.date_de_naissance" :disabled="!editMode" type="date"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'" />
          </div>
          
          <!-- Lieu de naissance -->
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Lieu de naissance</label>
            <input v-model="student.lieu_de_naissance" :disabled="!editMode" type="text"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'" />
          </div>
          
          <!-- Sexe -->
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Sexe</label>
            <select v-model="student.sexe" :disabled="!editMode"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all appearance-none bg-right"
              style="background-image: url('data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%2712%27 height=%2712%27 viewBox=%270 0 12 12%27%3E%3Cpath fill=%27%23999%27 d=%27M6 8L1 3h10z%27/%3E%3C/svg%3E'); background-repeat: no-repeat; background-position: right 1rem center;"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'">
              <option value="">— Sélectionner —</option>
              <option value="M">Masculin</option>
              <option value="F">Féminin</option>
            </select>
          </div>

                    <!-- Nom d'utilisateur -->
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Nom d'utilisateur</label>
            <input v-model="student.username" :disabled="!editMode" type="text"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'" />
          </div>
          
          <!-- Adresse -->
          <div class="space-y-1.5 md:col-span-2">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Adresse complète</label>
            <textarea v-model="student.adresse" :disabled="!editMode" rows="2"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all resize-none"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'"></textarea>
          </div>
          
        </div>
      </div>
      
      <!-- ████ CONTACT ████ -->
      <div v-show="activeSection === 'contact'"
        class="bg-white rounded-2xl shadow-lg border border-slate-100 p-6 space-y-5">
        
        <div class="flex items-center gap-3 pb-4 border-b border-slate-100">
          <div class="w-10 h-10 rounded-xl bg-sky-100 flex items-center justify-center text-xl">📞</div>
          <div>
            <h2 class="text-lg font-bold text-slate-800">Contact</h2>
            <p class="text-xs text-slate-400">Coordonnées de contact</p>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          
          <!-- Téléphone -->
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Téléphone</label>
            <input v-model="student.telephone" :disabled="!editMode" type="tel"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'"
              placeholder="+509 3700 0000" />
            <span v-if="errors.telephone" class="text-xs text-red-500">{{ errors.telephone }}</span>
          </div>
          
          <!-- Email -->
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Email</label>
            <input v-model="student.email" :disabled="!editMode" type="email"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'"
              placeholder="prenom.nom@exemple.com" />
            <span v-if="errors.email" class="text-xs text-red-500">{{ errors.email }}</span>
          </div>
          
        </div>
      </div>
      
      <!-- ████ SCOLARITÉ ████ -->
      <div v-show="activeSection === 'scolarite'"
        class="bg-white rounded-2xl shadow-lg border border-slate-100 p-6 space-y-5">
        
        <div class="flex items-center gap-3 pb-4 border-b border-slate-100">
          <div class="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center text-xl">🎓</div>
          <div>
            <h2 class="text-lg font-bold text-slate-800">Scolarité</h2>
            <p class="text-xs text-slate-400">Informations académiques</p>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Classe</label>
            <input v-model="student.classe" disabled type="text"
              class="w-full px-4 py-2.5 border-2 border-slate-100 bg-slate-50 rounded-xl text-sm font-medium text-slate-600 cursor-not-allowed" />
          </div>
          
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Niveau</label>
            <input v-model="student.niveau" disabled type="text"
              class="w-full px-4 py-2.5 border-2 border-slate-100 bg-slate-50 rounded-xl text-sm font-medium text-slate-600 cursor-not-allowed" />
          </div>
          
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Année d'admission</label>
            <input v-model="student.annee_admission" disabled type="text"
              class="w-full px-4 py-2.5 border-2 border-slate-100 bg-slate-50 rounded-xl text-sm font-medium text-slate-600 cursor-not-allowed" />
          </div>
          
        </div>
        
        <div class="bg-sky-50 border border-sky-100 rounded-xl p-4 flex items-start gap-3">
          <span class="text-2xl shrink-0">ℹ️</span>
          <div class="text-xs text-sky-700 leading-relaxed">
            <strong>Note :</strong> Les informations de scolarité (classe, niveau, année d'admission) ne peuvent être modifiées que par l'administration de l'école. Contactez le secrétariat si ces informations sont incorrectes.
          </div>
        </div>
      </div>
      
      <!-- ████ TUTEUR LÉGAL ████ -->
      <div v-show="activeSection === 'tuteur'"
        class="bg-white rounded-2xl shadow-lg border border-slate-100 p-6 space-y-5">
        
        <div class="flex items-center gap-3 pb-4 border-b border-slate-100">
          <div class="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center text-xl">👨‍👩‍👦</div>
          <div>
            <h2 class="text-lg font-bold text-slate-800">Tuteur légal</h2>
            <p class="text-xs text-slate-400">Coordonnées du tuteur</p>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Nom du tuteur</label>
            <input v-model="student.nom_responsable" :disabled="!editMode" type="text"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'" />
          </div>

            <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Prénom du tuteur</label>
            <input v-model="student.prenom_responsable" :disabled="!editMode" type="text"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'" />
          </div>
          
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Téléphone du tuteur</label>
            <input v-model="student.telephone_responsable" :disabled="!editMode" type="tel"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'" />
          </div>
          
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Email du tuteur</label>
            <input v-model="student.email_responsable" :disabled="!editMode" type="email"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'" />
          </div>

                    <div class="space-y-1.5  md:col-span-2">
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Adresse du tuteur</label>
            <input v-model="student.adresse_responsable" :disabled="!editMode" type="email"
              class="w-full px-4 py-2.5 border-2 rounded-xl text-sm font-medium transition-all"
              :class="editMode
                ? 'border-slate-200 bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 outline-none'
                : 'border-slate-100 bg-slate-50 text-slate-600 cursor-not-allowed'" />
          </div>
          
        </div>
      </div>
      
    </div>


        <!-- ── MOT DE PASSE ── -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-2 md:p-6 my-8">
      <h2 class="text-sm font-bold text-slate-700 mb-5 flex items-center gap-2">
        <span class="w-6 h-6 rounded-md bg-slate-100 text-slate-500 flex items-center justify-center text-xs">🔑</span>
        Changer le mot de passe
      </h2>
      <form @submit.prevent="updatePassword">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Mot de passe actuel</label>
            <input v-model="passwordForm.current" type="password" placeholder="••••••••"
              class="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 bg-slate-50 focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100 transition" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Nouveau mot de passe</label>
            <input v-model="passwordForm.newPw" type="password" placeholder="••••••••"
              class="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 bg-slate-50 focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100 transition" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Confirmer</label>
            <input v-model="passwordForm.confirm" type="password" placeholder="••••••••"
              class="border border-slate-200 rounded-lg px-3 py-2 text-sm bg-slate-50 focus:outline-none transition"
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
    
    <!-- ══════════════════════ TOAST ══════════════════════ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0 translate-y-4">
        <div v-if="toast.show"
          class="fixed top-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-2xl text-sm font-medium text-white max-w-sm"
          :class="toast.type === 'success' ? 'bg-emerald-600' : 'bg-red-600'">
          <span class="text-xl">{{ toast.type === 'success' ? '✅' : '❌' }}</span>
          <span>{{ toast.msg }}</span>
        </div>
      </Transition>
    </Teleport>
    
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
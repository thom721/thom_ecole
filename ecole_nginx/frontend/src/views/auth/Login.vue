<template>
  <div class="min-h-screen bg-[#0d0d14] flex overflow-hidden">

    <!-- LEFT PANEL — Illustration -->
    <div class="hidden lg:flex flex-col justify-between w-[52%] relative overflow-hidden p-12"
      :style="{ background: activeRole.bg }">

      <!-- Noise texture overlay -->
      <div class="absolute inset-0 opacity-[0.03]"
        style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 256 256%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.9%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');">
        <!-- <img v-if="useSchoolInfo.school_info?.logo_image_base64" :src="useSchoolInfo.school_info?.logo_image_base64" class="object h-full w-full"> -->
      
      </div>

      <!-- Glow orbs -->
      <div class="absolute top-1/4 left-1/4 w-80 h-80 rounded-full blur-3xl opacity-20"
        :style="{ background: activeRole.orb1 }"></div>
      <div class="absolute bottom-1/4 right-1/4 w-64 h-64 rounded-full blur-3xl opacity-15"
        :style="{ background: activeRole.orb2 }"></div>

      <!-- Logo -->
      <div class="relative z-10">
        <div class="flex items-center gap-3">
          <div class="w-20 h-20 rounded-full flex items-center justify-center text-xl"
            :style="{ background: 'rgba(255,255,255,0.15)' }">
            <img v-if="useSchoolInfo.school_info?.logo_image_base64" :src="useSchoolInfo.school_info?.logo_image_base64" class="object-contain flex items-center justify-center w-20 h-20">
          </div>
          <span class="font-serif text-white text-xl font-bold tracking-wide">{{useSchoolInfo.school_info?.nom || 'Aplekol 360'}}</span>
        </div>
      </div>
<!-- {{ useSchoolInfo.school_info }} -->
      <!-- Center content -->
      <div class="relative z-10">
        <!-- <div class="text-7xl mb-8 transition-all duration-500">{{ activeRole.emoji }}</div> -->
        <h2 class="font-serif text-4xl font-bold text-white leading-tight mb-4">
          {{ activeRole.title }}
        </h2>
        <p class="text-white/60 text-lg leading-relaxed max-w-sm">
          {{ activeRole.subtitle }}
        </p>

        <!-- Features -->
        <div class="mt-10 space-y-3">
          <div v-for="feat in activeRole.features" :key="feat"
            class="flex items-center gap-3 text-white/70 text-sm">
            <div class="w-5 h-5 rounded-full flex items-center justify-center shrink-0"
              :style="{ background: 'rgba(255,255,255,0.15)' }">
              <span class="text-xs">✓</span>
            </div>
            {{ feat }}
          </div>
        </div>
      </div>

      <!-- Bottom quote -->
      <div class="relative z-10">
        <div class="h-px bg-white/10 mb-6"></div>
        <p class="font-serif text-white/40 text-sm italic">"{{ activeRole.quote }}"</p>
      </div>
    </div>

    <!-- RIGHT PANEL — Form -->
    <div class="flex-1 flex flex-col justify-center px-8 sm:px-12 lg:px-16 bg-[#0d0d14] relative">

      <!-- Top mobile logo -->
      <div class="lg:hidden flex items-center gap-2 mb-10">
        <span class="text-2xl">🎓</span>
        <span class="font-serif text-[#c9a84c] text-xl font-bold">{{useSchoolInfo.school_info?.nom || 'Aplekol 360'}}</span>
      </div>

      <div class="max-w-sm w-full mx-auto">
        <p class="text-center text-xs text-gray-400 mt-8">
          <router-link to="/" class="text-gold no-underline hover:underline font-semibold">
            ← Retour à l'accueil
          </router-link>
        </p>
        <!-- Role selector -->
        <div class="mb-8">
          <p class="text-[#555] text-xs font-semibold tracking-widest uppercase mb-3">Je suis...</p>
          <div class="flex gap-2">
            <!-- <button v-for="role in roles" :key="role.key"
              @click="selectedRole = role.key"
              :class="selectedRole === role.key
                ? 'border-[#c9a84c] text-white bg-white/5'
                : 'border-[#222] text-[#555] hover:border-[#333] hover:text-[#888]'"
              class="flex-1 flex flex-col items-center gap-1.5 py-3 px-2 rounded-xl border transition-all cursor-pointer">
              <span class="text-xl">{{ role.emoji }}</span>
              <span class="text-xs font-semibold">{{ role.label }}</span>
            </button> -->
            <button
              v-for="role in roles"
              :key="role.key"
              type="button"
              @click="selectedRole = role.key; form.login_as = role.key"
              :class="selectedRole === role.key
                ? 'border-[#c9a84c] text-white bg-white/5'
                : 'border-[#222] text-[#555] hover:border-[#333] hover:text-[#888]'"
              class="flex-1 flex flex-col items-center gap-1.5 py-3 px-2 rounded-xl border transition-all cursor-pointer">
              <span class="text-xl">{{ role.emoji }}</span>
              <span class="text-xs font-semibold">{{ role.label }}</span>
            </button>
          </div>
        </div>

        <!-- Header -->
        <div class="mb-8">
          <h1 class="font-serif text-3xl font-bold text-white mb-2">Connexion</h1>
          <p class="text-[#555] text-sm">{{ activeRole.formSubtitle }}</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="submit" class="" :class="['space-y-3' ? globalError : 'space-y-5']">

          <!-- Email -->
          <div>
            <label class="block text-xs font-semibold text-[#888] mb-2 tracking-wide uppercase">
              {{ selectedRole === 'etudiant' ? 'Identifiant / Email' : 'Email' }}
            </label>
            <div class="relative">
              <span class="absolute left-4 top-1/2 -translate-y-1/2 text-[#444]">
                {{ selectedRole === 'etudiant' ? '👤' : '✉️' }}
              </span>
              <input
                v-model="form.email"
                type="text"
                :placeholder="activeRole.emailPlaceholder"
                class="w-full bg-[#111] border border-[#222] rounded-xl pl-11 pr-4 py-3.5 text-white text-sm placeholder-[#333] outline-none transition-all focus:border-[#c9a84c] focus:ring-1 focus:ring-[#c9a84c]/30"
                autocomplete="username"
              />
            </div>
            <p v-if="form.errors.email" class="text-[#e74c3c] text-xs mt-1.5">{{ form.errors.email }}</p>
          </div>

          <!-- Password -->
          <div>
            <div class="flex justify-between items-center mb-2">
              <label class="text-xs font-semibold text-[#888] tracking-wide uppercase">Mot de passe</label>
              <router-link to="/forgot-password" class="text-xs text-[#c9a84c] hover:underline">
                Oublié ?
              </router-link>
            </div>
            <div class="relative">
              <span class="absolute left-4 top-1/2 -translate-y-1/2 text-[#444]">🔒</span>
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                class="w-full bg-[#111] border border-[#222] rounded-xl pl-11 pr-12 py-3.5 text-white text-sm placeholder-[#333] outline-none transition-all focus:border-[#c9a84c] focus:ring-1 focus:ring-[#c9a84c]/30"
                autocomplete="current-password"
              />
              <button type="button" @click="showPassword = !showPassword"
                class="absolute right-4 top-1/2 -translate-y-1/2 text-[#444] hover:text-[#888] transition-colors cursor-pointer text-sm">
                {{ showPassword ? '🙈' : '👁' }}
              </button>
            </div>
            <p v-if="form.errors.password" class="text-[#e74c3c] text-xs mt-1.5">{{ form.errors.password }}</p>
          </div>

          <!-- Remember -->
          <div class="flex items-center justify-between pt-1">
            <label class="flex items-center gap-2.5 cursor-pointer group">
              <div class="relative">
                <input type="checkbox" v-model="form.remember" class="sr-only"/>
                <div :class="form.remember ? 'bg-[#c9a84c] border-[#c9a84c]' : 'bg-transparent border-[#333]'"
                  class="w-5 h-5 rounded-md border-2 transition-all flex items-center justify-center">
                  <span v-if="form.remember" class="text-[#0d0d14] text-xs font-bold">✓</span>
                </div>
              </div>
              <span class="text-sm text-[#555] group-hover:text-[#888] transition-colors">Se souvenir de moi</span>
            </label>
          </div>

          <!-- Submit -->
          <button type="submit"
            :disabled="form.processing"
            class="w-full py-3.5 rounded-xl font-semibold text-sm transition-all cursor-pointer mt-2 relative overflow-hidden"
            :style="{ background: form.processing ? '#555' : activeRole.btnColor, color: '#0d0d14' }">
            <span v-if="!form.processing" class="flex items-center justify-center gap-2">
              {{ activeRole.btnLabel }}
              <span>→</span>
            </span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Connexion en cours...
            </span>
          </button>

        </form>

        <!-- Error global -->
        <div v-if="globalError"
          class="mt-4 p-3.5 rounded-xl bg-[#e74c3c]/10 border border-[#e74c3c]/20 text-[#e74c3c] text-sm flex items-center gap-2">
          <span>⚠️</span> {{ globalError }}
        </div>

        <!-- Footer -->
        <p class="text-center text-[#333] text-xs mt-10">
          © {{ new Date().getFullYear() }} Lekol 360 · Tous droits réservés
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Swal from 'sweetalert2'

const router    = useRouter()
const authStore = useAuthStore()

import { storeToRefs } from 'pinia'; 
import { useSchoolStore,useSchoolStoreInfo } from '../../stores/schoolStore';  
const useSchoolInfo = useSchoolStoreInfo()

 
const selectedRole = ref('etudiant')

const roles = [
  { key: 'etudiant',   label: 'Étudiant',   emoji: '🎒' },
  { key: 'professeur', label: 'Professeur',  emoji: '👨‍🏫' },
  { key: 'personnel',  label: 'Personnel',   emoji: '🏫' },
]

const roleConfig = {
  etudiant: {
    bg:             'linear-gradient(135deg, #1a3a6b 0%, #0d0d14 100%)',
    orb1:           '#3b82f6',
    orb2:           '#c9a84c',
    emoji:          '🎒',
    title:          'Bienvenue dans votre espace étudiant',
    subtitle:       'Accédez à vos cours, notes, paiements et bien plus encore.',
    formSubtitle:   'Accédez à votre espace personnel',
    emailPlaceholder: 'Votre identifiant ou email',
    btnColor:       '#c9a84c',
    btnLabel:       'Se connecter',
    quote:          'Le savoir est la seule richesse qu\'on ne peut voler.',
    features: [
      'Consulter vos notes et bulletins',
      'Suivre vos paiements',
      'Voir votre emploi du temps',
      'Accéder à vos ressources',
    ],
    login_as:'App\\Models\\Etudiant'
  },
  professeur: {
    bg:             'linear-gradient(135deg, #1a4a2e 0%, #0d0d14 100%)',
    orb1:           '#10b981',
    orb2:           '#c9a84c',
    emoji:          '👨‍🏫',
    title:          'Espace enseignant',
    subtitle:       'Gérez vos classes, saisissez les notes et suivez la progression de vos élèves.',
    formSubtitle:   'Accédez à votre espace enseignant',
    emailPlaceholder: 'Votre adresse email',
    btnColor:       '#10b981',
    btnLabel:       'Accéder à l\'espace prof',
    quote:          'Enseigner, c\'est apprendre deux fois.',
    login_as:'App\\Models\\Professeur',
    features: [
      'Saisir et gérer les notes',
      'Suivre les présences',
      'Gérer votre programme',
      'Communiquer avec les parents',
    ]
  },
  personnel: {
    bg:             'linear-gradient(135deg, #4a1a3a 0%, #0d0d14 100%)',
    orb1:           '#ec4899',
    orb2:           '#c9a84c',
    emoji:          '🏫',
    title:          'Espace administration',
    subtitle:       'Gérez les inscriptions, paiements et la vie scolaire de l\'établissement.',
    formSubtitle:   'Accédez au panneau d\'administration',
    emailPlaceholder: 'Votre adresse email',
    btnColor:       '#ec4899',
    btnLabel:       'Accéder à l\'administration',
    quote:          'L\'organisation est la clé du succès collectif.',
    login_as:'App\\Models\\Personnel',
    features: [
      'Gérer les inscriptions',
      'Suivre les paiements',
      'Administrer les utilisateurs',
      'Générer les rapports',
    ]
  }
}

const activeRole = computed(() => roleConfig[selectedRole.value])

/* ── FORM ── */
const showPassword = ref(false)
const globalError  = ref('')

const form = reactive({
  email:      '',
  password:   '',
  login_as:'',
  remember:   false,
  processing: false,
  errors:     {}
})

const submit = async () => {
  form.processing = true
  form.errors     = {}
  globalError.value = ''
  

  try {
    const response = await authStore.login({
      email:    form.email,
      password: form.password,
      login_as: activeRole.value?.login_as
    })

    const user = response.user
    console.log(user);
    
    if (user.password_changed_at == '') {
      router.push('/reset-password?first=1')
    }else{
    if (user.userable_type === 'App\\Models\\Professeur') {
      router.push({ name: 'teacher.dashboard' })
    } else if (user.userable_type === 'App\\Models\\Etudiant') {
      router.push({ name: 'etudiant.dashboard' })
    } else {
      router.push({ name: 'Dashboard' })
    }
    }

  } catch (err) {
    console.error('Erreur login:', err.response)
    const status = err.response?.status
    if (status === 401 || status === 422) {
      globalError.value = err.response?.data?.detail ?? 'Email ou mot de passe incorrect.'
    } else {
      globalError.value = 'Impossible de joindre le serveur. Réessayez.'
    }
  } finally {
    form.processing = false
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');
.font-serif { font-family: 'Playfair Display', serif; }
* { font-family: 'DM Sans', sans-serif; }

.fade-up-enter-active, .fade-up-leave-active { transition: all 0.3s ease; }
.fade-up-enter-from { opacity: 0; transform: translateY(12px); }
.fade-up-leave-to   { opacity: 0; transform: translateY(-12px); }
</style>
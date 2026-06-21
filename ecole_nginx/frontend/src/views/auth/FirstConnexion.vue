<template>
  <div class="min-h-screen bg-[#0d0d14] flex overflow-hidden  animate-[fadeUp_0.4s_ease_both]">

    <!-- LEFT PANEL -->
    <div class="hidden lg:flex flex-col justify-between w-[52%] relative overflow-hidden p-12"
      :style="{ background: currentStep === 'email' ? 'linear-gradient(135deg, #1a3a6b 0%, #0d0d14 100%)' : 'linear-gradient(135deg, #1a4a2e 0%, #0d0d14 100%)' }">

      <!-- Glow orbs -->
      <div class="absolute top-1/4 left-1/4 w-80 h-80 rounded-full blur-3xl opacity-20"
        :style="{ background: currentStep === 'email' ? '#3b82f6' : '#10b981' }"></div>
      <div class="absolute bottom-1/4 right-1/4 w-64 h-64 rounded-full blur-3xl opacity-15 bg-[#c9a84c]"></div>

      <!-- Logo -->
      <div class="relative z-10 flex items-center gap-3">
        <div class="w-20 h-20 rounded-full bg-white/10 flex items-center justify-center text-xl">
           <img v-if="useSchoolInfo.school_info?.logo_image_base64" :src="useSchoolInfo.school_info?.logo_image_base64" class="object-contain flex items-center justify-center w-12 h-12">
        </div>
        <span class="font-serif text-white text-xl font-bold tracking-wide">{{useSchoolInfo.school_info?.nom || 'Aplekol 360'}}</span>
      </div>

      <!-- Center -->
      <div class="relative z-10">
        <Transition name="fade-up" mode="out-in">
          <div :key="currentStep">
            <div class="text-7xl mb-8">{{ stepConfig[currentStep].emoji }}</div>
            <h2 class="font-serif text-4xl font-bold text-white leading-tight mb-4">
              {{ stepConfig[currentStep].leftTitle }}
            </h2>
            <p class="text-white/60 text-lg leading-relaxed max-w-sm">
              {{ stepConfig[currentStep].leftSubtitle }}
            </p>

            <!-- Steps indicator -->
            <div class="flex items-center gap-3 mt-10">
              <div v-for="(s, i) in steps" :key="s.key"
                class="flex items-center gap-3">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all"
                    :class="isStepDone(s.key)
                      ? 'bg-[#10b981] text-white'
                      : currentStep === s.key
                        ? 'bg-[#c9a84c] text-[#0d0d14]'
                        : 'bg-white/10 text-white/30'">
                    <span v-if="isStepDone(s.key)">✓</span>
                    <span v-else>{{ i + 1 }}</span>
                  </div>
                  <span class="text-sm transition-all"
                    :class="currentStep === s.key ? 'text-white font-semibold' : 'text-white/30'">
                    {{ s.label }}
                  </span>
                </div>
                <div v-if="i < steps.length - 1" class="w-8 h-px bg-white/10"></div>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Quote -->
      <div class="relative z-10">
        <div class="h-px bg-white/10 mb-6"></div>
        <p class="font-serif text-white/40 text-sm italic">"La sécurité commence par un mot de passe fort."</p>
      </div>
    </div>

    <!-- RIGHT PANEL -->
    <div class="flex-1 flex flex-col justify-center px-8 sm:px-12 lg:px-16 bg-[#0d0d14]">

      <!-- Mobile logo -->
      <div class="lg:hidden flex items-center gap-2 mb-8 mt-4">
        <img v-if="useSchoolInfo.school_info?.logo_image_base64" :src="useSchoolInfo.school_info?.logo_image_base64" class="object-contain flex items-center justify-center w-10 h-10">
        <span v-else class="text-2xl">🎓</span>
        <span class="font-serif text-[#c9a84c] text-xl font-bold">{{useSchoolInfo.school_info?.nom || 'Aplekol 360'}}</span>
      </div>

      <div class="max-w-md w-full flex justify-center items-center mx-auto mt-4">

        <div>
        <!-- FIRST LOGIN BANNER -->
        <div v-if="isFirstLogin && currentStep === 'password'"
          class="mb-4 p-4 rounded-md bg-[#c9a84c]/10 border border-[#c9a84c]/20 flex items-start gap-3">
          <span class="text-xl shrink-0">👋</span>
          <div>
            <p class="text-[#c9a84c] text-sm font-semibold">Première connexion</p>
            <p class="text-[#888] text-xs mt-0.5 leading-relaxed">
              Pour votre sécurité, vous devez définir un nouveau mot de passe avant de continuer.
            </p>
          </div>
        </div>

        <!-- ══ STEP 1 : EMAIL ══ -->
        <Transition name="fade-up" mode="out-in">
          <div v-if="currentStep === 'email'" key="email">
        
          </div>

          <!-- ══ STEP 3 : NOUVEAU MOT DE PASSE ══ -->
          <div v-else-if="currentStep === 'password'" key="password">
            <div class="mb-6">
              <h1 class="font-serif text-2xl font-bold text-white mb-1">Nouveau mot de passe</h1>
              <p class="text-[#555] text-sm">Choisissez un mot de passe fort et mémorable.</p>
            </div>

            <form @submit.prevent="resetPassword" class="space-y-4">
              <!-- New password -->
              <div>
                <label class="block text-xs font-semibold text-[#888] mb-1 tracking-wide uppercase">
                  Nouveau mot de passe
                </label>
                <div class="relative">
                  <span class="absolute left-4 top-1/2 -translate-y-1/2 text-[#444]">🔒</span>
                  <input v-model="form.password" :type="showPw ? 'text' : 'password'"
                    placeholder="Minimum 8 caractères"
                    class="w-full bg-[#111] border border-[#222] rounded-md pl-11 pr-12 py-2.5 text-white text-sm placeholder-[#333] outline-none transition-all focus:border-[#c9a84c] focus:ring-1 focus:ring-[#c9a84c]/30"/>
                  <button type="button" @click="showPw = !showPw"
                    class="absolute right-4 top-1/2 -translate-y-1/2 text-[#444] hover:text-[#888] cursor-pointer text-sm">
                    {{ showPw ? '🙈' : '👁' }}
                  </button>
                </div>

              
                <p v-if="errors.password" class="text-[#e74c3c] text-xs mt-1.5">{{ errors.password }}</p>
              </div>

              <!-- Confirm password -->
              <div>
                <label class="block text-xs font-semibold text-[#888] mb-1 tracking-wide uppercase">
                  Confirmer le mot de passe
                </label>
                <div class="relative">
                  <span class="absolute left-4 top-1/2 -translate-y-1/2 text-[#444]">🔑</span>
                  <input v-model="form.confirmPassword" :type="showConfirm ? 'text' : 'password'"
                    placeholder="Répétez le mot de passe"
                    class="w-full bg-[#111] rounded-md pl-11 pr-12 py-2.5 text-white text-sm placeholder-[#333] outline-none transition-all"
                    :class="form.confirmPassword
                      ? form.password === form.confirmPassword
                        ? 'border-1 border-[#10b981]'
                        : 'border-1 border-[#e74c3c]'
                      : 'border border-[#222] focus:border-[#c9a84c]'"/>
                  <button type="button" @click="showConfirm = !showConfirm"
                    class="absolute right-4 top-1/2 -translate-y-1/2 text-[#444] hover:text-[#888] cursor-pointer text-sm">
                    {{ showConfirm ? '🙈' : '👁' }}
                  </button>
                  <span v-if="form.confirmPassword" class="absolute right-11 top-1/2 -translate-y-1/2 text-sm">
                    {{ form.password === form.confirmPassword ? '✅' : '❌' }}
                  </span>
                </div>
                <p v-if="errors.confirmPassword" class="text-[#e74c3c] text-xs mt-1.5">{{ errors.confirmPassword }}</p>
              </div>

              <!-- Rules -->
              <div class="bg-[#111] rounded-md p-4 space-y-2">
                <p class="text-[#777] text-xs font-semibold uppercase tracking-wide mb-3">Exigences</p>
                <div v-for="rule in pwRules" :key="rule.label"
                  class="flex items-center gap-2.5 text-xs transition-colors"
                  :class="rule.valid ? 'text-[#10b981]' : 'text-[#444]'">
                  <span>{{ rule.valid ? '✓' : '○' }}</span>
                  {{ rule.label }}
                </div>
              </div>

              <button type="submit"
                :disabled="processing || form.password !== form.confirmPassword || !allRulesValid"
                class="w-full py-2.5 rounded-md font-semibold text-sm bg-[#10b981] text-white hover:bg-[#0d9e72] transition-all cursor-pointer disabled:opacity-40 flex items-center justify-center gap-2">
                <svg v-if="processing" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                <span>{{ processing ? 'Enregistrement...' : isFirstLogin ? '✓ Définir mon mot de passe' : '✓ Réinitialiser' }}</span>
              </button>
            </form>
          </div>

          <!-- ══ STEP 4 : SUCCÈS ══ -->
          <div v-else-if="currentStep === 'success'" key="success" class="text-center">
            <div class="w-20 h-20 rounded-full bg-[#10b981]/15 flex items-center justify-center text-4xl mx-auto mb-6">
              ✅
            </div>
            <h1 class="font-serif text-3xl font-bold text-white mb-3">
              {{ isFirstLogin ? 'Mot de passe défini !' : 'Réinitialisé !' }}
            </h1>
            <p class="text-[#555] text-sm leading-relaxed mb-8">
              {{ isFirstLogin
                ? 'Votre mot de passe a été défini avec succès. Vous pouvez maintenant accéder à votre espace.'
                : 'Votre mot de passe a été réinitialisé. Vous pouvez maintenant vous connecter.' }}
            </p> 
            <router-link to="/connexion"
              class="w-full py-2.5 rounded-md font-semibold text-sm bg-[#c9a84c] text-[#0d0d14] hover:bg-[#dbb85a] transition-all cursor-pointer px-8">
              → Aller à la connexion
            </router-link>
          </div>
        </Transition>

        <!-- Global error -->
        <div v-if="globalError"
          class="mt-4 p-3.5 rounded-xl bg-[#e74c3c]/10 border border-[#e74c3c]/20 text-[#e74c3c] text-sm flex items-center gap-2">
          <span>⚠️</span> {{ globalError }}
        </div>
        
        <p class="text-center text-[#333] text-xs mt-10">
          © {{ new Date().getFullYear() }} Aplekol 360
        </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route  = useRoute()

const isFirstLogin = computed(() => route.meta?.firstLogin)
import { useSchoolStoreInfo } from '../../stores/schoolStore'; 
const useSchoolInfo = useSchoolStoreInfo()

/* ── STEPS ── */
const steps = [
  // { key: 'email',    label: 'Email'      },
  // { key: 'code',     label: 'Code'       },
  { key: 'password', label: 'Mot de passe' },
]

const stepConfig = {
  // email: {
  //   emoji:       '📧',
  //   leftTitle:   'Récupération de compte',
  //   leftSubtitle:'Entrez votre email pour recevoir un code de vérification sécurisé.',
  // },
  // code: {
  //   emoji:       '🔐',
  //   leftTitle:   'Vérification en deux étapes',
  //   leftSubtitle:'Un code à 6 chiffres a été envoyé à votre adresse email.',
  // },
  password: {
    emoji:       '🔑',
    leftTitle:   'Nouveau mot de passe',
    leftSubtitle:'Choisissez un mot de passe fort pour sécuriser votre compte.',
  },
  success: {
    emoji:       '✅',
    leftTitle:   'Compte sécurisé !',
    leftSubtitle:'Votre mot de passe a été mis à jour avec succès.',
  },
}

const currentStep = ref('password')
const processing  = ref(false)
const globalError = ref('')

function isStepDone(key) {
  const order = ['password', 'success']
  return order.indexOf(key) < order.indexOf(currentStep.value)
}

/* ── FORM ── */
const form = reactive({
  email:           '',
  password:        '',
  confirmPassword: '',
  token:           '',
})
const errors   = reactive({})
const showPw      = ref(false)
const showConfirm = ref(false)

/* ── CODE INPUTS ── */
const codeDigits = ref(['', '', '', '', '', ''])
const codeRefs   = ref([])
const resendCooldown = ref(0)

const codeComplete = computed(() => codeDigits.value.every(d => d !== ''))
const fullCode     = computed(() => codeDigits.value.join(''))

function onCodeInput(i) {
  codeDigits.value[i] = codeDigits.value[i].replace(/\D/g, '').slice(-1)
  if (codeDigits.value[i] && i < 5) {
    codeRefs.value[i + 1]?.focus()
  }
}
function onBackspace(i) {
  if (!codeDigits.value[i] && i > 0) {
    codeDigits.value[i - 1] = ''
    codeRefs.value[i - 1]?.focus()
  }
}
function onPaste(e) {
  const text = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
  text.split('').forEach((c, i) => { codeDigits.value[i] = c })
  codeRefs.value[Math.min(text.length, 5)]?.focus()
}

function startResendCooldown() {
  resendCooldown.value = 60
  const t = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) clearInterval(t)
  }, 1000)
}

/* ── PASSWORD STRENGTH ── */
const pwRules = computed(() => [
  { label: 'Au moins 8 caractères',             valid: form.password.length >= 8 },
  { label: 'Une lettre majuscule',               valid: /[A-Z]/.test(form.password) },
  { label: 'Un chiffre',                         valid: /\d/.test(form.password) },
  { label: 'Un caractère spécial (!@#$%...)',    valid: /[^A-Za-z0-9]/.test(form.password) },
])

const allRulesValid = computed(() => pwRules.value.every(r => r.valid))

const pwStrength = computed(() => {
  const score = pwRules.value.filter(r => r.valid).length
  if (score <= 1) return { score: 1, color: 'bg-[#e74c3c]', textColor: 'text-[#e74c3c]', label: 'Trop faible' }
  if (score === 2) return { score: 2, color: 'bg-[#f97316]', textColor: 'text-[#f97316]', label: 'Faible' }
  if (score === 3) return { score: 3, color: 'bg-[#c9a84c]', textColor: 'text-[#c9a84c]', label: 'Moyen' }
  return { score: 4, color: 'bg-[#10b981]', textColor: 'text-[#10b981]', label: 'Fort ✓' }
})

/* ── API CALLS ── */
async function sendCode() {
  errors.email = ''
  if (!form.email) { errors.email = 'Email requis'; return }
  processing.value = true
  globalError.value = ''
  try {
    await axios.post('/password-reset-request', { email: form.email })
    currentStep.value = 'code'
    startResendCooldown()
  } catch (e) {
    globalError.value = e.response?.data?.detail ?? 'Erreur lors de l\'envoi du code.'
  } finally {
    processing.value = false
  }
}

async function resendCode() {
  if (resendCooldown.value > 0) return
  await sendCode()
}

async function verifyCode() {
  errors.code = ''
  if (!codeComplete.value) { errors.code = 'Entrez les 6 chiffres'; return }
  processing.value = true
  globalError.value = ''
  try {
    const res = await axios.post('/password-reset-verify', {
      email: form.email,
      code:  fullCode.value,
    })
    form.token        = res.data.token || fullCode.value
    currentStep.value = 'password'
  } catch (e) {
    errors.code = e.response?.data?.detail ?? 'Code invalide ou expiré.'
  } finally {
    processing.value = false
  }
}

async function resetPassword() {
  errors.password        = ''
  errors.confirmPassword = ''
  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Les mots de passe ne correspondent pas.'
    return
  }
  if (!allRulesValid.value) {
    errors.password = 'Le mot de passe ne respecte pas les exigences.'
    return
  }
  processing.value  = true
  globalError.value = ''
  //password-change-user-global
  try {
    await axios.put('/password-change-user-global', {
      email:                 form.email,
      token:                 form.token,
      current_password:      '@#Itsme1',
      password:              form.password,
      password_confirmation: form.confirmPassword,
    })
    currentStep.value = 'success'
    localStorage.removeItem('auth-token')
    sessionStorage.removeItem('auth-token')
    localStorage.removeItem('api_token')
  } catch (e) {
    globalError.value = e.response?.data?.detail ?? 'Erreur lors de la réinitialisation.'
  } finally {
    processing.value = false
  }
}
</script>

<style>
/* @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap'); */
.font-serif { font-family: 'Playfair Display', serif; }
* { font-family: 'DM Sans', sans-serif; }

.fade-up-enter-active, .fade-up-leave-active { transition: all 0.3s ease; }
.fade-up-enter-from { opacity: 0; transform: translateY(12px); }
.fade-up-leave-to   { opacity: 0; transform: translateY(-12px); }
</style>
<template>
  <div class="min-h-screen flex bg-white">
    <!-- Panneau de marque -->
    <div class="hidden lg:flex lg:w-1/2 bg-gray-900 text-white relative overflow-hidden flex-col justify-between p-12">
      <div class="absolute inset-0 opacity-[0.07]"
        style="background-image: radial-gradient(circle at 1px 1px, white 1px, transparent 0); background-size: 28px 28px;">
      </div>

      <div class="relative">
        <span class="text-sm font-semibold tracking-wide text-gray-400">{{ t('auth.login.brand') }}</span>
      </div>

      <div class="relative max-w-md">
        <h2 class="text-3xl font-bold leading-tight mb-3">
          {{ t('auth.login.heroTitle') }}
        </h2>
        <p class="text-gray-400 text-sm leading-relaxed">
          {{ t('auth.login.heroSubtitle') }}
        </p>

        <ul class="mt-8 space-y-3 text-sm text-gray-300">
          <li class="flex items-center gap-3">
            <span class="w-1.5 h-1.5 rounded-full bg-gray-500"></span>
            {{ t('auth.login.heroFeature1') }}
          </li>
          <li class="flex items-center gap-3">
            <span class="w-1.5 h-1.5 rounded-full bg-gray-500"></span>
            {{ t('auth.login.heroFeature2') }}
          </li>
          <li class="flex items-center gap-3">
            <span class="w-1.5 h-1.5 rounded-full bg-gray-500"></span>
            {{ t('auth.login.heroFeature3') }}
          </li>
        </ul>
      </div>

      <p class="relative text-xs text-gray-500">© {{ new Date().getFullYear() }} IUSTH</p>
    </div>

    <!-- Formulaire de connexion -->
    <div class="flex-1 flex items-center justify-center p-8">
      <form class="w-full max-w-sm" @submit.prevent="onSubmit">
        <div class="flex items-center justify-between mb-1">
          <h1 class="text-2xl font-bold text-gray-900">{{ t('auth.login.welcomeBack') }}</h1>
          <LanguageSwitcher />
        </div>
        <p class="text-sm text-gray-500 mb-8">{{ t('auth.login.subtitle') }}</p>

        <p v-if="resetSuccess" class="text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2 mb-4">
          {{ t('auth.login.resetSuccess') }}
        </p>

        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('auth.login.email') }}</label>
        <input v-model="email" type="email" required autocomplete="username"
          class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-gray-900" />

        <div class="flex items-center justify-between mb-1">
          <label class="block text-sm font-medium text-gray-700">{{ t('auth.login.password') }}</label>
          <router-link to="/forgot-password" class="text-xs text-gray-500 hover:underline">{{ t('auth.login.forgotPassword') }}</router-link>
        </div>
        <div class="relative mb-4">
          <input v-model="password" :type="showPassword ? 'text' : 'password'" required autocomplete="current-password"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-gray-900" />
          <button type="button" @click="showPassword = !showPassword"
            class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
            :aria-label="showPassword ? t('auth.login.hidePassword') : t('auth.login.showPassword')">
            <svg v-if="showPassword" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2 2 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd" />
              <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.064 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
            </svg>
          </button>
        </div>

        <p v-if="error" class="text-sm text-red-600 mb-4">{{ error }}</p>

        <button type="submit" :disabled="loading"
          class="w-full bg-gray-900 text-white rounded-lg py-2.5 text-sm font-semibold hover:bg-gray-800 disabled:opacity-50">
          {{ loading ? t('auth.login.submitting') : t('auth.login.submit') }}
        </button>

        <details class="mt-6">
          <summary class="text-xs text-gray-400 hover:text-gray-600 cursor-pointer select-none">{{ t('auth.login.cookiesLabel') }}</summary>
          <p class="text-xs text-gray-400 mt-2 leading-relaxed">{{ t('auth.login.cookiesBody') }}</p>
        </details>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const { t } = useI18n()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const resetSuccess = computed(() => route.query.reset === '1')

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    await auth.fetchMe()
    if (auth.user?.must_change_password) router.push('/change-password')
    else if (typeof route.query.redirect === 'string') router.push(route.query.redirect)
    else if (auth.isAdmin) router.push('/admin/courses')
    else if (auth.isTeacher) router.push('/teacher/courses')
    else if (auth.isStaff) router.push('/staff/staff-meetings')
    else router.push('/student/courses')
  } catch (e) {
    error.value = e.response?.data?.detail || t('auth.login.invalidCredentials')
  } finally {
    loading.value = false
  }
}
</script>

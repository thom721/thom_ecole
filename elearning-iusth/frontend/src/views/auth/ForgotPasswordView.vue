<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <form class="bg-white p-8 rounded-xl shadow-sm w-full max-w-sm" @submit.prevent="onSubmit">
      <h1 class="text-lg font-bold mb-2 text-gray-900">{{ t('auth.forgotPassword.title') }}</h1>
      <p class="text-sm text-gray-500 mb-6">{{ t('auth.forgotPassword.subtitle') }}</p>

      <label class="block text-sm text-gray-600 mb-1">{{ t('auth.forgotPassword.email') }}</label>
      <input v-model="email" type="email" required
        class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 text-sm" />

      <p v-if="message" class="text-sm text-green-700 mb-4">{{ message }}</p>
      <p v-if="error" class="text-sm text-red-600 mb-4">{{ error }}</p>

      <button type="submit" :disabled="loading || !!message"
        class="w-full bg-gray-900 text-white rounded-lg py-2 text-sm font-semibold disabled:opacity-50">
        {{ loading ? t('auth.forgotPassword.submitting') : t('auth.forgotPassword.submit') }}
      </button>

      <router-link to="/login" class="block text-center text-sm text-gray-500 hover:underline mt-4">
        {{ t('auth.forgotPassword.backToLogin') }}
      </router-link>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const email = ref('')
const message = ref('')
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    message.value = await auth.forgotPassword(email.value)
  } catch (e) {
    error.value = e.response?.data?.detail || t('auth.forgotPassword.error')
  } finally {
    loading.value = false
  }
}
</script>

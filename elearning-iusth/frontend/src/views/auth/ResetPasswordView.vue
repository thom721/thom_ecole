<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <form v-if="token" class="bg-white p-8 rounded-xl shadow-sm w-full max-w-sm" @submit.prevent="onSubmit">
      <h1 class="text-lg font-bold mb-2 text-gray-900">{{ t('auth.resetPassword.title') }}</h1>

      <label class="block text-sm text-gray-600 mb-1">{{ t('auth.resetPassword.newPassword') }}</label>
      <input v-model="newPassword" type="password" required minlength="8"
        class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 text-sm" />

      <label class="block text-sm text-gray-600 mb-1">{{ t('auth.resetPassword.confirmPassword') }}</label>
      <input v-model="confirmPassword" type="password" required
        class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 text-sm" />

      <p v-if="error" class="text-sm text-red-600 mb-4">{{ error }}</p>

      <button type="submit" :disabled="loading"
        class="w-full bg-gray-900 text-white rounded-lg py-2 text-sm font-semibold disabled:opacity-50">
        {{ loading ? t('auth.resetPassword.submitting') : t('auth.resetPassword.submit') }}
      </button>
    </form>

    <div v-else class="bg-white p-8 rounded-xl shadow-sm w-full max-w-sm text-center">
      <p class="text-sm text-red-600">{{ t('auth.resetPassword.invalidLink') }}</p>
      <router-link to="/forgot-password" class="block text-sm text-gray-500 hover:underline mt-4">
        {{ t('auth.resetPassword.requestNewLink') }}
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const token = ref(route.query.token || '')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  if (newPassword.value !== confirmPassword.value) {
    error.value = t('auth.resetPassword.passwordMismatch')
    return
  }
  loading.value = true
  try {
    await auth.resetPassword(token.value, newPassword.value)
    router.push({ path: '/login', query: { reset: '1' } })
  } catch (e) {
    error.value = e.response?.data?.detail || t('auth.resetPassword.error')
  } finally {
    loading.value = false
  }
}
</script>

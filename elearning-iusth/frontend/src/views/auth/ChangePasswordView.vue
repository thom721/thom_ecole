<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <form class="bg-white p-8 rounded-xl shadow-sm w-full max-w-sm" @submit.prevent="onSubmit">
      <h1 class="text-lg font-bold mb-2 text-gray-900">{{ t('auth.changePassword.title') }}</h1>
      <p class="text-sm text-gray-500 mb-6">{{ t('auth.changePassword.subtitle') }}</p>

      <label class="block text-sm text-gray-600 mb-1">{{ t('auth.changePassword.currentPassword') }}</label>
      <input v-model="currentPassword" type="password" required
        class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 text-sm" />

      <label class="block text-sm text-gray-600 mb-1">{{ t('auth.changePassword.newPassword') }}</label>
      <input v-model="newPassword" type="password" required minlength="8"
        class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 text-sm" />

      <label class="block text-sm text-gray-600 mb-1">{{ t('auth.changePassword.confirmPassword') }}</label>
      <input v-model="confirmPassword" type="password" required
        class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 text-sm" />

      <p v-if="error" class="text-sm text-red-600 mb-4">{{ error }}</p>

      <button type="submit" :disabled="loading"
        class="w-full bg-gray-900 text-white rounded-lg py-2 text-sm font-semibold disabled:opacity-50">
        {{ loading ? t('auth.changePassword.submitting') : t('auth.changePassword.submit') }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

async function onSubmit() {
  error.value = ''
  if (newPassword.value !== confirmPassword.value) {
    error.value = t('auth.changePassword.passwordMismatch')
    return
  }
  loading.value = true
  try {
    const { data } = await axios.post('/auth/change-password', {
      current_password: currentPassword.value,
      new_password: newPassword.value,
    })
    auth.user = data
    if (auth.isAdmin) router.push('/admin/courses')
    else if (auth.isTeacher) router.push('/teacher/courses')
    else router.push('/student/courses')
  } catch (e) {
    error.value = e.response?.data?.detail || t('auth.changePassword.error')
  } finally {
    loading.value = false
  }
}
</script>

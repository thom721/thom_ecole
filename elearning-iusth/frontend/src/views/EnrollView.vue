<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="bg-white p-8 rounded-xl shadow-sm w-full max-w-sm">
      <h1 class="text-lg font-bold text-gray-900 mb-1">{{ t('enroll.title') }}</h1>
      <p class="text-sm text-gray-500 mb-6">{{ t('enroll.subtitle') }}</p>

      <label class="block text-sm text-gray-600 mb-1">{{ t('enroll.keyLabel') }}</label>
      <input v-model="key" class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 text-sm" />

      <p v-if="error" class="text-sm text-red-600 mb-4">{{ error }}</p>
      <p v-if="success" class="text-sm text-green-700 mb-4">{{ success }}</p>

      <div class="space-y-2">
        <button class="w-full bg-gray-900 text-white rounded-lg py-2 text-sm font-semibold disabled:opacity-50" :disabled="loading" @click="onSelfEnroll">
          {{ t('enroll.selfEnroll') }}
        </button>
        <button class="w-full bg-gray-100 text-gray-700 rounded-lg py-2 text-sm font-semibold disabled:opacity-50" :disabled="loading" @click="onGuestEnroll">
          {{ t('enroll.guestEnroll') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useEnrollmentMethodsStore } from '@/stores/enrollmentMethods'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const enrollmentMethods = useEnrollmentMethodsStore()
const auth = useAuthStore()

const key = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

function goToCourse() {
  const base = auth.isTeacher || auth.isAdmin ? '/teacher' : '/student'
  router.push(`${base}/courses/${route.params.courseId}`)
}

async function onSelfEnroll() {
  error.value = ''
  loading.value = true
  try {
    await enrollmentMethods.enrollSelf(route.params.courseId, key.value)
    success.value = t('enroll.success')
    setTimeout(goToCourse, 800)
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  } finally {
    loading.value = false
  }
}

async function onGuestEnroll() {
  error.value = ''
  loading.value = true
  try {
    await enrollmentMethods.enrollGuest(route.params.courseId, key.value)
    success.value = t('enroll.success')
    setTimeout(goToCourse, 800)
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  } finally {
    loading.value = false
  }
}
</script>

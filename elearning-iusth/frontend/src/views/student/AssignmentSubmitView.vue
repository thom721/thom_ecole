<template>
  <div class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>

    <div v-if="submission?.status === 'graded'" class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
      <p class="font-semibold text-green-800">{{ t('student.assignmentSubmit.grade', { grade: submission.grade }) }}</p>
      <p v-if="submission.feedback" class="text-sm text-green-700 mt-1">{{ submission.feedback }}</p>
    </div>

    <h1 class="text-lg font-bold text-gray-900 mb-4">{{ t('student.assignmentSubmit.title') }}</h1>

    <label class="block text-sm text-gray-600 mb-1">{{ t('student.assignmentSubmit.answerLabel') }}</label>
    <textarea v-model="text" rows="8"
      class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 text-sm"></textarea>

    <label class="block text-sm text-gray-600 mb-1">{{ t('student.assignmentSubmit.fileLabel') }}</label>
    <input type="file" class="block mb-4 text-sm" @change="onFileChange" />

    <p v-if="message" class="text-sm mb-4" :class="error ? 'text-red-600' : 'text-green-600'">{{ message }}</p>

    <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onSubmit">
      {{ t('student.assignmentSubmit.submit') }}
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const route = useRoute()
const text = ref('')
const file = ref(null)
const submission = ref(null)
const message = ref('')
const error = ref(false)

function onFileChange(e) {
  file.value = e.target.files[0] || null
}

async function fetchExisting() {
  try {
    const { data } = await axios.get(`/assignments/${route.params.id}/submissions/me`)
    submission.value = data
    text.value = data.submitted_text || ''
  } catch {
    // pas encore de soumission — normal
  }
}

async function onSubmit() {
  message.value = ''
  error.value = false
  const formData = new FormData()
  if (text.value) formData.append('submitted_text', text.value)
  if (file.value) formData.append('file', file.value)

  try {
    const { data } = await axios.post(`/assignments/${route.params.id}/submissions`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    submission.value = data
    message.value = t('student.assignmentSubmit.submitSuccess')
  } catch (e) {
    error.value = true
    message.value = e.response?.data?.detail || t('student.assignmentSubmit.submitError')
  }
}

onMounted(fetchExisting)
</script>

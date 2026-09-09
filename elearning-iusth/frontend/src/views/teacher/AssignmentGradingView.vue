<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('teacher.assignmentGrading.title') }}</h1>

    <p v-if="!submissions.length" class="text-sm text-gray-500">{{ t('teacher.assignmentGrading.empty') }}</p>

    <div v-for="s in submissions" :key="s.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <p class="text-xs text-gray-500 mb-1">{{ t('teacher.assignmentGrading.student', { id: s.student_id }) }}</p>
      <p class="text-sm text-gray-800 whitespace-pre-wrap mb-3">{{ s.submitted_text || t('teacher.assignmentGrading.noText') }}</p>
      <p v-if="s.file_path" class="text-xs text-gray-500 mb-3">{{ t('teacher.assignmentGrading.attachedFile', { path: s.file_path }) }}</p>

      <div class="flex gap-2 items-center">
        <input v-model="grades[s.id]" type="number" :placeholder="t('teacher.assignmentGrading.gradePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
        <input v-model="feedbacks[s.id]" :placeholder="t('teacher.assignmentGrading.feedbackPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onGrade(s.id)">
          {{ t('teacher.assignmentGrading.gradeButton') }}
        </button>
      </div>
      <p v-if="s.status === 'graded'" class="text-xs text-green-600 mt-2">{{ t('teacher.assignmentGrading.alreadyGraded', { grade: s.grade }) }}</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const route = useRoute()
const submissions = ref([])
const grades = reactive({})
const feedbacks = reactive({})

async function load() {
  const { data } = await axios.get(`/assignments/${route.params.id}/submissions`)
  submissions.value = data
}

async function onGrade(submissionId) {
  await axios.patch(`/submissions/${submissionId}/grade`, {
    grade: Number(grades[submissionId]),
    feedback: feedbacks[submissionId] || null,
  })
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('lesson.gradingTitle') }}</h1>

    <p v-if="!queue.length" class="text-sm text-gray-500">{{ t('lesson.gradingEmpty') }}</p>

    <div v-for="pa in queue" :key="pa.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <p class="text-sm font-medium mb-1">{{ pa.page_title }}</p>
      <p class="text-xs text-gray-400 mb-2">{{ t('teacher.quizGrading.student', { id: pa.student_id }) }}</p>
      <p class="text-sm text-gray-600 mb-2">{{ pa.answer_text || t('teacher.quizGrading.noAnswer') }}</p>
      <div class="flex gap-2 items-center">
        <input v-model="grades[pa.id]" type="number" :placeholder="t('teacher.quizGrading.pointsPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
        <input v-model="feedbacks[pa.id]" :placeholder="t('teacher.quizGrading.feedbackPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onGrade(pa.id)">{{ t('teacher.quizGrading.gradeButton') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useLessonsStore } from '@/stores/lessons'

const { t } = useI18n()
const route = useRoute()
const lessonId = route.params.id
const lessons = useLessonsStore()

const queue = ref([])
const grades = reactive({})
const feedbacks = reactive({})

async function load() {
  queue.value = await lessons.fetchEssayGradingQueue(lessonId)
}

async function onGrade(pageAttemptId) {
  await lessons.gradeEssayPageAttempt(pageAttemptId, {
    points_awarded: Number(grades[pageAttemptId]),
    feedback: feedbacks[pageAttemptId] || null,
  })
  await load()
}

onMounted(load)
</script>

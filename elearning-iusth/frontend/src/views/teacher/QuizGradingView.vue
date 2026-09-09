<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('teacher.quizGrading.title') }}</h1>

    <p v-if="!attempts.length" class="text-sm text-gray-500">{{ t('teacher.quizGrading.empty') }}</p>

    <div v-for="a in attempts" :key="a.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <div class="flex items-center justify-between mb-2">
        <p class="text-sm">{{ t('teacher.quizGrading.student', { id: a.student_id }) }}</p>
        <span class="text-xs px-2 py-0.5 rounded-full"
          :class="a.status === 'graded' ? 'bg-green-100 text-green-700' : a.status === 'pending_manual_grading' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'">
          {{ a.status }}
        </span>
      </div>
      <p v-if="a.score !== null" class="text-sm text-gray-700 mb-2">{{ t('teacher.quizGrading.score', { score: a.score, max: a.max_score }) }}</p>
      <button v-if="a.status === 'pending_manual_grading'" class="text-blue-600 text-xs hover:underline" @click="openDetail(a.id)">
        {{ t('teacher.quizGrading.gradeEssays') }}
      </button>

      <div v-if="detail && detail.id === a.id" class="mt-3 border-t border-gray-100 pt-3">
        <div v-for="q in detail.questions.filter((x) => x.question_type === 'essay')" :key="q.question_id" class="mb-3">
          <p class="text-sm font-medium">{{ q.question_text }}</p>
          <p class="text-sm text-gray-600 mb-2">{{ q.answer_data?.text || t('teacher.quizGrading.noAnswer') }}</p>
          <div class="flex gap-2 items-center">
            <input v-model="grades[q.question_id]" type="number" :placeholder="t('teacher.quizGrading.pointsPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
            <input v-model="feedbacks[q.question_id]" :placeholder="t('teacher.quizGrading.feedbackPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
            <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onGrade(a.id, q.question_id)">{{ t('teacher.quizGrading.gradeButton') }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useQuizzesStore } from '@/stores/quizzes'

const { t } = useI18n()
const route = useRoute()
const quizId = route.params.id
const quizzes = useQuizzesStore()

const attempts = ref([])
const detail = ref(null)
const grades = reactive({})
const feedbacks = reactive({})

async function load() {
  attempts.value = await quizzes.fetchQuizAttempts(quizId)
}

async function openDetail(attemptId) {
  detail.value = await quizzes.fetchAttempt(attemptId)
}

async function onGrade(attemptId, questionId) {
  await quizzes.gradeResponse(attemptId, questionId, {
    points_awarded: Number(grades[questionId]),
    feedback: feedbacks[questionId] || null,
  })
  await load()
  detail.value = await quizzes.fetchAttempt(attemptId)
}

onMounted(load)
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>

    <div v-if="loading" class="text-sm text-gray-500">{{ t('common.loading') }}</div>

    <div v-else-if="startError === 'restricted'" class="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <p class="font-semibold text-gray-900 mb-2">{{ t('access.restrictedTitle') }}</p>
      <p class="text-sm text-gray-600">{{ restrictedReason }}</p>
    </div>

    <div v-else-if="!attempt" class="bg-white border border-gray-200 rounded-xl p-4">
      <h1 class="text-lg font-bold text-gray-900 mb-3">{{ t('lesson.title') }}</h1>
      <input v-model="password" type="password" :placeholder="t('lesson.passwordPromptPlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3" />
      <p v-if="startError" class="text-xs text-red-600 mb-3">{{ startError }}</p>
      <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onStart">{{ t('lesson.start') }}</button>
    </div>

    <div v-else>
      <div v-if="attempt.status === 'completed'" class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
        <p class="font-semibold text-green-800">{{ t('lesson.completedScore', { score: attempt.score, max: attempt.max_score }) }}</p>
      </div>
      <div v-else-if="attempt.status === 'pending_manual_grading'" class="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
        <p class="font-semibold text-amber-800">{{ t('lesson.pendingManualGrading') }}</p>
      </div>

      <div v-else-if="attempt.current_page" class="bg-white border border-gray-200 rounded-xl p-4">
        <div class="h-1.5 bg-gray-100 rounded-full mb-4 overflow-hidden">
          <div class="h-full bg-gray-900" :style="{ width: attempt.progress_percent + '%' }"></div>
        </div>

        <h2 class="font-semibold text-gray-900 mb-2">{{ attempt.current_page.title }}</h2>
        <p class="text-sm text-gray-700 mb-4 whitespace-pre-wrap">{{ attempt.current_page.content }}</p>

        <template v-if="!lastResult">
          <div v-if="['content', 'true_false', 'multiple_choice'].includes(attempt.current_page.page_type)">
            <label v-for="a in attempt.current_page.answers" :key="a.id" class="flex items-center gap-2 text-sm mb-2">
              <input type="radio" name="answer" :value="a.id" v-model="selectedAnswerId" />
              {{ a.answer_text }}
            </label>
          </div>
          <div v-else-if="attempt.current_page.page_type === 'short_answer'">
            <input v-model="freeText" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" :placeholder="t('student.quizTake.answerPlaceholder')" />
          </div>
          <div v-else-if="attempt.current_page.page_type === 'numerical'">
            <input v-model="freeText" type="number" step="any" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" :placeholder="t('student.quizTake.numericAnswerPlaceholder')" />
          </div>
          <div v-else-if="attempt.current_page.page_type === 'essay'">
            <textarea v-model="freeText" rows="5" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"></textarea>
          </div>

          <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold mt-3" @click="onAnswer">{{ t('lesson.answerButton') }}</button>
        </template>

        <template v-else>
          <p v-if="lastResult.is_correct !== null" class="text-sm mb-3" :class="lastResult.is_correct ? 'text-green-600' : 'text-red-600'">
            {{ lastResult.is_correct ? t('student.quizTake.correct') : t('student.quizTake.incorrect') }}
          </p>
          <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onContinue">{{ t('lesson.continueButton') }}</button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useLessonsStore } from '@/stores/lessons'

const { t } = useI18n()
const route = useRoute()
const lessons = useLessonsStore()

const loading = ref(false)
const password = ref('')
const startError = ref('')
const restrictedReason = ref('')
const attempt = ref(null)
const selectedAnswerId = ref('')
const freeText = ref('')
const lastResult = ref(null)

async function refreshAttempt() {
  attempt.value = await lessons.fetchAttempt(attempt.value.id)
}

async function onStart() {
  startError.value = ''
  try {
    const started = await lessons.startAttempt(route.params.id, password.value)
    attempt.value = started
    await refreshAttempt()
  } catch (e) {
    if (e.response?.status === 403) {
      startError.value = 'restricted'
      restrictedReason.value = e.response?.data?.detail || ''
    } else {
      startError.value = e.response?.data?.detail || t('common.error')
    }
  }
}

async function onAnswer() {
  const page = attempt.value.current_page
  const payload = {}
  if (['content', 'true_false', 'multiple_choice'].includes(page.page_type)) payload.answer_id = selectedAnswerId.value
  else payload.answer_text = freeText.value

  lastResult.value = await lessons.answerPage(attempt.value.id, page.id, payload)
  selectedAnswerId.value = ''
  freeText.value = ''
}

async function onContinue() {
  const reachedEnd = lastResult.value?.end_of_lesson
  lastResult.value = null
  if (reachedEnd) {
    attempt.value = await lessons.completeAttempt(attempt.value.id)
  } else {
    await refreshAttempt()
  }
}

onMounted(load)

async function load() {
  loading.value = true
  try {
    const started = await lessons.startAttempt(route.params.id, '')
    attempt.value = started
    await refreshAttempt()
  } catch (e) {
    if (e.response?.status === 400) {
      // mot de passe requis ou incorrect — laisser l'utilisateur le saisir
      attempt.value = null
    } else if (e.response?.status === 403) {
      startError.value = 'restricted'
      restrictedReason.value = e.response?.data?.detail || ''
    }
  } finally {
    loading.value = false
  }
}
</script>

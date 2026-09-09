<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('interactiveVideo.gradingTitle') }}</h1>

    <p v-if="!queue.length" class="text-sm text-gray-500">{{ t('interactiveVideo.gradingEmpty') }}</p>

    <div v-for="r in queue" :key="r.response_id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <p class="text-sm font-medium mb-1">{{ r.question_text }}</p>
      <p class="text-xs text-gray-400 mb-2">{{ t('teacher.quizGrading.student', { id: r.student_id }) }}</p>
      <p class="text-sm text-gray-600 mb-2">{{ r.answer_text || t('teacher.quizGrading.noAnswer') }}</p>
      <div class="flex gap-2 items-center">
        <input v-model="grades[r.response_id]" type="number" :placeholder="t('teacher.quizGrading.pointsPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
        <input v-model="feedbacks[r.response_id]" :placeholder="t('teacher.quizGrading.feedbackPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onGrade(r.response_id)">{{ t('teacher.quizGrading.gradeButton') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useInteractiveVideosStore } from '@/stores/interactiveVideos'

const { t } = useI18n()
const route = useRoute()
const videoId = route.params.id
const interactiveVideos = useInteractiveVideosStore()

const queue = ref([])
const grades = reactive({})
const feedbacks = reactive({})

async function load() {
  queue.value = await interactiveVideos.fetchEssayGrading(videoId)
}

async function onGrade(responseId) {
  await interactiveVideos.gradeEssayResponse(responseId, {
    points_awarded: Number(grades[responseId]),
    feedback: feedbacks[responseId] || null,
  })
  await load()
}

onMounted(load)
</script>

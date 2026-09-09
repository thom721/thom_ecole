<template>
  <div v-if="video">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-lg font-bold text-gray-900">{{ video.title }}</h1>
      <router-link :to="`/teacher/interactive-videos/${videoId}/grading`" class="text-sm text-blue-600 hover:underline">
        {{ t('interactiveVideo.viewGrading') }}
      </router-link>
    </div>

    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4 text-sm text-gray-600">
      <p>{{ t('interactiveVideo.sourceLabel') }} : {{ video.source_type === 'file' ? video.original_filename : video.video_url }}</p>
    </div>

    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('interactiveVideo.checkpointsTitle') }}</h2>
      <ul class="text-sm mb-3">
        <li v-for="cp in video.checkpoints" :key="cp.id" class="flex items-center justify-between py-1 border-t border-gray-100 first:border-t-0">
          <span>{{ formatTime(cp.timestamp_seconds) }} — {{ questionText(cp.question_id) }} ({{ cp.points }} pts)</span>
          <button class="text-red-600 text-xs" @click="onDeleteCheckpoint(cp.id)">{{ t('common.remove') }}</button>
        </li>
      </ul>
    </div>

    <details class="bg-white border border-gray-200 rounded-xl p-4" open>
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('interactiveVideo.addCheckpoint') }}</summary>
      <div class="mt-3 space-y-2">
        <div class="flex gap-2">
          <input v-model="newCheckpoint.timestamp_seconds" type="number" :placeholder="t('interactiveVideo.timestampPlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm w-32" />
          <input v-model="newCheckpoint.points" type="number" :placeholder="t('common.points')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm w-32" />
        </div>
        <select v-model="newCheckpoint.question_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="">{{ t('interactiveVideo.selectQuestion') }}</option>
          <option v-for="q in questions" :key="q.id" :value="q.id">{{ q.question_text }} ({{ q.question_type }})</option>
        </select>
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onAddCheckpoint">{{ t('common.add') }}</button>
      </div>
    </details>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useInteractiveVideosStore } from '@/stores/interactiveVideos'
import { useQuizzesStore } from '@/stores/quizzes'

const { t } = useI18n()
const route = useRoute()
const videoId = route.params.id
const interactiveVideos = useInteractiveVideosStore()
const quizzes = useQuizzesStore()

const video = ref(null)
const questions = ref([])
const newCheckpoint = ref({ timestamp_seconds: '', points: '', question_id: '' })

function formatTime(seconds) {
  const s = Math.floor(seconds)
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

function questionText(questionId) {
  const q = questions.value.find((q) => q.id === questionId)
  return q ? q.question_text : questionId
}

async function load() {
  video.value = await interactiveVideos.fetchVideo(videoId)
  questions.value = await quizzes.fetchCourseQuestions(video.value.course_id)
}

async function onAddCheckpoint() {
  if (!newCheckpoint.value.timestamp_seconds || !newCheckpoint.value.question_id) return
  await interactiveVideos.createCheckpoint(videoId, {
    timestamp_seconds: newCheckpoint.value.timestamp_seconds,
    question_id: newCheckpoint.value.question_id,
    points: newCheckpoint.value.points || null,
  })
  newCheckpoint.value = { timestamp_seconds: '', points: '', question_id: '' }
  await load()
}

async function onDeleteCheckpoint(id) {
  await interactiveVideos.deleteCheckpoint(id)
  await load()
}

onMounted(load)
</script>

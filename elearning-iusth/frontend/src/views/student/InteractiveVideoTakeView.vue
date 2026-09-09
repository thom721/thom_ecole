<template>
  <div class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>

    <div v-if="!video" class="text-sm text-gray-500">{{ t('common.loading') }}</div>

    <div v-else-if="video.access_restricted" class="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <p class="font-semibold text-gray-900 mb-2">{{ t('access.restrictedTitle') }}</p>
      <ul class="text-sm text-gray-600 list-disc list-inside">
        <li v-for="(r, i) in video.access_reasons" :key="i">{{ r }}</li>
      </ul>
    </div>

    <div v-else class="bg-white border border-gray-200 rounded-xl p-4">
      <h1 class="text-lg font-bold text-gray-900 mb-3">{{ video.title }}</h1>

      <div v-if="attempt && attempt.status === 'completed'" class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
        <p class="font-semibold text-green-800">{{ t('interactiveVideo.completedScore', { score: attempt.score, max: attempt.max_score }) }}</p>
      </div>
      <div v-else-if="attempt && attempt.status === 'pending_manual_grading'" class="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
        <p class="font-semibold text-amber-800">{{ t('interactiveVideo.pendingManualGrading') }}</p>
      </div>

      <template v-if="!attempt">
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onStart">{{ t('interactiveVideo.start') }}</button>
      </template>

      <template v-else-if="attempt.status === 'in_progress'">
        <video v-if="videoSrc" ref="videoEl" :src="videoSrc" controls class="w-full rounded-lg mb-3"
               @timeupdate="onTimeUpdate" @ended="onEnded" @loadedmetadata="onLoadedMetadata"></video>

        <div v-if="activeCheckpoint" class="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-3">
          <p class="text-sm font-medium text-gray-900 mb-2">{{ activeCheckpoint.question_text }}</p>

          <div v-if="['true_false', 'multiple_choice'].includes(activeCheckpoint.question_type)">
            <label v-for="o in activeCheckpoint.options" :key="o.id" class="flex items-center gap-2 text-sm mb-2">
              <input type="radio" name="cp-answer" :value="o.id" v-model="selectedOptionId" />
              {{ o.option_text }}
            </label>
          </div>
          <div v-else-if="activeCheckpoint.question_type === 'short_answer'">
            <input v-model="freeText" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div v-else-if="activeCheckpoint.question_type === 'numerical'">
            <input v-model="freeText" type="number" step="any" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div v-else-if="activeCheckpoint.question_type === 'essay'">
            <textarea v-model="freeText" rows="4" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"></textarea>
          </div>

          <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold mt-2" @click="onAnswer">{{ t('interactiveVideo.answerButton') }}</button>
        </div>

        <button v-if="videoEnded && allAnswered" class="bg-green-700 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onFinish">
          {{ t('interactiveVideo.finishButton') }}
        </button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useInteractiveVideosStore } from '@/stores/interactiveVideos'

const { t } = useI18n()
const route = useRoute()
const videoId = route.params.id
const interactiveVideos = useInteractiveVideosStore()

const video = ref(null)
const attempt = ref(null)
const videoSrc = ref(null)
const videoEl = ref(null)
const activeCheckpoint = ref(null)
const answeredIds = ref(new Set())
const selectedOptionId = ref('')
const freeText = ref('')
const videoEnded = ref(false)
let syncInterval = null

const allAnswered = computed(() => video.value && video.value.checkpoints.every((c) => answeredIds.value.has(c.id)))

async function loadVideoSrc() {
  if (video.value.source_type === 'url') {
    videoSrc.value = video.value.video_url
  } else {
    const resp = await axios.get(`/interactive-videos/${videoId}/media`, { responseType: 'blob' })
    videoSrc.value = URL.createObjectURL(resp.data)
  }
}

async function load() {
  video.value = await interactiveVideos.fetchVideo(videoId)
  attempt.value = video.value.my_attempt
  if (attempt.value && attempt.value.status === 'in_progress') {
    await loadVideoSrc()
  }
}

async function onStart() {
  attempt.value = await interactiveVideos.startAttempt(videoId)
  await loadVideoSrc()
  syncInterval = setInterval(syncPosition, 10000)
}

function onLoadedMetadata() {
  if (videoEl.value && attempt.value.last_position_seconds > 0) {
    videoEl.value.currentTime = Number(attempt.value.last_position_seconds)
  }
  if (!syncInterval) syncInterval = setInterval(syncPosition, 10000)
}

function syncPosition() {
  if (videoEl.value && !videoEl.value.paused) {
    interactiveVideos.updatePosition(attempt.value.id, videoEl.value.currentTime)
  }
}

function onTimeUpdate() {
  if (activeCheckpoint.value || !videoEl.value) return
  const t = videoEl.value.currentTime
  const next = video.value.checkpoints.find((c) => !answeredIds.value.has(c.id) && t >= Number(c.timestamp_seconds))
  if (next) {
    videoEl.value.pause()
    activeCheckpoint.value = next
    selectedOptionId.value = ''
    freeText.value = ''
  }
}

async function onAnswer() {
  const cp = activeCheckpoint.value
  let answerData = {}
  if (['true_false', 'multiple_choice'].includes(cp.question_type)) {
    answerData = { option_id: selectedOptionId.value }
  } else {
    answerData = { text: freeText.value, value: freeText.value }
  }
  await interactiveVideos.answerCheckpoint(attempt.value.id, cp.id, answerData)
  answeredIds.value.add(cp.id)
  activeCheckpoint.value = null
  videoEl.value?.play()
}

function onEnded() {
  videoEnded.value = true
  if (syncInterval) {
    clearInterval(syncInterval)
    syncInterval = null
  }
}

async function onFinish() {
  attempt.value = await interactiveVideos.finishAttempt(attempt.value.id)
}

onBeforeUnmount(() => {
  if (syncInterval) clearInterval(syncInterval)
})

onMounted(load)
</script>

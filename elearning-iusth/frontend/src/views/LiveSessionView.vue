<template>
  <div v-if="session && inCall" class="fixed inset-0 z-50 bg-black">
    <div id="jitsi-container" class="w-full h-full"></div>
  </div>

  <div v-else-if="loadError" class="max-w-3xl">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <div class="bg-amber-50 border border-amber-200 rounded-xl p-4">
      <p class="text-sm text-amber-800">{{ loadError }}</p>
    </div>
  </div>

  <div v-else-if="session" class="max-w-3xl">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>

    <div>
      <h1 class="text-lg font-bold text-gray-900 mb-1">{{ session.title }}</h1>
      <p v-if="session.description" class="text-sm text-gray-500 mb-4">{{ session.description }}</p>

      <div class="bg-white border border-gray-200 rounded-xl p-4 space-y-2 text-sm text-gray-600">
        <p v-if="session.scheduled_start">{{ t('liveSession.scheduledStart') }} : {{ formatDate(session.scheduled_start) }}</p>
        <p v-if="session.scheduled_end">{{ t('liveSession.scheduledEnd') }} : {{ formatDate(session.scheduled_end) }}</p>
      </div>

      <div v-if="!session.is_joinable" class="bg-amber-50 border border-amber-200 rounded-xl p-4 mt-4">
        <p class="text-sm text-amber-800">{{ session.not_joinable_reason }}</p>
      </div>
      <button v-else class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold mt-4" @click="onJoin">
        {{ t('liveSession.join') }}
      </button>

      <router-link v-if="!auth.isStudent" :to="`/teacher/live-sessions/${sessionId}/attendance`" class="block text-sm text-blue-600 hover:underline mt-4">
        {{ t('liveSession.viewAttendance') }}
      </router-link>

      <details v-if="!auth.isStudent" class="bg-white border border-gray-200 rounded-xl p-4 mt-4 text-sm">
        <summary class="cursor-pointer font-semibold text-gray-900">{{ t('liveSession.editSettings') }}</summary>
        <div class="mt-3 space-y-2">
          <input v-model="editTitle" :placeholder="t('teacher.courseDetail.titlePlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          <textarea v-model="editDescription" :placeholder="t('teacher.courseDetail.contentPlaceholder')" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"></textarea>
          <div class="flex gap-2">
            <div class="flex-1">
              <label class="block text-xs text-gray-500 mb-1">{{ t('liveSession.scheduledStart') }}</label>
              <input v-model="editStart" type="datetime-local" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div class="flex-1">
              <label class="block text-xs text-gray-500 mb-1">{{ t('liveSession.scheduledEnd') }}</label>
              <input v-model="editEnd" type="datetime-local" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">{{ t('liveSession.joinWindowLabel') }}</label>
            <input v-model.number="editWindow" type="number" min="0" class="w-24 border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onSaveSettings">{{ t('common.save') }}</button>
        </div>
      </details>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useLiveSessionsStore } from '@/stores/liveSessions'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const route = useRoute()
const sessionId = route.params.id
const liveSessions = useLiveSessionsStore()
const auth = useAuthStore()

const session = ref(null)
const inCall = ref(false)
const loadError = ref('')
let jitsiApi = null

const editTitle = ref('')
const editDescription = ref('')
const editStart = ref('')
const editEnd = ref('')
const editWindow = ref(10)

function formatDate(value) {
  return new Date(value).toLocaleString()
}

function toDatetimeLocal(value) {
  return value ? value.slice(0, 16) : ''
}

async function load() {
  try {
    session.value = await liveSessions.fetchLiveSession(sessionId)
    editTitle.value = session.value.title
    editDescription.value = session.value.description || ''
    editStart.value = toDatetimeLocal(session.value.scheduled_start)
    editEnd.value = toDatetimeLocal(session.value.scheduled_end)
    editWindow.value = session.value.join_window_minutes_before
  } catch (e) {
    loadError.value = e.response?.data?.detail || t('liveSession.loadError')
  }
}

async function onSaveSettings() {
  await liveSessions.updateLiveSession(sessionId, {
    title: editTitle.value,
    description: editDescription.value || null,
    scheduled_start: editStart.value || null,
    scheduled_end: editEnd.value || null,
    join_window_minutes_before: editWindow.value,
  })
  await load()
}

function loadExternalApi(baseUrl) {
  return new Promise((resolve, reject) => {
    if (window.JitsiMeetExternalAPI) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = `${baseUrl}/external_api.js`
    script.onload = resolve
    script.onerror = reject
    document.head.appendChild(script)
  })
}

async function onJoin() {
  const { jitsi_base_url, room_name, jwt } = await liveSessions.join(sessionId)
  await loadExternalApi(jitsi_base_url)
  inCall.value = true
  // Attendre que Vue ait réellement inséré #jitsi-container dans le DOM
  // avant de le chercher — sans ce nextTick, document.getElementById
  // renvoie null (la mise à jour du DOM après inCall=true est
  // asynchrone), parentNode vaut null, et le widget Jitsi échoue en
  // silence (aucune erreur visible, juste rien qui s'affiche).
  await nextTick()

  // external_api.js construit TOUJOURS une URL https://<domain>/<room>
  // pour le constructeur (domaine, options) à deux arguments — vérifié
  // empiriquement (chargement réel du script dans un DOM headless) : ni
  // une URL complète avec protocole, ni aucune option connue (noSsl,
  // scheme, protocol...) ne change ce comportement. Le serveur Jitsi doit
  // donc réellement servir du HTTPS (voir docker-compose.jitsi.yml —
  // certificat auto-signé généré par le conteneur, DISABLE_HTTPS retiré).
  const domain = new URL(jitsi_base_url).host
  jitsiApi = new window.JitsiMeetExternalAPI(domain, {
    roomName: room_name,
    jwt,
    parentNode: document.getElementById('jitsi-container'),
    configOverwrite: { prejoinPageEnabled: false },
  })
  jitsiApi.addEventListener('videoConferenceLeft', onLeave)
  jitsiApi.addEventListener('readyToClose', onLeave)
}

async function onLeave() {
  if (jitsiApi) {
    jitsiApi.dispose()
    jitsiApi = null
  }
  inCall.value = false
  try {
    await liveSessions.leave(sessionId)
  } finally {
    await load()
  }
}

onBeforeUnmount(() => {
  if (jitsiApi) {
    jitsiApi.dispose()
    jitsiApi = null
  }
})

onMounted(load)
</script>

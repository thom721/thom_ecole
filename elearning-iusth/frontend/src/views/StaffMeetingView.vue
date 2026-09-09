<template>
  <div v-if="meeting && inCall" class="fixed inset-0 z-50 bg-black">
    <div id="staff-meeting-jitsi-container" class="w-full h-full"></div>
  </div>

  <div v-else-if="loadError" class="max-w-3xl">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <div class="bg-amber-50 border border-amber-200 rounded-xl p-4">
      <p class="text-sm text-amber-800">{{ loadError }}</p>
    </div>
  </div>

  <div v-else-if="meeting" class="max-w-3xl">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>

    <h1 class="text-lg font-bold text-gray-900 mb-1">{{ meeting.title }}</h1>
    <p v-if="meeting.description" class="text-sm text-gray-500 mb-4">{{ meeting.description }}</p>

    <div class="bg-white border border-gray-200 rounded-xl p-4 space-y-2 text-sm text-gray-600 mb-4">
      <p v-if="meeting.scheduled_start">{{ t('liveSession.scheduledStart') }} : {{ formatDate(meeting.scheduled_start) }}</p>
      <p v-if="meeting.scheduled_end">{{ t('liveSession.scheduledEnd') }} : {{ formatDate(meeting.scheduled_end) }}</p>
    </div>

    <div class="flex gap-2 mb-4">
      <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onJoin">
        {{ t('liveSession.join') }}
      </button>
      <button v-if="canManage" class="border border-red-300 text-red-600 rounded-lg px-4 py-2 text-sm font-semibold" @click="onDelete">
        {{ t('common.remove') }}
      </button>
    </div>

    <details v-if="canManage" class="bg-white border border-gray-200 rounded-xl p-4">
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('liveSession.editSettings') }}</summary>
      <div class="mt-3 space-y-2">
        <input v-model="editTitle" :placeholder="t('common.title')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <textarea v-model="editDescription" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"></textarea>
        <div class="flex gap-2">
          <input v-model="editStart" type="datetime-local" class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          <input v-model="editEnd" type="datetime-local" class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        </div>
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onSaveSettings">{{ t('common.save') }}</button>
      </div>
    </details>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useStaffMeetingsStore } from '@/stores/staffMeetings'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const meetingId = route.params.id
const staffMeetings = useStaffMeetingsStore()
const auth = useAuthStore()

const meeting = ref(null)
const inCall = ref(false)
const loadError = ref('')
const editTitle = ref('')
const editDescription = ref('')
const editStart = ref('')
const editEnd = ref('')
let jitsiApi = null

const canManage = computed(() => meeting.value && (meeting.value.is_creator || auth.isAdmin))

function formatDate(value) {
  return new Date(value).toLocaleString()
}

function toLocalInput(value) {
  if (!value) return ''
  const d = new Date(value)
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
}

async function load() {
  try {
    meeting.value = await staffMeetings.fetchMeeting(meetingId)
    editTitle.value = meeting.value.title
    editDescription.value = meeting.value.description || ''
    editStart.value = toLocalInput(meeting.value.scheduled_start)
    editEnd.value = toLocalInput(meeting.value.scheduled_end)
  } catch (e) {
    loadError.value = e.response?.data?.detail || t('liveSession.loadError')
  }
}

async function onSaveSettings() {
  meeting.value = await staffMeetings.updateMeeting(meetingId, {
    title: editTitle.value, description: editDescription.value || null,
    scheduled_start: editStart.value || null, scheduled_end: editEnd.value || null,
  })
  editStart.value = toLocalInput(meeting.value.scheduled_start)
  editEnd.value = toLocalInput(meeting.value.scheduled_end)
}

async function onDelete() {
  await staffMeetings.deleteMeeting(meetingId)
  router.back()
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
  const { jitsi_base_url, room_name, jwt } = await staffMeetings.join(meetingId)
  await loadExternalApi(jitsi_base_url)
  inCall.value = true
  // Voir LiveSessionView.vue pour la raison de ce nextTick — sans lui,
  // #staff-meeting-jitsi-container n'existe pas encore dans le DOM.
  await nextTick()

  const domain = new URL(jitsi_base_url).host
  jitsiApi = new window.JitsiMeetExternalAPI(domain, {
    roomName: room_name,
    jwt,
    parentNode: document.getElementById('staff-meeting-jitsi-container'),
    configOverwrite: { prejoinPageEnabled: false },
  })
  jitsiApi.addEventListener('videoConferenceLeft', onLeave)
  jitsiApi.addEventListener('readyToClose', onLeave)
}

function onLeave() {
  if (jitsiApi) {
    jitsiApi.dispose()
    jitsiApi = null
  }
  inCall.value = false
}

onBeforeUnmount(() => {
  if (jitsiApi) {
    jitsiApi.dispose()
    jitsiApi = null
  }
})

onMounted(load)
</script>

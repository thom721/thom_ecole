<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-lg font-bold text-gray-900 mb-1">{{ t('staffMeeting.title') }}</h1>
    <p class="text-sm text-gray-500 mb-6">{{ t('staffMeeting.subtitle') }}</p>

    <details v-if="canCreate" class="bg-white border border-gray-200 rounded-xl p-4 mb-6" open>
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('staffMeeting.addMeeting') }}</summary>
      <div class="mt-3 space-y-2">
        <input v-model="newTitle" :placeholder="t('common.title')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <textarea v-model="newDescription" :placeholder="t('teacher.courseDetail.contentPlaceholder')" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"></textarea>
        <div class="flex gap-2">
          <input v-model="newStart" type="datetime-local" class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          <input v-model="newEnd" type="datetime-local" class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div class="border border-gray-200 rounded-lg p-2 max-h-48 overflow-y-auto">
          <label v-for="u in eligibleUsers" :key="u.id" class="flex items-center gap-2 text-sm py-1">
            <input type="checkbox" :value="u.id" v-model="selectedInviteeIds" />
            <span>{{ u.first_name }} {{ u.last_name }} <span class="text-gray-400">({{ u.system_role }})</span></span>
          </label>
        </div>
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-50"
          :disabled="creating" @click="onCreate">{{ creating ? t('common.loading') : t('common.create') }}</button>
      </div>
    </details>

    <div class="bg-white border border-gray-200 rounded-xl p-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('staffMeeting.mine') }}</h2>
      <p v-if="!meetings.length" class="text-sm text-gray-500">{{ t('staffMeeting.none') }}</p>
      <router-link v-for="m in meetings" :key="m.id" :to="`${basePath}/staff-meetings/${m.id}`"
        class="block border-t border-gray-100 first:border-t-0 py-2 no-underline text-inherit hover:bg-gray-50">
        <p class="text-sm font-medium">{{ m.title }} <span v-if="m.is_creator" class="text-xs text-gray-400">({{ t('staffMeeting.youCreated') }})</span></p>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStaffMeetingsStore } from '@/stores/staffMeetings'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const staffMeetings = useStaffMeetingsStore()
const auth = useAuthStore()
const basePath = computed(() => (auth.isAdmin ? '/admin' : '/teacher'))

const canCreate = ref(false)
const eligibleUsers = ref([])
const meetings = ref([])
const newTitle = ref('')
const newDescription = ref('')
const newStart = ref('')
const newEnd = ref('')
const selectedInviteeIds = ref([])
const creating = ref(false)

async function load() {
  meetings.value = await staffMeetings.fetchMine()
  try {
    eligibleUsers.value = await staffMeetings.fetchEligibleUsers()
    canCreate.value = true
  } catch {
    canCreate.value = false
  }
}

async function onCreate() {
  if (!newTitle.value || creating.value) return
  creating.value = true
  try {
    await staffMeetings.createMeeting({
      title: newTitle.value, description: newDescription.value || null,
      scheduled_start: newStart.value || null, scheduled_end: newEnd.value || null,
      invitee_user_ids: selectedInviteeIds.value,
    })
    newTitle.value = ''
    newDescription.value = ''
    newStart.value = ''
    newEnd.value = ''
    selectedInviteeIds.value = []
    await load()
  } finally {
    creating.value = false
  }
}

onMounted(load)
</script>

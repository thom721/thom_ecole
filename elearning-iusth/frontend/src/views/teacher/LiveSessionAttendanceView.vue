<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('liveSession.attendanceTitle') }}</h1>

    <table class="w-full text-sm bg-white border border-gray-200 rounded-xl overflow-hidden">
      <thead class="bg-gray-50 text-left text-xs text-gray-500">
        <tr>
          <th class="px-3 py-2">{{ t('liveSession.colStudent') }}</th>
          <th class="px-3 py-2">{{ t('liveSession.colFirstJoined') }}</th>
          <th class="px-3 py-2">{{ t('liveSession.colLastLeft') }}</th>
          <th class="px-3 py-2">{{ t('liveSession.colJoinCount') }}</th>
          <th class="px-3 py-2">{{ t('liveSession.colStatus') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in attendance" :key="row.student_id" class="border-t border-gray-100">
          <td class="px-3 py-2">{{ row.student_name }}</td>
          <td class="px-3 py-2 text-gray-500">{{ new Date(row.first_joined_at).toLocaleString() }}</td>
          <td class="px-3 py-2 text-gray-500">{{ row.last_left_at ? new Date(row.last_left_at).toLocaleString() : '—' }}</td>
          <td class="px-3 py-2">{{ row.join_count }}</td>
          <td class="px-3 py-2">
            <span v-if="row.is_currently_in_session" class="text-green-700">{{ t('liveSession.statusInSession') }}</span>
            <span v-else class="text-gray-400">{{ t('liveSession.statusLeft') }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useLiveSessionsStore } from '@/stores/liveSessions'

const { t } = useI18n()
const route = useRoute()
const liveSessions = useLiveSessionsStore()
const attendance = ref([])

onMounted(async () => {
  attendance.value = await liveSessions.fetchAttendance(route.params.id)
})
</script>

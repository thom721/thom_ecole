<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('teacher.accessLog.title') }}</h1>

    <h2 class="font-semibold text-gray-900 mb-2">{{ t('teacher.accessLog.byContent') }}</h2>
    <table class="w-full text-sm bg-white border border-gray-200 rounded-xl overflow-hidden mb-6">
      <thead class="bg-gray-50 text-left text-xs text-gray-500">
        <tr>
          <th class="px-3 py-2">{{ t('teacher.accessLog.colContent') }}</th>
          <th class="px-3 py-2">{{ t('teacher.accessLog.colType') }}</th>
          <th class="px-3 py-2">{{ t('teacher.accessLog.colViews') }}</th>
          <th class="px-3 py-2">{{ t('teacher.accessLog.colUniqueStudents') }}</th>
          <th class="px-3 py-2">{{ t('teacher.accessLog.colLastAccess') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in summary" :key="r.item_type + (r.item_id || '')" class="border-t border-gray-100">
          <td class="px-3 py-2">{{ r.title }}</td>
          <td class="px-3 py-2 text-gray-500">{{ r.item_type }}</td>
          <td class="px-3 py-2">{{ r.view_count }}</td>
          <td class="px-3 py-2">{{ r.unique_student_count }}</td>
          <td class="px-3 py-2 text-gray-500">{{ new Date(r.last_accessed_at).toLocaleString(locale === 'en' ? 'en-US' : 'fr-FR') }}</td>
        </tr>
      </tbody>
    </table>

    <h2 class="font-semibold text-gray-900 mb-2">{{ t('teacher.accessLog.byStudent') }}</h2>
    <table class="w-full text-sm bg-white border border-gray-200 rounded-xl overflow-hidden">
      <thead class="bg-gray-50 text-left text-xs text-gray-500">
        <tr>
          <th class="px-3 py-2">{{ t('teacher.accessLog.colStudent') }}</th>
          <th class="px-3 py-2">{{ t('teacher.accessLog.colTotalViews') }}</th>
          <th class="px-3 py-2">{{ t('teacher.accessLog.colLastAccess') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="s in students" :key="s.student_id" class="border-t border-gray-100">
          <td class="px-3 py-2">{{ s.student_name }}</td>
          <td class="px-3 py-2">{{ s.total_views }}</td>
          <td class="px-3 py-2 text-gray-500">{{ new Date(s.last_accessed_at).toLocaleString(locale === 'en' ? 'en-US' : 'fr-FR') }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAccessLogStore } from '@/stores/accessLog'

const { t, locale } = useI18n()
const route = useRoute()
const accessLog = useAccessLogStore()
const summary = ref([])
const students = ref([])

onMounted(async () => {
  summary.value = await accessLog.fetchSummary(route.params.id)
  students.value = await accessLog.fetchStudentSummary(route.params.id)
})
</script>

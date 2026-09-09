<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('teacher.completionReport.title') }}</h1>

    <table class="w-full text-sm bg-white border border-gray-200 rounded-xl overflow-hidden">
      <thead class="bg-gray-50 text-left text-xs text-gray-500">
        <tr>
          <th class="px-3 py-2">{{ t('teacher.completionReport.student') }}</th>
          <th class="px-3 py-2">{{ t('teacher.completionReport.progress') }}</th>
          <th class="px-3 py-2">{{ t('teacher.completionReport.completedCount') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.student_id" class="border-t border-gray-100">
          <td class="px-3 py-2">{{ row.student_name }}</td>
          <td class="px-3 py-2">
            <div class="flex items-center gap-2">
              <div class="w-32 h-2 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full bg-gray-900" :style="{ width: row.percent + '%' }"></div>
              </div>
              <span>{{ row.percent.toFixed(0) }}%</span>
            </div>
          </td>
          <td class="px-3 py-2 text-gray-500">{{ row.completed_count }} / {{ row.total_count }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCompletionStore } from '@/stores/completion'

const { t } = useI18n()
const route = useRoute()
const completion = useCompletionStore()
const rows = ref([])

onMounted(async () => {
  rows.value = await completion.fetchReport(route.params.id)
})
</script>

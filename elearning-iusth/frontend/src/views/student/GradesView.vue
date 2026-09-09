<template>
  <div v-if="row" class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('student.grades.title') }}</h1>

    <div class="bg-gray-900 text-white rounded-xl p-4 mb-6 text-center">
      <p class="text-xs uppercase tracking-wide text-gray-300">{{ t('student.grades.finalGrade') }}</p>
      <p class="text-3xl font-bold">
        <template v-if="row.final_percent !== null">
          {{ Number(row.final_percent).toFixed(1) }}% <span v-if="row.final_letter" class="text-gray-300 font-normal">({{ row.final_letter }})</span>
        </template>
        <template v-else>{{ t('common.none') }}</template>
      </p>
    </div>

    <div v-for="group in groups" :key="group.id ?? 'uncat'" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <div class="flex items-center justify-between mb-3">
        <h2 class="font-semibold text-gray-900">{{ group.name }}</h2>
        <span class="text-sm font-medium text-gray-700">{{ subtotalLabel(group.id) }}</span>
      </div>
      <div v-for="item in group.items" :key="item.id" class="flex items-center justify-between text-sm py-1.5 border-t border-gray-100">
        <span class="text-gray-600">{{ item.title }}</span>
        <span class="font-medium">{{ entryLabel(item) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useGradesStore } from '@/stores/grades'

const { t } = useI18n()
const route = useRoute()
const courseId = route.params.id
const grades = useGradesStore()

const report = ref(null)
const row = computed(() => report.value?.rows?.[0] ?? null)

const groups = computed(() => {
  if (!report.value) return []
  const byCategory = {}
  const uncategorized = []
  for (const item of report.value.items) {
    if (item.grade_category_id) {
      byCategory[item.grade_category_id] = byCategory[item.grade_category_id] || []
      byCategory[item.grade_category_id].push(item)
    } else {
      uncategorized.push(item)
    }
  }
  const result = report.value.categories.map((c) => ({ id: c.id, name: c.name, items: byCategory[c.id] || [] }))
  if (uncategorized.length) result.push({ id: null, name: t('common.uncategorized'), items: uncategorized })
  return result
})

function entryLabel(item) {
  const entry = row.value.entries[item.id]
  if (!entry || !entry.is_graded) return t('common.none')
  if (entry.label) return entry.label
  return `${entry.earned}/${entry.possible}`
}

function subtotalLabel(categoryId) {
  const subtotal = categoryId ? row.value.category_subtotals[categoryId] : row.value.uncategorized_subtotal
  if (!subtotal) return t('common.none')
  return `${Number(subtotal.percent).toFixed(1)}%`
}

onMounted(async () => {
  report.value = await grades.fetchMyGrades(courseId)
})
</script>

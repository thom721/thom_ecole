<template>
  <div v-if="report">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('teacher.gradebook.title') }}</h1>

    <div class="overflow-x-auto border border-gray-200 rounded-xl mb-6">
      <table class="text-sm border-collapse">
        <thead>
          <tr class="bg-gray-50">
            <th class="sticky left-0 bg-gray-50 px-3 py-2 text-left border-b border-gray-200">{{ t('teacher.gradebook.student') }}</th>
            <template v-for="group in groups" :key="group.id ?? 'uncat'">
              <th :colspan="group.items.length + 1" class="px-3 py-1 text-center border-b border-l border-gray-200 font-semibold">
                {{ group.name }} <span v-if="group.weight_percent !== null" class="text-gray-400 font-normal">({{ group.weight_percent }}%)</span>
                <span v-if="group.evaluation_phase === 'intra'" class="text-blue-500 font-normal">· {{ t('teacher.gradebook.phaseIntra') }}</span>
                <span v-if="group.evaluation_phase === 'finale'" class="text-blue-500 font-normal">· {{ t('teacher.gradebook.phaseFinale') }}</span>
              </th>
            </template>
            <th class="sticky right-0 bg-gray-50 px-3 py-2 text-center border-b border-l border-gray-200 font-semibold">{{ t('teacher.gradebook.finalGrade') }}</th>
          </tr>
          <tr class="bg-gray-50 text-xs text-gray-500">
            <th class="sticky left-0 bg-gray-50 px-3 py-1 border-b border-gray-200"></th>
            <template v-for="group in groups" :key="'h-' + (group.id ?? 'uncat')">
              <th v-for="item in group.items" :key="item.id" class="px-2 py-1 border-b border-l border-gray-200 font-normal whitespace-nowrap">
                {{ item.title }}<br />
                <span class="text-gray-400">{{ item.max_points ?? t('teacher.gradebook.variable') }} {{ t('common.pts') }}</span>
              </th>
              <th class="px-2 py-1 border-b border-l border-gray-200 font-medium">{{ t('teacher.gradebook.subtotal') }}</th>
            </template>
            <th class="sticky right-0 bg-gray-50 px-3 py-1 border-b border-l border-gray-200"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in report.rows" :key="row.student_id" class="border-t border-gray-100">
            <td class="sticky left-0 bg-white px-3 py-2 whitespace-nowrap">{{ row.student_name }}</td>
            <template v-for="group in groups" :key="'r-' + row.student_id + '-' + (group.id ?? 'uncat')">
              <td v-for="item in group.items" :key="item.id" class="px-2 py-2 border-l border-gray-100 text-center">
                <template v-if="item.kind === 'manual'">
                  <select v-if="item.scale_id" class="w-24 border border-gray-300 rounded px-1 py-0.5 text-center text-xs"
                    :value="row.entries[item.id]?.earned"
                    @change="onManualGrade(item.id, row.student_id, $event.target.value)">
                    <option value="">…</option>
                    <option v-for="lvl in scaleFor(item.scale_id)?.levels" :key="lvl.id" :value="lvl.rank">{{ lvl.label }}</option>
                  </select>
                  <input v-else type="number" class="w-16 border border-gray-300 rounded px-1 py-0.5 text-center"
                    :value="row.entries[item.id]?.earned"
                    @change="onManualGrade(item.id, row.student_id, $event.target.value)" />
                </template>
                <template v-else>
                  <router-link v-if="item.kind === 'assignment'" :to="`/teacher/assignments/${item.assignment_id}`" class="text-gray-700 no-underline hover:underline">
                    {{ entryLabel(row, item) }}
                  </router-link>
                  <router-link v-else-if="item.kind === 'quiz'" :to="`/teacher/quizzes/${item.quiz_id}/attempts`" class="text-gray-700 no-underline hover:underline">
                    {{ entryLabel(row, item) }}
                  </router-link>
                </template>
              </td>
              <td class="px-2 py-2 border-l border-gray-100 text-center font-medium">
                {{ subtotalLabel(row, group.id) }}
              </td>
            </template>
            <td class="sticky right-0 bg-white px-3 py-2 border-l border-gray-200 text-center font-bold">
              <template v-if="row.final_percent !== null">
                {{ Number(row.final_percent).toFixed(1) }}% <span v-if="row.final_letter" class="text-gray-400 font-normal">({{ row.final_letter }})</span>
              </template>
              <template v-else>{{ t('common.none') }}</template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <details class="bg-white border border-gray-200 rounded-xl p-4">
        <summary class="cursor-pointer font-semibold text-gray-900">{{ t('teacher.gradebook.addCategory') }}</summary>
        <div class="mt-3 flex gap-2">
          <input v-model="newCategoryName" :placeholder="t('teacher.gradebook.categoryNamePlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1" />
          <input v-model="newCategoryWeight" type="number" :placeholder="t('teacher.gradebook.categoryWeightPlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm w-28" />
          <select v-model="newCategoryPhase" class="border border-gray-300 rounded-lg px-2 py-2 text-sm w-32">
            <option value="">{{ t('teacher.gradebook.phaseNone') }}</option>
            <option value="intra">{{ t('teacher.gradebook.phaseIntra') }}</option>
            <option value="finale">{{ t('teacher.gradebook.phaseFinale') }}</option>
          </select>
          <button class="bg-gray-900 text-white rounded-lg px-3 py-2 text-sm font-semibold" @click="onAddCategory">{{ t('common.add') }}</button>
        </div>
      </details>

      <details class="bg-white border border-gray-200 rounded-xl p-4">
        <summary class="cursor-pointer font-semibold text-gray-900">{{ t('teacher.gradebook.addManualGrade') }}</summary>
        <div class="mt-3 space-y-2">
          <input v-model="newItemTitle" :placeholder="t('teacher.gradebook.itemTitlePlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          <div class="flex gap-2">
            <input v-model="newItemMaxPoints" type="number" :placeholder="t('teacher.gradebook.maxPointsPlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1" />
            <select v-model="newItemCategoryId" class="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1">
              <option value="">{{ t('common.uncategorized') }}</option>
              <option v-for="c in report.categories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <select v-model="newItemScaleId" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="">{{ t('scales.noScale') }}</option>
            <option v-for="s in scales" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
          <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onAddItem">{{ t('common.create') }}</button>
        </div>
      </details>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useGradesStore } from '@/stores/grades'
import { useScalesStore } from '@/stores/scales'

const { t } = useI18n()
const route = useRoute()
const courseId = route.params.id
const grades = useGradesStore()
const scalesStore = useScalesStore()

const report = ref(null)
const scales = ref([])
const newCategoryName = ref('')
const newCategoryWeight = ref('')
const newCategoryPhase = ref('')
const newItemTitle = ref('')
const newItemMaxPoints = ref('')
const newItemCategoryId = ref('')
const newItemScaleId = ref('')

function scaleFor(scaleId) {
  return scales.value.find((s) => s.id === scaleId)
}

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
  const result = report.value.categories.map((c) => ({
    id: c.id, name: c.name, weight_percent: c.weight_percent, evaluation_phase: c.evaluation_phase, items: byCategory[c.id] || [],
  }))
  if (uncategorized.length) result.push({ id: null, name: t('common.uncategorized'), weight_percent: null, items: uncategorized })
  return result
})

function entryLabel(row, item) {
  const entry = row.entries[item.id]
  if (!entry || !entry.is_graded) return t('common.none')
  if (entry.label) return entry.label
  return `${entry.earned}/${entry.possible}`
}

function subtotalLabel(row, categoryId) {
  const subtotal = categoryId ? row.category_subtotals[categoryId] : row.uncategorized_subtotal
  if (!subtotal) return t('common.none')
  return `${Number(subtotal.percent).toFixed(1)}%`
}

async function load() {
  report.value = await grades.fetchGradeReport(courseId)
  scales.value = await scalesStore.fetchScales(courseId)
}

async function onManualGrade(itemId, studentId, value) {
  if (value === '') return
  await grades.setManualGrade(itemId, studentId, { points: Number(value) })
  await load()
}

async function onAddCategory() {
  if (!newCategoryName.value || !newCategoryWeight.value) return
  await grades.createGradeCategory(courseId, {
    name: newCategoryName.value,
    weight_percent: Number(newCategoryWeight.value),
    evaluation_phase: newCategoryPhase.value || null,
  })
  newCategoryName.value = ''
  newCategoryWeight.value = ''
  newCategoryPhase.value = ''
  await load()
}

async function onAddItem() {
  if (!newItemTitle.value || !newItemMaxPoints.value) return
  await grades.createGradeItem(courseId, {
    title: newItemTitle.value, max_points: Number(newItemMaxPoints.value),
    grade_category_id: newItemCategoryId.value || null,
    scale_id: newItemScaleId.value || null,
  })
  newItemTitle.value = ''
  newItemMaxPoints.value = ''
  newItemCategoryId.value = ''
  newItemScaleId.value = ''
  await load()
}

onMounted(load)
</script>

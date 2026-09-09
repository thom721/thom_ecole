<template>
  <div class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ title || itemType }}</h1>

    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-2">{{ t('access.completionTitle') }}</h2>
      <select v-model="completionMode" @change="onSaveMode" class="border border-gray-300 rounded-lg px-3 py-2 text-sm">
        <option value="none">{{ t('access.modeNone') }}</option>
        <option value="manual">{{ t('access.modeManual') }}</option>
        <option value="automatic">{{ t('access.modeAutomatic') }}</option>
      </select>
      <p class="text-xs text-gray-500 mt-2">{{ t('access.automaticHint', { type: itemType }) }}</p>
    </div>

    <div class="bg-white border border-gray-200 rounded-xl p-4">
      <h2 class="font-semibold text-gray-900 mb-2">{{ t('access.conditionsTitle') }}</h2>
      <p v-if="!conditions.length" class="text-sm text-gray-500 mb-3">{{ t('access.noConditions') }}</p>
      <ul class="text-sm mb-3">
        <li v-for="c in conditions" :key="c.id" class="flex items-center justify-between py-1 border-t border-gray-100 first:border-t-0">
          <span>{{ describeCondition(c) }} <span class="text-gray-400">({{ c.logic }})</span></span>
          <button class="text-red-600 text-xs" @click="onDeleteCondition(c.id)">{{ t('common.remove') }}</button>
        </li>
      </ul>

      <details class="text-sm">
        <summary class="cursor-pointer text-gray-600">{{ t('access.addCondition') }}</summary>
        <div class="mt-2 space-y-2">
          <select v-model="newCondition.condition_type" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm">
            <option value="date">{{ t('access.typeDate') }}</option>
            <option value="grade">{{ t('access.typeGrade') }}</option>
            <option value="activity_completion">{{ t('access.typeCompletion') }}</option>
            <option value="group">{{ t('access.typeGroup') }}</option>
          </select>
          <select v-model="newCondition.logic" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm">
            <option value="and">{{ t('access.logicAnd') }}</option>
            <option value="or">{{ t('access.logicOr') }}</option>
          </select>

          <div v-if="newCondition.condition_type === 'date'" class="flex gap-2">
            <input v-model="newCondition.available_from" type="datetime-local" class="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm" :placeholder="t('access.fromLabel')" />
            <input v-model="newCondition.available_until" type="datetime-local" class="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm" :placeholder="t('access.untilLabel')" />
          </div>

          <div v-else-if="newCondition.condition_type === 'grade'" class="flex gap-2">
            <select v-model="newCondition.grade_item_id" class="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm">
              <option value="">{{ t('access.chooseGradeItem') }}</option>
              <option v-for="gi in gradeItems" :key="gi.id" :value="gi.id">{{ gi.title }}</option>
            </select>
            <input v-model="newCondition.min_percent" type="number" min="0" max="100" class="w-24 border border-gray-300 rounded-lg px-2 py-1 text-sm" placeholder="%" />
          </div>

          <div v-else-if="newCondition.condition_type === 'activity_completion'" class="flex gap-2">
            <select v-model="newCondition.required_item_type" class="w-32 border border-gray-300 rounded-lg px-2 py-1 text-sm">
              <option value="resource">{{ t('common.section') }} — 📎</option>
              <option value="assignment">📄</option>
              <option value="quiz">📝</option>
              <option value="forum">💬</option>
              <option value="choice">🗳️</option>
            </select>
            <input v-model="newCondition.required_item_id" :placeholder="t('access.itemIdPlaceholder')" class="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          </div>

          <select v-else-if="newCondition.condition_type === 'group'" v-model="newCondition.group_id" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm">
            <option value="">{{ t('access.chooseGroup') }}</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>

          <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onAddCondition">{{ t('common.add') }}</button>
          <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
        </div>
      </details>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCompletionStore } from '@/stores/completion'
import { useAccessConditionsStore } from '@/stores/accessConditions'
import { useGroupsStore } from '@/stores/groups'
import axios from 'axios'

const { t } = useI18n()
const route = useRoute()
const completion = useCompletionStore()
const accessConditions = useAccessConditionsStore()
const groupsStore = useGroupsStore()

const itemType = route.params.itemType
const itemId = route.params.itemId
const title = computed(() => route.query.title || '')

const completionMode = ref('none')
const conditions = ref([])
const groups = ref([])
const gradeItems = ref([])
const error = ref('')

const newCondition = reactive({
  condition_type: 'date', logic: 'and',
  available_from: '', available_until: '',
  grade_item_id: '', min_percent: '',
  required_item_type: 'resource', required_item_id: '',
  group_id: '',
})

function describeCondition(c) {
  if (c.condition_type === 'date') {
    const parts = []
    if (c.available_from) parts.push(t('access.fromLabel') + ' ' + new Date(c.available_from).toLocaleString())
    if (c.available_until) parts.push(t('access.untilLabel') + ' ' + new Date(c.available_until).toLocaleString())
    return parts.join(', ')
  }
  if (c.condition_type === 'grade') return `${t('access.typeGrade')} ≥ ${c.min_percent}%`
  if (c.condition_type === 'activity_completion') return `${t('access.typeCompletion')}: ${c.required_item_type}/${c.required_item_id}`
  if (c.condition_type === 'group') {
    const g = groups.value.find((g) => g.id === c.group_id)
    return `${t('access.typeGroup')}: ${g?.name || c.group_id}`
  }
  return c.condition_type
}

async function load() {
  const config = await completion.fetchConfig(itemType, itemId)
  completionMode.value = config.mode
  conditions.value = await accessConditions.fetchConditions(itemType, itemId)
}

async function onSaveMode() {
  await completion.updateConfig(itemType, itemId, completionMode.value)
}

async function onAddCondition() {
  error.value = ''
  try {
    const payload = { condition_type: newCondition.condition_type, logic: newCondition.logic }
    if (newCondition.condition_type === 'date') {
      payload.available_from = newCondition.available_from || null
      payload.available_until = newCondition.available_until || null
    } else if (newCondition.condition_type === 'grade') {
      payload.grade_item_id = newCondition.grade_item_id
      payload.min_percent = Number(newCondition.min_percent)
    } else if (newCondition.condition_type === 'activity_completion') {
      payload.required_item_type = newCondition.required_item_type
      payload.required_item_id = newCondition.required_item_id
    } else if (newCondition.condition_type === 'group') {
      payload.group_id = newCondition.group_id
    }
    await accessConditions.createCondition(itemType, itemId, payload)
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  }
}

async function onDeleteCondition(id) {
  await accessConditions.deleteCondition(id)
  await load()
}

onMounted(async () => {
  await load()
  try {
    const { data: course } = await axios.get(`/courses/${route.query.courseId}`)
    groups.value = await groupsStore.fetchGroups(course.id)
    const report = await axios.get(`/courses/${course.id}/grades/report`)
    gradeItems.value = report.data.items
  } catch {
    // courseId absent de la query — listes groupes/notes non pré-remplies,
    // le formulaire reste utilisable en saisissant les identifiants directement.
  }
})
</script>

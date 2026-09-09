<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('badges.title') }}</h1>

    <div v-for="b in badges" :key="b.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <div class="flex items-center justify-between mb-2">
        <p class="font-medium text-gray-900">{{ b.image_emoji }} {{ b.name }} <span v-if="!b.course_id" class="text-xs text-gray-400">({{ t('scales.siteWide') }})</span></p>
        <span class="text-xs px-2 py-0.5 rounded-full" :class="b.status === 'active' ? 'bg-green-100 text-green-700' : b.status === 'draft' ? 'bg-gray-100 text-gray-600' : 'bg-amber-100 text-amber-700'">
          {{ t(`badges.status.${b.status}`) }}
        </span>
      </div>
      <p v-if="b.description" class="text-sm text-gray-500 mb-2">{{ b.description }}</p>

      <details class="text-sm mb-2">
        <summary class="cursor-pointer text-gray-600">{{ t('badges.editCriteria') }}</summary>
        <div class="mt-2 space-y-2">
          <select v-model="editing[b.id].criteria_logic" class="border border-gray-300 rounded-lg px-2 py-1 text-xs">
            <option value="and">{{ t('access.logicAnd') }}</option>
            <option value="or">{{ t('access.logicOr') }}</option>
          </select>
          <div v-for="(c, i) in editing[b.id].criteria" :key="i" class="border border-gray-200 rounded-lg p-2">
            <select v-model="c.criteria_type" class="border border-gray-300 rounded-lg px-2 py-1 text-xs mb-1">
              <option value="activity">{{ t('badges.criteriaType.activity') }}</option>
              <option value="course" v-if="b.course_id">{{ t('badges.criteriaType.course') }}</option>
              <option value="grade" v-if="b.course_id">{{ t('badges.criteriaType.grade') }}</option>
              <option value="cohort">{{ t('badges.criteriaType.cohort') }}</option>
            </select>
            <div v-if="c.criteria_type === 'activity'" class="flex gap-2">
              <select v-model="c.required_item_type" class="border border-gray-300 rounded-lg px-2 py-1 text-xs">
                <option value="resource">{{ t('badges.itemType.resource') }}</option>
                <option value="assignment">{{ t('badges.itemType.assignment') }}</option>
                <option value="quiz">{{ t('badges.itemType.quiz') }}</option>
                <option value="lesson">{{ t('badges.itemType.lesson') }}</option>
                <option value="workshop">{{ t('badges.itemType.workshop') }}</option>
              </select>
              <input v-model="c.required_item_id" :placeholder="t('badges.itemIdPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-xs flex-1" />
            </div>
            <input v-else-if="c.criteria_type === 'grade'" v-model="c.min_percent" type="number" :placeholder="t('badges.minPercentPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-xs w-32" />
            <input v-else-if="c.criteria_type === 'cohort'" v-model="c.cohort_id" :placeholder="t('badges.cohortIdPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-xs w-full" />
            <button class="text-red-600 text-xs mt-1" @click="editing[b.id].criteria.splice(i, 1)">{{ t('common.remove') }}</button>
          </div>
          <button class="text-xs text-blue-600 block" @click="editing[b.id].criteria.push({ criteria_type: 'activity', required_item_type: 'assignment', required_item_id: '', min_percent: '', cohort_id: '' })">{{ t('badges.addCriterion') }}</button>
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onSaveCriteria(b)">{{ t('common.save') }}</button>
          <p v-if="criteriaError[b.id]" class="text-xs text-red-600">{{ criteriaError[b.id] }}</p>
        </div>
      </details>

      <div class="flex gap-2 items-center">
        <input v-model="awardEmail[b.id]" :placeholder="t('badges.awardEmailPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
        <button class="bg-gray-100 rounded-lg px-3 py-1 text-sm" @click="onAward(b.id)">{{ t('badges.awardManually') }}</button>
        <button class="text-blue-600 text-sm" @click="onReevaluate">{{ t('badges.reevaluate') }}</button>
        <button class="text-red-600 text-xs" @click="onDelete(b.id)">{{ t('common.remove') }}</button>
      </div>
      <p v-if="awardError[b.id]" class="text-xs text-red-600 mt-1">{{ awardError[b.id] }}</p>
    </div>

    <details class="bg-white border border-gray-200 rounded-xl p-4" open>
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('badges.addBadge') }}</summary>
      <div class="mt-3 space-y-2">
        <input v-model="newBadge.name" :placeholder="t('common.title')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <input v-model="newBadge.description" :placeholder="t('badges.descriptionPlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <div class="flex gap-2">
          <input v-model="newBadge.image_emoji" :placeholder="t('badges.emojiPlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm w-20" />
          <select v-model="newBadge.status" class="border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="draft">{{ t('badges.status.draft') }}</option>
            <option value="active">{{ t('badges.status.active') }}</option>
          </select>
        </div>
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onCreate">{{ t('common.create') }}</button>
      </div>
    </details>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useBadgesStore } from '@/stores/badges'
import axios from 'axios'

const { t } = useI18n()
const route = useRoute()
const courseId = route.params.id
const badgesStore = useBadgesStore()

const badges = ref([])
const editing = reactive({})
const criteriaError = reactive({})
const awardEmail = reactive({})
const awardError = reactive({})
const newBadge = reactive({ name: '', description: '', image_emoji: '🏅', status: 'draft' })

async function load() {
  badges.value = await badgesStore.fetchCourseBadges(courseId)
  for (const b of badges.value) {
    const detail = await badgesStore.fetchBadge(b.id)
    editing[b.id] = {
      criteria_logic: b.criteria_logic,
      criteria: detail.criteria.map((c) => ({ ...c, min_percent: c.min_percent ?? '', required_item_id: c.required_item_id ?? '', cohort_id: c.cohort_id ?? '' })),
    }
  }
}

async function onCreate() {
  if (!newBadge.name) return
  await badgesStore.createCourseBadge(courseId, { ...newBadge })
  newBadge.name = ''
  newBadge.description = ''
  newBadge.image_emoji = '🏅'
  newBadge.status = 'draft'
  await load()
}

async function onSaveCriteria(badge) {
  criteriaError[badge.id] = ''
  const payload = editing[badge.id].criteria.map((c) => ({
    criteria_type: c.criteria_type,
    required_item_type: c.criteria_type === 'activity' ? c.required_item_type : null,
    required_item_id: c.criteria_type === 'activity' ? c.required_item_id : null,
    min_percent: c.criteria_type === 'grade' ? Number(c.min_percent) : null,
    cohort_id: c.criteria_type === 'cohort' ? c.cohort_id : null,
  }))
  try {
    if (editing[badge.id].criteria_logic !== badge.criteria_logic) {
      await badgesStore.updateBadge(badge.id, { criteria_logic: editing[badge.id].criteria_logic })
    }
    await badgesStore.replaceCriteria(badge.id, payload)
    await load()
  } catch (e) {
    criteriaError[badge.id] = e.response?.data?.detail || t('common.error')
  }
}

async function onAward(badgeId) {
  awardError[badgeId] = ''
  if (!awardEmail[badgeId]) return
  try {
    const { data: user } = await axios.get('/users/lookup', { params: { email: awardEmail[badgeId] } })
    await badgesStore.awardBadge(badgeId, user.id)
    awardEmail[badgeId] = ''
  } catch (e) {
    awardError[badgeId] = e.response?.data?.detail || t('common.error')
  }
}

async function onReevaluate() {
  await badgesStore.reevaluate(courseId)
}

async function onDelete(badgeId) {
  try {
    await badgesStore.deleteBadge(badgeId)
    await load()
  } catch (e) {
    criteriaError[badgeId] = e.response?.data?.detail || t('common.error')
  }
}

onMounted(load)
</script>

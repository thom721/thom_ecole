<template>
  <div>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('competency.plansTitle') }}</h1>

    <div v-for="p in plans" :key="p.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <div class="flex items-center justify-between mb-2">
        <button class="font-medium text-gray-900 text-left" @click="onOpen(p.id)">{{ p.name }}</button>
        <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">{{ t(`competency.planStatus.${p.status}`) }}</span>
      </div>
      <p v-if="p.description" class="text-sm text-gray-500 mb-2">{{ p.description }}</p>

      <div v-if="detail && detail.id === p.id" class="border-t border-gray-100 pt-2 mt-2">
        <select v-model="statusEdit" class="border border-gray-300 rounded-lg px-2 py-1 text-xs mb-2" @change="onUpdateStatus(p.id)">
          <option value="draft">{{ t('competency.planStatus.draft') }}</option>
          <option value="active">{{ t('competency.planStatus.active') }}</option>
          <option value="complete">{{ t('competency.planStatus.complete') }}</option>
          <option value="waiting_for_review">{{ t('competency.planStatus.waiting_for_review') }}</option>
          <option value="in_review">{{ t('competency.planStatus.in_review') }}</option>
        </select>
        <ul class="text-sm mb-2">
          <li v-for="c in detail.competencies" :key="c.id" class="flex items-center justify-between py-1 border-t border-gray-100 first:border-t-0">
            <span>{{ c.competency_name }} <span v-if="c.proficiency !== null" class="text-xs" :class="c.proficiency ? 'text-green-700' : 'text-gray-400'">({{ c.proficiency ? '✓' : '✗' }})</span></span>
            <button class="text-red-600 text-xs" @click="onRemoveCompetency(c.id, p.id)">{{ t('common.remove') }}</button>
          </li>
        </ul>
        <div class="flex gap-2">
          <input v-model="newCompetencyId" :placeholder="t('competency.competencyIdPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-xs flex-1" />
          <button class="bg-gray-100 rounded-lg px-2 py-1 text-xs" @click="onAddCompetency(p.id)">{{ t('common.add') }}</button>
        </div>
      </div>
    </div>

    <details class="bg-white border border-gray-200 rounded-xl p-4" open>
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('competency.addPlan') }}</summary>
      <div class="mt-3 space-y-2">
        <input v-model="newPlan.name" :placeholder="t('common.title')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <input v-model="newPlan.description" :placeholder="t('badges.descriptionPlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onCreatePlan">{{ t('common.create') }}</button>
      </div>
    </details>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCompetenciesStore } from '@/stores/competencies'

const { t } = useI18n()
const store = useCompetenciesStore()

const plans = ref([])
const detail = ref(null)
const statusEdit = ref('draft')
const newCompetencyId = ref('')
const newPlan = reactive({ name: '', description: '' })

async function load() {
  plans.value = await store.fetchMyPlans()
}

async function onCreatePlan() {
  if (!newPlan.name) return
  await store.createPlan({ name: newPlan.name, description: newPlan.description || null })
  newPlan.name = ''
  newPlan.description = ''
  await load()
}

async function onOpen(planId) {
  detail.value = await store.fetchPlan(planId)
  statusEdit.value = detail.value.status
}

async function onUpdateStatus(planId) {
  await store.updatePlan(planId, { status: statusEdit.value })
  await load()
}

async function onAddCompetency(planId) {
  if (!newCompetencyId.value) return
  await store.addPlanCompetency(planId, newCompetencyId.value)
  newCompetencyId.value = ''
  detail.value = await store.fetchPlan(planId)
}

async function onRemoveCompetency(linkId, planId) {
  await store.removePlanCompetency(linkId)
  detail.value = await store.fetchPlan(planId)
}

onMounted(load)
</script>

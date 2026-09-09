<template>
  <div>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('cohorts.title') }}</h1>

    <div class="flex gap-2 mb-6">
      <input v-model="newCohortName" :placeholder="t('cohorts.namePlaceholder')" class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm flex-1" />
      <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onCreateCohort">{{ t('common.create') }}</button>
    </div>

    <div v-for="c in cohorts" :key="c.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-3">
      <div class="flex items-center justify-between mb-2">
        <p class="font-semibold text-gray-900">{{ c.name }}</p>
        <button class="text-red-600 text-xs" @click="onDeleteCohort(c.id)">{{ t('common.remove') }}</button>
      </div>
      <ul class="text-sm mb-2">
        <li v-for="m in c.members" :key="m.user_id" class="flex items-center justify-between py-0.5">
          <span>{{ m.name }} ({{ m.email }})</span>
          <button class="text-red-600 text-xs" @click="onRemoveMember(c, m.user_id)">{{ t('common.remove') }}</button>
        </li>
      </ul>
      <div class="flex gap-2">
        <input v-model="newMemberEmail[c.id]" :placeholder="t('groups.memberEmailPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-xs flex-1" />
        <button class="bg-gray-100 rounded-lg px-2 py-1 text-xs" @click="onAddMember(c)">{{ t('common.add') }}</button>
      </div>
      <p v-if="memberError[c.id]" class="text-xs text-red-600 mt-1">{{ memberError[c.id] }}</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCohortsStore } from '@/stores/cohorts'
import axios from 'axios'

const { t } = useI18n()
const cohortsStore = useCohortsStore()

const cohorts = ref([])
const newCohortName = ref('')
const newMemberEmail = reactive({})
const memberError = reactive({})

async function load() {
  cohorts.value = await cohortsStore.fetchCohorts()
}

async function onCreateCohort() {
  if (!newCohortName.value) return
  await cohortsStore.createCohort({ name: newCohortName.value })
  newCohortName.value = ''
  await load()
}

async function onDeleteCohort(id) {
  await cohortsStore.deleteCohort(id)
  await load()
}

async function onAddMember(cohort) {
  memberError[cohort.id] = ''
  try {
    const { data: user } = await axios.get('/users/lookup', { params: { email: newMemberEmail[cohort.id] } })
    await cohortsStore.addMember(cohort.id, user.id)
    newMemberEmail[cohort.id] = ''
    await load()
  } catch (e) {
    memberError[cohort.id] = e.response?.data?.detail || t('common.error')
  }
}

async function onRemoveMember(cohort, userId) {
  await cohortsStore.removeMember(cohort.id, userId)
  await load()
}

onMounted(load)
</script>

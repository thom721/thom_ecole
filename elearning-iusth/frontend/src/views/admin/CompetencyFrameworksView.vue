<template>
  <div>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('competency.frameworksTitle') }}</h1>

    <div v-for="f in frameworks" :key="f.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <div class="flex items-center justify-between mb-2">
        <p class="font-medium text-gray-900">{{ f.name }} <span class="text-xs text-gray-400">({{ f.idnumber }})</span></p>
        <button class="text-red-600 text-xs" @click="onDeleteFramework(f.id)">{{ t('common.remove') }}</button>
      </div>

      <ul class="text-sm mb-2">
        <li v-for="c in competenciesByFramework[f.id] || []" :key="c.id" class="flex items-center justify-between py-1 border-t border-gray-100 first:border-t-0">
          <span>{{ c.parent_id ? '— ' : '' }}{{ c.name }} <span class="text-gray-400 text-xs" v-if="c.rule_type !== 'none'">({{ c.rule_type }} → {{ c.rule_outcome }})</span></span>
          <button class="text-red-600 text-xs" @click="onDeleteCompetency(f.id, c.id)">{{ t('common.remove') }}</button>
        </li>
      </ul>

      <details class="text-sm">
        <summary class="cursor-pointer text-gray-600">{{ t('competency.addCompetency') }}</summary>
        <div class="mt-2 space-y-2">
          <input v-model="newCompetency[f.id].name" :placeholder="t('common.title')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          <select v-model="newCompetency[f.id].parent_id" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm">
            <option value="">{{ t('competency.noParent') }}</option>
            <option v-for="c in competenciesByFramework[f.id] || []" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <input v-model="newCompetency[f.id].proficient_min_rank" type="number" :placeholder="t('competency.proficientMinRankPlaceholder')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          <div class="flex gap-2">
            <select v-model="newCompetency[f.id].rule_type" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1">
              <option value="none">{{ t('competency.ruleType.none') }}</option>
              <option value="all">{{ t('competency.ruleType.all') }}</option>
              <option value="any">{{ t('competency.ruleType.any') }}</option>
            </select>
            <select v-model="newCompetency[f.id].rule_outcome" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1">
              <option value="none">{{ t('competency.ruleOutcome.none') }}</option>
              <option value="evidence">{{ t('competency.ruleOutcome.evidence') }}</option>
              <option value="complete">{{ t('competency.ruleOutcome.complete') }}</option>
            </select>
          </div>
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1 text-sm" @click="onAddCompetency(f.id)">{{ t('common.add') }}</button>
        </div>
      </details>
    </div>

    <details class="bg-white border border-gray-200 rounded-xl p-4" open>
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('competency.addFramework') }}</summary>
      <div class="mt-3 space-y-2">
        <input v-model="newFramework.name" :placeholder="t('common.title')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <input v-model="newFramework.idnumber" :placeholder="t('competency.idnumberPlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <input v-model="newFramework.scale_id" :placeholder="t('competency.scaleIdPlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onCreateFramework">{{ t('common.create') }}</button>
        <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
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

const frameworks = ref([])
const competenciesByFramework = reactive({})
const newCompetency = reactive({})
const newFramework = reactive({ name: '', idnumber: '', scale_id: '' })
const error = ref('')

async function load() {
  frameworks.value = await store.fetchFrameworks()
  for (const f of frameworks.value) {
    competenciesByFramework[f.id] = await store.fetchFrameworkCompetencies(f.id)
    if (!newCompetency[f.id]) {
      newCompetency[f.id] = { name: '', parent_id: '', proficient_min_rank: '', rule_type: 'none', rule_outcome: 'none' }
    }
  }
}

async function onCreateFramework() {
  error.value = ''
  if (!newFramework.name || !newFramework.idnumber) return
  try {
    await store.createFramework({
      name: newFramework.name, idnumber: newFramework.idnumber, scale_id: newFramework.scale_id || null,
    })
    newFramework.name = ''
    newFramework.idnumber = ''
    newFramework.scale_id = ''
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  }
}

async function onDeleteFramework(id) {
  try {
    await store.deleteFramework(id)
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  }
}

async function onAddCompetency(frameworkId) {
  const form = newCompetency[frameworkId]
  if (!form.name) return
  await store.createCompetency(frameworkId, {
    name: form.name, parent_id: form.parent_id || null,
    proficient_min_rank: form.proficient_min_rank !== '' ? Number(form.proficient_min_rank) : null,
    rule_type: form.rule_type, rule_outcome: form.rule_outcome,
  })
  newCompetency[frameworkId] = { name: '', parent_id: '', proficient_min_rank: '', rule_type: 'none', rule_outcome: 'none' }
  await load()
}

async function onDeleteCompetency(frameworkId, competencyId) {
  try {
    await store.deleteCompetency(competencyId)
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  }
}

onMounted(load)
</script>

<template>
  <div v-if="workshop">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-lg font-bold text-gray-900">{{ workshop.title }}</h1>
      <router-link :to="`/teacher/workshops/${workshopId}/grading`" class="text-sm text-blue-600 hover:underline">
        {{ t('workshop.viewGrading') }}
      </router-link>
    </div>

    <!-- Phase -->
    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('workshop.phaseTitle') }}</h2>
      <div class="flex items-center gap-2 mb-3 text-xs">
        <span v-for="p in phases" :key="p" class="px-2 py-1 rounded-full"
          :class="p === workshop.phase ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-500'">
          {{ t(`workshop.phase.${p}`) }}
        </span>
      </div>
      <select v-model="nextPhase" class="border border-gray-300 rounded-lg px-2 py-1 text-sm mr-2">
        <option v-for="p in phases" :key="p" :value="p">{{ t(`workshop.phase.${p}`) }}</option>
      </select>
      <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onSwitchPhase">{{ t('workshop.switchPhase') }}</button>
    </div>

    <!-- Réglages -->
    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('lesson.settingsTitle') }}</h2>
      <div class="grid grid-cols-2 gap-2">
        <label class="text-xs text-gray-500">{{ t('workshop.gradeLabel') }}
          <input v-model="settings.grade" type="number" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
        </label>
        <label class="text-xs text-gray-500">{{ t('workshop.gradinggradeLabel') }}
          <input v-model="settings.gradinggrade" type="number" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
        </label>
        <label class="text-xs text-gray-500">{{ t('workshop.comparisonLabel') }}
          <input v-model="settings.comparison" type="number" min="1" max="9" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
        </label>
        <label class="flex items-center gap-2 text-sm mt-4">
          <input type="checkbox" v-model="settings.use_peer_assessment" /> {{ t('workshop.usePeerAssessment') }}
        </label>
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="settings.use_self_assessment" /> {{ t('workshop.useSelfAssessment') }}
        </label>
      </div>
      <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold mt-2" @click="onSaveSettings">{{ t('common.save') }}</button>
    </div>

    <!-- Dimensions -->
    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-1">{{ t('workshop.dimensionsTitle') }} <span class="text-gray-400 text-xs">({{ t(`workshop.strategy.${workshop.strategy}`) }})</span></h2>
      <div v-for="(d, i) in dimensions" :key="i" class="border border-gray-200 rounded-lg p-2 mb-2">
        <input v-model="d.description" :placeholder="t('workshop.dimensionDescriptionPlaceholder')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm mb-1" />

        <div v-if="workshop.strategy === 'accumulative'" class="flex gap-2">
          <input v-model="d.grade" type="number" :placeholder="t('common.points')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
          <input v-model="d.weight" type="number" :placeholder="t('workshop.weightPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
        </div>

        <div v-else-if="workshop.strategy === 'numerrors'" class="flex gap-2">
          <input v-model="d.label_no" :placeholder="t('workshop.labelNoPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <input v-model="d.label_yes" :placeholder="t('workshop.labelYesPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <input v-model="d.weight" type="number" :placeholder="t('workshop.weightPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-20" />
        </div>

        <div v-else-if="workshop.strategy === 'rubric'">
          <div v-for="(lvl, li) in d.levels" :key="li" class="flex gap-2 mb-1">
            <input v-model="lvl.grade" type="number" :placeholder="t('common.points')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-20" />
            <input v-model="lvl.definition" :placeholder="t('workshop.levelDefinitionPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          </div>
          <button class="text-xs text-blue-600" @click="d.levels.push({ grade: '', definition: '', sort_order: d.levels.length })">{{ t('workshop.addLevel') }}</button>
        </div>

        <button class="text-red-600 text-xs mt-1" @click="dimensions.splice(i, 1)">{{ t('common.remove') }}</button>
      </div>
      <button class="text-xs text-blue-600 mb-2 block" @click="addDimension">{{ t('workshop.addDimension') }}</button>
      <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onSaveDimensions">{{ t('common.save') }}</button>
    </div>

    <!-- Table nombre d'erreurs -->
    <div v-if="workshop.strategy === 'numerrors'" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-1">{{ t('workshop.numerrorsMapTitle') }}</h2>
      <p class="text-xs text-gray-500 mb-2">{{ t('workshop.numerrorsMapHint') }}</p>
      <div v-for="(row, i) in numerrorsMap" :key="i" class="flex items-center gap-2 mb-1">
        <input v-model="row.error_count" type="number" min="1" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
        <span class="text-gray-400 text-xs">→</span>
        <input v-model="row.grade_percent" type="number" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
        <span class="text-gray-400 text-xs">%</span>
        <button class="text-red-600 text-xs" @click="numerrorsMap.splice(i, 1)">{{ t('common.remove') }}</button>
      </div>
      <button class="text-xs text-blue-600 mb-2 block" @click="numerrorsMap.push({ error_count: numerrorsMap.length + 1, grade_percent: '' })">{{ t('common.add') }}</button>
      <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onSaveNumerrorsMap">{{ t('common.save') }}</button>
    </div>

    <!-- Allocation -->
    <div class="bg-white border border-gray-200 rounded-xl p-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('workshop.allocationTitle') }}</h2>
      <ul class="text-sm mb-3">
        <li v-for="s in submissions" :key="s.id" class="py-1 border-t border-gray-100 first:border-t-0">
          {{ s.title }} — {{ t('workshop.byAuthor', { id: s.author_id }) }}
          <span v-if="s.final_grade !== null" class="text-gray-400">({{ s.final_grade }} / {{ workshop.grade }})</span>
        </li>
      </ul>
      <div class="flex gap-2 mb-3">
        <select v-model="allocSubmissionId" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1">
          <option value="">{{ t('workshop.chooseSubmission') }}</option>
          <option v-for="s in submissions" :key="s.id" :value="s.id">{{ s.title }}</option>
        </select>
        <input v-model="allocReviewerId" :placeholder="t('workshop.reviewerIdPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
        <button class="bg-gray-100 rounded-lg px-3 py-1 text-sm" @click="onAllocateManual">{{ t('common.add') }}</button>
      </div>
      <div class="flex items-center gap-2">
        <input v-model="reviewsPerSubmission" type="number" min="1" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onAllocateRandom">{{ t('workshop.allocateRandom') }}</button>
      </div>
      <p v-if="allocError" class="text-xs text-red-600 mt-2">{{ allocError }}</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useWorkshopsStore } from '@/stores/workshops'

const { t } = useI18n()
const route = useRoute()
const workshopId = route.params.id
const workshops = useWorkshopsStore()

const phases = ['setup', 'submission', 'assessment', 'evaluation', 'closed']

const workshop = ref(null)
const dimensions = ref([])
const numerrorsMap = ref([])
const submissions = ref([])
const nextPhase = ref('setup')
const allocSubmissionId = ref('')
const allocReviewerId = ref('')
const reviewsPerSubmission = ref(2)
const allocError = ref('')

const settings = reactive({ grade: '', gradinggrade: '', comparison: '', use_peer_assessment: true, use_self_assessment: false })

async function load() {
  workshop.value = await workshops.fetchWorkshop(workshopId)
  dimensions.value = (await workshops.fetchDimensions(workshopId)).map((d) => ({
    ...d, levels: (d.levels || []).map((l) => ({ ...l })),
  }))
  submissions.value = await workshops.fetchSubmissions(workshopId)
  if (workshop.value.strategy === 'numerrors') {
    numerrorsMap.value = await workshops.fetchNumerrorsMap(workshopId)
  }
  nextPhase.value = workshop.value.phase
  settings.grade = workshop.value.grade
  settings.gradinggrade = workshop.value.gradinggrade
  settings.comparison = workshop.value.comparison
  settings.use_peer_assessment = workshop.value.use_peer_assessment
  settings.use_self_assessment = workshop.value.use_self_assessment
}

function addDimension() {
  dimensions.value.push({ description: '', sort_order: dimensions.value.length, grade: '', weight: 1, label_no: '', label_yes: '', levels: [] })
}

async function onSaveSettings() {
  await workshops.updateWorkshop(workshopId, {
    grade: Number(settings.grade), gradinggrade: Number(settings.gradinggrade), comparison: Number(settings.comparison),
    use_peer_assessment: settings.use_peer_assessment, use_self_assessment: settings.use_self_assessment,
  })
  await load()
}

async function onSwitchPhase() {
  await workshops.switchPhase(workshopId, nextPhase.value)
  await load()
}

async function onSaveDimensions() {
  const payload = dimensions.value.map((d, i) => ({
    description: d.description, sort_order: i,
    grade: d.grade !== '' ? Number(d.grade) : null,
    weight: d.weight !== '' ? Number(d.weight) : 1,
    label_no: d.label_no || null, label_yes: d.label_yes || null,
    levels: (d.levels || []).map((l, li) => ({ grade: Number(l.grade), definition: l.definition, sort_order: li })),
  }))
  await workshops.replaceDimensions(workshopId, payload)
  await load()
}

async function onSaveNumerrorsMap() {
  await workshops.replaceNumerrorsMap(workshopId, numerrorsMap.value.map((r) => ({
    error_count: Number(r.error_count), grade_percent: Number(r.grade_percent),
  })))
}

async function onAllocateManual() {
  allocError.value = ''
  if (!allocSubmissionId.value || !allocReviewerId.value) return
  try {
    await workshops.allocateManual(workshopId, { submission_id: allocSubmissionId.value, reviewer_id: allocReviewerId.value })
    allocSubmissionId.value = ''
    allocReviewerId.value = ''
  } catch (e) {
    allocError.value = e.response?.data?.detail || t('common.error')
  }
}

async function onAllocateRandom() {
  allocError.value = ''
  try {
    await workshops.allocateRandom(workshopId, Number(reviewsPerSubmission.value))
  } catch (e) {
    allocError.value = e.response?.data?.detail || t('common.error')
  }
}

onMounted(load)
</script>

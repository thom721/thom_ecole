<template>
  <div v-if="workshop" class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-1">{{ workshop.title }}</h1>
    <p class="text-xs text-gray-400 mb-6">{{ t(`workshop.phase.${workshop.phase}`) }}</p>

    <!-- Soumission -->
    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-2">{{ t('workshop.mySubmissionTitle') }}</h2>

      <template v-if="workshop.phase === 'submission'">
        <input v-model="form.title" :placeholder="t('common.title')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-2" />
        <textarea v-model="form.content" rows="4" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-2"></textarea>
        <input type="file" @change="onFileChange" class="text-sm mb-2" />
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold block" @click="onSubmit">{{ t('common.save') }}</button>
      </template>

      <template v-if="mySubmission">
        <p class="text-sm text-gray-700 mt-2">{{ mySubmission.title }}</p>
        <p v-if="mySubmission.final_grade !== null" class="text-sm font-medium mt-1">
          {{ t('workshop.finalGrade', { grade: mySubmission.final_grade, max: workshop.grade }) }}
        </p>
        <p v-if="mySubmission.feedback_author" class="text-xs text-gray-500 mt-1">{{ mySubmission.feedback_author }}</p>
      </template>
      <p v-else class="text-sm text-gray-500">{{ t('workshop.noSubmissionYet') }}</p>
    </div>

    <!-- Évaluations à faire -->
    <div v-if="workshop.phase === 'assessment'" class="bg-white border border-gray-200 rounded-xl p-4">
      <h2 class="font-semibold text-gray-900 mb-2">{{ t('workshop.myAssessmentsTitle') }}</h2>
      <p v-if="!myAssessments.length" class="text-sm text-gray-500">{{ t('workshop.noAssessmentsAssigned') }}</p>
      <router-link v-for="a in myAssessments" :key="a.id" :to="`/student/workshop-assessments/${a.id}`"
        class="block bg-gray-50 rounded-lg p-2 text-sm mb-1 hover:bg-gray-100">
        {{ t('workshop.assessSubmission') }} →
      </router-link>
    </div>

    <p v-if="workshop.conclusion && workshop.phase === 'closed'" class="text-sm text-gray-600 mt-4 whitespace-pre-wrap">{{ workshop.conclusion }}</p>
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

const workshop = ref(null)
const mySubmission = ref(null)
const myAssessments = ref([])
const form = reactive({ title: '', content: '' })
let file = null

function onFileChange(e) {
  file = e.target.files[0] || null
}

async function load() {
  workshop.value = await workshops.fetchWorkshop(workshopId)
  mySubmission.value = await workshops.fetchMySubmission(workshopId)
  if (mySubmission.value) {
    form.title = mySubmission.value.title
    form.content = mySubmission.value.content || ''
  }
  if (workshop.value.phase === 'assessment') {
    myAssessments.value = await workshops.fetchMyAssessments(workshopId)
  }
}

async function onSubmit() {
  const formData = new FormData()
  formData.append('title', form.title || 'Sans titre')
  formData.append('content', form.content || '')
  if (file) formData.append('file', file)
  mySubmission.value = await workshops.submit(workshopId, formData)
  await load()
}

onMounted(load)
</script>

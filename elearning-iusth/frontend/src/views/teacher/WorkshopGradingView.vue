<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('workshop.gradingTitle') }}</h1>

    <div v-for="s in submissions" :key="s.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <div class="flex items-center justify-between mb-2">
        <p class="font-medium text-gray-900">{{ s.title }}</p>
        <span class="text-xs text-gray-400">{{ t('workshop.byAuthor', { id: s.author_id }) }}</span>
      </div>
      <p class="text-sm text-gray-600 mb-2">{{ t('workshop.computedGrade', { percent: s.grade_percent ?? '—', final: s.final_grade ?? '—' }) }}</p>

      <div class="flex gap-2 items-center mb-2">
        <input v-model="overrides[s.id]" type="number" :placeholder="t('workshop.gradeOverridePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-32" />
        <input v-model="feedbacks[s.id]" :placeholder="t('teacher.assignmentGrading.feedbackPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onOverride(s.id)">{{ t('common.save') }}</button>
      </div>

      <details class="text-sm">
        <summary class="cursor-pointer text-gray-600">{{ t('workshop.receivedAssessments') }}</summary>
        <div v-for="a in (assessmentsBySubmission[s.id] || [])" :key="a.id" class="border-t border-gray-100 pt-2 mt-2">
          <p class="text-xs text-gray-500">{{ t('workshop.byReviewer', { id: a.reviewer_id }) }} — {{ t('workshop.qualityGrade', { percent: a.gradinggrade_percent ?? '—' }) }}</p>
          <div class="flex gap-2 items-center mt-1">
            <input v-model="gradingOverrides[a.id]" type="number" :placeholder="t('workshop.gradinggradeOverridePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-32" />
            <input v-model="gradingFeedbacks[a.id]" :placeholder="t('workshop.feedbackReviewerPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
            <button class="bg-gray-100 rounded-lg px-3 py-1 text-sm" @click="onFeedbackReviewer(a.id)">{{ t('common.save') }}</button>
          </div>
        </div>
      </details>
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

const submissions = ref([])
const assessmentsBySubmission = reactive({})
const overrides = reactive({})
const feedbacks = reactive({})
const gradingOverrides = reactive({})
const gradingFeedbacks = reactive({})

async function load() {
  submissions.value = await workshops.fetchSubmissions(workshopId)
  for (const s of submissions.value) {
    const detail = await workshops.fetchSubmission(s.id)
    s.grade_percent = detail.grade_percent
    s.final_grade = detail.final_grade
    assessmentsBySubmission[s.id] = detail.assessments
  }
}

async function onOverride(submissionId) {
  await workshops.overrideSubmission(submissionId, {
    grade_override: overrides[submissionId] !== undefined && overrides[submissionId] !== '' ? Number(overrides[submissionId]) : null,
    feedback_author: feedbacks[submissionId] || null,
  })
  await load()
}

async function onFeedbackReviewer(assessmentId) {
  await workshops.setFeedbackReviewer(assessmentId, {
    gradinggrade_override: gradingOverrides[assessmentId] !== undefined && gradingOverrides[assessmentId] !== '' ? Number(gradingOverrides[assessmentId]) : null,
    feedback_reviewer: gradingFeedbacks[assessmentId] || null,
  })
  await load()
}

onMounted(load)
</script>

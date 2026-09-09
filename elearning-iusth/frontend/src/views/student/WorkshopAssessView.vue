<template>
  <div v-if="submission" class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-1">{{ submission.title }}</h1>
    <p class="text-sm text-gray-600 mb-6 whitespace-pre-wrap">{{ submission.content }}</p>

    <div v-for="d in dimensions" :key="d.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-3">
      <p class="font-medium text-gray-900 mb-2">{{ d.description }}</p>

      <div v-if="workshop.strategy === 'accumulative'" class="flex items-center gap-2">
        <input v-model="answers[d.id].grade" type="number" min="0" :max="d.grade" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
        <span class="text-xs text-gray-400">/ {{ d.grade }}</span>
      </div>

      <div v-else-if="workshop.strategy === 'comments'"></div>

      <div v-else-if="workshop.strategy === 'numerrors'" class="flex items-center gap-3 text-sm">
        <label class="flex items-center gap-1"><input type="radio" :name="d.id" value="0" v-model="answers[d.id].grade" /> {{ d.label_no }}</label>
        <label class="flex items-center gap-1"><input type="radio" :name="d.id" value="1" v-model="answers[d.id].grade" /> {{ d.label_yes }}</label>
      </div>

      <div v-else-if="workshop.strategy === 'rubric'">
        <label v-for="lvl in d.levels" :key="lvl.id" class="flex items-center gap-2 text-sm mb-1">
          <input type="radio" :name="d.id" :value="lvl.grade" v-model="answers[d.id].grade" />
          {{ lvl.definition }} <span class="text-gray-400">({{ lvl.grade }} pts)</span>
        </label>
      </div>

      <textarea v-model="answers[d.id].peer_comment" :placeholder="t('workshop.peerCommentPlaceholder')" rows="2"
        class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm mt-2"></textarea>
    </div>

    <textarea v-model="feedbackAuthor" :placeholder="t('workshop.feedbackAuthorPlaceholder')" rows="3"
      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3"></textarea>

    <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onSave">{{ t('common.save') }}</button>
    <p v-if="error" class="text-xs text-red-600 mt-2">{{ error }}</p>
    <p v-if="saved" class="text-xs text-green-700 mt-2">{{ t('workshop.assessmentSaved') }}</p>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useWorkshopsStore } from '@/stores/workshops'

const { t } = useI18n()
const route = useRoute()
const assessmentId = route.params.id
const workshops = useWorkshopsStore()

const assessment = ref(null)
const submission = ref(null)
const workshop = ref(null)
const dimensions = ref([])
const answers = reactive({})
const feedbackAuthor = ref('')
const error = ref('')
const saved = ref(false)

async function load() {
  assessment.value = await workshops.fetchAssessment(assessmentId)
  submission.value = await workshops.fetchSubmission(assessment.value.submission_id)
  workshop.value = await workshops.fetchWorkshop(submission.value.workshop_id)
  dimensions.value = await workshops.fetchDimensions(submission.value.workshop_id)
  feedbackAuthor.value = assessment.value.feedback_author || ''

  const existing = {}
  for (const g of assessment.value.grades) existing[g.dimension_id] = g

  for (const d of dimensions.value) {
    const g = existing[d.id]
    answers[d.id] = { grade: g?.grade !== undefined && g?.grade !== null ? String(g.grade) : '', peer_comment: g?.peer_comment || '' }
  }
}

async function onSave() {
  error.value = ''
  saved.value = false
  const grades = dimensions.value.map((d) => ({
    dimension_id: d.id,
    grade: answers[d.id].grade !== '' ? Number(answers[d.id].grade) : null,
    peer_comment: answers[d.id].peer_comment || null,
  }))
  try {
    assessment.value = await workshops.saveGrades(assessmentId, { grades, feedback_author: feedbackAuthor.value })
    saved.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  }
}

onMounted(load)
</script>

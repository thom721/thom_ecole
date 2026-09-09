<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('competency.courseCompetenciesTitle') }}</h1>

    <div v-for="link in links" :key="link.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <div class="flex items-center justify-between mb-3">
        <p class="font-medium text-gray-900">{{ competencyName(link.competency_id) }}</p>
        <button class="text-red-600 text-xs" @click="onUnlink(link.id)">{{ t('common.remove') }}</button>
      </div>

      <table class="text-sm w-full mb-2">
        <thead>
          <tr class="text-left text-gray-500">
            <th>{{ t('common.student') }}</th>
            <th>{{ t('competency.gradeRank') }}</th>
            <th>{{ t('competency.proficient') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in students" :key="s.user_id" class="border-t border-gray-100">
            <td class="py-1">{{ s.user_id }}</td>
            <td>
              <input v-model="gradeInputs[link.competency_id + s.user_id]" type="number" class="w-16 border border-gray-300 rounded px-1 py-0.5 text-center" />
              <button class="text-blue-600 text-xs ml-1" @click="onGrade(link.competency_id, s.user_id)">{{ t('common.save') }}</button>
            </td>
            <td>{{ statusFor(link.competency_id, s.user_id) }}</td>
          </tr>
        </tbody>
      </table>

      <details class="text-xs">
        <summary class="cursor-pointer text-gray-600">{{ t('competency.linkActivity') }}</summary>
        <div class="mt-2 flex gap-2">
          <select v-model="activityType[link.id]" class="border border-gray-300 rounded-lg px-2 py-1 text-xs">
            <option value="resource">{{ t('badges.itemType.resource') }}</option>
            <option value="assignment">{{ t('badges.itemType.assignment') }}</option>
            <option value="quiz">{{ t('badges.itemType.quiz') }}</option>
            <option value="lesson">{{ t('badges.itemType.lesson') }}</option>
            <option value="workshop">{{ t('badges.itemType.workshop') }}</option>
          </select>
          <input v-model="activityId[link.id]" :placeholder="t('badges.itemIdPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-xs flex-1" />
          <button class="bg-gray-100 rounded-lg px-2 py-1 text-xs" @click="onLinkActivity(link)">{{ t('common.add') }}</button>
        </div>
      </details>
    </div>

    <div class="bg-white border border-gray-200 rounded-xl p-4">
      <h2 class="font-semibold text-gray-900 mb-2">{{ t('competency.linkCompetency') }}</h2>
      <div class="flex gap-2">
        <select v-model="newLinkId" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1">
          <option value="">{{ t('competency.chooseCompetency') }}</option>
          <option v-for="c in allCompetencies" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onLink">{{ t('common.add') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCompetenciesStore } from '@/stores/competencies'
import axios from 'axios'

const { t } = useI18n()
const route = useRoute()
const courseId = route.params.id
const store = useCompetenciesStore()

const links = ref([])
const allCompetencies = ref([])
const students = ref([])
const statuses = reactive({})
const gradeInputs = reactive({})
const newLinkId = ref('')
const activityType = reactive({})
const activityId = reactive({})

function competencyName(id) {
  return allCompetencies.value.find((c) => c.id === id)?.name || id
}

function statusFor(competencyId, studentId) {
  const s = statuses[competencyId + studentId]
  if (!s) return '—'
  return s.course_proficiency === true ? '✓' : s.course_proficiency === false ? '✗' : '—'
}

async function load() {
  links.value = await store.fetchCourseCompetencies(courseId)

  const frameworks = await store.fetchFrameworks()
  const all = []
  for (const f of frameworks) {
    const comps = await store.fetchFrameworkCompetencies(f.id)
    all.push(...comps)
  }
  allCompetencies.value = all

  const { data: enrollments } = await axios.get(`/courses/${courseId}/enrollments`)
  students.value = enrollments.filter((e) => e.role_in_course === 'student')

  const mineForAll = await store.fetchMyCourseCompetencies(courseId).catch(() => [])
  for (const link of links.value) {
    for (const s of students.value) {
      // pas d'endpoint "par etudiant" cote professeur : on utilise la note deja
      // renvoyee par le dernier PATCH, ou on laisse vide tant que non note
      if (!statuses[link.competency_id + s.user_id]) statuses[link.competency_id + s.user_id] = null
    }
  }
}

async function onLink() {
  if (!newLinkId.value) return
  await store.linkCourseCompetency(courseId, newLinkId.value)
  newLinkId.value = ''
  await load()
}

async function onUnlink(linkId) {
  await store.unlinkCourseCompetency(linkId)
  await load()
}

async function onLinkActivity(link) {
  if (!activityType[link.id] || !activityId[link.id]) return
  await store.linkModuleCompetency(activityType[link.id], activityId[link.id], courseId, link.competency_id)
  activityType[link.id] = ''
  activityId[link.id] = ''
}

async function onGrade(competencyId, studentId) {
  const rank = gradeInputs[competencyId + studentId]
  if (rank === undefined || rank === '') return
  const result = await store.gradeStudentCompetency(courseId, competencyId, studentId, Number(rank))
  statuses[competencyId + studentId] = result
}

onMounted(load)
</script>

<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('teacher.assignmentGrading.title') }}</h1>

    <!-- Devoir de groupe : une carte par groupe, une seule note par groupe -->
    <template v-if="assignment?.group_mode">
      <p v-if="!groups.length" class="text-sm text-gray-500">{{ t('teacher.assignmentGrading.noGroups') }}</p>

      <div v-for="g in groups" :key="g.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
        <p class="text-sm font-semibold text-gray-800 mb-1">{{ t('teacher.assignmentGrading.groupLabel', { name: g.name }) }}</p>
        <p class="text-xs text-gray-500 mb-3">{{ t('teacher.assignmentGrading.groupMembers', { members: g.members.map(m => m.name).join(', ') }) }}</p>

        <div class="flex gap-2 items-center">
          <input v-model="grades[g.id]" type="number" :placeholder="t('teacher.assignmentGrading.gradePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
          <input v-model="feedbacks[g.id]" :placeholder="t('teacher.assignmentGrading.feedbackPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onGradeGroup(g.id)">
            {{ t('teacher.assignmentGrading.gradeButton') }}
          </button>
        </div>
        <p v-if="groupGrade(g.id) !== null" class="text-xs text-green-600 mt-2">{{ t('teacher.assignmentGrading.alreadyGraded', { grade: groupGrade(g.id) }) }}</p>
      </div>
    </template>

    <!-- Devoir individuel : comportement existant, inchangé -->
    <template v-else>
      <p v-if="!submissions.length" class="text-sm text-gray-500">{{ t('teacher.assignmentGrading.empty') }}</p>

      <div v-for="s in submissions" :key="s.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
        <p class="text-xs text-gray-500 mb-1">{{ t('teacher.assignmentGrading.student', { id: s.student_name || s.student_id }) }}</p>
        <p class="text-sm text-gray-800 whitespace-pre-wrap mb-3">{{ s.submitted_text || t('teacher.assignmentGrading.noText') }}</p>
        <button v-if="s.file_download_url" @click="downloadFile(s.file_download_url, s.file_name)"
          class="text-xs text-blue-600 hover:underline mb-3 block">
          📎 {{ t('teacher.assignmentGrading.attachedFile', { path: s.file_name }) }}
        </button>

        <div class="flex gap-2 items-center">
          <input v-model="grades[s.id]" type="number" :placeholder="t('teacher.assignmentGrading.gradePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
          <input v-model="feedbacks[s.id]" :placeholder="t('teacher.assignmentGrading.feedbackPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onGrade(s.id)">
            {{ t('teacher.assignmentGrading.gradeButton') }}
          </button>
        </div>
        <p v-if="s.status === 'graded'" class="text-xs text-green-600 mt-2">{{ t('teacher.assignmentGrading.alreadyGraded', { grade: s.grade }) }}</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const route = useRoute()
const assignment = ref(null)
const submissions = ref([])
const groups = ref([])
const grades = reactive({})
const feedbacks = reactive({})

// Devoir de groupe : les Submission (une par membre, voir RSubmissions.py::
// grade_group) portent toutes le même group_id — on lit la note du groupe
// depuis la première trouvée pour cet id.
function groupGrade(groupId) {
  const s = submissions.value.find(s => s.group_id === groupId && s.status === 'graded')
  return s ? s.grade : null
}

async function load() {
  const { data } = await axios.get(`/assignments/${route.params.id}`)
  assignment.value = data

  const { data: subs } = await axios.get(`/assignments/${route.params.id}/submissions`)
  submissions.value = subs

  if (data.group_mode && data.course_id) {
    const { data: courseGroups } = await axios.get(`/courses/${data.course_id}/groups`)
    groups.value = courseGroups
  }
}

// Le lien direct ne fonctionnerait pas : le token d'authentification est
// envoyé en header Authorization par axios (voir main.js), jamais en
// cookie — un <a href> classique n'authentifierait pas la requête.
// On récupère donc le fichier via axios (déjà authentifié) puis on
// déclenche l'enregistrement via une URL blob temporaire.
async function downloadFile(url, filename) {
  const response = await axios.get(url, { responseType: 'blob' })
  const blobUrl = window.URL.createObjectURL(response.data)
  const link = document.createElement('a')
  link.href = blobUrl
  link.download = filename || 'fichier'
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(blobUrl)
}

async function onGrade(submissionId) {
  await axios.patch(`/submissions/${submissionId}/grade`, {
    grade: Number(grades[submissionId]),
    feedback: feedbacks[submissionId] || null,
  })
  await load()
}

async function onGradeGroup(groupId) {
  await axios.patch(`/assignments/${route.params.id}/groups/${groupId}/grade`, {
    grade: Number(grades[groupId]),
    feedback: feedbacks[groupId] || null,
  })
  await load()
}

onMounted(load)
</script>

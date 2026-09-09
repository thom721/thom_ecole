<template>
  <div class="max-w-lg">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('teacher.courseImport.title') }}</h1>

    <div class="bg-white border border-gray-200 rounded-xl p-4 space-y-3">
      <div>
        <label class="block text-xs text-gray-600 mb-1">{{ t('teacher.courseImport.fileLabel') }}</label>
        <input type="file" accept="application/json" @change="onFileChange" class="text-sm" />
      </div>
      <div>
        <label class="block text-xs text-gray-600 mb-1">{{ t('courseExport.targetLabel') }}</label>
        <select v-model="targetCourseId" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="">{{ t('courseExport.targetNewCourse') }}</option>
          <option v-for="c in myCourses" :key="c.id" :value="c.id">{{ c.full_name }}</option>
        </select>
      </div>
      <template v-if="!targetCourseId">
        <div>
          <label class="block text-xs text-gray-600 mb-1">{{ t('teacher.courseImport.shortNameLabel') }}</label>
          <input v-model="shortName" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="block text-xs text-gray-600 mb-1">{{ t('teacher.courseImport.fullNameLabel') }}</label>
          <input v-model="fullName" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        </div>
      </template>
      <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onImport">
        {{ t('teacher.courseImport.importButton') }}
      </button>
      <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
    </div>

    <div v-if="result" class="bg-green-50 border border-green-200 rounded-xl p-4 mt-4">
      <p class="font-semibold text-green-800 mb-2">{{ t('teacher.courseImport.importedTitle', { name: result.course.full_name }) }}</p>
      <router-link :to="`/teacher/courses/${result.course.id}`" class="text-blue-600 text-sm hover:underline">
        {{ t('teacher.courseImport.openCourse') }}
      </router-link>
      <div v-if="result.warnings.length" class="mt-3">
        <p class="text-xs font-semibold text-amber-700 mb-1">{{ t('teacher.courseImport.warningsTitle') }}</p>
        <ul class="text-xs text-amber-700 list-disc list-inside">
          <li v-for="(w, i) in result.warnings" :key="i">{{ w }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseExportStore } from '@/stores/courseExport'
import { useCoursesStore } from '@/stores/courses'

const { t } = useI18n()
const courseExport = useCourseExportStore()
const coursesStore = useCoursesStore()
const fileContent = ref(null)
const shortName = ref('')
const fullName = ref('')
const targetCourseId = ref('')
const myCourses = ref([])
const error = ref('')
const result = ref(null)

onMounted(async () => {
  await coursesStore.fetchMyCourses()
  myCourses.value = coursesStore.myCourses
})

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    try {
      fileContent.value = JSON.parse(reader.result)
    } catch {
      error.value = t('teacher.courseImport.invalidJson')
    }
  }
  reader.readAsText(file)
}

async function onImport() {
  error.value = ''
  result.value = null
  if (!fileContent.value || (!targetCourseId.value && !shortName.value)) {
    error.value = t('teacher.courseImport.missingFields')
    return
  }
  try {
    result.value = await courseExport.importCourse({
      short_name: targetCourseId.value ? null : shortName.value,
      full_name: targetCourseId.value ? null : (fullName.value || null),
      target_course_id: targetCourseId.value || null,
      export: fileContent.value,
    })
  } catch (e) {
    error.value = e.response?.data?.detail || t('teacher.courseImport.importError')
  }
}
</script>

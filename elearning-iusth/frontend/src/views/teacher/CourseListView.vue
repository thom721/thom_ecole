<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-lg font-bold text-gray-900">{{ t('teacher.courseList.title') }}</h1>
      <div class="flex gap-2">
        <router-link to="/teacher/courses/import" class="bg-gray-100 text-gray-700 rounded-lg px-3 py-1.5 text-sm font-semibold no-underline">
          {{ t('teacher.courseList.importCourse') }}
        </router-link>
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="showCreate = true">
          {{ t('teacher.courseList.newCourse') }}
        </button>
      </div>
    </div>

    <div v-if="showCreate" class="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label class="block text-xs text-gray-600 mb-1">{{ t('teacher.courseList.shortNameLabel') }}</label>
          <input v-model="form.short_name" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="block text-xs text-gray-600 mb-1">{{ t('teacher.courseList.fullNameLabel') }}</label>
          <input v-model="form.full_name" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        </div>
      </div>
      <label class="block text-xs text-gray-600 mb-1">{{ t('teacher.courseList.summaryLabel') }}</label>
      <textarea v-model="form.summary" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3"></textarea>
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label class="block text-xs text-gray-600 mb-1">{{ t('courseFormat.formatLabel') }}</label>
          <select v-model="form.format" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="topics">{{ t('courseFormat.format.topics') }}</option>
            <option value="weeks">{{ t('courseFormat.format.weeks') }}</option>
            <option value="social">{{ t('courseFormat.format.social') }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-gray-600 mb-1">{{ t('courseFormat.displayLabel') }}</label>
          <select v-model="form.course_display" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="single_page">{{ t('courseFormat.display.single_page') }}</option>
            <option value="paginated">{{ t('courseFormat.display.paginated') }}</option>
          </select>
        </div>
      </div>
      <div class="flex gap-2">
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onCreate">{{ t('common.create') }}</button>
        <button class="text-sm text-gray-500" @click="showCreate = false">{{ t('common.cancel') }}</button>
      </div>
    </div>

    <p v-if="!courses.myCourses.length" class="text-sm text-gray-500">{{ t('teacher.courseList.empty') }}</p>

    <div class="grid gap-3">
      <router-link v-for="c in courses.myCourses" :key="c.id" :to="`/teacher/courses/${c.id}`"
        class="bg-white border border-gray-200 rounded-xl p-4 hover:border-gray-400 transition-colors">
        <p class="text-xs text-gray-500 mb-1">{{ c.short_name }}</p>
        <p class="font-semibold text-gray-900">{{ c.full_name }}</p>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCoursesStore } from '@/stores/courses'

const { t } = useI18n()
const courses = useCoursesStore()
const showCreate = ref(false)
const form = reactive({ short_name: '', full_name: '', summary: '', format: 'topics', course_display: 'single_page' })

async function onCreate() {
  await courses.createCourse({ ...form })
  showCreate.value = false
  form.short_name = ''
  form.full_name = ''
  form.summary = ''
  form.format = 'topics'
  form.course_display = 'single_page'
  await courses.fetchMyCourses()
}

onMounted(() => courses.fetchMyCourses())
</script>

<template>
  <div>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('student.courseList.title') }}</h1>

    <p v-if="!courses.myCourses.length" class="text-sm text-gray-500">
      {{ t('student.courseList.empty') }}
    </p>

    <div class="grid gap-3">
      <router-link v-for="c in courses.myCourses" :key="c.id" :to="`/student/courses/${c.id}`"
        class="bg-white border border-gray-200 rounded-xl p-4 hover:border-gray-400 transition-colors">
        <p class="text-xs text-gray-500 mb-1">{{ c.short_name }}</p>
        <p class="font-semibold text-gray-900">{{ c.full_name }}</p>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCoursesStore } from '@/stores/courses'

const { t } = useI18n()
const courses = useCoursesStore()
onMounted(() => courses.fetchMyCourses())
</script>

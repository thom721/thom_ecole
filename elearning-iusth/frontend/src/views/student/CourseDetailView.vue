<template>
  <div v-if="course">
    <router-link to="/student/courses" class="text-sm text-gray-500 hover:underline">{{ t('common.backToMyCourses') }}</router-link>
    <div class="flex items-center justify-between mt-2 mb-1">
      <h1 class="text-lg font-bold text-gray-900">{{ course.full_name }}</h1>
      <div class="flex gap-3">
        <router-link :to="`/student/courses/${course.id}/grades`" class="text-sm text-blue-600 hover:underline">{{ t('student.courseDetail.myGrades') }}</router-link>
        <router-link :to="`/student/calendar?course_id=${course.id}`" class="text-sm text-blue-600 hover:underline">{{ t('student.courseDetail.calendar') }}</router-link>
      </div>
    </div>
    <p v-if="course.summary" class="text-sm text-gray-500 mb-1">{{ course.summary }}</p>
    <p v-if="completion" class="text-sm text-gray-600 mb-6">{{ t('student.courseDetail.progress', { percent: completion.percent.toFixed(0) }) }}</p>

    <div v-if="course.format === 'social'" class="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <router-link v-if="course.social_forum" :to="`/student/forums/${course.social_forum.id}`" class="text-blue-600 hover:underline font-semibold">
        💬 {{ course.social_forum.title }}
      </router-link>
      <p v-else class="text-sm text-gray-500">{{ t('courseFormat.noSocialForum') }}</p>
    </div>

    <template v-else>
    <div v-if="course.course_display === 'paginated' && course.sections.length" class="flex items-center justify-between mb-3 text-sm">
      <button class="text-blue-600 disabled:opacity-30" :disabled="pageIndex === 0" @click="pageIndex--">{{ t('admin.courses.prevPage') }}</button>
      <span class="text-gray-500">{{ course.sections[pageIndex]?.title || t('common.section') }}</span>
      <button class="text-blue-600 disabled:opacity-30" :disabled="pageIndex >= course.sections.length - 1" @click="pageIndex++">{{ t('admin.courses.nextPage') }}</button>
    </div>
    <div v-for="section in displayedSections" :key="section.id" class="mb-6">
      <h2 class="font-semibold text-gray-900 mb-1">{{ section.title || t('common.section') }}</h2>
      <p v-if="section.week_start" class="text-xs text-gray-400 mb-2">{{ t('courseFormat.weekRange', { start: formatDate(section.week_start), end: formatDate(section.week_end) }) }}</p>
      <p v-if="section.summary" class="text-sm text-gray-500 mb-3">{{ section.summary }}</p>

      <div class="grid gap-2">
        <div v-for="r in section.resources" :key="r.id" class="bg-white border border-gray-200 rounded-lg p-3 text-sm">
          <div class="flex items-start justify-between gap-2">
            <p class="font-medium text-gray-900 mb-1">{{ r.title }}</p>
            <label v-if="!r.access_restricted" class="flex items-center gap-1 text-xs text-gray-500 shrink-0">
              <input type="checkbox" :checked="isComplete('resource', r.id)" @change="onToggleResource(r.id, $event.target.checked)" />
              {{ t('student.courseDetail.done') }}
            </label>
          </div>
          <div v-if="r.access_restricted" class="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-2">
            <p class="font-medium mb-0.5">{{ t('access.restrictedTitle') }}</p>
            <ul class="list-disc list-inside">
              <li v-for="(reason, i) in r.access_reasons" :key="i">{{ reason }}</li>
            </ul>
          </div>
          <p v-else-if="r.resource_type === 'page'" class="text-gray-600"><AutoLinkedText :text="r.page_content" :course-id="course.id" /></p>
          <a v-else-if="r.resource_type === 'url'" :href="r.external_url" target="_blank" class="text-blue-600 hover:underline">{{ r.external_url }}</a>
          <ul v-else-if="r.files?.length">
            <li v-for="f in r.files" :key="f.id">
              <a href="#" class="text-blue-600 hover:underline" @click.prevent="downloadFile(f.id, f.original_filename)">{{ f.original_filename }}</a>
            </li>
          </ul>
        </div>

        <router-link v-for="a in section.assignments" :key="a.id" :to="`/student/assignments/${a.id}`"
          class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm hover:border-amber-400 transition-colors">
          <p class="font-medium text-gray-900">📄 {{ a.title }} <span v-if="isComplete('assignment', a.id)">✓</span></p>
          <p class="text-xs text-gray-500 mt-1">{{ t('student.courseDetail.outOfPoints', { points: a.max_points }) }}</p>
        </router-link>

        <router-link v-for="q in section.quizzes" :key="q.id" :to="`/student/quizzes/${q.id}`"
          class="bg-purple-50 border border-purple-200 rounded-lg p-3 text-sm hover:border-purple-400 transition-colors">
          <p class="font-medium text-gray-900">📝 {{ q.title }} <span v-if="isComplete('quiz', q.id)">✓</span></p>
          <p class="text-xs text-gray-500 mt-1">
            <span v-if="q.time_limit_minutes">{{ t('student.courseDetail.minutes', { count: q.time_limit_minutes }) }}</span>
            <span v-else>{{ t('student.courseDetail.noTimeLimit') }}</span>
          </p>
        </router-link>

        <router-link v-for="f in section.forums" :key="f.id" :to="`/student/forums/${f.id}`"
          class="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm hover:border-blue-400 transition-colors">
          <p class="font-medium text-gray-900">💬 {{ f.title }}</p>
        </router-link>

        <router-link v-for="c in section.choices" :key="c.id" :to="`/student/choices/${c.id}`"
          class="bg-teal-50 border border-teal-200 rounded-lg p-3 text-sm hover:border-teal-400 transition-colors">
          <p class="font-medium text-gray-900">🗳️ {{ c.title }}</p>
        </router-link>

        <router-link v-for="g in section.glossaries" :key="g.id" :to="`/student/glossaries/${g.id}`"
          class="bg-indigo-50 border border-indigo-200 rounded-lg p-3 text-sm hover:border-indigo-400 transition-colors">
          <p class="font-medium text-gray-900">📖 {{ g.title }}</p>
        </router-link>

        <router-link v-for="w in section.wikis" :key="w.id" :to="`/student/wikis/${w.id}`"
          class="bg-cyan-50 border border-cyan-200 rounded-lg p-3 text-sm hover:border-cyan-400 transition-colors">
          <p class="font-medium text-gray-900">📚 {{ w.title }}</p>
        </router-link>

        <router-link v-for="l in section.lessons" :key="l.id" :to="`/student/lessons/${l.id}`"
          class="bg-rose-50 border border-rose-200 rounded-lg p-3 text-sm hover:border-rose-400 transition-colors">
          <p class="font-medium text-gray-900">📘 {{ l.title }} <span v-if="isComplete('lesson', l.id)">✓</span></p>
        </router-link>

        <router-link v-for="w in section.workshops" :key="w.id" :to="`/student/workshops/${w.id}`"
          class="bg-orange-50 border border-orange-200 rounded-lg p-3 text-sm hover:border-orange-400 transition-colors">
          <p class="font-medium text-gray-900">🛠️ {{ w.title }} <span v-if="isComplete('workshop', w.id)">✓</span></p>
        </router-link>

        <router-link v-for="ls in section.live_sessions" :key="ls.id" :to="`/student/live-sessions/${ls.id}`"
          class="bg-red-50 border border-red-200 rounded-lg p-3 text-sm hover:border-red-400 transition-colors">
          <p class="font-medium text-gray-900">🎥 {{ ls.title }} <span v-if="isComplete('live_session', ls.id)">✓</span></p>
        </router-link>

        <router-link v-for="iv in section.interactive_videos" :key="iv.id" :to="`/student/interactive-videos/${iv.id}`"
          class="bg-cyan-50 border border-cyan-200 rounded-lg p-3 text-sm hover:border-cyan-400 transition-colors">
          <p class="font-medium text-gray-900">🎬 {{ iv.title }} <span v-if="isComplete('interactive_video', iv.id)">✓</span></p>
        </router-link>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useCoursesStore } from '@/stores/courses'
import { useCompletionStore } from '@/stores/completion'
import AutoLinkedText from '@/components/AutoLinkedText.vue'

async function downloadFile(fileId, filename) {
  const resp = await axios.get(`/resource-files/${fileId}/download`, { responseType: 'blob' })
  const url = URL.createObjectURL(resp.data)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

const { t } = useI18n()
const route = useRoute()
const courses = useCoursesStore()
const completionStore = useCompletionStore()
const course = computed(() => courses.currentCourse)
const completion = ref(null)
const pageIndex = ref(0)

const displayedSections = computed(() => {
  if (!course.value) return []
  if (course.value.course_display === 'paginated') {
    return course.value.sections[pageIndex.value] ? [course.value.sections[pageIndex.value]] : []
  }
  return course.value.sections
})

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString()
}

function isComplete(itemType, itemId) {
  return completion.value?.items.some((i) => i.item_type === itemType && i.item_id === itemId && i.is_complete) ?? false
}

async function loadCompletion() {
  completion.value = await completionStore.fetchMine(route.params.id)
}

async function onToggleResource(resourceId, checked) {
  if (checked) await completionStore.markComplete(resourceId)
  else await completionStore.unmarkComplete(resourceId)
  await loadCompletion()
}

onMounted(async () => {
  await courses.fetchCourse(route.params.id)
  await loadCompletion()
})
</script>

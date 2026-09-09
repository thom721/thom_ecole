<template>
  <div v-if="lesson">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-lg font-bold text-gray-900">{{ lesson.title }}</h1>
      <router-link :to="`/teacher/lessons/${lessonId}/grading`" class="text-sm text-blue-600 hover:underline">
        {{ t('lesson.viewGrading') }}
      </router-link>
    </div>

    <!-- Réglages -->
    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('lesson.settingsTitle') }}</h2>
      <div class="grid grid-cols-2 gap-2">
        <input v-model="settings.password" :placeholder="t('lesson.passwordPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm" />
        <input v-model="settings.max_attempts_per_question" type="number" :placeholder="t('lesson.maxAttemptsPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm" />
        <input v-model="settings.time_limit_minutes" type="number" :placeholder="t('lesson.timeLimitPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm" />
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="settings.allow_retake" /> {{ t('lesson.allowRetake') }}
        </label>
      </div>
      <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold mt-2" @click="onSaveSettings">{{ t('common.save') }}</button>
    </div>

    <!-- Pages -->
    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('lesson.pagesTitle') }}</h2>
      <ul class="text-sm mb-3">
        <li v-for="(p, i) in lesson.pages" :key="p.id" class="flex items-center justify-between py-1 border-t border-gray-100 first:border-t-0">
          <span>{{ i + 1 }}. {{ p.title }} <span class="text-gray-400">({{ typeLabel(p.page_type) }})</span></span>
          <button class="text-red-600 text-xs" @click="onDeletePage(p.id)">{{ t('common.remove') }}</button>
        </li>
      </ul>
    </div>

    <!-- Ajouter une page -->
    <details class="bg-white border border-gray-200 rounded-xl p-4" open>
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('lesson.addPage') }}</summary>
      <div class="mt-3 space-y-2">
        <input v-model="newPage.title" :placeholder="t('common.title')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <select v-model="newPage.page_type" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="content">{{ t('lesson.typeContent') }}</option>
          <option value="true_false">{{ t('teacher.quizBuilder.typeTrueFalse') }}</option>
          <option value="multiple_choice">{{ t('teacher.quizBuilder.typeMultipleChoice') }}</option>
          <option value="short_answer">{{ t('teacher.quizBuilder.typeShortAnswer') }}</option>
          <option value="numerical">{{ t('teacher.quizBuilder.typeNumerical') }}</option>
          <option value="essay">{{ t('teacher.quizBuilder.typeEssay') }}</option>
        </select>
        <textarea v-model="newPage.content" :placeholder="t('lesson.contentPlaceholder')" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"></textarea>
        <input v-if="newPage.page_type !== 'content'" v-model="newPage.points" type="number" :placeholder="t('common.points')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm w-32" />

        <p v-if="newPage.page_type === 'short_answer' || newPage.page_type === 'numerical'" class="text-xs text-gray-500">
          {{ t('lesson.defaultAnswerHint') }}
        </p>

        <div v-if="newPage.page_type !== 'essay'">
          <div v-for="(a, i) in newPage.answers" :key="i" class="border border-gray-200 rounded-lg p-2 mb-2">
            <div class="flex items-center gap-2 mb-1">
              <input v-model="a.answer_text" :placeholder="answerPlaceholder" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
              <label v-if="newPage.page_type !== 'content'" class="text-xs flex items-center gap-1">
                <input type="checkbox" v-model="a.is_correct" /> {{ t('teacher.quizBuilder.correctLabel') }}
              </label>
              <input v-if="newPage.page_type === 'numerical'" v-model="a.tolerance" type="number" :placeholder="t('teacher.quizBuilder.tolerancePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
            </div>
            <div class="flex items-center gap-2">
              <select v-model="a.jump_type" class="border border-gray-300 rounded-lg px-2 py-1 text-xs">
                <option value="next_page">{{ t('lesson.jumpNextPage') }}</option>
                <option value="previous_page">{{ t('lesson.jumpPreviousPage') }}</option>
                <option value="specific_page">{{ t('lesson.jumpSpecificPage') }}</option>
                <option value="end_of_lesson">{{ t('lesson.jumpEndOfLesson') }}</option>
              </select>
              <select v-if="a.jump_type === 'specific_page'" v-model="a.jump_to_page_id" class="border border-gray-300 rounded-lg px-2 py-1 text-xs flex-1">
                <option value="">{{ t('lesson.choosePage') }}</option>
                <option v-for="p in lesson.pages" :key="p.id" :value="p.id">{{ p.title }}</option>
              </select>
              <button class="text-red-600 text-xs" @click="newPage.answers.splice(i, 1)">{{ t('common.remove') }}</button>
            </div>
          </div>
          <button class="text-xs text-blue-600" @click="addAnswerRow">{{ t('lesson.addAnswer') }}</button>
        </div>

        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold block mt-2" @click="onAddPage">{{ t('common.create') }}</button>
      </div>
    </details>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useLessonsStore } from '@/stores/lessons'

const { t } = useI18n()
const route = useRoute()
const lessonId = route.params.id
const lessons = useLessonsStore()

const lesson = ref(null)
const settings = reactive({ password: '', max_attempts_per_question: '', time_limit_minutes: '', allow_retake: true })

function blankAnswer() {
  return { answer_text: '', is_correct: false, tolerance: '', jump_type: 'next_page', jump_to_page_id: '', sort_order: 0 }
}

const newPage = reactive({ title: '', page_type: 'content', content: '', points: '1', answers: [blankAnswer()] })

const typeLabels = {
  content: 'typeContent', true_false: 'typeTrueFalse', multiple_choice: 'typeMultipleChoice',
  short_answer: 'typeShortAnswer', numerical: 'typeNumerical', essay: 'typeEssay',
}
function typeLabel(type) {
  const key = typeLabels[type] || 'typeContent'
  return key === 'typeContent' ? t('lesson.typeContent') : t(`teacher.quizBuilder.${key}`)
}

const answerPlaceholder = computed(() => {
  if (newPage.page_type === 'content') return t('lesson.buttonLabelPlaceholder')
  if (newPage.page_type === 'short_answer' || newPage.page_type === 'numerical') return t('lesson.candidateAnswerPlaceholder')
  return t('teacher.quizBuilder.optionPlaceholder')
})

function addAnswerRow() {
  newPage.answers.push(blankAnswer())
}

async function load() {
  lesson.value = await lessons.fetchLessonConfig(lessonId)
  settings.password = ''
  settings.max_attempts_per_question = lesson.value.max_attempts_per_question ?? ''
  settings.time_limit_minutes = lesson.value.time_limit_minutes ?? ''
  settings.allow_retake = lesson.value.allow_retake
}

async function onSaveSettings() {
  await lessons.updateLesson(lessonId, {
    max_attempts_per_question: settings.max_attempts_per_question === '' ? null : Number(settings.max_attempts_per_question),
    time_limit_minutes: settings.time_limit_minutes === '' ? null : Number(settings.time_limit_minutes),
    allow_retake: settings.allow_retake,
    ...(settings.password ? { password: settings.password } : {}),
  })
  await load()
}

async function onAddPage() {
  if (!newPage.title) return
  const answers = newPage.page_type === 'essay'
    ? [{ jump_type: 'next_page', sort_order: 0 }]
    : newPage.answers
        .filter((a) => a.answer_text || newPage.page_type === 'content')
        .map((a, i) => ({
          answer_text: a.answer_text || null,
          is_correct: !!a.is_correct,
          tolerance: newPage.page_type === 'numerical' && a.tolerance !== '' ? Number(a.tolerance) : null,
          jump_type: a.jump_type,
          jump_to_page_id: a.jump_type === 'specific_page' ? (a.jump_to_page_id || null) : null,
          sort_order: i,
        }))

  await lessons.addPage(lessonId, {
    page_type: newPage.page_type, title: newPage.title, content: newPage.content || null,
    points: Number(newPage.points) || 1, sort_order: lesson.value.pages.length, answers,
  })
  newPage.title = ''
  newPage.content = ''
  newPage.points = '1'
  newPage.answers = [blankAnswer()]
  await load()
}

async function onDeletePage(pageId) {
  await lessons.deletePage(pageId)
  await load()
}

onMounted(load)
</script>

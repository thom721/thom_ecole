<template>
  <div class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>

    <div v-if="loading" class="text-sm text-gray-500">{{ t('common.loading') }}</div>

    <div v-else-if="maxAttemptsReached && !attempt" class="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <p class="font-semibold text-gray-900 mb-2">{{ t('student.quizTake.maxAttemptsReached') }}</p>
      <div v-for="a in pastAttempts" :key="a.id" class="text-sm bg-white border border-gray-200 rounded-lg p-3 mt-2">
        <p>{{ t('student.quizTake.status', { status: a.status }) }}</p>
        <p v-if="a.score !== null">{{ t('student.quizTake.score', { score: a.score, max: a.max_score }) }}</p>
      </div>
    </div>

    <div v-else-if="attempt">
      <div v-if="attempt.status === 'graded'" class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
        <p class="font-semibold text-green-800">{{ t('student.quizTake.graded', { score: attempt.score, max: attempt.max_score }) }}</p>
      </div>
      <div v-else-if="attempt.status === 'pending_manual_grading'" class="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
        <p class="font-semibold text-amber-800">{{ t('student.quizTake.pendingManualGrading') }}</p>
      </div>

      <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('student.quizTake.title') }}</h1>

      <div v-for="q in attempt.questions" :key="q.question_id" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
        <p class="font-medium text-gray-900 mb-1">{{ q.question_text }}</p>
        <p class="text-xs text-gray-500 mb-3">{{ q.points }} {{ t('common.points') }}</p>

        <template v-if="attempt.status === 'in_progress'">
          <div v-if="q.question_type === 'multiple_choice' || q.question_type === 'true_false'">
            <label v-for="o in q.options" :key="o.id" class="flex items-center gap-2 text-sm mb-1">
              <input type="radio" :name="q.question_id" :value="o.id"
                v-model="answers[q.question_id].option_id"
                @change="onAnswer(q.question_id)" />
              {{ o.option_text }}
            </label>
          </div>

          <div v-else-if="q.question_type === 'short_answer'">
            <input v-model="answers[q.question_id].text" @blur="onAnswer(q.question_id)"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>

          <div v-else-if="q.question_type === 'essay'">
            <textarea v-model="answers[q.question_id].text" @blur="onAnswer(q.question_id)" rows="4"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"></textarea>
          </div>

          <div v-else-if="q.question_type === 'matching'">
            <div v-for="o in q.options" :key="o.id" class="flex items-center gap-2 text-sm mb-1">
              <span class="flex-1">{{ o.option_text }}</span>
              <input v-model="answers[q.question_id].pairs[o.id]" @blur="onAnswer(q.question_id)"
                class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" :placeholder="t('student.quizTake.answerPlaceholder')" />
            </div>
          </div>

          <div v-else-if="q.question_type === 'numerical' || q.question_type === 'calculated'">
            <input v-model="answers[q.question_id].value" type="number" step="any" @blur="onAnswer(q.question_id)"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" :placeholder="t('student.quizTake.numericAnswerPlaceholder')" />
          </div>

          <div v-else-if="q.question_type === 'ordering'">
            <p class="text-xs text-gray-500 mb-2">{{ t('student.quizTake.orderingHint') }}</p>
            <div v-for="(o, i) in answers[q.question_id].orderedOptions" :key="o.id"
              class="flex items-center gap-2 text-sm mb-1 bg-gray-50 rounded-lg px-2 py-1.5">
              <span class="text-gray-400 w-5">{{ i + 1 }}.</span>
              <span class="flex-1">{{ o.option_text }}</span>
              <button type="button" class="text-gray-500 disabled:opacity-30" :disabled="i === 0"
                @click="moveOrderingItem(q.question_id, i, -1)">↑</button>
              <button type="button" class="text-gray-500 disabled:opacity-30" :disabled="i === answers[q.question_id].orderedOptions.length - 1"
                @click="moveOrderingItem(q.question_id, i, 1)">↓</button>
            </div>
          </div>

          <div v-else-if="q.question_type === 'drag_and_drop'">
            <p class="text-xs text-gray-500 mb-2">{{ t('student.quizTake.dragDropHint') }}</p>
            <div class="flex flex-wrap gap-2 mb-3">
              <span v-for="o in q.options" :key="o.id" draggable="true"
                @dragstart="onDragStart(o.id)"
                class="bg-gray-100 border border-gray-300 rounded-lg px-2 py-1 text-sm cursor-move">
                {{ o.option_text }}
              </span>
            </div>
            <div v-for="o in q.options" :key="'zone-' + o.id"
              @dragover.prevent @drop="onDrop(q.question_id, o.match_text)"
              class="border-2 border-dashed border-gray-300 rounded-lg px-3 py-2 text-sm mb-1 min-h-10 flex items-center justify-between">
              <span class="text-gray-500">{{ o.match_text }}</span>
              <span class="font-medium">{{ labelForZone(q, o.match_text) }}</span>
            </div>
          </div>

          <div v-else-if="q.question_type === 'multianswer'" class="space-y-2">
            <div v-for="part in q.cloze_parts" :key="part.position" class="flex items-center gap-2">
              <span class="text-xs text-gray-400 w-6">[{{ part.position }}]</span>
              <input v-if="part.sub_type === 'short_answer'" v-model="answers[q.question_id].parts[part.position]"
                @blur="onAnswer(q.question_id)" class="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm" />
              <input v-else-if="part.sub_type === 'numerical'" v-model="answers[q.question_id].parts[part.position]"
                type="number" step="any" @blur="onAnswer(q.question_id)" class="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm" />
              <select v-else-if="part.sub_type === 'multiple_choice'" v-model="answers[q.question_id].parts[part.position]"
                @change="onAnswer(q.question_id)" class="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm">
                <option value="">…</option>
                <option v-for="(opt, idx) in part.options" :key="idx" :value="idx">{{ opt }}</option>
              </select>
            </div>
          </div>
        </template>

        <template v-else>
          <p class="text-sm text-gray-600">{{ t('student.quizTake.yourAnswer', { answer: formatAnswer(q) }) }}</p>
          <p v-if="q.is_correct !== undefined && q.is_correct !== null" class="text-xs mt-1"
             :class="q.is_correct ? 'text-green-600' : 'text-red-600'">
            {{ q.is_correct ? t('student.quizTake.correct') : t('student.quizTake.incorrect') }} — {{ t('student.quizTake.awardedOf', { awarded: q.points_awarded ?? '?', points: q.points }) }}
          </p>
          <p v-else-if="q.question_type === 'essay'" class="text-xs text-amber-600 mt-1">{{ t('student.quizTake.awaitingCorrection') }}</p>
          <p v-if="q.feedback" class="text-xs text-gray-500 mt-1">{{ q.feedback }}</p>
        </template>
      </div>

      <button v-if="attempt.status === 'in_progress'" class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold"
        @click="onSubmit">
        {{ t('student.quizTake.submitQuiz') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useQuizzesStore } from '@/stores/quizzes'

const { t } = useI18n()
const route = useRoute()
const quizzes = useQuizzesStore()

const loading = ref(true)
const attempt = ref(null)
const answers = reactive({})
const maxAttemptsReached = ref(false)
const pastAttempts = ref([])
let draggingOptionId = null

function initAnswers() {
  for (const q of attempt.value.questions) {
    answers[q.question_id] = {
      option_id: q.answer_data?.option_id ?? null,
      text: q.answer_data?.text ?? '',
      pairs: q.answer_data?.pairs ?? {},
      value: q.answer_data?.value ?? '',
      parts: q.answer_data?.parts ?? {},
      orderedOptions: q.question_type === 'ordering' ? [...q.options].sort((a, b) => a.sort_order - b.sort_order) : [],
    }
  }
}

function formatAnswer(q) {
  if (q.question_type === 'multianswer') {
    return (q.cloze_parts || []).map((p) => q.answer_data?.parts?.[p.position] ?? '?').join(' / ')
  }
  if (q.question_type === 'ordering') {
    const order = q.answer_data?.order || []
    return order.map((id) => q.options.find((o) => o.id === id)?.option_text ?? '?').join(' → ')
  }
  if (q.answer_data?.value !== undefined && q.answer_data?.value !== null) return String(q.answer_data.value)
  if (q.answer_data?.text) return q.answer_data.text
  if (q.answer_data?.option_id) {
    const o = q.options.find((opt) => opt.id === q.answer_data.option_id)
    return o?.option_text ?? t('student.quizTake.noAnswerShort')
  }
  if (q.answer_data?.pairs) return JSON.stringify(q.answer_data.pairs)
  return t('student.quizTake.noAnswer')
}

function labelForZone(q, matchText) {
  const entry = Object.entries(answers[q.question_id].pairs).find(([, v]) => v === matchText)
  if (!entry) return ''
  return q.options.find((o) => o.id === entry[0])?.option_text ?? ''
}

function onDragStart(optionId) {
  draggingOptionId = optionId
}

function onDrop(questionId, matchText) {
  if (!draggingOptionId) return
  answers[questionId].pairs[draggingOptionId] = matchText
  draggingOptionId = null
  onAnswer(questionId)
}

function moveOrderingItem(questionId, index, delta) {
  const list = answers[questionId].orderedOptions
  const target = index + delta
  if (target < 0 || target >= list.length) return
  ;[list[index], list[target]] = [list[target], list[index]]
  onAnswer(questionId)
}

async function onAnswer(questionId) {
  const a = answers[questionId]
  const q = attempt.value.questions.find((x) => x.question_id === questionId)
  let payload = {}
  if (q.question_type === 'multiple_choice' || q.question_type === 'true_false') payload = { option_id: a.option_id }
  else if (q.question_type === 'matching' || q.question_type === 'drag_and_drop') payload = { pairs: a.pairs }
  else if (q.question_type === 'numerical' || q.question_type === 'calculated') payload = { value: a.value === '' ? null : Number(a.value) }
  else if (q.question_type === 'ordering') payload = { order: a.orderedOptions.map((o) => o.id) }
  else if (q.question_type === 'multianswer') payload = { parts: a.parts }
  else payload = { text: a.text }
  await quizzes.saveResponse(attempt.value.id, questionId, payload)
}

async function onSubmit() {
  attempt.value = await quizzes.submitAttempt(attempt.value.id)
  attempt.value = await quizzes.fetchAttempt(attempt.value.id)
}

onMounted(async () => {
  try {
    const started = await quizzes.startAttempt(route.params.id)
    attempt.value = await quizzes.fetchAttempt(started.id)
    if (attempt.value.status === 'in_progress') initAnswers()
  } catch (e) {
    if (e.response?.status === 400) {
      maxAttemptsReached.value = true
      pastAttempts.value = await quizzes.fetchMyQuizAttempts(route.params.id)
    }
  } finally {
    loading.value = false
  }
})
</script>

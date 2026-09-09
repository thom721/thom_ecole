<template>
  <div v-if="quiz">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-lg font-bold text-gray-900">{{ quiz.title }}</h1>
      <router-link :to="`/teacher/quizzes/${quizId}/attempts`" class="text-sm text-blue-600 hover:underline">
        {{ t('teacher.quizBuilder.viewAttempts') }}
      </router-link>
    </div>

    <!-- Questions fixes -->
    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('teacher.quizBuilder.fixedQuestions') }}</h2>
      <ul class="text-sm mb-3">
        <li v-for="qq in quiz.quiz_questions" :key="qq.id" class="flex items-center justify-between py-1">
          <span>{{ qq.question_text }} ({{ typeLabel(qq.question_type) }})</span>
          <button class="text-red-600 text-xs" @click="onRemoveQuestion(qq.id)">{{ t('common.remove') }}</button>
        </li>
      </ul>
      <div class="flex gap-2">
        <select v-model="selectedQuestionId" class="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1">
          <option value="">{{ t('teacher.quizBuilder.chooseQuestion') }}</option>
          <option v-for="q in allQuestions" :key="q.id" :value="q.id">{{ q.question_text }} ({{ typeLabel(q.question_type) }})</option>
        </select>
        <button class="bg-gray-900 text-white rounded-lg px-3 py-2 text-sm font-semibold" @click="onAddQuestion">{{ t('common.add') }}</button>
      </div>
    </div>

    <!-- Règles de tirage -->
    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('teacher.quizBuilder.randomDraw') }}</h2>
      <ul class="text-sm mb-3">
        <li v-for="r in quiz.draw_rules" :key="r.id" class="flex items-center justify-between py-1">
          <span>{{ t('teacher.quizBuilder.questionsFromCategory', { count: r.count, category: categoryName(r.category_id) }) }}</span>
          <button class="text-red-600 text-xs" @click="onRemoveRule(r.id)">{{ t('common.remove') }}</button>
        </li>
      </ul>
      <div class="flex gap-2">
        <select v-model="drawCategoryId" class="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1">
          <option value="">{{ t('teacher.quizBuilder.categoryPlaceholder') }}</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <input v-model="drawCount" type="number" :placeholder="t('teacher.quizBuilder.countPlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm w-24" />
        <button class="bg-gray-900 text-white rounded-lg px-3 py-2 text-sm font-semibold" @click="onAddRule">{{ t('common.add') }}</button>
      </div>
      <p v-if="ruleError" class="text-xs text-red-600 mt-2">{{ ruleError }}</p>
    </div>

    <!-- Banque de questions -->
    <details class="bg-white border border-gray-200 rounded-xl p-4">
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('teacher.quizBuilder.questionBank') }}</summary>
      <div class="mt-3 space-y-2">
        <div class="flex gap-2">
          <input v-model="newCategoryName" :placeholder="t('teacher.quizBuilder.newCategoryPlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1" />
          <button class="bg-gray-100 rounded-lg px-3 py-2 text-sm" @click="onCreateCategory">{{ t('teacher.quizBuilder.addCategory') }}</button>
        </div>

        <select v-model="newQuestion.category_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="">{{ t('teacher.quizBuilder.categoryOptional') }}</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>

        <select v-model="newQuestion.question_type" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="multiple_choice">{{ t('teacher.quizBuilder.typeMultipleChoice') }}</option>
          <option value="true_false">{{ t('teacher.quizBuilder.typeTrueFalse') }}</option>
          <option value="short_answer">{{ t('teacher.quizBuilder.typeShortAnswer') }}</option>
          <option value="essay">{{ t('teacher.quizBuilder.typeEssay') }}</option>
          <option value="matching">{{ t('teacher.quizBuilder.typeMatching') }}</option>
          <option value="numerical">{{ t('teacher.quizBuilder.typeNumerical') }}</option>
          <option value="calculated">{{ t('teacher.quizBuilder.typeCalculated') }}</option>
          <option value="multianswer">{{ t('teacher.quizBuilder.typeMultianswer') }}</option>
          <option value="ordering">{{ t('teacher.quizBuilder.typeOrdering') }}</option>
          <option value="drag_and_drop">{{ t('teacher.quizBuilder.typeDragAndDrop') }}</option>
        </select>

        <textarea v-model="newQuestion.question_text" :placeholder="clozeTypes.includes(newQuestion.question_type) ? t('teacher.quizBuilder.clozeTextHint') : t('teacher.quizBuilder.questionTextPlaceholder')" rows="2"
          class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"></textarea>

        <!-- QCM / Vrai-Faux -->
        <div v-if="['multiple_choice', 'true_false'].includes(newQuestion.question_type)">
          <div v-for="(opt, i) in newQuestion.options" :key="i" class="flex items-center gap-2 mb-1">
            <input v-model="opt.option_text" :placeholder="t('teacher.quizBuilder.optionPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
            <label class="text-xs flex items-center gap-1">
              <input type="checkbox" v-model="opt.is_correct" /> {{ t('teacher.quizBuilder.correctLabel') }}
            </label>
          </div>
          <button class="text-xs text-blue-600" @click="addOptionRow">{{ t('teacher.quizBuilder.addOption') }}</button>
        </div>

        <!-- Réponse courte -->
        <div v-else-if="newQuestion.question_type === 'short_answer'">
          <input v-model="acceptedAnswersRaw" :placeholder="t('teacher.quizBuilder.acceptedAnswersPlaceholder')"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        </div>

        <!-- Appariement / glisser-déposer : mêmes paires option -> zone cible -->
        <div v-else-if="['matching', 'drag_and_drop'].includes(newQuestion.question_type)">
          <div v-for="(opt, i) in newQuestion.options" :key="i" class="flex items-center gap-2 mb-1">
            <input v-model="opt.option_text" :placeholder="t('teacher.quizBuilder.matchLeftPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
            <span class="text-gray-400 text-xs">→</span>
            <input v-model="opt.match_text" :placeholder="t('teacher.quizBuilder.matchRightPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          </div>
          <button class="text-xs text-blue-600" @click="addOptionRow">{{ t('teacher.quizBuilder.addOption') }}</button>
        </div>

        <!-- Remise en ordre -->
        <div v-else-if="newQuestion.question_type === 'ordering'">
          <p class="text-xs text-gray-500 mb-1">{{ t('teacher.quizBuilder.orderingHint') }}</p>
          <div v-for="(opt, i) in newQuestion.options" :key="i" class="flex items-center gap-2 mb-1">
            <span class="text-xs text-gray-400 w-5">{{ i + 1 }}.</span>
            <input v-model="opt.option_text" :placeholder="t('teacher.quizBuilder.optionPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          </div>
          <button class="text-xs text-blue-600" @click="addOptionRow">{{ t('teacher.quizBuilder.addOption') }}</button>
        </div>

        <!-- Numérique -->
        <div v-else-if="newQuestion.question_type === 'numerical'">
          <div v-for="(ans, i) in numericalAnswers" :key="i" class="flex items-center gap-2 mb-1">
            <input v-model="ans.value" type="number" :placeholder="t('teacher.quizBuilder.numericalValuePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
            <span class="text-gray-400 text-xs">±</span>
            <input v-model="ans.tolerance" type="number" :placeholder="t('teacher.quizBuilder.tolerancePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
          </div>
          <button class="text-xs text-blue-600" @click="numericalAnswers.push({ value: '', tolerance: '0' })">{{ t('teacher.quizBuilder.addAcceptedValue') }}</button>
        </div>

        <!-- Calculée -->
        <div v-else-if="newQuestion.question_type === 'calculated'" class="space-y-2">
          <p class="text-xs text-gray-500">{{ t('teacher.quizBuilder.calculatedHint') }}</p>
          <div class="flex items-center gap-2">
            <input v-model="calculatedFormula" :placeholder="t('teacher.quizBuilder.calculatedFormulaPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
            <span class="text-gray-400 text-xs">±</span>
            <input v-model="calculatedTolerance" type="number" :placeholder="t('teacher.quizBuilder.tolerancePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
          </div>
          <div v-for="(ds, i) in calculatedDatasets" :key="i" class="flex items-center gap-2">
            <input v-model="ds.variable_name" :placeholder="t('teacher.quizBuilder.variableNamePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
            <input v-model="ds.valuesRaw" :placeholder="t('teacher.quizBuilder.variableValuesPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          </div>
          <button class="text-xs text-blue-600" @click="calculatedDatasets.push({ variable_name: '', valuesRaw: '' })">{{ t('teacher.quizBuilder.addVariable') }}</button>
        </div>

        <!-- Texte à trous (cloze / multianswer) -->
        <div v-else-if="newQuestion.question_type === 'multianswer'" class="space-y-3">
          <p class="text-xs text-gray-500">{{ t('teacher.quizBuilder.clozeHint') }}</p>
          <div v-for="(part, i) in clozeParts" :key="i" class="border border-gray-200 rounded-lg p-2">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-xs text-gray-400 w-6">[{{ i }}]</span>
              <select v-model="part.sub_type" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1">
                <option value="short_answer">{{ t('teacher.quizBuilder.typeShortAnswer') }}</option>
                <option value="numerical">{{ t('teacher.quizBuilder.typeNumerical') }}</option>
                <option value="multiple_choice">{{ t('teacher.quizBuilder.typeMultipleChoice') }}</option>
              </select>
              <input v-model.number="part.points" type="number" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-20" :placeholder="t('common.points')" />
            </div>
            <input v-if="part.sub_type === 'short_answer'" v-model="part.acceptedRaw"
              :placeholder="t('teacher.quizBuilder.acceptedAnswersPlaceholder')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
            <div v-else-if="part.sub_type === 'numerical'" class="flex items-center gap-2">
              <input v-model="part.numValue" type="number" :placeholder="t('teacher.quizBuilder.numericalValuePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
              <span class="text-gray-400 text-xs">±</span>
              <input v-model="part.numTolerance" type="number" :placeholder="t('teacher.quizBuilder.tolerancePlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm w-24" />
            </div>
            <div v-else-if="part.sub_type === 'multiple_choice'">
              <input v-model="part.mcOptionsRaw" :placeholder="t('teacher.quizBuilder.mcOptionsPlaceholder')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm mb-1" />
              <input v-model.number="part.mcCorrectIndex" type="number" min="0" :placeholder="t('teacher.quizBuilder.mcCorrectIndexPlaceholder')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
            </div>
          </div>
          <button class="text-xs text-blue-600" @click="clozeParts.push({ position: clozeParts.length, sub_type: 'short_answer', points: 1, acceptedRaw: '', numValue: '', numTolerance: '0', mcOptionsRaw: '', mcCorrectIndex: 0 })">
            {{ t('teacher.quizBuilder.addClozePart') }}
          </button>
        </div>

        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onCreateQuestion">{{ t('teacher.quizBuilder.createQuestion') }}</button>
        <p v-if="questionError" class="text-xs text-red-600">{{ questionError }}</p>
      </div>
    </details>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useQuizzesStore } from '@/stores/quizzes'

const { t } = useI18n()
const route = useRoute()
const quizId = route.params.id
const quizzes = useQuizzesStore()

const quiz = ref(null)
const allQuestions = ref([])
const categories = ref([])

const selectedQuestionId = ref('')
const drawCategoryId = ref('')
const drawCount = ref('')
const ruleError = ref('')

const clozeTypes = ['multianswer']
const optionBasedTypes = ['multiple_choice', 'true_false', 'matching', 'ordering', 'drag_and_drop']

const newCategoryName = ref('')
const newQuestion = reactive({
  category_id: '', question_type: 'multiple_choice', question_text: '',
  options: [{ option_text: '', match_text: '', is_correct: false, sort_order: 0 }],
})
const acceptedAnswersRaw = ref('')
const numericalAnswers = ref([{ value: '', tolerance: '0' }])
const calculatedFormula = ref('')
const calculatedTolerance = ref('0')
const calculatedDatasets = ref([{ variable_name: '', valuesRaw: '' }])
const clozeParts = ref([{ position: 0, sub_type: 'short_answer', points: 1, acceptedRaw: '', numValue: '', numTolerance: '0', mcOptionsRaw: '', mcCorrectIndex: 0 }])
const questionError = ref('')

const typeLabels = {
  multiple_choice: 'typeMultipleChoice', true_false: 'typeTrueFalse', short_answer: 'typeShortAnswer',
  essay: 'typeEssay', matching: 'typeMatching', numerical: 'typeNumerical', calculated: 'typeCalculated',
  multianswer: 'typeMultianswer', ordering: 'typeOrdering', drag_and_drop: 'typeDragAndDrop',
}
function typeLabel(type) {
  return t(`teacher.quizBuilder.${typeLabels[type] || 'typeEssay'}`)
}

function categoryName(id) {
  return categories.value.find((c) => c.id === id)?.name || '?'
}

function addOptionRow() {
  newQuestion.options.push({ option_text: '', match_text: '', is_correct: false, sort_order: newQuestion.options.length })
}

function resetQuestionForm() {
  newQuestion.question_text = ''
  newQuestion.options = [{ option_text: '', match_text: '', is_correct: false, sort_order: 0 }]
  acceptedAnswersRaw.value = ''
  numericalAnswers.value = [{ value: '', tolerance: '0' }]
  calculatedFormula.value = ''
  calculatedTolerance.value = '0'
  calculatedDatasets.value = [{ variable_name: '', valuesRaw: '' }]
  clozeParts.value = [{ position: 0, sub_type: 'short_answer', points: 1, acceptedRaw: '', numValue: '', numTolerance: '0', mcOptionsRaw: '', mcCorrectIndex: 0 }]
}

async function loadAll() {
  quiz.value = await quizzes.fetchQuizConfig(quizId)
  const courseId = quiz.value.course_id
  categories.value = await quizzes.fetchCourseQuestionCategories(courseId)
  allQuestions.value = await quizzes.fetchCourseQuestions(courseId)
}

async function onAddQuestion() {
  if (!selectedQuestionId.value) return
  await quizzes.addQuizQuestion(quizId, { question_id: selectedQuestionId.value, sort_order: quiz.value.quiz_questions.length })
  selectedQuestionId.value = ''
  await loadAll()
}

async function onRemoveQuestion(quizQuestionId) {
  await quizzes.removeQuizQuestion(quizQuestionId)
  await loadAll()
}

async function onAddRule() {
  ruleError.value = ''
  if (!drawCategoryId.value || !drawCount.value) return
  try {
    await quizzes.addDrawRule(quizId, { category_id: drawCategoryId.value, count: Number(drawCount.value), sort_order: quiz.value.draw_rules.length })
    drawCategoryId.value = ''
    drawCount.value = ''
    await loadAll()
  } catch (e) {
    ruleError.value = e.response?.data?.detail || t('common.error')
  }
}

async function onRemoveRule(ruleId) {
  await quizzes.removeDrawRule(ruleId)
  await loadAll()
}

async function onCreateCategory() {
  if (!newCategoryName.value) return
  await quizzes.createQuestionCategory(quiz.value.course_id, { name: newCategoryName.value })
  newCategoryName.value = ''
  categories.value = await quizzes.fetchCourseQuestionCategories(quiz.value.course_id)
}

async function onCreateQuestion() {
  questionError.value = ''
  const type = newQuestion.question_type
  const payload = {
    category_id: newQuestion.category_id || null,
    question_type: type,
    question_text: newQuestion.question_text,
    options: optionBasedTypes.includes(type) ? newQuestion.options : [],
    accepted_answers: type === 'short_answer'
      ? acceptedAnswersRaw.value.split(',').map((s) => s.trim()).filter(Boolean)
      : [],
    numerical_answers: type === 'numerical'
      ? numericalAnswers.value.filter((a) => a.value !== '').map((a) => ({ value: Number(a.value), tolerance: Number(a.tolerance || 0) }))
      : [],
    calculated_formula: type === 'calculated' ? calculatedFormula.value : null,
    calculated_tolerance: type === 'calculated' ? Number(calculatedTolerance.value || 0) : null,
    calculated_datasets: type === 'calculated'
      ? calculatedDatasets.value.filter((d) => d.variable_name).map((d) => ({
          variable_name: d.variable_name,
          values: d.valuesRaw.split(',').map((v) => Number(v.trim())).filter((v) => !Number.isNaN(v)),
        }))
      : [],
    cloze_parts: type === 'multianswer'
      ? clozeParts.value.map((p, i) => {
          let correct_answers = {}
          if (p.sub_type === 'short_answer') correct_answers = { accepted: p.acceptedRaw.split(',').map((s) => s.trim()).filter(Boolean) }
          else if (p.sub_type === 'numerical') correct_answers = { value: Number(p.numValue), tolerance: Number(p.numTolerance || 0) }
          else if (p.sub_type === 'multiple_choice') correct_answers = { options: p.mcOptionsRaw.split(',').map((s) => s.trim()).filter(Boolean), correct_index: p.mcCorrectIndex }
          return { position: i, sub_type: p.sub_type, correct_answers, points: p.points || 1 }
        })
      : [],
  }
  try {
    await quizzes.createQuestion(quiz.value.course_id, payload)
    resetQuestionForm()
    allQuestions.value = await quizzes.fetchCourseQuestions(quiz.value.course_id)
  } catch (e) {
    questionError.value = e.response?.data?.detail || t('common.error')
  }
}

onMounted(loadAll)
</script>

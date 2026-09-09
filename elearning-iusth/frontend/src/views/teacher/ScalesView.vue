<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('scales.title') }}</h1>

    <div class="grid grid-cols-2 gap-6">
      <div>
        <h2 class="font-semibold text-gray-900 mb-3">{{ t('scales.scalesTitle') }}</h2>
        <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
          <input v-model="newScaleName" :placeholder="t('scales.namePlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-2" />
          <div v-for="(lvl, i) in newLevels" :key="i" class="flex items-center gap-2 mb-1">
            <span class="text-xs text-gray-400 w-5">{{ i + 1 }}.</span>
            <input v-model="lvl.label" :placeholder="t('scales.levelPlaceholder')" class="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          </div>
          <button class="text-xs text-blue-600 mb-2" @click="newLevels.push({ label: '' })">{{ t('scales.addLevel') }}</button>
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold block" @click="onCreateScale">{{ t('common.create') }}</button>
          <p v-if="error" class="text-xs text-red-600 mt-2">{{ error }}</p>
        </div>

        <div v-for="s in scales" :key="s.id" class="bg-white border border-gray-200 rounded-xl p-3 mb-2">
          <div class="flex items-center justify-between mb-1">
            <p class="font-medium text-gray-900">{{ s.name }} <span v-if="!s.course_id" class="text-xs text-gray-400">({{ t('scales.siteWide') }})</span></p>
            <button class="text-red-600 text-xs" @click="onDeleteScale(s.id)">{{ t('common.remove') }}</button>
          </div>
          <p class="text-xs text-gray-500">{{ s.levels.map(l => l.label).join(' → ') }}</p>
        </div>
      </div>

      <div>
        <h2 class="font-semibold text-gray-900 mb-3">{{ t('scales.lettersTitle') }}</h2>
        <div class="bg-white border border-gray-200 rounded-xl p-4">
          <p class="text-xs text-gray-500 mb-3">{{ t('scales.lettersHint') }}</p>
          <div v-for="(l, i) in letters" :key="i" class="flex items-center gap-2 mb-2">
            <input v-model="l.letter" :placeholder="t('scales.letterPlaceholder')" class="w-32 border border-gray-300 rounded-lg px-2 py-1 text-sm" />
            <span class="text-gray-400 text-xs">≥</span>
            <input v-model="l.lower_boundary" type="number" min="0" max="100" class="w-20 border border-gray-300 rounded-lg px-2 py-1 text-sm" />
            <span class="text-gray-400 text-xs">%</span>
            <button class="text-red-600 text-xs" @click="letters.splice(i, 1)">{{ t('common.remove') }}</button>
          </div>
          <button class="text-xs text-blue-600 mb-3 block" @click="letters.push({ letter: '', lower_boundary: 0 })">{{ t('scales.addLetter') }}</button>
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onSaveLetters">{{ t('common.save') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useScalesStore } from '@/stores/scales'

const { t } = useI18n()
const route = useRoute()
const scalesStore = useScalesStore()

const scales = ref([])
const letters = ref([])
const newScaleName = ref('')
const newLevels = ref([{ label: '' }, { label: '' }])
const error = ref('')

async function load() {
  scales.value = await scalesStore.fetchScales(route.params.id)
  letters.value = await scalesStore.fetchGradeLetters(route.params.id)
}

async function onCreateScale() {
  error.value = ''
  const levels = newLevels.value
    .map((l, i) => ({ label: l.label, rank: i + 1, sort_order: i }))
    .filter((l) => l.label)
  if (!newScaleName.value || !levels.length) return
  try {
    await scalesStore.createScale(route.params.id, { name: newScaleName.value, levels })
    newScaleName.value = ''
    newLevels.value = [{ label: '' }, { label: '' }]
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  }
}

async function onDeleteScale(id) {
  try {
    await scalesStore.deleteScale(id)
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  }
}

async function onSaveLetters() {
  await scalesStore.replaceGradeLetters(route.params.id, letters.value.map((l) => ({
    letter: l.letter, lower_boundary: Number(l.lower_boundary),
  })))
  await load()
}

onMounted(load)
</script>

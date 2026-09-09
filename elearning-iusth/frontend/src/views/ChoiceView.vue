<template>
  <div v-if="choice" class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-1">{{ choice.title }}</h1>
    <p v-if="choice.description" class="text-sm text-gray-500 mb-6">{{ choice.description }}</p>

    <div v-if="choice.access_restricted" class="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4">
      <p class="text-sm text-amber-800 font-medium mb-1">{{ t('access.restrictedTitle') }}</p>
      <ul class="text-xs text-amber-700 list-disc list-inside">
        <li v-for="(r, i) in choice.access_reasons" :key="i">{{ r }}</li>
      </ul>
    </div>

    <div v-else class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <div v-if="!hasAnswered || choice.allow_update" class="space-y-2 mb-3">
        <label v-for="o in choice.options" :key="o.id" class="flex items-center gap-2 text-sm">
          <input v-if="choice.allow_multiple" type="checkbox" :value="o.id" v-model="selected" />
          <input v-else type="radio" :checked="selected.includes(o.id)" @change="selected = [o.id]" />
          {{ o.option_text }}
        </label>
        <label v-if="choice.show_unanswered" class="flex items-center gap-2 text-sm text-gray-500">
          <input type="radio" :checked="selected.length === 0" @change="selected = []" />
          {{ t('choice.noAnswerOption') }}
        </label>
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold mt-2" @click="onRespond">
          {{ hasAnswered ? t('choice.updateResponse') : t('choice.respond') }}
        </button>
        <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
      </div>
      <p v-else class="text-sm text-green-700 mb-3">{{ t('choice.alreadyAnswered') }}</p>
    </div>

    <div v-if="choice.results_visible" class="bg-white border border-gray-200 rounded-xl p-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('choice.resultsTitle') }}</h2>
      <div v-for="o in choice.options" :key="'r-' + o.id" class="mb-3">
        <div class="flex items-center justify-between text-sm mb-1">
          <span :class="{ 'font-semibold': choice.my_answer_option_ids.includes(o.id) }">{{ o.option_text }}</span>
          <span class="text-gray-500">{{ o.vote_count ?? 0 }}</span>
        </div>
        <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
          <div class="h-full bg-gray-900" :style="{ width: percentFor(o) + '%' }"></div>
        </div>
        <p v-if="o.respondents?.length" class="text-xs text-gray-400 mt-1">{{ o.respondents.join(', ') }}</p>
      </div>
    </div>
    <p v-else class="text-xs text-gray-400">{{ t('choice.resultsHidden') }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useChoicesStore } from '@/stores/choices'

const { t } = useI18n()
const route = useRoute()
const choices = useChoicesStore()

const choice = ref(null)
const selected = ref([])
const error = ref('')

const hasAnswered = computed(() => (choice.value?.my_answer_option_ids?.length ?? 0) > 0)
const totalVotes = computed(() => (choice.value?.options ?? []).reduce((sum, o) => sum + (o.vote_count ?? 0), 0))

function percentFor(option) {
  if (!totalVotes.value) return 0
  return Math.round(((option.vote_count ?? 0) / totalVotes.value) * 100)
}

async function load() {
  choice.value = await choices.fetchChoice(route.params.id)
  selected.value = [...choice.value.my_answer_option_ids]
}

async function onRespond() {
  error.value = ''
  try {
    if (selected.value.length === 0 && choice.value.show_unanswered) {
      choice.value = await choices.retract(route.params.id)
    } else {
      choice.value = await choices.respond(route.params.id, selected.value)
    }
    selected.value = [...choice.value.my_answer_option_ids]
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  }
}

onMounted(load)
</script>

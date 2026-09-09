<template>
  <div v-if="glossary" class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-1">{{ glossary.title }}</h1>
    <p v-if="glossary.description" class="text-sm text-gray-500 mb-6">{{ glossary.description }}</p>

    <details v-if="canAddEntry" class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('glossary.addEntry') }}</summary>
      <div class="mt-3 space-y-2">
        <input v-model="newConcept" :placeholder="t('glossary.conceptPlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <textarea v-model="newDefinition" :placeholder="t('glossary.definitionPlaceholder')" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"></textarea>
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onCreateEntry">{{ t('common.create') }}</button>
        <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
      </div>
    </details>

    <div v-for="e in glossary.entries" :key="e.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-2">
      <div class="flex items-center justify-between">
        <p class="font-semibold text-gray-900">{{ e.concept }}</p>
        <span v-if="!e.is_approved" class="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">{{ t('glossary.pending') }}</span>
      </div>
      <p class="text-sm text-gray-600 mt-1">{{ e.definition }}</p>
      <button v-if="!e.is_approved && isTeaching" class="text-xs text-blue-600 hover:underline mt-2" @click="onApprove(e.id)">
        {{ t('glossary.approve') }}
      </button>
    </div>
    <p v-if="!glossary.entries.length" class="text-sm text-gray-500">{{ t('glossary.empty') }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useGlossariesStore } from '@/stores/glossaries'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const route = useRoute()
const glossaries = useGlossariesStore()
const auth = useAuthStore()

const glossary = ref(null)
const newConcept = ref('')
const newDefinition = ref('')
const error = ref('')

const isTeaching = computed(() => auth.isTeacher || auth.isAdmin)
const canAddEntry = computed(() => isTeaching.value || glossary.value?.allow_student_entries)

async function load() {
  glossary.value = await glossaries.fetchGlossary(route.params.id)
}

async function onCreateEntry() {
  error.value = ''
  if (!newConcept.value || !newDefinition.value) return
  try {
    await glossaries.createEntry(route.params.id, { concept: newConcept.value, definition: newDefinition.value })
    newConcept.value = ''
    newDefinition.value = ''
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  }
}

async function onApprove(entryId) {
  await glossaries.approveEntry(entryId)
  await load()
}

onMounted(load)
</script>

<template>
  <div v-if="entry" class="max-w-lg">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <div class="bg-white border border-gray-200 rounded-xl p-4">
      <h1 class="text-lg font-bold text-gray-900 mb-2">{{ entry.concept }}</h1>
      <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ entry.definition }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useGlossariesStore } from '@/stores/glossaries'

const { t } = useI18n()
const route = useRoute()
const glossaries = useGlossariesStore()
const entry = ref(null)

onMounted(async () => {
  entry.value = await glossaries.fetchEntry(route.params.id)
})
</script>

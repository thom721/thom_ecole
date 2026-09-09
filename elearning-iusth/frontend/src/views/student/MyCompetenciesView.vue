<template>
  <div>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('competency.myCompetenciesTitle') }}</h1>

    <div v-for="c in competencies" :key="c.competency_id" class="bg-white border border-gray-200 rounded-xl p-4 mb-3">
      <div class="flex items-center justify-between">
        <p class="font-medium text-gray-900">{{ c.competency_name }}</p>
        <span class="text-xs px-2 py-0.5 rounded-full" :class="c.proficiency ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
          {{ c.proficiency ? t('competency.proficientYes') : t('competency.proficientNo') }}
        </span>
      </div>
      <details class="text-xs mt-2">
        <summary class="cursor-pointer text-gray-500">{{ t('competency.evidenceHistory') }}</summary>
        <ul class="mt-1 space-y-1">
          <li v-for="e in c.evidence" :key="e.id" class="text-gray-600">
            {{ t(`competency.evidenceAction.${e.action}`) }}
            <span v-if="e.grade_rank !== null"> — {{ t('competency.rank') }} {{ e.grade_rank }}</span>
            <span v-if="e.note"> — {{ e.note }}</span>
          </li>
        </ul>
      </details>
    </div>
    <p v-if="!competencies.length" class="text-sm text-gray-500">{{ t('competency.noCompetencies') }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCompetenciesStore } from '@/stores/competencies'

const { t } = useI18n()
const store = useCompetenciesStore()
const competencies = ref([])

onMounted(async () => {
  competencies.value = await store.fetchMyCompetencies()
})
</script>

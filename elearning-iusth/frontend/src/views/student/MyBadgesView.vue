<template>
  <div>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('badges.myBadgesTitle') }}</h1>

    <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div v-for="b in badges" :key="b.id" class="bg-white border border-gray-200 rounded-xl p-4 text-center"
        :class="b.is_earned ? '' : 'opacity-50'">
        <p class="text-3xl mb-2">{{ b.image_emoji || '🏅' }}</p>
        <p class="font-medium text-gray-900 text-sm">{{ b.name }}</p>
        <p v-if="b.description" class="text-xs text-gray-500 mt-1">{{ b.description }}</p>
        <p v-if="b.is_earned" class="text-xs text-green-700 mt-2">{{ t('badges.earnedOn', { date: formatDate(b.issued_at) }) }}</p>
        <div v-else class="mt-2 text-xs text-gray-500 text-left">
          <p v-for="p in b.criteria_progress" :key="p.criteria_type">
            {{ p.met ? '✓' : '○' }} {{ t(`badges.criteriaType.${p.criteria_type}`) }}
          </p>
        </div>
      </div>
    </div>
    <p v-if="!badges.length" class="text-sm text-gray-500">{{ t('badges.noBadges') }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useBadgesStore } from '@/stores/badges'

const { t } = useI18n()
const badgesStore = useBadgesStore()
const badges = ref([])

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString()
}

onMounted(async () => {
  badges.value = await badgesStore.fetchMyBadges()
})
</script>

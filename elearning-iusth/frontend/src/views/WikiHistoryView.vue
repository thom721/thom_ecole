<template>
  <div class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('wiki.history') }}</h1>

    <table class="w-full text-sm bg-white border border-gray-200 rounded-xl overflow-hidden mb-6">
      <thead class="bg-gray-50 text-left text-xs text-gray-500">
        <tr>
          <th class="px-3 py-2">{{ t('wiki.version') }}</th>
          <th class="px-3 py-2">{{ t('wiki.date') }}</th>
          <th class="px-3 py-2 text-center">{{ t('wiki.compareFrom') }}</th>
          <th class="px-3 py-2 text-center">{{ t('wiki.compareTo') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="v in versions" :key="v.version" class="border-t border-gray-100">
          <td class="px-3 py-2 font-medium">v{{ v.version }}</td>
          <td class="px-3 py-2 text-gray-500">{{ new Date(v.created_at).toLocaleString(locale === 'en' ? 'en-US' : 'fr-FR') }}</td>
          <td class="px-3 py-2 text-center"><input type="radio" :value="v.version" v-model="fromVersion" /></td>
          <td class="px-3 py-2 text-center"><input type="radio" :value="v.version" v-model="toVersion" /></td>
        </tr>
      </tbody>
    </table>

    <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold mb-4" :disabled="!fromVersion || !toVersion" @click="onCompare">
      {{ t('wiki.compare') }}
    </button>

    <pre v-if="diff" class="bg-gray-900 text-gray-100 rounded-xl p-4 text-xs overflow-x-auto"><span
      v-for="(line, i) in diff.lines" :key="i"
      :class="lineClass(line)">{{ line }}
</span></pre>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useWikisStore } from '@/stores/wikis'

const { t, locale } = useI18n()
const route = useRoute()
const wikis = useWikisStore()

const versions = ref([])
const fromVersion = ref(null)
const toVersion = ref(null)
const diff = ref(null)

function lineClass(line) {
  if (line.startsWith('+') && !line.startsWith('+++')) return 'text-green-400'
  if (line.startsWith('-') && !line.startsWith('---')) return 'text-red-400'
  if (line.startsWith('@@')) return 'text-blue-400'
  return 'text-gray-400'
}

async function onCompare() {
  diff.value = await wikis.fetchDiff(route.params.id, fromVersion.value, toVersion.value)
}

onMounted(async () => {
  versions.value = await wikis.fetchVersions(route.params.id)
  if (versions.value.length >= 2) {
    toVersion.value = versions.value[0].version
    fromVersion.value = versions.value[1].version
  }
})
</script>

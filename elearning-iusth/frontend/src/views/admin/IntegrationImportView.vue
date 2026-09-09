<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-lg font-bold text-gray-900 mb-1">{{ t('admin.integrationImport.title') }}</h1>
    <p class="text-sm text-gray-500 mb-6">
      {{ t('admin.integrationImport.subtitle') }}
    </p>

    <div class="bg-white border border-gray-200 rounded-xl p-4">
      <label class="block text-xs text-gray-600 mb-1">{{ t('admin.integrationImport.yearLabel') }}</label>
      <select v-model="selectedAnnee" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3">
        <option value="">{{ t('admin.integrationImport.yearPlaceholder') }}</option>
        <option v-for="a in annees" :key="a.id" :value="a.id">{{ a.label }} ({{ a.date_debut }} → {{ a.date_fin }})</option>
      </select>

      <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-50"
        :disabled="!selectedAnnee || loading" @click="onImport">
        {{ loading ? t('admin.integrationImport.importing') : t('admin.integrationImport.importButton') }}
      </button>
      <p v-if="error" class="text-xs text-red-600 mt-2">{{ error }}</p>
    </div>

    <div v-if="result" class="space-y-3 mt-4">
      <div class="bg-green-50 border border-green-200 rounded-xl p-4">
        <p class="font-semibold text-green-800">
          {{ t('admin.integrationImport.resultSummary', { created: result.imported_count, updated: result.updated_count }) }}
        </p>
      </div>

      <div v-if="result.accounts_created.length" class="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <p class="text-xs font-semibold text-blue-700 mb-1">
          {{ t('admin.integrationImport.accountsCreatedTitle', { count: result.accounts_created.length }) }}
        </p>
        <ul class="text-xs text-blue-700 list-disc list-inside space-y-0.5">
          <li v-for="(a, i) in result.accounts_created" :key="i">{{ a }}</li>
        </ul>
      </div>

      <div v-if="result.warnings.length" class="bg-amber-50 border border-amber-200 rounded-xl p-4">
        <p class="text-xs font-semibold text-amber-700 mb-1">{{ t('admin.integrationImport.warningsTitle') }}</p>
        <ul class="text-xs text-amber-700 list-disc list-inside space-y-0.5">
          <li v-for="(w, i) in result.warnings" :key="i">{{ w }}</li>
        </ul>
      </div>
    </div>

    <div class="bg-white border border-gray-200 rounded-xl p-4 mt-6">
      <h2 class="font-semibold text-gray-900 mb-1">{{ t('admin.integrationImport.credentialsSyncTitle') }}</h2>
      <p class="text-xs text-gray-500 mb-3">{{ t('admin.integrationImport.credentialsSyncSubtitle') }}</p>

      <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-50"
        :disabled="syncingCredentials" @click="onSyncCredentials">
        {{ syncingCredentials ? t('admin.integrationImport.syncing') : t('admin.integrationImport.syncButton') }}
      </button>
      <p v-if="credentialsError" class="text-xs text-red-600 mt-2">{{ credentialsError }}</p>

      <div v-if="credentialsResult" class="mt-3 space-y-2">
        <p class="text-xs text-green-700">
          {{ t('admin.integrationImport.credentialsCreated', { count: credentialsResult.accounts_created.length }) }}
        </p>
        <p class="text-xs text-gray-500">
          {{ t('admin.integrationImport.credentialsSkipped', { count: credentialsResult.skipped_existing.length }) }}
        </p>
        <ul v-if="credentialsResult.accounts_created.length" class="text-xs text-green-700 list-disc list-inside space-y-0.5">
          <li v-for="(a, i) in credentialsResult.accounts_created" :key="i">{{ a }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useIntegrationStore } from '@/stores/integration'

const { t } = useI18n()
const integration = useIntegrationStore()
const annees = ref([])
const selectedAnnee = ref('')
const loading = ref(false)
const error = ref('')
const result = ref(null)
const syncingCredentials = ref(false)
const credentialsError = ref('')
const credentialsResult = ref(null)

onMounted(async () => {
  try {
    annees.value = await integration.fetchEcoleNginxAnnees()
  } catch (e) {
    error.value = e.response?.data?.detail || t('admin.integrationImport.unreachableError')
  }
})

async function onImport() {
  error.value = ''
  result.value = null
  loading.value = true
  try {
    result.value = await integration.importFromEcoleNginx(selectedAnnee.value)
  } catch (e) {
    error.value = e.response?.data?.detail || t('admin.integrationImport.importError')
  } finally {
    loading.value = false
  }
}

async function onSyncCredentials() {
  credentialsError.value = ''
  credentialsResult.value = null
  syncingCredentials.value = true
  try {
    credentialsResult.value = await integration.syncStaffCredentials()
  } catch (e) {
    credentialsError.value = e.response?.data?.detail || t('admin.integrationImport.syncError')
  } finally {
    syncingCredentials.value = false
  }
}
</script>

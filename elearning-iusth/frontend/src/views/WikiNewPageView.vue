<template>
  <div class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-1">{{ t('wiki.createPage') }}</h1>
    <p class="text-sm text-gray-500 mb-6">{{ t('wiki.createPageHint', { title }) }}</p>

    <div class="bg-white border border-gray-200 rounded-xl p-4">
      <textarea v-model="content" rows="10" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3"
        :placeholder="t('wiki.editHint')"></textarea>
      <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onCreate">{{ t('common.create') }}</button>
      <p v-if="error" class="text-xs text-red-600 mt-2">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useWikisStore } from '@/stores/wikis'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const wikis = useWikisStore()

const title = computed(() => route.query.title || '')
const subwikiId = computed(() => route.query.subwiki_id || '')
const content = ref('')
const error = ref('')
const basePath = route.path.startsWith('/teacher') ? '/teacher' : '/student'

async function onCreate() {
  error.value = ''
  try {
    const page = await wikis.createPage(subwikiId.value, { title: title.value, content: content.value })
    router.replace(`${basePath}/wiki-pages/${page.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || t('common.error')
  }
}
</script>

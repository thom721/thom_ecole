<template>
  <div v-if="page" class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-lg font-bold text-gray-900">{{ page.title }}</h1>
      <div class="flex gap-3 text-sm">
        <router-link :to="historyPath" class="text-blue-600 hover:underline">{{ t('wiki.history') }}</router-link>
        <button v-if="!editing && !page.is_readonly" class="text-blue-600 hover:underline" @click="startEdit">{{ t('wiki.edit') }}</button>
      </div>
    </div>

    <div v-if="!editing" class="bg-white border border-gray-200 rounded-xl p-4">
      <WikiLinkedContent :text="page.cached_content" :subwiki-id="page.subwiki_id" />
      <p v-if="!page.cached_content" class="text-sm text-gray-400 italic">{{ t('wiki.emptyPage') }}</p>
    </div>

    <div v-else class="bg-white border border-gray-200 rounded-xl p-4">
      <textarea v-model="draft" rows="10" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3"
        :placeholder="t('wiki.editHint')"></textarea>
      <div class="flex gap-2">
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onSave">{{ t('common.save') }}</button>
        <button class="text-sm text-gray-500" @click="editing = false">{{ t('common.cancel') }}</button>
      </div>
    </div>
    <p v-if="page.is_readonly" class="text-xs text-gray-400 mt-2">{{ t('wiki.readonly') }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useWikisStore } from '@/stores/wikis'
import WikiLinkedContent from '@/components/WikiLinkedContent.vue'

const { t } = useI18n()
const route = useRoute()
const wikis = useWikisStore()

const page = ref(null)
const editing = ref(false)
const draft = ref('')

const basePath = computed(() => (route.path.startsWith('/teacher') ? '/teacher' : '/student'))
const historyPath = computed(() => `${basePath.value}/wiki-pages/${route.params.id}/history`)

async function load() {
  page.value = await wikis.fetchPage(route.params.id)
}

function startEdit() {
  draft.value = page.value.cached_content
  editing.value = true
}

async function onSave() {
  page.value = await wikis.saveVersion(route.params.id, draft.value)
  editing.value = false
}

onMounted(load)
</script>

<template>
  <div v-if="forum" class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-1">{{ forum.title }}</h1>
    <p v-if="forum.description" class="text-sm text-gray-500 mb-6">{{ forum.description }}</p>

    <div v-if="forum.access_restricted" class="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4">
      <p class="text-sm text-amber-800 font-medium mb-1">{{ t('access.restrictedTitle') }}</p>
      <ul class="text-xs text-amber-700 list-disc list-inside">
        <li v-for="(r, i) in forum.access_reasons" :key="i">{{ r }}</li>
      </ul>
    </div>

    <details v-else class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('forum.newDiscussion') }}</summary>
      <div class="mt-3 space-y-2">
        <input v-model="newTitle" :placeholder="t('forum.titlePlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <textarea v-model="newBody" :placeholder="t('forum.messagePlaceholder')" rows="3" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"></textarea>
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onCreateDiscussion">{{ t('forum.publish') }}</button>
      </div>
    </details>

    <div v-for="d in forum.discussions" :key="d.id"
      class="bg-white border border-gray-200 rounded-xl p-4 mb-2 cursor-pointer hover:border-gray-400 transition-colors"
      @click="$router.push(`/forum-discussions/${d.id}`)">
      <div class="flex items-center justify-between">
        <p class="font-medium" :class="d.is_unread ? 'text-gray-900 font-bold' : 'text-gray-700'">
          {{ d.title }} <span v-if="d.is_unread" class="w-2 h-2 inline-block bg-blue-600 rounded-full ml-1"></span>
        </p>
        <span v-if="d.is_subscribed" class="text-xs text-gray-400">🔔</span>
      </div>
      <p class="text-xs text-gray-500 mt-1">{{ t('forum.postCount', { count: d.post_count }) }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useForumsStore } from '@/stores/forums'

const { t } = useI18n()
const route = useRoute()
const forumId = route.params.id
const forums = useForumsStore()

const forum = ref(null)
const newTitle = ref('')
const newBody = ref('')

async function load() {
  forum.value = await forums.fetchForum(forumId)
}

async function onCreateDiscussion() {
  if (!newTitle.value || !newBody.value) return
  await forums.createDiscussion(forumId, { title: newTitle.value, body: newBody.value })
  newTitle.value = ''
  newBody.value = ''
  await load()
}

onMounted(load)
</script>

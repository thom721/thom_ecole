<template>
  <div v-if="discussion" class="max-w-2xl mx-auto">
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-lg font-bold text-gray-900">{{ discussion.title }}</h1>
      <button class="text-xs text-blue-600 hover:underline" @click="onToggleSubscribe">
        {{ discussion.is_subscribed ? t('forum.subscribed') : t('forum.subscribe') }}
      </button>
    </div>

    <div v-for="post in rootPosts" :key="post.id" class="bg-white border border-gray-200 rounded-xl p-4 mb-3">
      <p class="text-sm text-gray-800"><AutoLinkedText :text="post.body" :course-id="discussion.course_id" /></p>
      <p class="text-xs text-gray-400 mt-2">{{ new Date(post.created_at).toLocaleString(locale === 'en' ? 'en-US' : 'fr-FR') }}</p>

      <div v-for="reply in repliesFor(post.id)" :key="reply.id" class="ml-8 mt-3 border-l-2 border-gray-100 pl-3">
        <p class="text-sm text-gray-700"><AutoLinkedText :text="reply.body" :course-id="discussion.course_id" /></p>
        <p class="text-xs text-gray-400 mt-1">{{ new Date(reply.created_at).toLocaleString(locale === 'en' ? 'en-US' : 'fr-FR') }}</p>
      </div>

      <div class="mt-3 flex gap-2">
        <input v-model="replyBody[post.id]" :placeholder="t('forum.replyPlaceholder')"
          class="flex-1 border border-gray-300 rounded-lg px-2 py-1.5 text-sm" />
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm" @click="onReply(post.id)">{{ t('forum.reply') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useForumsStore } from '@/stores/forums'
import AutoLinkedText from '@/components/AutoLinkedText.vue'

const { t, locale } = useI18n()
const route = useRoute()
const discussionId = route.params.id
const forums = useForumsStore()

const discussion = ref(null)
const replyBody = reactive({})

const rootPosts = computed(() => discussion.value?.posts.filter((p) => !p.parent_post_id) ?? [])
function repliesFor(postId) {
  return discussion.value?.posts.filter((p) => p.parent_post_id === postId) ?? []
}

async function load() {
  discussion.value = await forums.fetchDiscussion(discussionId)
}

async function onReply(parentPostId) {
  const body = replyBody[parentPostId]
  if (!body) return
  await forums.createPost(discussionId, { body, parent_post_id: parentPostId })
  replyBody[parentPostId] = ''
  await load()
}

async function onToggleSubscribe() {
  if (discussion.value.is_subscribed) await forums.unsubscribe(discussionId)
  else await forums.subscribe(discussionId)
  await load()
}

onMounted(load)
</script>

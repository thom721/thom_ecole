<template>
  <span class="whitespace-pre-wrap">
    <template v-for="(seg, i) in segments" :key="i">
      <a v-if="seg.isLink" href="#" @click.prevent="onClickLink(seg.title)"
        class="text-indigo-700 underline decoration-dotted hover:decoration-solid cursor-pointer">{{ seg.title }}</a>
      <template v-else>{{ seg.text }}</template>
    </template>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWikisStore } from '@/stores/wikis'

const props = defineProps({
  text: { type: String, default: '' },
  subwikiId: { type: String, required: true },
})

const route = useRoute()
const router = useRouter()
const wikis = useWikisStore()
const basePath = route.path.startsWith('/teacher') ? '/teacher' : '/student'

const segments = computed(() => {
  const result = []
  const regex = /\[\[([^\]]+)\]\]/g
  let lastIndex = 0
  let match
  while ((match = regex.exec(props.text)) !== null) {
    if (match.index > lastIndex) result.push({ text: props.text.slice(lastIndex, match.index), isLink: false })
    result.push({ title: match[1], isLink: true })
    lastIndex = regex.lastIndex
  }
  if (lastIndex < props.text.length) result.push({ text: props.text.slice(lastIndex), isLink: false })
  return result
})

async function onClickLink(title) {
  try {
    const page = await wikis.fetchPageByTitle(props.subwikiId, title)
    router.push(`${basePath}/wiki-pages/${page.id}`)
  } catch (e) {
    if (e.response?.status === 404) {
      router.push({ path: `${basePath}/wiki-pages/new`, query: { subwiki_id: props.subwikiId, title } })
    }
  }
}
</script>

<template>
  <span class="whitespace-pre-wrap">
    <template v-for="(seg, i) in segments" :key="i">
      <router-link v-if="seg.entryId" :to="`${basePath}/glossary-entries/${seg.entryId}`"
        class="text-teal-700 underline decoration-dotted hover:decoration-solid">{{ seg.text }}</router-link>
      <template v-else>{{ seg.text }}</template>
    </template>
  </span>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useGlossariesStore } from '@/stores/glossaries'

const props = defineProps({
  text: { type: String, default: '' },
  courseId: { type: String, required: true },
})

const route = useRoute()
const glossaries = useGlossariesStore()
const basePath = route.path.startsWith('/teacher') ? '/teacher' : '/student'

onMounted(() => {
  glossaries.fetchCourseConcepts(props.courseId)
})

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

const segments = computed(() => {
  const concepts = glossaries.conceptsByCourse[props.courseId] || []
  if (!concepts.length || !props.text) return [{ text: props.text, entryId: null }]

  // Concepts les plus longs d'abord — évite qu'un concept court capture
  // une sous-partie d'un concept plus long qui le contient.
  const sorted = [...concepts].sort((a, b) => b.concept.length - a.concept.length)
  const byLowerConcept = new Map(sorted.map((c) => [c.concept.toLowerCase(), c.entry_id]))
  const pattern = sorted.map((c) => escapeRegExp(c.concept)).join('|')
  if (!pattern) return [{ text: props.text, entryId: null }]

  const regex = new RegExp(`\\b(${pattern})\\b`, 'gi')
  const result = []
  let lastIndex = 0
  let match
  while ((match = regex.exec(props.text)) !== null) {
    if (match.index > lastIndex) result.push({ text: props.text.slice(lastIndex, match.index), entryId: null })
    result.push({ text: match[0], entryId: byLowerConcept.get(match[0].toLowerCase()) })
    lastIndex = regex.lastIndex
  }
  if (lastIndex < props.text.length) result.push({ text: props.text.slice(lastIndex), entryId: null })
  return result
})
</script>

<template>
  <div>
    <div class="relative overflow-hidden" style="height:38vh;min-height:260px;background:#0B1F3A">
      <img v-if="article?.image_url" :src="toAbsoluteUrl(article.image_url)" :alt="article.title" class="w-full h-full object-cover block opacity-40"/>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p v-if="article" class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">
          {{ article.category?.name || 'Actualité' }}
        </p>
        <h1 v-if="article" class="font-serif text-white mb-2" style="font-size:clamp(1.6rem,4vw,2.6rem);max-width:800px">
          {{ article.title }}
        </h1>
        <p v-if="article" class="text-xs" style="color:rgba(255,255,255,.6)">{{ formatDate(article.published_at ?? article.created_at) }}</p>
      </div>
    </div>

    <section class="py-16">
      <div class="max-w-2xl mx-auto px-6">
        <div v-if="loading" class="text-center text-gray-500 py-16">Chargement…</div>
        <div v-else-if="!article" class="text-center text-gray-500 py-16">
          Cet article n'existe pas ou n'est plus disponible.
        </div>
        <div v-else class="article-content text-gray-500 leading-relaxed reveal" v-html="sanitizedContent"></div>

        <div class="mt-12 text-center">
          <router-link to="/" class="text-sm font-semibold no-underline" style="color:#1A7A4A">← Retour à l'accueil</router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import DOMPurify from 'dompurify'
import { initReveal } from '@/composables/useReveal.js'

const route = useRoute()
const url = import.meta.env.VITE_APP_BASE_URL
const apiOrigin = url.replace(/\/api\/v1\/?$/, '')
const toAbsoluteUrl = (path) => (!path ? null : path.startsWith('http') ? path : `${apiOrigin}${path}`)

const article = ref(null)
const loading = ref(false)
// article.content est du HTML rédigé via l'éditeur riche de l'admin —
// sanitizé avant affichage (page publique, defense-in-depth même si seul un
// admin authentifié peut l'écrire).
const sanitizedContent = computed(() => DOMPurify.sanitize(article.value?.content ?? ''))

const formatDate = (dt) => dt ? new Date(dt).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' }) : ''

const fetchArticle = async () => {
  loading.value = true
  article.value = null
  try {
    const { data } = await axios.get(`${url}/news/${route.params.id}`)
    article.value = data
  } catch (e) { console.error('[Actualité]', e) }
  finally { loading.value = false; initReveal() }
}

onMounted(() => { window.scrollTo(0, 0); fetchArticle() })
watch(() => route.params.id, () => { window.scrollTo(0, 0); fetchArticle() })
</script>

<style scoped>
.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3) {
  font-family: 'Playfair Display', serif;
  color: #0B1F3A;
  margin: 1.5em 0 .5em;
  line-height: 1.25;
}
.article-content :deep(h1) { font-size: 1.8rem; }
.article-content :deep(h2) { font-size: 1.5rem; }
.article-content :deep(h3) { font-size: 1.25rem; }
.article-content :deep(p) { margin: 0 0 1em; }
.article-content :deep(blockquote) {
  border-left: 3px solid #D4A853;
  margin: 1.5em 0;
  padding: .25em 0 .25em 1.25em;
  font-style: italic;
  color: #4b5563;
}
.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 0 0 1em 1.25em;
}
.article-content :deep(a) { color: #1A7A6E; }
.article-content :deep(strong) { color: #0B1F3A; }
</style>

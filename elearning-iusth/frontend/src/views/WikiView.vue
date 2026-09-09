<template>
  <div v-if="subwikis" class="max-w-lg">
    <h1 class="text-lg font-bold text-gray-900 mb-4">{{ t('wiki.individualSubwikisTitle') }}</h1>
    <div class="grid gap-2">
      <router-link v-for="s in subwikis" :key="s.id" :to="`${basePath}/wiki-pages/${s.root_page_id}`"
        class="bg-white border border-gray-200 rounded-xl p-3 text-sm hover:border-gray-400 transition-colors">
        {{ s.owner_name }}
      </router-link>
    </div>
  </div>
  <div v-else class="text-sm text-gray-500">{{ t('common.loading') }}</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useWikisStore } from '@/stores/wikis'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const wikis = useWikisStore()
const auth = useAuthStore()
const basePath = route.path.startsWith('/teacher') ? '/teacher' : '/student'

const subwikis = ref(null)

onMounted(async () => {
  if (auth.isTeacher || auth.isAdmin) {
    try {
      subwikis.value = await wikis.fetchIndividualSubwikis(route.params.id)
      return
    } catch {
      // Wiki collaboratif (400 "pas en mode individuel") — un enseignant
      // rejoint alors la sous-wiki partagée comme tout le monde.
    }
  }
  const subwiki = await wikis.fetchMySubwiki(route.params.id)
  router.replace(`${basePath}/wiki-pages/${subwiki.root_page_id}`)
})
</script>

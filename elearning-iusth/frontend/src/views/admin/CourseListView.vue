<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-lg font-bold text-gray-900">{{ t('admin.courses.title') }}</h1>
      <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="showCreate = true">
        {{ t('admin.courses.newCourse') }}
      </button>
    </div>

    <div class="flex items-center justify-between gap-3 mb-6">
      <input v-model="search" :placeholder="t('admin.courses.searchPlaceholder')"
        class="w-full max-w-sm border border-gray-300 rounded-lg px-3 py-2 text-sm" />
      <span class="text-xs text-gray-500 whitespace-nowrap">{{ t('admin.courses.resultsCount', { total }) }}</span>
    </div>

    <div v-if="showCreate" class="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <input v-model="form.short_name" :placeholder="t('admin.courses.shortNamePlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <input v-model="form.full_name" :placeholder="t('admin.courses.fullNamePlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
      </div>
      <textarea v-model="form.summary" rows="2" :placeholder="t('admin.courses.summaryPlaceholder')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3"></textarea>
      <div class="flex gap-2">
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onCreate">{{ t('common.create') }}</button>
        <button class="text-sm text-gray-500" @click="showCreate = false">{{ t('common.cancel') }}</button>
      </div>
    </div>

    <p v-if="!courses.allCourses.length" class="text-sm text-gray-500">{{ t('admin.courses.noResults') }}</p>

    <div class="grid gap-3 mb-6">
      <router-link v-for="c in courses.allCourses" :key="c.id" :to="`/teacher/courses/${c.id}`"
        class="bg-white border border-gray-200 rounded-xl p-4 hover:border-gray-400 transition-colors">
        <p class="text-xs text-gray-500 mb-1">{{ c.short_name }}</p>
        <p class="font-semibold text-gray-900">{{ c.full_name }}</p>
      </router-link>
    </div>

    <div v-if="totalPages > 1" class="flex items-center justify-center gap-4">
      <button class="text-sm text-gray-600 hover:text-gray-900 disabled:opacity-40 disabled:hover:text-gray-600"
        :disabled="page <= 1" @click="page -= 1">
        {{ t('admin.courses.prevPage') }}
      </button>
      <span class="text-sm text-gray-500">{{ t('admin.courses.pageOf', { page, pages: totalPages }) }}</span>
      <button class="text-sm text-gray-600 hover:text-gray-900 disabled:opacity-40 disabled:hover:text-gray-600"
        :disabled="page >= totalPages" @click="page += 1">
        {{ t('admin.courses.nextPage') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCoursesStore } from '@/stores/courses'

const { t } = useI18n()
const courses = useCoursesStore()
const showCreate = ref(false)
const form = reactive({ short_name: '', full_name: '', summary: '' })

const search = ref('')
const page = ref(1)
const pageSize = 20
const total = computed(() => courses.allCoursesTotal)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

let searchDebounce = null
watch(search, () => {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    page.value = 1
    load()
  }, 300)
})

watch(page, load)

function load() {
  return courses.fetchAllCourses({ q: search.value, page: page.value, pageSize })
}

async function onCreate() {
  await courses.createCourse({ ...form })
  showCreate.value = false
  form.short_name = ''
  form.full_name = ''
  form.summary = ''
  await load()
}

onMounted(load)
</script>

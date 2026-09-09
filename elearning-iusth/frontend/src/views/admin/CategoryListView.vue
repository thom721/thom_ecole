<template>
  <div>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('admin.categories.title') }}</h1>

    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <div class="flex gap-2 mb-2">
        <input v-model="form.name" :placeholder="t('admin.categories.namePlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1" />
        <input v-model="form.slug" :placeholder="t('admin.categories.slugPlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1" />
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onCreate">{{ t('common.create') }}</button>
      </div>
      <p v-if="message" class="text-xs text-red-600">{{ message }}</p>
    </div>

    <ul class="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100">
      <li v-for="c in categories" :key="c.id" class="px-4 py-2 text-sm">{{ c.name }} <span class="text-gray-400">({{ c.slug }})</span></li>
    </ul>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCoursesStore } from '@/stores/courses'

const { t } = useI18n()
const courses = useCoursesStore()
const categories = ref([])
const message = ref('')
const form = reactive({ name: '', slug: '' })

async function load() {
  categories.value = await courses.fetchCategories()
}

async function onCreate() {
  message.value = ''
  try {
    await courses.createCategory({ ...form })
    form.name = ''
    form.slug = ''
    await load()
  } catch (e) {
    message.value = e.response?.data?.detail || t('common.error')
  }
}

onMounted(load)
</script>

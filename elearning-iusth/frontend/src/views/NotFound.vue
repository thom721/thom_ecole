<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="text-center">
      <p class="text-4xl font-bold text-gray-900 mb-2">404</p>
      <p class="text-gray-500 mb-4">{{ t('notFound.title') }}</p>
      <router-link to="/" class="text-blue-600 hover:underline">{{ t('notFound.backHome') }}</router-link>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

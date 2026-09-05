<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
import { registerHead } from '@/composables/usePageMeta'

registerHead()
</script>

<style> 
body {
  margin: 0;
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
}
</style>
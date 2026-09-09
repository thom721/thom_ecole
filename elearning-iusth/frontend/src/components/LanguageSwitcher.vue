<template>
  <select :value="locale" @change="setLocale($event.target.value)"
    class="bg-transparent text-gray-500 text-sm border-none focus:outline-none cursor-pointer">
    <option value="fr">Français</option>
    <option value="en">English</option>
  </select>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { setLocale } from '@/i18n'

const { locale } = useI18n()
</script>

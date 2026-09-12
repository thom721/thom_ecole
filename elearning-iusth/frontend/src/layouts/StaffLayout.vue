<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 flex items-center justify-between gap-3">
      <router-link to="/staff/staff-meetings" class="font-bold text-gray-900 shrink-0">{{ t('layout.staffBrand') }}</router-link>

      <nav class="flex items-center gap-4 text-sm text-gray-600">
        <router-link to="/staff/staff-meetings" class="hover:text-gray-900">{{ t('staffMeeting.navLink') }}</router-link>
        <MessagingBell />
        <NotificationBell />
        <LanguageSwitcher />
        <span class="hidden sm:inline">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</span>
        <button class="text-red-600 hover:underline" @click="logout">{{ t('common.logout') }}</button>
      </nav>
    </header>
    <main class="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import NotificationBell from '@/components/NotificationBell.vue'
import MessagingBell from '@/components/MessagingBell.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white border-b border-gray-200">
      <div class="px-4 sm:px-6 py-3 flex items-center justify-between gap-3">
        <router-link to="/student/courses" class="font-bold text-gray-900 shrink-0">{{ t('layout.studentBrand') }}</router-link>

        <div class="hidden md:flex items-center gap-4 text-sm text-gray-600 flex-wrap">
          <router-link v-if="auth.isAdmin" to="/admin/courses" class="text-blue-600 hover:underline">
            {{ t('layout.backToAdmin') }}
          </router-link>
          <router-link to="/student/dashboard" class="hover:text-gray-900">{{ t('dashboard.navLink') }}</router-link>
          <router-link to="/student/calendar" class="hover:text-gray-900">📅</router-link>
          <router-link to="/student/badges" class="hover:text-gray-900">🏅</router-link>
          <router-link to="/student/competencies" class="hover:text-gray-900">🎯</router-link>
          <router-link to="/student/plans" class="hover:text-gray-900">📋</router-link>
          <MessagingBell />
          <NotificationBell />
          <LanguageSwitcher />
          <span>{{ auth.user?.first_name }} {{ auth.user?.last_name }}</span>
          <button class="text-red-600 hover:underline" @click="logout">{{ t('common.logout') }}</button>
        </div>

        <button class="md:hidden p-2 -mr-2 text-gray-600" :aria-expanded="mobileMenuOpen" :aria-label="t('layout.menuToggle')" @click="mobileMenuOpen = !mobileMenuOpen">
          <svg v-if="!mobileMenuOpen" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
          <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg>
        </button>
      </div>

      <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-200 px-4 py-3 space-y-3">
        <nav class="flex flex-col gap-3 text-sm" @click="mobileMenuOpen = false">
          <router-link v-if="auth.isAdmin" to="/admin/courses" class="text-blue-600 hover:underline">
            {{ t('layout.backToAdmin') }}
          </router-link>
          <router-link to="/student/dashboard" class="text-gray-600 hover:text-gray-900">{{ t('dashboard.navLink') }}</router-link>
          <router-link to="/student/calendar" class="text-gray-600 hover:text-gray-900">📅 {{ t('layout.navCalendar') }}</router-link>
          <router-link to="/student/badges" class="text-gray-600 hover:text-gray-900">{{ t('badges.navLink') }}</router-link>
          <router-link to="/student/competencies" class="text-gray-600 hover:text-gray-900">🎯 {{ t('competency.navLink') }}</router-link>
          <router-link to="/student/plans" class="text-gray-600 hover:text-gray-900">📋 {{ t('layout.navPlans') }}</router-link>
        </nav>
        <div class="flex items-center gap-4 text-sm text-gray-600 pt-3 border-t border-gray-100">
          <MessagingBell />
          <NotificationBell />
          <LanguageSwitcher />
        </div>
        <div class="flex items-center justify-between text-sm text-gray-600 pt-3 border-t border-gray-100">
          <span>{{ auth.user?.first_name }} {{ auth.user?.last_name }}</span>
          <button class="text-red-600 hover:underline" @click="logout">{{ t('common.logout') }}</button>
        </div>
      </div>
    </header>
    <main class="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import NotificationBell from '@/components/NotificationBell.vue'
import MessagingBell from '@/components/MessagingBell.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const mobileMenuOpen = ref(false)

watch(() => route.fullPath, () => { mobileMenuOpen.value = false })

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

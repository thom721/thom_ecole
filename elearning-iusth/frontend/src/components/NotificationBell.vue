<template>
  <div class="relative">
    <button class="relative text-lg" @click="toggleOpen">
      🔔
      <span v-if="unreadCount > 0" class="absolute -top-1 -right-1 bg-red-600 text-white text-[10px] leading-none rounded-full px-1.5 py-0.5">
        {{ unreadCount > 9 ? '9+' : unreadCount }}
      </span>
    </button>

    <div v-if="open" class="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-xl shadow-lg z-50 text-sm">
      <div class="flex items-center justify-between px-3 py-2 border-b border-gray-100">
        <span class="font-semibold text-gray-900">{{ t('notifications.title') }}</span>
        <button class="text-xs text-blue-600 hover:underline" @click="onMarkAllRead">{{ t('notifications.markAllRead') }}</button>
      </div>
      <div class="max-h-80 overflow-y-auto">
        <p v-if="!notifications.length" class="text-xs text-gray-500 p-3">{{ t('notifications.empty') }}</p>
        <button v-for="n in notifications" :key="n.id"
          class="w-full text-left px-3 py-2 border-b border-gray-50 hover:bg-gray-50 block"
          :class="{ 'bg-blue-50/50': !n.is_read }"
          @click="onClickNotification(n)">
          <p class="font-medium text-gray-900">{{ n.title }}</p>
          <p v-if="n.body" class="text-xs text-gray-500 truncate">{{ n.body }}</p>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useNotificationsStore } from '@/stores/notifications'

const { t } = useI18n()
const store = useNotificationsStore()
const router = useRouter()

const open = ref(false)
const unreadCount = ref(0)
const notifications = ref([])
let pollInterval = null

async function refreshCount() {
  unreadCount.value = await store.fetchUnreadCount()
}

async function toggleOpen() {
  open.value = !open.value
  if (open.value) {
    notifications.value = await store.fetchMine()
  }
}

async function onMarkAllRead() {
  await store.markAllRead()
  notifications.value = notifications.value.map((n) => ({ ...n, is_read: true }))
  unreadCount.value = 0
}

async function onClickNotification(n) {
  if (!n.is_read) {
    await store.markRead(n.id)
    n.is_read = true
    await refreshCount()
  }
  open.value = false
  if (n.link_url) router.push(n.link_url)
}

onMounted(() => {
  refreshCount()
  pollInterval = setInterval(refreshCount, 30000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

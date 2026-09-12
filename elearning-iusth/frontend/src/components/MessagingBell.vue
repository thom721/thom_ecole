<template>
  <router-link :to="messagesPath" class="relative text-lg">
    💬
    <span v-if="unreadCount > 0" class="absolute -top-1 -right-1 bg-red-600 text-white text-[10px] leading-none rounded-full px-1.5 py-0.5">
      {{ unreadCount > 9 ? '9+' : unreadCount }}
    </span>
  </router-link>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMessagingStore } from '@/stores/messaging'
import { useAuthStore } from '@/stores/auth'

const store = useMessagingStore()
const auth = useAuthStore()
const unreadCount = ref(0)
let pollInterval = null

const messagesPath = computed(() => {
  const base = auth.isAdmin ? '/admin' : auth.isTeacher ? '/teacher' : auth.isStaff ? '/staff' : '/student'
  return `${base}/messages`
})

async function refreshCount() {
  unreadCount.value = await store.fetchUnreadCount()
}

onMounted(() => {
  refreshCount()
  pollInterval = setInterval(refreshCount, 30000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

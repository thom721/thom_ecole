<template>
  <div class="min-h-screen bg-[#080c10] text-slate-200">
    <!-- Scroll progress bar -->
    <div class="fixed top-0 left-0 z-[200] h-[2px] pointer-events-none transition-[width] duration-75"
      :style="`width:${scrollPct}%;background:linear-gradient(90deg,#06b6d4,#f59e0b)`"/>
    <AppNavbar />

    <router-view v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="$route.path" />
      </Transition>
    </router-view>

    <AppFooter />
    <DemoModal v-if="open" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import AppNavbar      from '@/components/AppNavbar.vue'
import AppFooter      from '@/components/AppFooter.vue'
import DemoModal      from '@/components/DemoModal.vue'
import { useDemoStore } from '@/stores/demo.js'

const { open } = useDemoStore()

const scrollPct = ref(0)
function onScroll() {
  const max = document.documentElement.scrollHeight - window.innerHeight
  scrollPct.value = max > 0 ? (window.scrollY / max) * 100 : 0
}
onMounted(()  => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(()=> window.removeEventListener('scroll', onScroll))
</script>

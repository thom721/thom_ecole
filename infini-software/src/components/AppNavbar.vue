<template>
  <nav
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
    :class="scrolled ? 'bg-[#080c10]/95 backdrop-blur-xl border-b border-[#1e2a38]' : 'bg-transparent'"
  >
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">

      <!-- Logo -->
      <router-link to="/" class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-[#06b6d4] to-[#0891b2] flex items-center justify-center">
          <svg class="w-4 h-4 text-[#080c10]" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 4a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm8 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V4zM3 12a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H4a1 1 0 01-1-1v-4zm8 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/>
          </svg>
        </div>
        <span class="font-syne font-extrabold text-[.95rem] tracking-tight">
          Infini<span class="text-[#06b6d4]">Software</span>
        </span>
      </router-link>

      <!-- Desktop links -->
      <div class="hidden md:flex items-center gap-7">
        <router-link v-for="item in navItems" :key="item.to"
          :to="item.to" class="nav-link">{{ item.label }}</router-link>
      </div>

      <!-- CTA + burger -->
      <div class="flex items-center gap-3">
        <router-link to="/contact" class="hidden md:inline-flex btn-primary">
          Nous contacter
        </router-link>
        <button class="md:hidden p-2 text-[#64748b] hover:text-white transition-colors"
          @click="menuOpen = !menuOpen">
          <svg v-if="!menuOpen" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile menu -->
    <Transition name="fade">
      <div v-if="menuOpen"
        class="md:hidden border-t border-[#1e2a38] bg-[#080c10]/98 backdrop-blur-xl">
        <div class="px-6 py-6 flex flex-col gap-5">
          <router-link v-for="item in navItems" :key="item.to"
            :to="item.to" class="nav-link text-base" @click="menuOpen=false">
            {{ item.label }}
          </router-link>
          <router-link to="/contact" class="btn-primary justify-center mt-2" @click="menuOpen=false">
            Nous contacter
          </router-link>
        </div>
      </div>
    </Transition>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const scrolled  = ref(false)
const menuOpen  = ref(false)

const navItems = [
  { to: '/',        label: 'Accueil' },
  { to: '/store',   label: 'Store' },
  { to: '/about',   label: 'À propos' },
  { to: '/contact', label: 'Contact' },
]

function onScroll() { scrolled.value = window.scrollY > 20 }
onMounted(()  => window.addEventListener('scroll', onScroll))
onUnmounted(()=> window.removeEventListener('scroll', onScroll))
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

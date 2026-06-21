<template>
 
<div>
  <!-- NAVBAR -->
  <nav
    v-if="!hideShell"
    :class="[
      'fixed top-0 left-0 right-0 z-50 transition-all duration-500 py-5',
      scrolled ? 'nav-scrolled py-3' : '',
    ]"
  >
    <div class="max-w-6xl mx-auto px-6 flex items-center justify-between gap-4">

      <!-- Logo -->
      <router-link to="/" class="flex items-center gap-2.5 no-underline">
        <div
          class="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg flex-shrink-0"          
        >
        <!-- style="background: linear-gradient(135deg, #d4a853, #1a7a6e)" -->
        <img v-if="useSchoolInfo.school_info?.logo_image_base64" :src="useSchoolInfo.school_info?.logo_image_base64" alt="Logo"
          class="h-10 w-10 rounded-full object-cover border-2 border-white/30 shadow" />
      </div>
        <span
          class="font-serif text-xl font-bold transition-colors duration-300"
          :class="scrolled ? 'text-navy' : 'text-white'"
        >
          <span class="text-gold">{{useSchoolInfo.school_info?.nom || 'Lekol 360'}}</span>
        </span>
      </router-link>

      <!-- Liens desktop -->
      <div class="hidden md:flex items-center gap-7">
        <router-link
          v-for="p in navPages"
          :key="p.path"  :to="p.path" 
          class="nav-link relative text-sm font-medium tracking-wide no-underline transition-colors duration-300"
          :class="scrolled ? 'text-gray-500' : 'text-white/90'"
        >
          {{ p.label }}
        </router-link>
      </div>

      <!-- CTA -->
      <div class="flex items-center gap-3">
        <router-link
          to="/connexion"
          class="hidden sm:inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold no-underline border transition-all duration-300"
          :class="
            scrolled
              ? 'border-navy/20 text-navy hover:bg-navy hover:text-white'
              : 'border-white/30 text-white hover:bg-white hover:text-navy'
          "
        >
          Connexion
        </router-link>

        <router-link
          to="/admission"
          class="btn-gold hidden sm:inline-flex items-center gap-2 px-5 py-2 rounded-full text-sm font-semibold no-underline"
        >
          S'inscrire
        </router-link>

        <!-- Burger mobile -->
        <button
          class="md:hidden bg-transparent border-none cursor-pointer p-1"
          @click="mobileOpen = !mobileOpen"
        >
          <span
            v-for="i in 3"
            :key="i"
            :class="['block w-5 h-0.5 my-1.5 rounded transition-all', scrolled ? 'bg-navy' : 'bg-white']"
          ></span>
        </button>
      </div>
    </div>
  </nav>

  <!-- Menu mobile -->
  <transition name="fade">
    <div
      v-if="mobileOpen && !hideShell"
      class="fixed top-[60px] left-0 right-0 z-40 bg-white shadow-xl py-4 px-6"
    >
      <router-link
        v-for="p in navPages"
        :key="p.path"
        :to="p.path"
        class="block py-3.5 border-b border-gray-50 text-sm font-medium last:border-none no-underline text-navy"
        @click="mobileOpen = false"
      >
        {{ p.label }}
      </router-link>
      <router-link
        to="/connexion"
        class="block py-3.5 text-sm font-medium text-gold no-underline"
        @click="mobileOpen = false"
      >
        Connexion
      </router-link>
    </div>
  </transition>

 
  <router-view v-slot="{ Component }">
    <transition name="slide" mode="out-in" @after-enter="initReveal">
      <component :is="Component" />
    </transition>
  </router-view>
 
  <footer v-if="!hideShell" style="background: #0b1f3a; color: #fff" class="py-16">
    <div class="max-w-6xl mx-auto px-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-10">

        <div>
          <router-link to="/" class="flex items-center gap-2.5 mb-3.5 no-underline">
            <div
              class="w-9 h-9 rounded-xl flex items-center justify-center text-white font-bold flex-shrink-0"
              style="background: linear-gradient(135deg, #d4a853, #1a7a6e)"
            >E</div>
            <span class="font-serif text-lg font-bold"><span class="text-gold">{{useSchoolInfo.school_info?.nom || 'Lekol 360'}}</span></span>
          </router-link>
          <p class="text-sm leading-relaxed" style="color: rgba(255,255,255,.55)">
            La plateforme de référence pour la gestion scolaire moderne en Afrique francophone et en France.
          </p>
        </div>

        <div>
          <h4 class="text-xs font-bold uppercase tracking-widest text-gold mb-4">Navigation</h4>
          <router-link
            v-for="p in navPages"
            :key="p.path"
            :to="p.path"
            class="block text-sm leading-8 no-underline transition-colors hover:text-white/90"
            style="color: rgba(255,255,255,.55)"
          >
            {{ p.label }}
          </router-link>
        </div>

        <div>
          <h4 class="text-xs font-bold uppercase tracking-widest text-gold mb-4">Formations</h4>
          <p
            v-for="f in ['Primaire & Collège', 'Lycée Général', 'Lycée Professionnel', 'BTS & DUT']"
            :key="f"
            class="text-sm leading-8"
            style="color: rgba(255,255,255,.55)"
          >{{ f }}</p>
        </div>

        <div>
          <h4 class="text-xs font-bold uppercase tracking-widest text-gold mb-4">Contact</h4>
          <p class="text-sm leading-8" style="color: rgba(255,255,255,.55)">📧 {{useSchoolInfo.school_info?.email}}</p>
          <p class="text-sm leading-8" style="color: rgba(255,255,255,.55)">📞 {{useSchoolInfo.school_info?.ligne1}}</p>
          <p class="text-sm leading-8" style="color: rgba(255,255,255,.55)">📍 {{useSchoolInfo.school_info?.adresse}}</p>
        </div>
      </div>

      <div
        class="border-t text-center pt-6 text-xs"
        style="border-color: rgba(255,255,255,.08); color: rgba(255,255,255,.3)"
      >
        © 2025 EduSphere. Tous droits réservés. Conçu avec ♥ pour l'éducation.
      </div>
    </div>
  </footer>
 
  <transition name="fade">
    <button
  v-if="scrolled && !hideShell"
  class="fixed bottom-7 right-7 w-11 h-11 rounded-full text-white border-none cursor-pointer flex items-center justify-center z-50 transition-transform hover:-translate-y-1"
  style="background: linear-gradient(135deg,#d4a853,#b8860b); box-shadow: 0 6px 20px rgba(212,168,83,.4)"
  @click="scrollToTop"
>
  <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
    <path d="M5 15l7-7 7 7" />
  </svg>
</button>
 
  </transition>
  </div>
</template>

<style scoped> 

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* .slide-enter-from {
  transform: translateY(30px);
  opacity: 0;
}
.slide-enter-to {
  transform: translateY(0);
  opacity: 1;
}

.slide-leave-from {
  transform: translateY(0);
  opacity: 1;
}
.slide-leave-to {
  transform: translateY(-15px);
  opacity: 0.9; 
} */


/* .slide-enter-active,
.slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}*/

.slide-enter-from {
  transform: translateY(16px);
  opacity:0.8;
}

.slide-enter-to {
  transform: translateY(0);
  opacity: 1;
}

.slide-leave-from {
  transform: translateY(0);
  opacity: 0.8;
}

.slide-leave-to {
  transform: translateY(-16px);
  opacity: 0.8;
} 

</style>

<script setup>

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { initReveal } from '@/composables/useReveal.js'
import { useSchoolStore, useSchoolStoreInfo } from '../stores/schoolStore';
const useSchoolInfo = useSchoolStoreInfo();

const scrolled   = ref(false)
const mobileOpen = ref(false)

function onScroll() {
  scrolled.value = window.scrollY > 60
}
onMounted(()  => window.addEventListener('scroll', onScroll))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const route    = useRoute()
const hideShell = computed(() => !!route.meta?.hideShell)


import { watch } from 'vue'
watch(() => route.path, () => { mobileOpen.value = false })


const navPages = [
  { path: '/',           label: 'Accueil' },
  { path: '/formations', label: 'Formations' },
  { path: '/admission',  label: 'Admission' },
  { path: '/evenements', label: 'Événements' },
  { path: '/a-propos',   label: 'À Propos' },
  { path: '/contact',    label: 'Contact' },
]
</script>

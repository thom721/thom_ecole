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
          <span class="text-gold">{{useSchoolInfo.school_info?.nom || 'IUSTH'}}</span>
        </span>
      </router-link>

      <!-- Liens desktop -->
      <div class="hidden md:flex items-center gap-7">
        <template v-for="p in navPages" :key="p.path || p.label">
          <!-- Entrée avec sous-menu (ex: Accueil, Formation) — cliquable si p.path
               existe (Accueil mène quand même à /), sinon juste un déclencheur -->
          <div v-if="p.children" class="relative group py-2">
            <router-link
              v-if="p.path"
              :to="p.path"
              class="nav-link relative text-sm font-medium tracking-wide no-underline transition-colors duration-300"
              :class="[scrolled ? 'text-gray-500' : 'text-white/90', isParentActive(p) ? 'router-link-active' : '']"
            >{{ p.label }}</router-link>
            <span
              v-else
              class="nav-link relative text-sm font-medium tracking-wide cursor-default transition-colors duration-300"
              :class="scrolled ? 'text-gray-500' : 'text-white/90'"
            >{{ p.label }}</span>
            <div class="absolute left-0 top-full pt-1 hidden group-hover:block">
              <div class="bg-white rounded-xl shadow-lg py-2 w-[240px]">
                <router-link
                  v-for="c in p.children" :key="c.path" :to="c.path"
                  class="block px-4 py-2 text-sm leading-snug text-navy no-underline hover:bg-gray-50"
                >{{ c.label }}</router-link>
              </div>
            </div>
          </div>
          <!-- Entrée simple -->
          <router-link
            v-else
            :to="p.path"
            class="nav-link relative text-sm font-medium tracking-wide no-underline transition-colors duration-300"
            :class="scrolled ? 'text-gray-500' : 'text-white/90'"
          >
            {{ p.label }}
          </router-link>
        </template>
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
      <template v-for="p in navPages" :key="p.path || p.label">
        <template v-if="p.children">
          <p class="pt-3.5 pb-1 text-xs font-bold uppercase tracking-widest text-gray-500">{{ p.label }}</p>
          <router-link
            v-for="c in p.children" :key="c.path" :to="c.path"
            class="block py-2.5 pl-3 border-b border-gray-50 text-sm font-medium last:border-none no-underline text-navy"
            @click="mobileOpen = false"
          >{{ c.label }}</router-link>
        </template>
        <router-link
          v-else
          :to="p.path"
          class="block py-3.5 border-b border-gray-50 text-sm font-medium last:border-none no-underline text-navy"
          @click="mobileOpen = false"
        >
          {{ p.label }}
        </router-link>
      </template>
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
            <span class="font-serif text-lg font-bold"><span class="text-gold">{{useSchoolInfo.school_info?.nom || 'IUSTH'}}</span></span>
          </router-link>
          <p class="text-sm leading-relaxed" style="color: rgba(255,255,255,.55)">
            Institution d'enseignement supérieur et de recherche reconnue d'utilité publique par l'État haïtien.
          </p>
        </div>

        <div>
          <h4 class="text-xs font-bold uppercase tracking-widest text-gold mb-4">Navigation</h4>
          <router-link
            v-for="p in footerNavLinks"
            :key="p.path"
            :to="p.path"
            class="block text-sm leading-8 no-underline transition-colors hover:text-white/90"
            style="color: rgba(255,255,255,.55)"
          >
            {{ p.label }}
          </router-link>
        </div>

        <div>
          <h4 class="text-xs font-bold uppercase tracking-widest text-gold mb-4">Facultés</h4>
          <router-link
            to="/facultes"
            v-for="f in ['Sciences Infirmières', 'Sciences Administratives', 'Sciences Informatiques', 'Sciences Agronomiques', 'Génie Civil & Architecture']"
            :key="f"
            class="block text-sm leading-8 no-underline transition-colors hover:text-white/90"
            style="color: rgba(255,255,255,.55)"
          >{{ f }}</router-link>
        </div>

        <div>
          <h4 class="text-xs font-bold uppercase tracking-widest text-gold mb-4">Contact</h4>
          <p class="text-sm leading-8" style="color: rgba(255,255,255,.55)">📧 {{useSchoolInfo.school_info?.email}}</p>
          <p class="text-sm leading-8" style="color: rgba(255,255,255,.55)">📞 {{useSchoolInfo.school_info?.ligne1}}</p>
          <p class="text-sm leading-8" style="color: rgba(255,255,255,.55)">📍 {{useSchoolInfo.school_info?.adresse}}</p>
        </div>
      </div>

      <div
        class="border-t flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4 pt-6 text-xs"
        style="border-color: rgba(255,255,255,.08); color: rgba(255,255,255,.3)"
      >
        <span>© {{ new Date().getFullYear() }} {{ useSchoolInfo.school_info?.nom || 'IUSTH' }}. Tous droits réservés.</span>
        <span class="hidden sm:inline">·</span>
        <router-link to="/mentions-legales" class="no-underline hover:underline" style="color: rgba(255,255,255,.5)">Mentions légales</router-link>
        <span class="hidden sm:inline">·</span>
        <router-link to="/mentions-legales#confidentialite" class="no-underline hover:underline" style="color: rgba(255,255,255,.5)">Confidentialité</router-link>
        <span class="hidden sm:inline">·</span>
        <router-link to="/mentions-legales#cookies" class="no-underline hover:underline" style="color: rgba(255,255,255,.5)">Cookies</router-link>
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


// "Formation" et "À Propos" ont un sous-menu. Le Président du CA,
// Fonctionnement et Notre mission relèvent tous de la page À Propos — ils
// étaient auparavant rattachés au menu "Accueil" (incohérence relevée par
// l'audit, point 4.2 : "un sous-menu Accueil illogique") ; ils sont
// maintenant dans le sous-menu de la rubrique à laquelle ils appartiennent
// réellement. SANS "Admission" dans celui de Formation : elle a déjà sa
// propre entrée dans le grand menu, pas besoin de la dupliquer.
const navPages = [
  { path: '/', label: 'Accueil' },
  { path: '/formations', label: 'Formation', children: [
      { path: '/facultes',   label: 'Les Facultés' },
      { path: '/formations', label: 'Les Diplômes' },
    ] },
  { path: '/admission',  label: 'Admission' },
  { path: '/evenements', label: 'Événements' },
  { path: '/a-propos',   label: 'À Propos', children: [
      { path: '/a-propos#mission',        label: 'Notre mission' },
      { path: '/a-propos#mot-recteur',    label: 'Mot du Recteur' },
      { path: '/a-propos#president',      label: 'Le Président du Conseil d\'Administration de l\'IUSTH' },
      { path: '/a-propos#fonctionnement', label: 'Fonctionnement' },
    ] },
  { path: '/contact',    label: 'Contact' },
]

// Pied de page : liste plate (déplie les sous-menus, ex. "Formation").
const footerNavLinks = navPages.flatMap(p => p.children ?? [p])

// Pour un item à sous-menu (ex: Formation), le surlignage automatique de
// Vue Router (.router-link-active) ne couvre que son propre `path` — pas
// ses enfants qui sont des routes séparées (/facultes vs /formations). On
// l'étend ici pour que "Formation" reste surligné sur les deux.
const isParentActive = (p) =>
  !!p.children && p.children.some(c => c.path.split('#')[0] === route.path)
</script>

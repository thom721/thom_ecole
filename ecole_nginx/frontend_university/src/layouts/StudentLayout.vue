<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'   // adapter selon votre store

import { storeToRefs } from 'pinia'; 
import { useSchoolStore,useSchoolStoreInfo } from '../stores/schoolStore';  
const authStore = useAuthStore(); 
const useSchoolInfo = useSchoolStoreInfo() 
const { user, isAdmin, isTeacher, roleNames } = storeToRefs(authStore);
const { hasRole } = authStore;
const schoolStore = useSchoolStore();
const { niveau, professeur, annee,classes,faculte,cours, loadingi } = storeToRefs(schoolStore);

/* ── props ── */
defineProps({
  title: String,
})

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

/* ── sidebar ── */
const sidebarOpen = ref(false)

const showSidebar = ()  => { sidebarOpen.value = true }
const hideSidebar = ()  => { sidebarOpen.value = false }
const toggleSidebar = () => { sidebarOpen.value ? hideSidebar() : showSidebar() }

/* ── sous-menus ── */
const adminOpen   = ref(false)
const financeOpen = ref(false)
const toggleAdmin   = () => { adminOpen.value   = !adminOpen.value }
const toggleFinance = () => { financeOpen.value = !financeOpen.value }

/* ── dropdown profil ── */
const profileDropdown = ref(false)
const toggleProfileDropdown = () => { profileDropdown.value = !profileDropdown.value }
const closeProfileDropdown  = () => { profileDropdown.value = false }

/* ── route active ── */
const isActive = (name) => route.name === name

/* ── responsive : fermer sur petit écran ── */
const handleResize = () => {
  if (window.innerWidth < 992) hideSidebar()
  else showSidebar()
}

/* ── fermer sidebar au clic hors zone (mobile) ── */
const handleOutsideClick = (e) => {
  if (window.innerWidth < 540 && !e.target.closest('#sidebar') && !e.target.closest('#sidebar-toggle')) {
    hideSidebar()
  }
  if (!e.target.closest('#profile-menu')) {
    closeProfileDropdown()
  }
}

/* ── loader de navigation ── */
const loading = ref(false)
router.beforeEach(() => { loading.value = true })
router.afterEach(()  => { loading.value = false })

/* ── déconnexion ── */
const logout = async () => {
  localStorage.removeItem('auth-token')
  sessionStorage.removeItem('auth-token')
  localStorage.removeItem('api_token')
  await auth.logout()          // si votre store expose un logout()
  router.push({ name: 'login' })
}

onMounted( async () => {
  if (!authStore.user) await authStore.initializeAuth();
  window.addEventListener('resize', handleResize)
  window.addEventListener('click', handleOutsideClick)
  handleResize()

  /* stocker le token si disponible depuis le store */
  const token = auth.apiToken
  if (token) {
    localStorage.setItem('auth-token', token)
    sessionStorage.setItem('auth-token', token)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('click', handleOutsideClick)
})

/* ── données depuis le store (adapter selon votre store) ── */
const school     = computed(() => auth.school)
// const user       = computed(() => auth.user)
const cartCount  = computed(() => auth.cartCount ?? 0)
</script>

<template>
  <div class="min-h-screen bg-slate-50 font-sans">

    <!-- ══════════════════════ SIDEBAR ══════════════════════ -->
    <aside id="sidebar"
      class="fixed left-0 top-0 h-full bg-gradient-to-br from-[#0d0d14] to-[#1a1a2e] z-50 flex flex-col transition-all duration-300 ease-in-out overflow-hidden shadow-xl"
      :class="sidebarOpen ? 'w-56' : 'w-0'">
 
      <!-- Logo / école -->
      <div class="flex items-center justify-center h-[56px] border-b border-slate-700/60 shrink-0 px-3">
        <img v-if="useSchoolInfo.school_info?.logo_image_base64" :src="useSchoolInfo.school_info?.logo_image_base64" alt="Logo"
          class="h-9 w-9 rounded-full object-cover border-2 border-white/30 shadow" />
        <div v-else
          class="h-9 w-9 rounded-full bg-gray-700 border-2 border-white/30 flex items-center justify-center text-white text-lg">
          🏫
        </div>
        <span v-if="school?.nom" class="ml-2.5 text-white font-bold text-sm truncate leading-tight">
          {{ school.nom }}
        </span>
      </div>

      <!-- Nav items -->
      <nav class="flex-1 overflow-y-auto py-3 pb-20">
        <ul class="space-y-0.5 px-2">

          <li>
            <RouterLink :to="{ name: 'etudiant.dashboard' }" @click="handleResize"
              class="flex items-center gap-3 px-4 py-3 rounded-xl text-green-100 text-sm font-medium transition-all duration-200 hover:bg-white/10 hover:text-white"
              :class="{ 'bg-white/15 text-white font-semibold shadow-inner': isActive('etudiant.dashboard') }">
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
              </svg>
              Dashboard
            </RouterLink>
          </li>

          <li>
            <RouterLink :to="{ name: 'etudiant.cours' }" @click="handleResize"
              class="flex items-center gap-3 px-4 py-3 rounded-xl text-green-100 text-sm font-medium transition-all duration-200 hover:bg-white/10 hover:text-white"
              :class="{ 'bg-white/15 text-white font-semibold shadow-inner': isActive('etudiant.cours') }">
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
              Cours
            </RouterLink>
          </li>

          <li>
            <RouterLink :to="{ name: 'etudiant.notes' }" @click="handleResize"
              class="flex items-center gap-3 px-4 py-3 rounded-xl text-green-100 text-sm font-medium transition-all duration-200 hover:bg-white/10 hover:text-white"
              :class="{ 'bg-white/15 text-white font-semibold shadow-inner': isActive('etudiant.notes') }">
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              Notes
            </RouterLink>
          </li>

           <li>
            <RouterLink :to="{ name: 'etudiant.paiement' }" @click="handleResize"
              class="flex items-center gap-3 px-4 py-3 rounded-xl text-green-100 text-sm font-medium transition-all duration-200 hover:bg-white/10 hover:text-white"
              :class="{ 'bg-white/15 text-white font-semibold shadow-inner': isActive('etudiant.paiement') }">
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              Paiements
            </RouterLink>
          </li>

          <li>
            <RouterLink :to="{ name: 'etudiant.profile' }" @click="handleResize"
              class="flex items-center gap-3 px-4 py-3 rounded-xl text-green-100 text-sm font-medium transition-all duration-200 hover:bg-white/10 hover:text-white"
              :class="{ 'bg-white/15 text-white font-semibold shadow-inner': isActive('etudiant.profile') }">
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              Profil
            </RouterLink>
          </li>

          <!-- Séparateur -->
          <li class="pt-3">
            <div class="h-px bg-white/10 mx-2"></div>
          </li>

          <!-- Déconnexion -->
          <li class="pt-2">
            <button @click="logout"
              class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-300 text-sm font-medium transition-all duration-200 hover:bg-red-500/20 hover:text-red-200">
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
              </svg>
              Se déconnecter
            </button>
          </li>

        </ul>
      </nav>

      <!-- Badge version bas de sidebar -->
      <div class="shrink-0 px-4 py-3 border-t border-green-700/50">
        <p class="text-green-400/60 text-[10px] text-center tracking-wider uppercase">infini-software v2</p>
      </div>
    </aside>

    <!-- Overlay mobile -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
      leave-active-class="transition duration-150" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="sidebarOpen" class="fixed inset-0 bg-black/40 z-40 lg:hidden" @click="hideSidebar"></div>
    </Transition>

    <!-- ══════════════════════ MAIN ══════════════════════ -->
    <main class="min-h-screen flex flex-col transition-all duration-300"
      :class="sidebarOpen ? 'lg:ml-56' : 'ml-0'">

      <!-- ── TOPBAR ── -->
      <header class="sticky top-0 z-30 h-[56px] bg-white border-b border-slate-200 shadow-sm flex items-center px-4 gap-3">

        <!-- Toggle sidebar -->
        <button id="sidebar-toggle" @click="toggleSidebar"
          class="w-9 h-9 flex items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition-colors">
          <!-- Hamburger animé -->
          <svg class="w-5 h-5 transition-transform duration-200" :class="{ 'rotate-90': sidebarOpen }"
            fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>

        <!-- Titre de la page (optionnel) -->
        <span v-if="title" class="text-sm font-semibold text-slate-600 hidden sm:block">{{ title }}</span>

        <!-- Spacer -->
        <div class="flex-1"></div>

        <!-- Panier (si applicable) -->
        <button v-if="cartCount > 0"
          class="relative w-9 h-9 flex items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
          </svg>
          <span class="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center">
            {{ cartCount }}
          </span>
        </button>

        <!-- Dropdown profil -->
        <div id="profile-menu" class="relative">
          <button @click="toggleProfileDropdown"
            class="flex items-center gap-2.5 px-2 py-1.5 rounded-xl hover:bg-slate-100 transition-colors">
            <!-- Avatar -->
            <div class="w-8 h-8 rounded-full overflow-hidden border-2 border-slate-200 shrink-0">
              <img v-if="user?.profile_photo_url" :src="user.profile_photo_url" :alt="authStore.user?.user?.name" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full bg-green-700 flex items-center justify-center text-white text-xs font-bold">
                {{ authStore.user?.user?.name?.charAt(0)?.toUpperCase() ?? '?' }}
              </div>
            </div>
            <!-- Nom -->
            <span class="text-sm font-medium text-slate-700 hidden md:block max-w-[120px] truncate">
              {{ authStore.user?.user?.name ?? 'Utilisateur' }}
            </span>
            <!-- Chevron -->
            <svg class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200 hidden md:block"
              :class="{ 'rotate-180': profileDropdown }"
              fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5"/>
            </svg>
          </button>

          <!-- Menu déroulant -->
          <Transition
            enter-active-class="transition duration-150 ease-out"
            enter-from-class="opacity-0 scale-95 -translate-y-1"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition duration-100 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95">
            <div v-if="profileDropdown"
              class="absolute right-0 top-full mt-1.5 w-52 bg-white rounded-xl border border-slate-200 shadow-lg overflow-hidden z-50">

              <!-- Entête -->
              <div class="px-4 py-3 border-b border-slate-100 bg-slate-50">
                <p class="text-xs text-slate-400 uppercase tracking-wider font-semibold">Mon compte</p>
                <p class="text-sm font-semibold text-slate-700 mt-0.5 truncate">{{ authStore.user?.user?.name }}</p>
                <p class="text-xs text-slate-400 truncate">{{ user?.email }}</p>
              </div>

              <div class="py-1">
                <RouterLink :to="{ name: 'etudiant.profile' }" @click="closeProfileDropdown"
                  class="flex items-center gap-2.5 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors">
                  <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                  </svg>
                  Profil
                </RouterLink>

                <div class="h-px bg-slate-100 mx-3 my-1"></div>

                <button @click="logout"
                  class="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-500 hover:bg-red-50 transition-colors">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                  </svg>
                  Se déconnecter
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </header>

      <!-- ── BARRE DE CHARGEMENT ── -->
      <div class="h-0.5 bg-slate-100 relative overflow-hidden">
        <Transition
          enter-active-class="transition-all duration-300"
          leave-active-class="transition-all duration-500"
          enter-from-class="w-0 opacity-0"
          enter-to-class="w-3/4 opacity-100"
          leave-from-class="w-3/4 opacity-100"
          leave-to-class="w-full opacity-0">
          <div v-if="loading" class="absolute top-0 left-0 h-full bg-green-500 rounded-full
            animate-[shimmer_1s_ease-in-out_infinite]"></div>
        </Transition>
      </div>

      <!-- ── CONTENU ── -->
      <div class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-5 pb-20">
           <RouterView  :key="route.fullPath"  v-slot="{ Component, route }">
            <transition name="fade" mode="out-in">
               <component :is="Component" />
            </transition>
          </RouterView>
      </div>

      <!-- ── FOOTER ── -->
      <footer class="fixed bottom-0 left-0 w-full bg-white/90 backdrop-blur-sm border-t border-slate-200 py-2.5 z-20 transition-all duration-300"
        :class="sidebarOpen ? 'lg:pl-56' : 'pl-0'">
        <p class="text-center text-xs text-slate-400">
          <span class="font-semibold text-slate-500">infini-software</span>
          &nbsp;©&nbsp;Tous droits réservés {{ new Date().getFullYear() }}
        </p>
      </footer>

    </main>
  </div>
</template>

<style scoped>
/* Barre de progression shimmer */
@keyframes shimmer {
  0%   { transform: translateX(-100%); opacity: 1; }
  60%  { transform: translateX(0%);    opacity: 1; }
  100% { transform: translateX(100%);  opacity: 0; }
}

/* Scrollbar sidebar fine */
aside::-webkit-scrollbar       { width: 4px; }
aside::-webkit-scrollbar-track  { background: transparent; }
aside::-webkit-scrollbar-thumb  { background: rgba(255,255,255,.2); border-radius: 99px; }
</style>
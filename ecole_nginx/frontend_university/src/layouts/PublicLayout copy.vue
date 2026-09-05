<template>
  <!-- <div class="flex flex-col min-h-screen font-sans text-gray-900">
    
    <nav :class="['fixed w-full z-50 transition-all duration-300 px-6 py-4', 
                 isScrolled ? 'bg-white shadow-lg py-2' : 'bg-transparent text-white']">
      <div class="max-w-7xl mx-auto flex justify-between items-center">
        <RouterLink to="/" class="flex items-center gap-2">
          <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-white shadow-lg">
            E
          </div>
          <span :class="['text-xl font-bold tracking-tight', isScrolled ? 'text-gray-800' : 'text-white']">
            ECOLE<span class="text-blue-500">PRO</span>
          </span>
        </RouterLink>

        <div class="hidden md:flex items-center gap-8 font-medium">
          <RouterLink v-for="link in navLinks" :key="link.path" :to="link.path"
            class="hover:text-blue-500 transition-colors duration-200">
            {{ link.name }}
          </RouterLink>
          
          <RouterLink v-if="!authStore.token" to="/login" 
            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-full transition-all shadow-md hover:shadow-xl">
            Connexion
          </RouterLink>
          
          <div v-else class="flex items-center gap-4">
            <RouterLink to="/admin/dashboard" :class="isScrolled ? 'text-blue-600' : 'text-blue-400'" class="font-bold underline">Admin</RouterLink>
            <button @click="handleLogout" class="text-red-500 hover:text-red-700">Déconnexion</button>
          </div>
        </div>
      </div>
    </nav> -->
    <div class="flex flex-col min-h-screen font-sans text-gray-900">
    <nav :class="['fixed w-full z-50 transition-all duration-300 px-6 py-4', 
                 isScrolled || isMobileMenuOpen ? 'bg-white shadow-lg py-2 text-gray-800' : 'bg-transparent text-white']">
      <div class="max-w-7xl mx-auto flex justify-between items-center">
        
        <RouterLink to="/" class="flex items-center gap-2">
          <span class="text-xl font-bold tracking-tight">ECOLE<span class="text-blue-500">PRO</span></span>
        </RouterLink>

        <button @click="isMobileMenuOpen = !isMobileMenuOpen" class="md:hidden p-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path v-if="!isMobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div class="hidden md:flex items-center gap-8 font-medium">
          <RouterLink v-for="link in navLinks" :key="link.path" :to="link.path" class="hover:text-blue-500 underline-offset-4 hover:underline">
            {{ link.name }}
          </RouterLink>
          <RouterLink to="/login" class="bg-blue-600 text-white px-6 py-2 rounded-full shadow-md">Connexion</RouterLink>
        </div>
      </div>

      <div v-if="isMobileMenuOpen" class="md:hidden bg-white text-gray-800 absolute top-full left-0 w-full shadow-xl border-t p-6 flex flex-col gap-4 animate__animated animate__fadeInDown">
        <RouterLink v-for="link in navLinks" :key="link.path" :to="link.path" @click="isMobileMenuOpen = false" class="text-lg font-semibold border-b pb-2">
          {{ link.name }}
        </RouterLink>
        <RouterLink to="/login" @click="isMobileMenuOpen = false" class="bg-blue-600 text-white text-center py-3 rounded-lg">Connexion</RouterLink>
      </div>
    </nav>

     <main class="flex-grow pt-20"> 
      <RouterView v-slot="{ Component, route }">
        <!-- <transition 
          name="page-fade" 
          mode="out-in"
          enter-active-class="animate__animated animate__fadeIn animate__faster"
          leave-active-class="animate__animated animate__fadeOut animate__faster"
        > -->
          <component :is="Component" :key="route.fullPath" />
        <!-- </transition> -->
      </RouterView>
    </main>

    <footer class="bg-gray-900 text-white py-10 px-6 mt-auto">
      <div class="max-w-7xl mx-auto text-center">
        <p>© 2026 Ecole Pro - Excellence & Futur</p>
      </div>
    </footer>

    <!-- <footer class="bg-gray-900 text-gray-300 py-12 px-6">
      <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
        <div class="col-span-1 md:col-span-2">
          <h2 class="text-2xl font-bold text-white mb-4 italic">ECOLE PRO</h2>
          <p class="max-w-sm mb-6">
            L'établissement de référence pour les leaders de demain. Formation d'excellence et suivi personnalisé.
          </p>
        </div>
        <div>
          <h3 class="text-white font-bold mb-4">Navigation</h3>
          <ul class="space-y-2">
            <li><RouterLink to="/about" class="hover:text-white">À propos</RouterLink></li>
            <li><RouterLink to="/formation" class="hover:text-white">Formations</RouterLink></li>
            <li><RouterLink to="/admission" class="hover:text-white">Admissions</RouterLink></li>
          </ul>
        </div>
        <div>
          <h3 class="text-white font-bold mb-4">Contact</h3>
          <ul class="space-y-2">
            <li>📍 123 Rue de l'Éducation</li>
            <li>📞 +225 01 02 03 04</li>
            <li>✉️ contact@ecole-pro.com</li>
          </ul>
        </div>
      </div>
      <div class="max-w-7xl mx-auto border-t border-gray-800 mt-12 pt-8 text-center text-sm">
        &copy; 2026 ECOLE PRO. Tous droits réservés.
      </div>
    </footer> -->

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const isScrolled = ref(false)
const isMobileMenuOpen = ref(false)

const navLinks = [
  { name: 'Accueil', path: '/' },
  { name: 'Admission', path: '/admission' },
  { name: 'Formation', path: '/formation' },
  { name: 'Événements', path: '/evenement' },
  { name: 'Contact', path: '/contact' },
]

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

const updateScroll = () => {
  isScrolled.value = window.scrollY > 50
}

onMounted(() => window.addEventListener('scroll', updateScroll))
onUnmounted(() => window.removeEventListener('scroll', updateScroll))
</script>
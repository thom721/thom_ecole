<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { RouterLink, useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Swal from 'sweetalert2';
import { storeToRefs } from 'pinia'; 
import { useSchoolStore,useSchoolStoreInfo } from '../stores/schoolStore';  

const props = defineProps({
  title: String,
});

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();  
const useSchoolInfo = useSchoolStoreInfo()
const { user, isAdmin, isTeacher, roleNames } = storeToRefs(authStore);
const { hasRole } = authStore;

const menuIsVisible = ref(true);
const isMobile = ref(false);

// --- Navigation ---
const navLinks = [
  { name: 'Dashboard', path: '/dashboard', icon: 'fas fa-tachometer-alt' },
  { name: 'Administration', path: 'administration', icon: 'fas fa-user-shield' },
  { name: 'Étudiants', path: '/etudiants', icon: 'fas fa-user-graduate' },
  { name: 'Professeurs', path: '/professeurs', icon: 'fas fa-chalkboard-teacher' },
  { name: 'Notes', path: '/notes', icon: 'fas fa-file-signature' },
  { name: 'Cours', path: '/cours', icon: 'fas fa-book' },
  { name: 'Paiements', path: '/paiements', icon: 'fas fa-money-bill-wave' },
  { name: 'Paramètres', path: '/parametres', icon: 'fas fa-gears' },
  { name: 'Profile', path: '/profile', icon: 'ri-user' },
  { name: 'Rapport', path: '/rapport', icon: 'fas fa-gears' },
];

const isActive = (path) => route.path === path;

// --- Logique d'affichage ---
const toggleMenu = () => {
  menuIsVisible.value = !menuIsVisible.value;
};

const handleResize = () => {
  isMobile.value = window.innerWidth < 1024;
  if (isMobile.value) {
    menuIsVisible.value = false;
  } else {
    menuIsVisible.value = true;
  }
};

const logout = async () => {
  const result = await Swal.fire({
    title: 'Déconnexion ?',
    text: "Voulez-vous vraiment quitter la session ?",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#0284c7',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Oui, déconnexion'
  });

  if (result.isConfirmed) {
    await authStore.logout();
    router.push('/login');
  }
};

onMounted( async () => {
  if (!authStore.user) await authStore.initializeAuth();
  
  if (!authStore.roleNames.includes('admin')) {
    router.push({ name: 'login' });
  }
   console.log('user 2:', user.value);
  console.log('isAdmin1:', isAdmin.value);
  console.log('isTeacher:', isTeacher.value);
  console.log('roleNames:', roleNames.value);
  console.log('hasRole:', hasRole(['admin', 'teacher']));
  
  window.addEventListener('resize', handleResize);
  handleResize();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<template>
  <div class="flex min-h-screen bg-slate-100 font-sans">

    <aside 
      class="bg-sky-600 transition-all duration-300 ease-in-out shadow-xl flex-shrink-0 z-50 overflow-y-auto overflow-x-hidden"
      :class="[
        menuIsVisible ? 'w-64' : 'w-0',
        isMobile ? 'fixed h-full' : 'relative sticky top-0 h-screen'
      ]"
    > 
      <div class="w-64">
        <div class="flex flex-col items-center py-6 bg-sky-700 border-b border-sky-500">
          <div class="h-16 w-16 bg-white rounded-full flex items-center justify-center shadow-inner overflow-hidden mb-2">
             <img v-if="useSchoolInfo.school_info?.logo_image_base64" :src="useSchoolInfo.school_info?.logo_image_base64" class="object h-full w-full">
             <span v-else class="text-sky-700 font-bold text-2xl">EP</span>
          </div> 
          <span class="text-white font-bold text-sm tracking-widest uppercase">Ecole Pro</span>
        </div>

        <nav class="mt-4 flex flex-col px-3 gap-1">
   
      
<!-- flex items-center py-3 px-4 rounded-lg text-sky-50 transition-all duration-200 hover:bg-sky-500 group -->
          <RouterLink 
          v-for="link in navLinks" 
          :key="link.path"  :to="link.path"
          class="flex items-center py-3 px-4 rounded-lg text-sky-50 hover:text-blue-white transition-colors duration-200 hover:bg-sky-500 group"
          :class="{ 'bg-sky-700 font-bold': $route.path === link.path }"
        >
          <i :class="[link.icon, 'w-6 text-center mr-3 group-hover:scale-110 transition-transform']"></i>
          <span class="text-sm">{{ link.name }}</span>
        </RouterLink>

            <div class="flex items-center py-3 px-4 rounded-lg text-sky-50 transition-all duration-200 hover:bg-sky-500 group">
              <router-link v-if="isTeacher" to="/teacher/dashboard">
                    Portail Professeur
              </router-link>
              </div>

          <button 
            @click="logout"
            class="mt-8 flex items-center py-3 px-4 rounded-lg text-red-100 hover:bg-red-600 transition-all duration-200 group"
          >
            <i class="fas fa-sign-out-alt w-6 text-center mr-3 group-hover:translate-x-1 transition-transform"></i>
            <span class="text-sm font-bold">Quitter la session</span>
          </button>
        </nav>
      </div>
    </aside>

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      
      <header class="h-16 bg-white shadow-sm flex items-center justify-between px-6 sticky top-0 z-40">
        <div class="flex items-center gap-4">
          <button 
            @click="toggleMenu" 
            class="bg-sky-500 hover:bg-sky-400 text-white rounded-full transition-all border border-sky-100 shadow-sm focus:outline-none cursor-pointer h-8 w-8 flex items-center justify-center"
          >
            <i :class="menuIsVisible ? 'fas fa-chevron-left' : 'ri-menu-line'" class="text-xl w-8 h-8 rounded-full"></i>
          </button>
          <h2 class="font-bold text-slate-700 hidden md:block">Système de Gestion Scolaire</h2>
        </div>

        <div class="flex items-center gap-3">
          <div class="text-right hidden sm:block">
            <p class="text-sm font-bold text-slate-800 leading-tight">{{ authStore.user?.user?.name }}</p>
            <p class="text-xs text-slate-400 font-medium">Administrateur</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-sky-600 text-white flex items-center justify-center font-bold shadow-md border-2 border-white">
            {{ authStore.user?.user?.name?.charAt(0).toUpperCase() }}
          </div>
        </div>
      </header>

      <main class="p-4 md:p-6 flex-grow overflow-y-auto bg-slate-50">
  <!-- <RouterView :key="$route.fullPath" /> -->
          <!-- <RouterView  :key="$route.fullPath" v-slot="{ Component, route }">
            <transition name="fade" mode="out-in">
               <component :is="Component" :key="route.fullPath" />
            </transition>
          </RouterView> -->

          <RouterView  :key="route.fullPath" v-slot="{ Component, route }">
  <transition name="fade" mode="out-in">
    <component :is="Component" />
  </transition>
</RouterView>
   
      </main>

      <footer class="bg-white border-t py-4 px-6 text-center text-slate-400 text-xs">
        <p><strong>Ecole Pro</strong> © 2026 - Infini Software. Tous droits réservés.</p>
      </footer>
    </div>

    <div 
      v-if="isMobile && menuIsVisible" 
      @click="menuIsVisible = false"
      class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-40 transition-opacity"
    ></div>

    <button 
      v-if="isMobile && !menuIsVisible" 
      @click="toggleMenu"
      class="fixed bottom-6 right-6 w-14 h-14 bg-sky-600 text-white rounded-full shadow-2xl z-[60] flex items-center justify-center animate-bounce border-4 border-white"
    >
      <i class="ri-menu-line text-xl"></i>
    </button>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Animation de transition douce */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Scrollbar discrète pour la sidebar */
aside::-webkit-scrollbar {
  width: 3px;
}
aside::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
</style>
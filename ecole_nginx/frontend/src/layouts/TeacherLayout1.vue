<template>
  <div>
    <!-- Sidebar -->
    <div 
      class="fixed left-0 top-0 h-full bg-slate-600 z-50 transition-all duration-300 ease-in-out overflow-y-auto"
      :class="{ 'w-0 sidebar-menu': !menuIsVisible, 'w-56': menuIsVisible }"
    >
      <div 
        class="flex justify-center items-center h-[50px] bg-slate-700 border-b border-b-gray-50 transition-all duration-300 ease-in-out"
        :class="{ 'fixed': admin }"
      >
      <!-- <button @click.stop="toggle" id="sidebar-toggle">
    <i class="ri-menu-line"></i>
</button> -->
        <!-- <div class="d-flex justify-content-center py-1">
          <img 
            v-if="school" 
            class="shadow-1 rounded-circle border border-light" 
            height="50"
            width="50" 
            :src="school.logo_image_url" 
            alt=""
          >
        </div> -->
      </div>

      <ul 
        class="mt-4 pb-10"
        :class="{ 
          'hidden': !menuIsVisible, 
          'show shows': menuIsVisible, 
          'pt-16': admin 
        }"
      >
        <router-link 
          to="/teacher/dashboard"
          class="flex items-center py-4 px-6 text-white transition-all duration-500 hover:bg-gray-800 hover:text-white hover:text-xl text-lg border-b-gray-400 border-b"
          :class="{ 'bg-slate-700 text-gray-50 font-bold': isActiveRoute('/teacher/dashboard') }"
        >
          <i class="fas fa-tachometer-alt fa-fw textPrimary1 me-2"></i>Dashboard
        </router-link>

        <router-link 
          to="/teacher/cours"
          class="flex items-center py-4 px-6 text-white transition-all duration-500 hover:bg-slate-700 hover:text-white hover:text-xl text-lg border-b-gray-400 border-b"
          :class="{ 'bg-slate-700 text-gray-50 font-bold': isActiveRoute('/teacher/cours') }"
        >
          <i class="fas fa-user-group fa-fw textPrimary1 me-2"></i> Cours
        </router-link>

        <router-link 
          to="/teacher/notes"
          class="flex items-center py-4 px-6 text-white transition-all duration-500 hover:bg-slate-700 hover:text-white hover:text-xl text-lg border-b-gray-400 border-b"
          :class="{ 'bg-slate-700 text-gray-50 font-bold': isActiveRoute('/teacher/notes') }"
        >
          <i class="fas fa-user-group fa-fw textPrimary1 me-2"></i> Notes
        </router-link>

        <router-link 
          to="/teacher/profile"
          class="flex items-center py-4 px-6 text-white transition-all duration-500 hover:bg-slate-700 hover:text-white hover:text-xl text-lg border-b-gray-400 border-b"
          :class="{ 'bg-slate-700 text-gray-50 font-bold': isActiveRoute('/teacher/profile') }"
        >
          <i class="fas fa-user-check fa-fw textPrimary1 me-2"></i> Profile
        </router-link>

        <router-link 
          v-if="isAdmin"
          to="/admin/dashboard"
          class="flex items-center py-4 px-6 text-white transition-all duration-500 hover:bg-slate-700 hover:text-white hover:text-xl text-lg border-b-gray-400 border-b"
        >
          <i class="fas fa-user-check fa-fw textPrimary1 me-2"></i> Portail Admin
        </router-link>

        <button
          @click="logout"
          class="w-full flex items-center py-4 px-6 text-white transition-all duration-500 hover:bg-slate-700 hover:text-white hover:text-xl text-lg border-b-gray-400 border-b text-left"
        >
          <i class="fas fa-sign-out-alt fa-fw textPrimary1 me-2"></i> Log Out
        </button>
      </ul>
    </div>

    <!-- Main Content -->
    <main class="md:p-6 flex-grow overflow-y-auto bg-slate-50">
      <!-- Header -->
      <div 
        class="h-[50px] px-6 bg-white flex items-center shadow-sm border-b shadow-black/5 sticky top-0 left-0 z-30 transition-all duration-300"
        :class="{ 'ml-0': !menuIsVisible, 'sm:ml-56': menuIsVisible }"
      >
        <button 
          ref="menuBtn" 
          type="button" 
          class="text-lg text-gray-600" 
          @click="toggle"
        >
          <i class="ri-menu-line me-4"></i>
        </button>

        <div class="flex ml-auto justify-end items-center">
          <!-- User Dropdown -->
          <div class="ms-3 relative">
            <div class="relative">
              <button
                @click="toggleDropdown"
                class="flex items-center md:gap-4"
              >
                <p class="text-slate-600 text-lg hidden md:block" v-if="user">
                  {{ user.name }}
                </p>
                <div class="flex text-sm border-2 border-transparent rounded-full focus:outline-none focus:border-gray-300 transition">
                  <img 
                    v-if="user?.profile_photo_url"
                    class="h-8 w-8 rounded-full border object-cover"
                    :src="user.profile_photo_url"
                    :alt="user.name"
                  >
                  <span v-else>
                    <i class="ri-user-2-fill text-2xl text-slate-500 h-8 w-8 border-slate-500 rounded-full border p-1"></i>
                  </span>
                </div>
              </button>

              <!-- Dropdown Menu -->
              <div 
                v-if="dropdownOpen"
                class="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5"
              >
                <div class="py-1">
                  <div class="block px-4 py-2 text-xs text-gray-400">
                    Manage Account
                  </div>
                  <router-link
                    to="/teacher/profile"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    @click="dropdownOpen = false"
                  >
                    Profile
                  </router-link>
                  <div class="py-1">
                    <p v-if="user">{{ user.name }}</p>
                    <img v-if="school" :src="school.logo_image_url" />
                    <router-link v-if="hasRole" to="/admin/dashboard">
                         Portail Admin
                    </router-link>
                    </div>
                  <div class="border-t border-gray-200"></div>
                  <button
                    @click="logout"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Log Out
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Page Content -->
      <div 
        class="transition-all duration-300 pb-16"
        :class="{ 'ml-0': !menuIsVisible, 'md:ml-56': menuIsVisible }"
      >
        <!-- Loading Spinner -->
        <div v-if="loading" class="max-w-7xl px-4 mx-auto sm:px-6 lg:px-8 pt-4">
          <div class="flex justify-center items-center h-screen">
            <svg 
              class="containers" 
              x="0px" 
              y="0px" 
              viewBox="0 0 50.10 23.1" 
              height="23.1" 
              width="50"
              preserveAspectRatio="xMidYMid meet"
            >
              <path 
                class="track" 
                fill="none" 
                stroke-width="2" 
                pathlength="100"
                d="M26.7,12.2c3.5,3.4,7.4,7.8,12.7,7.8c5.5,0,9.6-4.4,9.6-9.5C49,5,45.1,1,39.8,1c-5.5,0-9.5,4.2-13.1,7.8l-3.4,3.3c-3.6,3.6-7.6,7.8-13.1,7.8C4.9,20,1,16,1,10.5C1,5.4,5.1,1,10.6,1c5.3,0,9.2,4.5,12.7,7.8L26.7,12.2z" 
              />
              <path 
                class="car" 
                fill="none" 
                stroke-width="2" 
                pathlength="100"
                d="M26.7,12.2c3.5,3.4,7.4,7.8,12.7,7.8c5.5,0,9.6-4.4,9.6-9.5C49,5,45.1,1,39.8,1c-5.5,0-9.5,4.2-13.1,7.8l-3.4,3.3c-3.6,3.6-7.6,7.8-13.1,7.8C4.9,20,1,16,1,10.5C1,5.4,5.1,1,10.6,1c5.3,0,9.2,4.5,12.7,7.8L26.7,12.2z" 
              />
            </svg>
          </div>
        </div>

        <!-- Main Content Slot -->
        <div v-else class="max-w-7xl px-4 mx-auto sm:px-6 lg:px-8 pt-4" >
             <RouterView v-slot="{ Component, route }">
            <transition name="fade" mode="out-in">
               
               <component :is="Component" :key="route.fullPath" />
            </transition>
          </RouterView>
        </div>
      </div>

      <!-- Footer -->
      <footer class="fixed left-0 bottom-0 w-full">
        <div class="border-t border-gray-300 shadow bg-gray-100 py-2">
          <p 
          
            class="flex justify-center text-lg text-slate-600 items-center transition-all duration-300"
            :class="{ 'ml-0': !menuIsVisible, 'sm:ml-56': menuIsVisible }"
          >
            <span class="text-medium me-2">infini-software</span> © Tous droits réservés. 
          </p>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import Swal from 'sweetalert2';
import { useAuthStore } from '@/stores/auth'; 
import { storeToRefs } from 'pinia';
const authStore = useAuthStore();
import { isGlobalLoading } from '@/router'; 
 

// Router
const router = useRouter();
const route = useRoute();


const { user, isAdmin, isTeacher, roleNames } = storeToRefs(authStore);
const { hasRole } = authStore;

// Refs
const menuIsVisible = ref(false);
const menuBtn = ref(null);
const admin = ref(false); 
const dropdownOpen = ref(false);
const loading = ref(false);

// Methods
const showSwalInfo = (text, color) => {
  Swal.fire({
    position: "top-end",
    text: text,
    showConfirmButton: false,
    timer: 2000,
    color: color,
  });
};

const toggle = () => {
  menuIsVisible.value = !menuIsVisible.value;
  admin.value = false;
};

const show = () => {
  menuIsVisible.value = true;
};

const hide = () => {
     console.log('menuIsVisible.value ' +menuIsVisible.value);
     console.log('admin.value  '+admin.value);
     
  menuIsVisible.value = false;
  admin.value = false;
};

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
};

const isActiveRoute = (path) => {
  return route.path === path;
};

const logout = async () => {
  await authStore.logout();
  router.push('/login');
};

const logout1 = async () => {
  try {
    // Supprimer les tokens
    localStorage.removeItem('auth-token');
    sessionStorage.removeItem('auth-token');
    localStorage.removeItem('api_token');
    
    // Appel API de déconnexion
    await fetch('/api/logout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth-token')}`
      }
    });
    
    // Redirection vers la page de login
    router.push('/login');
  } catch (error) {
    console.error('Logout error:', error);
    router.push('/login');
  }
};

const handleResize = () => {
     window.innerWidth < 992 ? menuIsVisible.value = false : menuIsVisible.value = true;
  if (window.innerWidth < 992) {
    hide();
  } else {
    show();
  }
};

const handleClickOutside = (event) => {
  if (window.innerWidth < 540 && menuIsVisible.value) {
    if (menuBtn.value && !menuBtn.value.contains(event.target)) {
      hide();
    }
  }
  
  // Fermer le dropdown si on clique ailleurs
  if (dropdownOpen.value && !event.target.closest('.relative')) {
    dropdownOpen.value = false;
  }
};
 

onMounted(async() => {
if (!authStore.user) await authStore.initializeAuth();
  
  if (!authStore.roleNames.includes('teacher')) {
    router.push({ name: 'login' });
  }
  window.addEventListener('resize', handleResize);
  window.addEventListener('click', handleClickOutside);
  handleResize();
  
});

// onUnmounted(() => {
//   window.removeEventListener('resize', handleResize);
//   window.removeEventListener('click', handleClickOutside);
// });

 


const handleClickOutside1 = (event) => {
  // 1. Gestion Sidebar Mobile
  console.log(event);
  
  if (window.innerWidth < 992 && menuIsVisible.value) {
    const sidebar = document.querySelector('.sidebar-menu');
    const toggleBtn = document.querySelector('#sidebar-toggle');
    
    // Si le clic n'est ni sur la sidebar, ni sur le bouton toggle
    if (sidebar && !sidebar.contains(event.target) && !toggleBtn?.contains(event.target)) {
      menuIsVisible.value = false;
    }
  }
  
  // 2. Gestion Dropdown
  if (dropdownOpen.value && !event.target.closest('.relative')) {
    dropdownOpen.value = false;
  }
};
</script>

<style scoped>
.containers {
  --uib-size: 200px;
  --uib-color: rgb(44, 119, 218);
  --uib-speed: 1.3s;
  --uib-bg-opacity: .1;
  height: calc(var(--uib-size) * (2.1 / 5));
  width: var(--uib-size);
  transform-origin: center;
  overflow: visible;
}

.car {
  fill: none;
  stroke: var(--uib-color);
  stroke-dasharray: 15, 85;
  stroke-dashoffset: 0;
  stroke-linecap: round;
  animation: travel var(--uib-speed) linear infinite;
  will-change: stroke-dasharray, stroke-dashoffset;
  transition: stroke 0.5s ease;
}

.track {
  stroke: var(--uib-color);
  opacity: var(--uib-bg-opacity);
}

@keyframes travel {
  0% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: 100;
  }
}
</style>
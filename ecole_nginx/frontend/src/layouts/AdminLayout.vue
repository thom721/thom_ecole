<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth';
import { storeToRefs } from 'pinia';
import { useSchoolStore, useSchoolStoreInfo } from '../stores/schoolStore';
import axios from 'axios';
import { useIdleTimer } from '../composables/useIdleTimer';

const authStore = useAuthStore();
const useSchoolInfo = useSchoolStoreInfo();
const schoolStore = useSchoolStore();
const { niveau, professeur, annee, classes, faculte, cours, loading } = storeToRefs(schoolStore);

const profileDropdown = ref(false);
const toggleProfileDropdown = () => { profileDropdown.value = !profileDropdown.value; };
const closeProfileDropdown = () => { profileDropdown.value = false; };

const router = useRouter();

const logout = async () => {
  localStorage.removeItem('auth-token');
  sessionStorage.removeItem('auth-token');
  localStorage.removeItem('api_token');
  await authStore.logout?.();
  router.push({ name: 'login' });
};

// ── Déconnexion automatique après 10 min d'inactivité ─────────────────────
const { showWarning, secondsLeft, stayConnected } = useIdleTimer(() => {
  logout()
});

// ── Props ──────────────────────────────────────────────────────────────────
const props = defineProps({
  appName:         { type: String, default: 'Lekol360' },
  appSub:          { type: String, default: 'Espace Admin' },
  appInitial:      { type: String, default: 'L' },
  teacherName:     { type: String, default: 'Admin' },
  teacherInitials: { type: String, default: 'AD' },
  teacherRole:     { type: String, default: 'Administrateur' },
  defaultAccent:   { type: String, default: '#4f8ef7' },
  navSections: {
    type: Array,
    default: () => [
      {
        label: 'Navigation',
        items: [
          {
            name: 'Dashboard', label: 'Tableau de Bord', to: '/dashboard', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>`
          },
          {
            name: 'teacher.classes', label: 'Administration', to: '/administration', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>`
          },
          {
            name: 'Étudiants', label: 'Étudiants', to: '/etudiants', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>`
          },
          {
            name: 'Professeurs', label: 'Professeurs', to: '/professeurs', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>`
          },
          {
            name: 'Notes', label: 'Notes', to: '/notes', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>`
          },
          {
            name: 'Cours', label: 'Cours', to: '/cours', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>`
          },
          {
            name: 'Paiements', label: 'Paiements', to: '/paiements', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><rect x="1" y="4" width="22" height="16" rx="2"/><path d="M1 10h22"/></svg>`
          },
          {
            name: 'Trésorerie', label: 'Trésorerie', to: '/tresorerie', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><rect x="1" y="4" width="22" height="16" rx="2"/><path d="M1 10h22"/></svg>`
          },

          {
            name: 'Communauté', label: 'Communauté', to: '/communaute', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><rect x="1" y="4" width="22" height="16" rx="2"/><path d="M1 10h22"/></svg>`
          },

          {
            name: 'Présences', label: 'Présences', to: '/presences', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><rect x="1" y="4" width="22" height="16" rx="2"/><path d="M1 10h22"/></svg>`
          },
          
          {
            name: 'Rapport', label: 'Rapport', to: '/rapport', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>`
          },
          {
            name: 'Paramètres', label: 'Paramètres', to: '/parametres', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><circle cx="12" cy="12" r="3"/></svg>`
          },
          {
            name: 'Abonnement', label: 'Abonnement', to: '/abonnement', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 2"/><circle cx="12" cy="12" r="9"/></svg>`
          },
        ]
      },
      {
        label: 'Gestion',
        items: [
          {
            name: 'calendrier', label: 'Calendrier', to: '/calendrier', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>`
          },
          {
            name: 'statistiques', label: 'Statistiques', to: '/statistiques', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>`
          },
          {
            name: 'Profile', label: 'Profil', to: '/profile', badge: null,
            icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" width="18" height="18"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>`
          },
        ]
      }
    ]
  }
});

// ── State ──────────────────────────────────────────────────────────────────
const sidebarOpen      = ref(true);
const sidebarCollapsed = ref(false);
const isMobile         = ref(false);
const showColorPanel   = ref(false);
const accentColor      = ref(props.defaultAccent);
const colorPanelRef    = ref(null);

// ── Router ─────────────────────────────────────────────────────────────────
const route = useRoute();
const currentRouteLabel = computed(() => {
  for (const s of props.navSections) {
    const item = s.items.find(i => i.to === route.path || route.path.startsWith(i.to + '/'));
    if (item) return item.label;
  }
  return route.meta?.label ?? 'Page';
});

// ── CSS vars ───────────────────────────────────────────────────────────────
const cssVars = computed(() => {
  const hex = accentColor.value.replace('#', '');
  const r = parseInt(hex.slice(0, 2), 16) || 79;
  const g = parseInt(hex.slice(2, 4), 16) || 142;
  const b = parseInt(hex.slice(4, 6), 16) || 247;
  return { '--accent': accentColor.value, '--accent-rgb': `${r},${g},${b}` };
});

// ── Presets ────────────────────────────────────────────────────────────────
const presetColors = [
  { name: 'Bleu',     value: '#4f8ef7' }, { name: 'Indigo',   value: '#818cf8' },
  { name: 'Violet',   value: '#a78bfa' }, { name: 'Rose',     value: '#f472b6' },
  { name: 'Corail',   value: '#f87171' }, { name: 'Ambre',    value: '#f59e0b' },
  { name: 'Vert',     value: '#6ee7b7' }, { name: 'Emeraude', value: '#10b981' },
  { name: 'Cyan',     value: '#22d3ee' }, { name: 'Ardoise',  value: '#94a3b8' },
];

// ── Methods ────────────────────────────────────────────────────────────────
const toggleSidebar = () => {
  if (isMobile.value) {
    sidebarOpen.value = !sidebarOpen.value;
  } else {
    sidebarOpen.value = !sidebarOpen.value;
    if (!sidebarOpen.value) sidebarCollapsed.value = false;
  }
};
const toggleCollapse = () => {
  if (!isMobile.value) sidebarCollapsed.value = !sidebarCollapsed.value;
};

const checkMobile = () => {
  const m = window.innerWidth < 768;
  if (m !== isMobile.value) {
    isMobile.value = m;
    sidebarOpen.value = !m;
    if (m) sidebarCollapsed.value = false;
  }
};

const onOutsideClick = (e) => {
  if (colorPanelRef.value && !colorPanelRef.value.contains(e.target)) {
    showColorPanel.value = false;
  }
  if (!e.target.closest('#profile-menu')) {
    closeProfileDropdown();
  }
};

// Correspondance nom d'item de nav → ID d'onglet (identique à kAllNavItems Flutter)
const NAV_TAB_ID = {
  'Dashboard':      'home',
  'Administration': 'admin',
  'Étudiants':      'etudiant',
  'Professeurs':    'prof',
  'Notes':          'notes',
  'Cours':          'cours',
  'Paiements':      'paiement',
  'Trésorerie':     'vente',
  'Présences':      'presences',
  'Rapport':        'rapport',
  'Paramètres':     'settings',
  'Abonnement':     'abonnement',
  'Profile':        'profile',
}

// Vérifier si un élément du menu doit être affiché selon les permissions
const shouldShowMenuItem = (itemName) => {
  // Profil toujours visible pour tous les utilisateurs authentifiés
  if (itemName === 'Profile') return true;

  // Utilisateurs avec seulement le rôle 'user' ne voient que Profile
  if (authStore.isBaseUser) return false;

  // Respecter accessible_tabs configuré par rôle (null = accès total)
  const tabs = authStore.user?.tab_ids ?? null;
  if (tabs !== null) {
    const tabId = NAV_TAB_ID[itemName];
    if (tabId && !tabs.includes(tabId)) return false;
  }

  // Vérifier les permissions spécifiques pour chaque élément du menu
  switch (itemName) {
    case 'Dashboard':
      return authStore.canAccessDashboard;
    case 'teacher.classes': // Administration
      return authStore.canAccessAdministration;
    case 'Étudiants':
      return authStore.canAccessEtudiants;
    case 'Professeurs':
      return authStore.canAccessProfesseurs;
    case 'Notes':
      return authStore.canAccessNotes;
    case 'Cours':
      return authStore.canAccessCours;
    case 'Paiements':
      return authStore.canAccessPaiement;
    case 'Trésorerie':
      return authStore.canAccessTresorerie;
    case 'Présences':
      return authStore.canAccessPresences;
    case 'Rapport':
      return authStore.canAccessRapports;
    case 'Paramètres':
      return authStore.canAccessParametres;
    case 'Abonnement':
      return authStore.isAdmin;
    case 'Communauté':
    case 'calendrier':
    case 'statistiques':
      // Ces éléments sont accessibles à tous les rôles métier
      return authStore.hasBusinessRole;
    default:
      return true;
  }
};

onMounted(async () => {
  checkMobile();
  window.addEventListener('resize', checkMobile);
  document.addEventListener('click', onOutsideClick);
  if (!authStore.user) await authStore.initializeAuth();
  // Suppression de la vérification stricte 'admin' pour permettre aux autres rôles d'accéder
});
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile);
  document.removeEventListener('click', onOutsideClick);
});

// Computed school name
const schoolName = computed(() => useSchoolInfo.school_info?.nom || props.appName);
const userInitial = computed(() => authStore.user?.user?.username?.charAt(0)?.toUpperCase() ?? '?');
const userName = computed(() => authStore.user?.user?.username ?? 'Utilisateur');
const userEmail = computed(() => authStore.user?.user?.email ?? '');
</script>

<template>
  <div
    class="min-h-screen bg-[#0f1117] text-[#e8eaf0] font-sans overflow-x-hidden"
    style="max-width: 100vw;"
    :style="cssVars"
  >

    <!-- ░░ MOBILE OVERLAY ░░ -->
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      leave-active-class="transition-opacity duration-300"
      leave-to-class="opacity-0"
    >
      <div
        v-if="sidebarOpen && isMobile"
        @click="sidebarOpen = false"
        class="fixed inset-0 bg-black/60 backdrop-blur-sm z-20"
      />
    </Transition>

    <!-- ░░ SIDEBAR ░░ -->
    <Transition
      enter-active-class="transition-transform duration-300 ease-out"
      enter-from-class="-translate-x-full"
      leave-active-class="transition-transform duration-300 ease-in"
      leave-to-class="-translate-x-full"
    >
      <aside
        v-show="sidebarOpen"
        class="fixed top-0 left-0 h-full z-30 flex flex-col bg-[#171b26] border-r border-white/[0.07] overflow-hidden transition-[width] duration-300 ease-in-out"
        :class="sidebarCollapsed && !isMobile ? 'w-[68px]' : 'w-[240px]'"
      >
        <!-- Accent bar -->
        <div class="h-[3px] w-full flex-shrink-0 transition-colors duration-300" :style="{ background: accentColor }" />

        <!-- LOGO -->
        <div
          class="flex items-center gap-3 px-4 py-5 border-b border-white/[0.07] flex-shrink-0"
          :class="sidebarCollapsed && !isMobile ? 'justify-center' : ''"
        >
          <div
            @click="toggleCollapse"
            class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 font-bold text-[17px] text-white cursor-pointer select-none shadow-lg transition-all duration-300"
            :style="{ background: accentColor, boxShadow: `0 4px 14px color-mix(in srgb, ${accentColor} 35%, transparent)` }"
          >{{ appInitial }}</div>
          <Transition
            enter-active-class="transition-opacity duration-200"
            enter-from-class="opacity-0"
            leave-active-class="transition-opacity duration-150"
            leave-to-class="opacity-0"
          >
            <div v-if="!sidebarCollapsed || isMobile" class="overflow-hidden whitespace-nowrap">
              <div class="text-[15px] font-semibold text-[#e8eaf0] leading-tight" style="font-family:'Playfair Display',serif">
                {{ schoolName }}
              </div>
              <div class="text-[11px] text-[#7c83a0] tracking-wide">{{ appSub }}</div>
            </div>
          </Transition>
        </div>

        <!-- NAV -->
        <nav class="flex-1 overflow-y-auto py-4 px-2 space-y-0.5">
          <template v-for="section in navSections" :key="section.label">
            <!-- Section label -->
            <p
              v-if="!sidebarCollapsed && section.label"
              class="text-[10px] uppercase tracking-[0.12em] text-[#7c83a0] font-medium px-3 pt-3 pb-1.5"
            >{{ section.label }}</p>

            <!-- Divider collapsed -->
            <div v-if="sidebarCollapsed && !isMobile && section.label" class="h-px bg-white/[0.06] mx-2 my-2" />

            <!-- Nav items — RouterLink avec `to` absolu -->
            <RouterLink
              v-for="item in section.items"
              :key="item.name"
              :to="item.to"
              custom
              v-slot="{ isActive, navigate }"
            >
              <div
                v-if="shouldShowMenuItem(item.name)"
                @click="() => { navigate(); if (isMobile) sidebarOpen = false; }"
                class="relative flex items-center gap-2.5 rounded-xl cursor-pointer transition-all duration-200 text-[13.5px] font-normal text-[#7c83a0] group mb-0.5"
                :class="[
                  sidebarCollapsed && !isMobile ? 'justify-center px-0 py-3 mx-1' : 'px-3 py-2.5',
                  isActive
                    ? 'text-[var(--accent)] font-medium'
                    : 'hover:bg-white/[0.05] hover:text-[#e8eaf0]'
                ]"
                :style="isActive ? { background: `color-mix(in srgb, ${accentColor} 13%, transparent)` } : {}"
              >
                <!-- Icon -->
                <span
                  class="w-[18px] h-[18px] flex-shrink-0 transition-colors duration-200"
                  :class="isActive ? 'text-[var(--accent)]' : 'text-[#7c83a0] group-hover:text-[#e8eaf0]'"
                  v-html="item.icon"
                />

                <!-- Label + badge -->
                <template v-if="!sidebarCollapsed || isMobile">
                  <span class="flex-1 whitespace-nowrap">{{ item.label }}</span>
                  <span
                    v-if="item.badge"
                    class="text-[10px] font-semibold px-[7px] py-[2px] rounded-full text-white"
                    :style="{ background: accentColor }"
                  >{{ item.badge }}</span>
                </template>

                <!-- Tooltip collapsed -->
                <div
                  v-if="sidebarCollapsed && !isMobile"
                  class="pointer-events-none absolute left-[calc(100%+12px)] top-1/2 -translate-y-1/2 bg-[#1e2335] text-[#e8eaf0] text-[12px] font-medium whitespace-nowrap px-2.5 py-1.5 rounded-lg border border-white/[0.08] opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-50 flex items-center gap-2"
                >
                  {{ item.label }}
                  <span v-if="item.badge" class="text-[10px] font-bold px-1.5 py-0.5 rounded-full text-white" :style="{ background: accentColor }">{{ item.badge }}</span>
                </div>
              </div>
            </RouterLink>
          </template>
        </nav>

        <!-- COLOR PICKER -->
        <div class="px-2 pb-2 flex-shrink-0 border-t border-white/[0.07] pt-2 relative" ref="colorPanelRef">
          <button
            @click.stop="showColorPanel = !showColorPanel"
            class="flex items-center gap-2 w-full rounded-xl transition-all duration-200 text-[#7c83a0] hover:text-[#e8eaf0] hover:bg-white/[0.05]"
            :class="sidebarCollapsed && !isMobile ? 'justify-center p-3' : 'px-3 py-2.5'"
          >
            <span class="w-3.5 h-3.5 rounded-full flex-shrink-0 border-2 border-white/20 transition-colors duration-300" :style="{ background: accentColor }" />
            <span v-if="!sidebarCollapsed || isMobile" class="text-[13px] font-medium">Couleur</span>
          </button>

          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-95 -translate-y-1"
            leave-active-class="transition-all duration-150 ease-in"
            leave-to-class="opacity-0 scale-95 -translate-y-1"
          >
            <div
              v-if="showColorPanel"
              class="absolute bottom-full left-2 right-2 mb-2 bg-[#1e2335] border border-white/[0.1] rounded-2xl p-4 shadow-2xl z-50"
            >
              <p class="text-[10px] uppercase tracking-widest text-[#7c83a0] font-medium mb-3">Couleur principale</p>
              <div class="grid grid-cols-5 gap-2 mb-3">
                <button
                  v-for="c in presetColors"
                  :key="c.value"
                  @click="accentColor = c.value"
                  :title="c.name"
                  :style="{ background: c.value }"
                  class="w-8 h-8 rounded-lg transition-all duration-150 hover:scale-110"
                  :class="accentColor === c.value ? 'scale-110 ring-2 ring-offset-2 ring-offset-[#1e2335]' : 'opacity-75 hover:opacity-100'"
                />
              </div>
              <div class="flex items-center gap-2">
                <input type="color" v-model="accentColor" class="w-8 h-8 rounded-lg cursor-pointer border-0 bg-transparent p-0" />
                <input
                  type="text" v-model="accentColor"
                  class="flex-1 bg-[#0f1117] border border-white/10 rounded-lg px-3 py-1.5 text-[12px] text-[#e8eaf0] font-mono focus:outline-none focus:border-white/20"
                  placeholder="#4f8ef7"
                />
              </div>
            </div>
          </Transition>
        </div>

        <!-- PROFILE BOTTOM -->
        <div
          class="border-t border-white/[0.07] p-4 flex-shrink-0 flex items-center gap-2.5"
          :class="sidebarCollapsed && !isMobile ? 'justify-center' : ''"
        >
          <div
            class="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 text-[13px] font-bold text-[#0f1117]"
            :style="{ background: `linear-gradient(135deg, ${accentColor}, #6ee7b7)` }"
          >{{ userInitial }}</div>
          <div v-if="!sidebarCollapsed || isMobile" class="overflow-hidden min-w-0">
            <p class="text-[13px] font-medium text-[#e8eaf0] truncate">{{ userName }}</p>
            <p class="text-[11px] text-[#7c83a0] truncate">{{ userEmail || teacherRole }}</p>
          </div>
        </div>

      </aside>
    </Transition>
 
    <div
      class="flex flex-col min-h-screen transition-[padding-left] duration-300 ease-in-out"
      :style="{
        paddingLeft: isMobile ? '0px' : sidebarOpen ? (sidebarCollapsed ? '68px' : '240px') : '0px'
      }"
    >
      <!-- TOPBAR -->
      <header class="sticky top-0 z-10 flex items-center gap-3 px-4 h-14 bg-[#0f1117]/95 backdrop-blur-md border-b border-white/[0.07] flex-shrink-0 w-full">

        <!-- Hamburger -->
        <button
          @click="toggleSidebar"
          class="flex flex-col justify-center items-center w-9 h-9 gap-[5px] rounded-xl hover:bg-white/[0.06] transition-colors duration-200 flex-shrink-0"
          aria-label="Menu"
        >
          <span class="block h-[2px] w-5 bg-[#e8eaf0] rounded-full transition-all duration-300" :class="sidebarOpen ? 'rotate-45 translate-y-[7px]' : ''" />
          <span class="block h-[2px] bg-[#e8eaf0] rounded-full transition-all duration-300" :class="sidebarOpen ? 'opacity-0 w-5' : 'w-4'" />
          <span class="block h-[2px] w-5 bg-[#e8eaf0] rounded-full transition-all duration-300" :class="sidebarOpen ? '-rotate-45 -translate-y-[7px]' : ''" />
        </button>

        <!-- Breadcrumb -->
        <div class="flex items-center gap-2 text-[13px] min-w-0 flex-1">
          <span class="text-[#7c83a0] truncate hidden sm:block">{{ schoolName }}</span>
          <span class="text-[#7c83a0]/40 hidden sm:block">/</span>
          <span class="text-[#e8eaf0] font-medium truncate">{{ currentRouteLabel }}</span>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-1 flex-shrink-0">
          <!-- Notifications -->
          <button class="relative w-9 h-9 flex items-center justify-center rounded-xl hover:bg-white/[0.06] transition-colors text-[#7c83a0] hover:text-[#e8eaf0]">
            <span class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full transition-colors duration-300" :style="{ background: accentColor }" />
            <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
              <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 01-3.46 0" />
            </svg>
          </button>

          <!-- Profile dropdown -->
          <div id="profile-menu" class="relative">
            <button
              @click.stop="toggleProfileDropdown"
              class="flex items-center gap-2 px-2 py-1.5 rounded-xl hover:bg-white/[0.06] transition-colors cursor-pointer"
            >
              <!-- Avatar -->
              <div class="w-8 h-8 rounded-full overflow-hidden shrink-0 flex items-center justify-center text-[13px] font-bold text-[#0f1117]"
                :style="{ background: `linear-gradient(135deg, ${accentColor}, #6ee7b7)` }">
                <img
                  v-if="authStore.user?.profile_photo_url"
                  :src="authStore.user.profile_photo_url"
                  :alt="userName"
                  class="w-full h-full object-cover"
                />
                <span v-else>{{ userInitial }}</span>
              </div>
              <!-- Nom -->
              <span class="text-[13px] font-medium text-[#e8eaf0] hidden md:block max-w-[100px] truncate">
                {{ userName }}
              </span>
              <!-- Chevron -->
              <svg class="w-3.5 h-3.5 text-[#7c83a0] transition-transform duration-200 hidden md:block flex-shrink-0"
                :class="{ 'rotate-180': profileDropdown }"
                fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
              </svg>
            </button>

            <!-- Dropdown -->
            <Transition
              enter-active-class="transition duration-150 ease-out"
              enter-from-class="opacity-0 scale-95 -translate-y-1"
              enter-to-class="opacity-100 scale-100 translate-y-0"
              leave-active-class="transition duration-100 ease-in"
              leave-from-class="opacity-100 scale-100"
              leave-to-class="opacity-0 scale-95"
            >
              <div
                v-if="profileDropdown"
                class="absolute right-0 top-full mt-1.5 w-52 bg-[#1e2335] rounded-xl border border-white/[0.1] shadow-xl overflow-hidden z-50"
              >
                <!-- Entête -->
                <div class="px-4 py-3 border-b border-white/[0.07]">
                  <p class="text-[10px] text-[#7c83a0] uppercase tracking-wider font-semibold">Mon compte</p>
                  <p class="text-[13px] font-semibold text-[#e8eaf0] mt-0.5 truncate">{{ userName }}</p>
                  <p class="text-[11px] text-[#7c83a0] truncate">{{ userEmail }}</p>
                </div>
                <div class="py-1">
                  <RouterLink
                    to="/profile"
                    @click="closeProfileDropdown"
                    class="flex items-center gap-2.5 px-4 py-2.5 text-[13px] text-[#a0a8c0] hover:bg-white/[0.06] hover:text-[#e8eaf0] transition-colors"
                  >
                    <svg class="w-4 h-4 text-[#7c83a0]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Profil
                  </RouterLink>
                  <div class="h-px bg-white/[0.06] mx-3 my-1"></div>
                  <button
                    @click="logout"
                    class="w-full flex items-center gap-2.5 px-4 py-2.5 text-[13px] text-red-400 hover:bg-red-500/10 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Se déconnecter
                  </button>
                </div>
              </div>
            </Transition>
          </div>

          <!-- Collapse toggle desktop only -->
          <button
            @click="toggleCollapse"
            class="hidden md:flex w-9 h-9 items-center justify-center rounded-xl hover:bg-white/[0.06] transition-colors text-[#7c83a0] hover:text-[#e8eaf0]"
          >
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path v-if="!sidebarCollapsed" d="M11 19l-7-7 7-7M19 19l-7-7 7-7" />
              <path v-else d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          </button>
        </div>

      </header>

      <!-- PAGE CONTENT -->
      <main class="flex-1 p-4 md:p-6 overflow-auto">
        <RouterView :key="route.fullPath" v-slot="{ Component, route: currentRoute }">
          <Transition name="fade" mode="out-in">
            <!--
              On enveloppe dans un <div> pour garantir un nœud racine unique.
              Vue <Transition> exige un seul élément racine animable.
              Les pages avec plusieurs racines (fragments) causaient le warning.
            -->
            <div :key="currentRoute?.fullPath">
              <component :is="Component" />
            </div>
          </Transition>
        </RouterView>
      </main>

      <!-- FOOTER -->
      <footer class="border-t border-white/[0.07] px-6 py-3 flex items-center justify-center text-[11px] text-[#7c83a0] flex-shrink-0">
        <span>{{ schoolName }} &copy; {{ new Date().getFullYear() }}</span>
      </footer>

    </div>

  </div>

  <!-- ── Modal inactivité ─────────────────────────────────────────────────── -->
  <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0"
              leave-active-class="transition duration-150" leave-to-class="opacity-0">
    <div v-if="showWarning" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div class="bg-[#0f1117] border border-amber-500/30 rounded-2xl w-full max-w-sm shadow-2xl p-6 text-center">
        <!-- Icône -->
        <div class="w-14 h-14 rounded-full bg-amber-500/15 flex items-center justify-center mx-auto mb-4">
          <svg class="w-7 h-7 text-amber-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/>
          </svg>
        </div>

        <h2 class="text-[16px] font-semibold text-[#e8eaf0] mb-2">Session inactive</h2>
        <p class="text-[13px] text-[#7c83a0] mb-5 leading-relaxed">
          Vous serez déconnecté dans
          <span class="font-mono text-amber-400 font-bold text-[15px]"> {{ secondsLeft }} </span>
          seconde{{ secondsLeft !== 1 ? 's' : '' }} en raison d'inactivité.
        </p>

        <!-- Barre de progression -->
        <div class="w-full h-1 bg-white/[0.07] rounded-full overflow-hidden mb-5">
          <div class="h-full bg-amber-400 rounded-full transition-all duration-1000"
               :style="{ width: (secondsLeft / 60 * 100) + '%' }"></div>
        </div>

        <div class="flex gap-3">
          <button @click="logout"
            class="flex-1 px-4 py-2.5 rounded-xl text-[13px] font-medium text-red-400 bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 transition-colors">
            Se déconnecter
          </button>
          <button @click="stayConnected"
            class="flex-1 px-4 py-2.5 rounded-xl text-[13px] font-medium text-white hover:opacity-90 transition-opacity"
            :style="{ background: 'var(--accent)' }">
            Rester connecté
          </button>
        </div>
      </div>
    </div>
  </Transition>

</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
</style>
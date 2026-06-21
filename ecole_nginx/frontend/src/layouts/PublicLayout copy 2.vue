<template>
  <div class="min-h-screen bg-[#faf8f3] font-body">

    <!-- ══════════ NAVBAR ══════════ -->
    <nav v-if="!hideNav"
      class="fixed top-0 left-0 right-0 z-50 transition-all duration-500"
      :class="[
        scrolled
          ? 'bg-[#0d0d14]/96 backdrop-blur-md shadow-2xl shadow-black/20 h-16'
          : 'bg-transparent h-20',
      ]"
    >
      <div class="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">

        <!-- LOGO -->
        <router-link to="/" class="flex items-center gap-3 cursor-pointer group">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-[#c9a84c] to-[#8a6520] flex items-center justify-center text-lg transition-transform group-hover:scale-110">
            🎓
          </div>
          <span class="font-serif text-white text-xl font-bold tracking-wide">
            Aplekol <span class="text-[#c9a84c]">360</span>
          </span>
        </router-link>

        <!-- DESKTOP NAV -->
        <div class="hidden md:flex items-center gap-1">
          <router-link
            v-for="link in navLinks" :key="link.label"
            :to="link.to"
            class="relative px-4 py-2 text-sm font-medium text-white/60 hover:text-white transition-colors rounded-lg hover:bg-white/5 cursor-pointer group"
            active-class="text-white"
          >
            {{ link.label }}
            <!-- Active underline -->
            <span class="absolute bottom-1 left-4 right-4 h-px bg-[#c9a84c] scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></span>
          </router-link>
        </div>

        <!-- DESKTOP CTA -->
        <div class="hidden md:flex items-center gap-3">
          <router-link to="/login"
            class="text-sm font-semibold text-white/60 hover:text-white px-4 py-2 transition-colors cursor-pointer rounded-lg hover:bg-white/5">
            Connexion
          </router-link>
          <router-link to="/login"
            class="text-sm font-bold bg-[#c9a84c] text-[#0d0d14] px-5 py-2.5 rounded-xl hover:bg-[#dbb85a] transition-all hover:scale-105 cursor-pointer shadow-lg shadow-[#c9a84c]/20">
            Commencer →
          </router-link>
        </div>

        <!-- MOBILE HAMBURGER -->
        <button
          @click="mobileOpen = !mobileOpen"
          class="md:hidden flex flex-col justify-center items-center w-10 h-10 gap-1.5 rounded-xl hover:bg-white/10 transition-all cursor-pointer"
          aria-label="Menu">
          <span class="w-5 h-0.5 bg-white transition-all duration-300"
            :class="mobileOpen ? 'rotate-45 translate-y-2' : ''"></span>
          <span class="w-5 h-0.5 bg-white transition-all duration-300"
            :class="mobileOpen ? 'opacity-0 scale-x-0' : ''"></span>
          <span class="w-5 h-0.5 bg-white transition-all duration-300"
            :class="mobileOpen ? '-rotate-45 -translate-y-2' : ''"></span>
        </button>
      </div>

      <!-- MOBILE MENU -->
      <Transition name="mobile-menu">
        <div v-if="mobileOpen"
          class="md:hidden bg-[#0d0d14]/98 backdrop-blur-md border-t border-white/5">
          <div class="max-w-7xl mx-auto px-6 py-4 space-y-1">
            <router-link
              v-for="link in navLinks" :key="link.label"
              :to="link.to"
              @click="mobileOpen = false"
              class="flex items-center gap-3 px-4 py-3 rounded-xl text-white/60 hover:text-white hover:bg-white/5 transition-all cursor-pointer text-sm font-medium">
              <span>{{ link.icon }}</span> {{ link.label }}
            </router-link>
            <div class="pt-3 mt-3 border-t border-white/5 flex flex-col gap-2">
              <router-link to="/login" @click="mobileOpen = false"
                class="px-4 py-3 rounded-xl text-center text-white/60 hover:text-white border border-white/10 hover:border-white/20 text-sm font-semibold transition-all cursor-pointer">
                Se connecter
              </router-link>
              <router-link to="/login" @click="mobileOpen = false"
                class="px-4 py-3 rounded-xl text-center bg-[#c9a84c] text-[#0d0d14] text-sm font-bold hover:bg-[#dbb85a] transition-all cursor-pointer">
                Commencer →
              </router-link>
            </div>
          </div>
        </div>
      </Transition>
    </nav>

    <!-- PAGE CONTENT -->
    <main>
      <router-view />
    </main>

    <!-- ══════════ FOOTER ══════════ -->
    <footer v-if="!hideNav" class="bg-[#0d0d14] relative overflow-hidden">
      <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#c9a84c]/30 to-transparent"></div>
      <div class="absolute -top-32 right-0 w-96 h-96 rounded-full blur-3xl opacity-5 bg-[#c9a84c]"></div>

      <div class="max-w-7xl mx-auto px-6 pt-16 pb-8 relative z-10">

        <!-- Top footer -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">

          <!-- Brand -->
          <div class="md:col-span-2">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-[#c9a84c] to-[#8a6520] flex items-center justify-center text-lg">🎓</div>
              <span class="font-serif text-white text-xl font-bold">Aplekol <span class="text-[#c9a84c]">360</span></span>
            </div>
            <p class="text-white/30 text-sm leading-relaxed max-w-xs">
              La plateforme de gestion scolaire moderne conçue pour les établissements haïtiens.
            </p>
            <div class="flex gap-3 mt-5">
              <a v-for="social in socials" :key="social.label" href="#"
                class="w-9 h-9 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white/40 hover:text-white hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer text-sm">
                {{ social.icon }}
              </a>
            </div>
          </div>

          <!-- Links col 1 -->
          <div>
            <h4 class="text-white text-xs font-bold tracking-widest uppercase mb-4">Navigation</h4>
            <ul class="space-y-2.5">
              <li v-for="link in footerNav" :key="link.label">
                <router-link :to="link.to"
                  class="text-white/30 hover:text-white/70 text-sm transition-colors cursor-pointer">
                  {{ link.label }}
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Links col 2 -->
          <div>
            <h4 class="text-white text-xs font-bold tracking-widest uppercase mb-4">Contact</h4>
            <ul class="space-y-2.5">
              <li v-for="info in contactInfo" :key="info.label"
                class="flex items-start gap-2.5 text-sm text-white/30">
                <span class="text-[#c9a84c] shrink-0 mt-0.5">{{ info.icon }}</span>
                <span>{{ info.value }}</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Bottom footer -->
        <div class="pt-6 border-t border-white/5 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p class="text-white/20 text-xs">© {{ new Date().getFullYear() }} Aplekol 360 · Tous droits réservés · Haïti</p>
          <div class="flex gap-5">
            <a v-for="l in legalLinks" :key="l" href="#"
              class="text-white/20 hover:text-white/50 text-xs transition-colors cursor-pointer">
              {{ l }}
            </a>
          </div>
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router';
 
const scrolled    = ref(false)
const mobileOpen  = ref(false)

const route   = useRoute()
// const hideNav = computed(() => route.meta?.hideNav)
// ✅ Avec fallback explicite
const hideNav = computed(() => route.meta?.hideNav ?? false)

function handleScroll() {
  scrolled.value   = window.scrollY > 40
  if (mobileOpen.value && window.scrollY > 100) mobileOpen.value = false
}

onMounted(() => window.addEventListener('scroll', handleScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', handleScroll))

const navLinks = [
  { label: 'Accueil',       to: '/',          icon: '🏠' },
  { label: 'À propos',      to: '/a-propos',  icon: '🏫' },
  { label: 'Fonctionnalités', to: '/#features', icon: '⚡' },
  { label: 'Contact',       to: '/contact',   icon: '✉️' },
]

const footerNav = [
  { label: 'Accueil',         to: '/'           },
  { label: 'À propos',        to: '/a-propos'   },
  { label: 'Fonctionnalités', to: '/#features'  },
  { label: 'Contact',         to: '/contact'    },
]

const contactInfo = [
  { icon: '📍', label: 'Adresse', value: 'Port-au-Prince, Haïti' },
  { icon: '📞', label: 'Téléphone', value: '+509 XXXX XXXX' },
  { icon: '✉️', label: 'Email', value: 'contact@aplekol360.ht' },
]

const socials = [
  { label: 'Facebook',  icon: 'f' },
  { label: 'WhatsApp',  icon: '💬' },
  { label: 'Instagram', icon: '📸' },
]
console.log(hideNav.value);

const legalLinks = ['Conditions d\'utilisation', 'Confidentialité', 'Support']
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

.font-serif { font-family: 'Playfair Display', serif !important; }
.font-body, * { font-family: 'DM Sans', sans-serif; }

.mobile-menu-enter-active,
.mobile-menu-leave-active { transition: all 0.3s ease; }
.mobile-menu-enter-from,
.mobile-menu-leave-to { opacity: 0; transform: translateY(-8px); }
</style>

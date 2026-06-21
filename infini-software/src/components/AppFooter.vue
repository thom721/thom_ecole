<template>
  <footer class="bg-[#080c10] border-t border-[#1e2a38] pt-16 pb-8">
    <div class="max-w-7xl mx-auto px-6">
      <div class="grid md:grid-cols-4 gap-10 mb-12">

        <!-- Brand -->
        <div class="md:col-span-2">
          <router-link to="/" class="flex items-center gap-2.5 mb-4 w-fit">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-[#06b6d4] to-[#0891b2] flex items-center justify-center">
              <svg class="w-4 h-4 text-[#080c10]" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm8 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V4zM3 12a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H4a1 1 0 01-1-1v-4zm8 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/>
              </svg>
            </div>
            <span class="font-syne font-extrabold text-[.95rem]">Infini<span class="text-[#06b6d4]">Software</span></span>
          </router-link>
          <p class="text-sm text-[#64748b] leading-relaxed max-w-xs mb-5">
            Solutions logicielles sur mesure pour les entreprises qui veulent aller plus loin.
          </p>
          <div class="flex gap-3">
            <a v-for="s in socials" :key="s.name" :href="s.url" :aria-label="s.name"
              class="w-8 h-8 rounded-lg bg-[#111820] border border-[#1e2a38] flex items-center justify-center text-[#64748b] hover:text-[#06b6d4] hover:border-[#06b6d4]/30 transition-colors">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                <path :d="s.path"/>
              </svg>
            </a>
          </div>
        </div>

        <!-- Nav links -->
        <div>
          <div class="text-xs font-bold uppercase tracking-widest text-[#374151] mb-4">Navigation</div>
          <div class="space-y-3">
            <div v-for="item in navItems" :key="item.to">
              <router-link :to="item.to"
                class="text-sm text-[#64748b] hover:text-[#06b6d4] transition-colors">
                {{ item.label }}
              </router-link>
            </div>
          </div>
        </div>

        <!-- Legal -->
        <div>
          <div class="text-xs font-bold uppercase tracking-widest text-[#374151] mb-4">Légal</div>
          <div class="space-y-3">
            <div>
              <router-link to="/privacy"
                class="text-sm text-[#64748b] hover:text-[#06b6d4] transition-colors">
                Politique de confidentialité
              </router-link>
            </div>
            <div>
              <router-link to="/terms"
                class="text-sm text-[#64748b] hover:text-[#06b6d4] transition-colors">
                Conditions générales
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Gradient line -->
      <div class="h-px mb-6" style="background:linear-gradient(90deg,transparent,#06b6d4,#f59e0b,transparent)"></div>

      <div class="flex flex-col md:flex-row justify-between items-center gap-3 text-xs text-[#374151]">
        <span>© {{ year }} Infini Software. Tous droits réservés.</span>
        <span class="font-mono">Built with ❤ by Infini Software</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
const navItems = [
  { to: '/',        label: 'Accueil' },
  { to: '/store',   label: 'Store' },
  { to: '/about',   label: 'À propos' },
  { to: '/contact', label: 'Contact' },
]
const socials = [
  { name: 'LinkedIn', url: '#', path: 'M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z' },
  { name: 'X',        url: '#', path: 'M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z' },
  { name: 'GitHub',   url: '#', path: 'M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12' },
  { name: 'Facebook', url: '#', path: 'M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z' },
]
</script>

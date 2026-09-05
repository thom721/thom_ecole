<template>
  <div class="min-h-screen bg-[#faf8f3] font-body overflow-x-hidden">

    <!-- ══════════ NAVBAR ══════════ -->
    <nav class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      :class="scrolled ? 'bg-[#0d0d14]/95 backdrop-blur-md shadow-xl' : 'bg-transparent'">
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-[#c9a84c] to-[#8a6520] flex items-center justify-center text-lg">🎓</div>
          <span class="font-serif text-white text-xl font-bold tracking-wide">Aplekol <span class="text-[#c9a84c]">360</span></span>
        </div>
        <div class="hidden md:flex items-center gap-8">
          <a v-for="link in navLinks" :key="link.label" :href="link.href"
            class="text-sm font-medium text-white/60 hover:text-white transition-colors cursor-pointer">
            {{ link.label }}
          </a>
        </div>
        <div class="flex items-center gap-3">
          <router-link to="/login"
            class="text-sm font-semibold text-white/70 hover:text-white transition-colors px-4 py-2 cursor-pointer">
            Connexion
          </router-link>
          <router-link to="/login"
            class="text-sm font-semibold bg-[#c9a84c] text-[#0d0d14] px-4 py-2 rounded-lg hover:bg-[#dbb85a] transition-all cursor-pointer">
            Commencer →
          </router-link>
        </div>
      </div>
    </nav>

    <!-- ══════════ HERO ══════════ -->
    <section class="relative min-h-screen bg-[#0d0d14] flex items-center overflow-hidden">

      <!-- Animated gradient background -->
      <div class="absolute inset-0">
        <div class="absolute top-0 left-0 w-full h-full"
          style="background: radial-gradient(ellipse 80% 60% at 20% 40%, rgba(26,58,107,0.6) 0%, transparent 60%),
                             radial-gradient(ellipse 60% 50% at 80% 20%, rgba(201,168,76,0.15) 0%, transparent 50%),
                             radial-gradient(ellipse 50% 40% at 60% 80%, rgba(26,122,74,0.1) 0%, transparent 50%);">
        </div>
        <!-- Grid pattern -->
        <div class="absolute inset-0 opacity-[0.04]"
          style="background-image: linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px);
                 background-size: 60px 60px;">
        </div>
      </div>

      <!-- Floating orbs -->
      <div class="absolute top-1/4 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-10 bg-[#c9a84c] animate-pulse"></div>
      <div class="absolute bottom-1/3 left-1/3 w-64 h-64 rounded-full blur-3xl opacity-10 bg-[#3b82f6]"
        style="animation: pulse 4s ease-in-out infinite 1s;"></div>

      <div class="relative z-10 max-w-7xl mx-auto px-6 pt-24 pb-16 grid lg:grid-cols-2 gap-16 items-center">

        <!-- Left content -->
        <div>
          <div class="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-1.5 mb-8">
            <span class="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></span>
            <span class="text-white/60 text-xs font-medium tracking-wide">Plateforme scolaire nouvelle génération</span>
          </div>

          <h1 class="font-serif text-6xl lg:text-7xl font-black text-white leading-[1.05] mb-6">
            L'école
            <span class="block text-transparent" style="background: linear-gradient(135deg, #c9a84c, #e8d5a3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
              réinventée.
            </span>
          </h1>

          <p class="text-white/50 text-lg leading-relaxed mb-10 max-w-lg">
            Aplekol 360 centralise la gestion scolaire — notes, paiements, cours, présences — dans une plateforme moderne, accessible à tous.
          </p>

          <div class="flex flex-wrap gap-4">
            <router-link to="/login"
              class="inline-flex items-center gap-2 bg-[#c9a84c] text-[#0d0d14] font-bold px-7 py-3.5 rounded-xl hover:bg-[#dbb85a] transition-all hover:scale-105 cursor-pointer text-sm shadow-xl shadow-[#c9a84c]/20">
              Accéder à la plateforme →
            </router-link>
            <a href="#features"
              class="inline-flex items-center gap-2 bg-white/5 border border-white/10 text-white/70 font-semibold px-7 py-3.5 rounded-xl hover:bg-white/10 transition-all cursor-pointer text-sm">
              Découvrir ↓
            </a>
          </div>

          <!-- Stats -->
          <div class="flex gap-8 mt-12 pt-8 border-t border-white/10">
            <div v-for="stat in heroStats" :key="stat.label">
              <div class="font-serif text-3xl font-bold text-white">{{ stat.value }}</div>
              <div class="text-white/40 text-xs mt-0.5">{{ stat.label }}</div>
            </div>
          </div>
        </div>

        <!-- Right — Dashboard mockup -->
        <div class="relative hidden lg:block">
          <!-- Glow -->
          <div class="absolute inset-0 bg-[#c9a84c]/10 rounded-3xl blur-3xl scale-110"></div>

          <!-- Card mockup -->
          <div class="relative bg-[#111] rounded-2xl border border-white/10 overflow-hidden shadow-2xl">
            <!-- Fake topbar -->
            <div class="bg-[#0d0d14] px-5 py-3 flex items-center justify-between border-b border-white/5">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full bg-[#e74c3c]"></div>
                <div class="w-3 h-3 rounded-full bg-[#c9a84c]"></div>
                <div class="w-3 h-3 rounded-full bg-[#10b981]"></div>
              </div>
              <div class="text-white/20 text-xs">aplekol360.ht</div>
            </div>

            <!-- Content mockup -->
            <div class="p-6 space-y-4">
              <!-- Header row -->
              <div class="flex items-center justify-between mb-2">
                <div>
                  <div class="h-3 w-32 bg-white/10 rounded mb-1.5"></div>
                  <div class="h-2 w-20 bg-white/5 rounded"></div>
                </div>
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#c9a84c] to-[#8a6520] flex items-center justify-center text-sm font-bold text-white">JD</div>
              </div>

              <!-- Stats row -->
              <div class="grid grid-cols-3 gap-3">
                <div v-for="(s, i) in mockStats" :key="i"
                  class="bg-white/5 rounded-xl p-3 border border-white/5">
                  <div class="text-[0.6rem] text-white/30 uppercase tracking-wide mb-1.5">{{ s.label }}</div>
                  <div class="font-serif text-xl font-bold" :style="{ color: s.color }">{{ s.val }}</div>
                </div>
              </div>

              <!-- Table mockup -->
              <div class="bg-white/5 rounded-xl overflow-hidden border border-white/5">
                <div class="bg-[#0d0d14] px-4 py-2.5 grid grid-cols-4 gap-4">
                  <div v-for="h in ['Matière','Coef.','Note','Statut']" :key="h"
                    class="h-2 bg-white/10 rounded text-[0] text-xs">{{ h }}</div>
                </div>
                <div v-for="(row, i) in mockRows" :key="i"
                  class="px-4 py-3 grid grid-cols-4 gap-4 border-t border-white/5">
                  <div class="h-2 rounded" :style="{ background: row.color + '40', width: row.w }"></div>
                  <div class="h-2 w-4 bg-white/10 rounded"></div>
                  <div class="h-2 w-8 rounded" :style="{ background: row.color }"></div>
                  <div class="h-2 w-12 rounded" :style="{ background: row.color + '30' }"></div>
                </div>
              </div>

              <!-- Progress bar -->
              <div class="bg-white/5 rounded-xl p-4 border border-white/5">
                <div class="flex justify-between items-center mb-2">
                  <div class="h-2 w-24 bg-white/10 rounded"></div>
                  <div class="h-2 w-8 bg-[#c9a84c]/50 rounded"></div>
                </div>
                <div class="bg-white/10 rounded-full h-2 overflow-hidden">
                  <div class="h-full rounded-full bg-gradient-to-r from-[#c9a84c] to-[#10b981]" style="width: 73%"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Floating badge -->
          <div class="absolute -bottom-4 -left-4 bg-[#10b981] text-white text-xs font-bold px-4 py-2 rounded-xl shadow-lg shadow-[#10b981]/30 flex items-center gap-2">
            <span>✓</span> Paiement validé
          </div>
          <div class="absolute -top-4 -right-4 bg-[#c9a84c] text-[#0d0d14] text-xs font-bold px-4 py-2 rounded-xl shadow-lg flex items-center gap-2">
            🏅 Major de classe
          </div>
        </div>
      </div>

      <!-- Wave separator -->
      <div class="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 80L48 68C96 56 192 32 288 24C384 16 480 24 576 36C672 48 768 64 864 64C960 64 1056 48 1152 40C1248 32 1344 32 1392 32L1440 32V80H0Z" fill="#faf8f3"/>
        </svg>
      </div>
    </section>

    <!-- ══════════ ROLES ══════════ -->
    <section class="py-20 bg-[#faf8f3]">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-14">
          <div class="inline-block bg-[#0d0d14] text-[#c9a84c] text-xs font-bold px-4 py-1.5 rounded-full mb-4 tracking-widest uppercase">Pour tout le monde</div>
          <h2 class="font-serif text-5xl font-bold text-[#0d0d14] mb-4">Un espace pour chacun</h2>
          <p class="text-[#888] text-lg max-w-xl mx-auto">Chaque acteur de l'école dispose d'une interface taillée sur mesure.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="role in roles" :key="role.title"
            class="group relative rounded-2xl overflow-hidden cursor-pointer hover:-translate-y-2 transition-all duration-300"
            :style="{ background: role.bg }">
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
              :style="{ background: role.hover }"></div>
            <div class="relative p-8">
              <div class="text-5xl mb-5">{{ role.emoji }}</div>
              <h3 class="font-serif text-2xl font-bold text-white mb-3">{{ role.title }}</h3>
              <p class="text-white/60 text-sm leading-relaxed mb-6">{{ role.desc }}</p>
              <ul class="space-y-2 mb-8">
                <li v-for="feat in role.features" :key="feat"
                  class="flex items-center gap-2.5 text-white/70 text-sm">
                  <span class="text-[#c9a84c] text-xs">✦</span> {{ feat }}
                </li>
              </ul>
              <div class="inline-flex items-center gap-2 text-[#c9a84c] text-sm font-bold group-hover:gap-3 transition-all">
                Accéder <span>→</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ FEATURES ══════════ -->
    <section id="features" class="py-24 bg-[#0d0d14] relative overflow-hidden">
      <div class="absolute inset-0 opacity-[0.03]"
        style="background-image: linear-gradient(rgba(255,255,255,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.8) 1px, transparent 1px); background-size: 40px 40px;"></div>
      <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#c9a84c]/30 to-transparent"></div>

      <div class="max-w-7xl mx-auto px-6 relative z-10">
        <div class="text-center mb-16">
          <div class="inline-block bg-[#c9a84c]/10 border border-[#c9a84c]/20 text-[#c9a84c] text-xs font-bold px-4 py-1.5 rounded-full mb-4 tracking-widest uppercase">Fonctionnalités</div>
          <h2 class="font-serif text-5xl font-bold text-white mb-4">Tout ce dont votre école a besoin</h2>
          <p class="text-white/40 text-lg max-w-xl mx-auto">Une suite complète d'outils pour moderniser la gestion scolaire.</p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          <div v-for="(feat, i) in features" :key="feat.title"
            class="group bg-white/[0.03] border border-white/[0.07] rounded-2xl p-6 hover:bg-white/[0.06] hover:border-white/10 transition-all duration-300 hover:-translate-y-1"
            :class="i === 0 ? 'md:col-span-2 lg:col-span-1' : ''">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-5"
              :style="{ background: feat.color + '15' }">
              {{ feat.emoji }}
            </div>
            <h3 class="font-serif text-xl font-bold text-white mb-2">{{ feat.title }}</h3>
            <p class="text-white/40 text-sm leading-relaxed">{{ feat.desc }}</p>
            <div class="mt-5 pt-5 border-t border-white/5 flex flex-wrap gap-2">
              <span v-for="tag in feat.tags" :key="tag"
                class="text-[0.65rem] font-semibold px-2.5 py-1 rounded-full"
                :style="{ background: feat.color + '15', color: feat.color }">
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ HOW IT WORKS ══════════ -->
    <section class="py-24 bg-[#faf8f3]">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-16">
          <div class="inline-block bg-[#0d0d14] text-[#c9a84c] text-xs font-bold px-4 py-1.5 rounded-full mb-4 tracking-widest uppercase">Simple & Rapide</div>
          <h2 class="font-serif text-5xl font-bold text-[#0d0d14] mb-4">Comment ça fonctionne ?</h2>
        </div>

        <div class="relative">
          <!-- Line -->
          <div class="absolute left-1/2 top-8 bottom-8 w-px bg-gradient-to-b from-[#c9a84c] to-transparent hidden md:block"></div>

          <div class="space-y-12">
            <div v-for="(step, i) in howItWorks" :key="step.title"
              class="grid md:grid-cols-2 gap-8 items-center"
              :class="i % 2 === 1 ? 'md:grid-flow-dense' : ''">

              <!-- Text -->
              <div :class="i % 2 === 1 ? 'md:col-start-2' : ''">
                <div class="flex items-center gap-4 mb-4">
                  <div class="w-10 h-10 rounded-full flex items-center justify-center font-serif font-bold text-lg"
                    :style="{ background: step.color, color: '#0d0d14' }">
                    {{ i + 1 }}
                  </div>
                  <span class="text-xs font-semibold text-[#aaa] tracking-widest uppercase">Étape {{ i + 1 }}</span>
                </div>
                <h3 class="font-serif text-2xl font-bold text-[#0d0d14] mb-3">{{ step.title }}</h3>
                <p class="text-[#888] leading-relaxed">{{ step.desc }}</p>
              </div>

              <!-- Visual card -->
              <div :class="i % 2 === 1 ? 'md:col-start-1 md:row-start-1' : ''">
                <div class="rounded-2xl p-6 border"
                  :style="{ background: step.color + '08', borderColor: step.color + '20' }">
                  <div class="text-5xl mb-3">{{ step.emoji }}</div>
                  <div class="h-2 rounded-full mb-2" :style="{ background: step.color + '30', width: '80%' }"></div>
                  <div class="h-2 rounded-full mb-2" :style="{ background: step.color + '20', width: '60%' }"></div>
                  <div class="h-2 rounded-full" :style="{ background: step.color + '15', width: '70%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ TESTIMONIALS ══════════ -->
    <section class="py-24 bg-[#0d0d14] relative overflow-hidden">
      <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#c9a84c]/20 to-transparent"></div>
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-14">
          <h2 class="font-serif text-5xl font-bold text-white mb-4">Ce qu'ils disent</h2>
          <p class="text-white/40">Des établissements qui font confiance à Aplekol 360</p>
        </div>
        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="t in testimonials" :key="t.name"
            class="bg-white/[0.04] border border-white/[0.07] rounded-2xl p-6 hover:border-[#c9a84c]/20 transition-all">
            <div class="flex gap-1 mb-4">
              <span v-for="n in 5" :key="n" class="text-[#c9a84c] text-sm">★</span>
            </div>
            <p class="text-white/60 text-sm leading-relaxed mb-5 italic">"{{ t.text }}"</p>
            <div class="flex items-center gap-3 pt-4 border-t border-white/5">
              <div class="w-9 h-9 rounded-full flex items-center justify-center font-serif font-bold text-sm"
                :style="{ background: t.color, color: '#0d0d14' }">
                {{ t.initials }}
              </div>
              <div>
                <div class="text-white text-sm font-semibold">{{ t.name }}</div>
                <div class="text-white/30 text-xs">{{ t.role }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ CTA ══════════ -->
    <section class="py-24 bg-[#faf8f3]">
      <div class="max-w-4xl mx-auto px-6 text-center">
        <div class="bg-[#0d0d14] rounded-3xl p-14 relative overflow-hidden">
          <div class="absolute -top-20 -right-20 w-64 h-64 rounded-full blur-3xl opacity-20 bg-[#c9a84c]"></div>
          <div class="absolute -bottom-20 -left-20 w-64 h-64 rounded-full blur-3xl opacity-10 bg-[#3b82f6]"></div>
          <div class="relative z-10">
            <div class="text-5xl mb-6">🚀</div>
            <h2 class="font-serif text-4xl font-bold text-white mb-4">Prêt à moderniser votre école ?</h2>
            <p class="text-white/50 mb-8 max-w-lg mx-auto">Rejoignez les établissements qui font confiance à Aplekol 360 pour une gestion scolaire efficace et moderne.</p>
            <div class="flex flex-wrap gap-4 justify-center">
              <router-link to="/login"
                class="inline-flex items-center gap-2 bg-[#c9a84c] text-[#0d0d14] font-bold px-8 py-4 rounded-xl hover:bg-[#dbb85a] transition-all hover:scale-105 cursor-pointer shadow-xl shadow-[#c9a84c]/20">
                Accéder à la plateforme →
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ FOOTER ══════════ -->
    <footer class="bg-[#0d0d14] border-t border-white/5 py-12">
      <div class="max-w-7xl mx-auto px-6">
        <div class="flex flex-col md:flex-row justify-between items-center gap-6">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-[#c9a84c] to-[#8a6520] flex items-center justify-center text-sm">🎓</div>
            <span class="font-serif text-white font-bold">Aplekol <span class="text-[#c9a84c]">360</span></span>
          </div>
          <p class="text-white/20 text-xs">© {{ new Date().getFullYear() }} Aplekol 360 · Tous droits réservés · Haïti</p>
          <div class="flex gap-6">
            <a v-for="l in footerLinks" :key="l" href="#"
              class="text-white/30 hover:text-white/60 text-xs transition-colors cursor-pointer">{{ l }}</a>
          </div>
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router  = useRouter()
const scrolled = ref(false)

function handleScroll() { scrolled.value = window.scrollY > 30 }
onMounted(() => window.addEventListener('scroll', handleScroll))
onUnmounted(() => window.removeEventListener('scroll', handleScroll))

const navLinks = [
  { label: 'Fonctionnalités', href: '#features' },
  { label: 'Espaces',         href: '#roles' },
  { label: 'Contact',         href: '#contact' },
]

const heroStats = [
  { value: '500+', label: 'Élèves gérés' },
  { value: '30+',  label: 'Enseignants' },
  { value: '99%',  label: 'Disponibilité' },
]

const mockStats = [
  { label: 'Moyenne', val: '15.4', color: '#c9a84c' },
  { label: 'Rang',    val: '2e',   color: '#3b82f6' },
  { label: 'Payé',    val: '73%',  color: '#10b981' },
]

const mockRows = [
  { color: '#8b5cf6', w: '70%' },
  { color: '#3b82f6', w: '85%' },
  { color: '#ef4444', w: '55%' },
  { color: '#10b981', w: '90%' },
]

const roles = [
  {
    emoji: '🎒',
    title: 'Espace Étudiant',
    desc: 'Suivez vos notes, consultez vos bulletins, vérifiez vos paiements et accédez à vos cours en un clic.',
    bg: 'linear-gradient(135deg, #1a3a6b 0%, #0d0d14 100%)',
    hover: 'linear-gradient(135deg, #1a4a8b 0%, #1a1a2e 100%)',
    features: ['Notes & bulletins', 'Suivi des paiements', 'Emploi du temps', 'Ressources pédagogiques'],
  },
  {
    emoji: '👨‍🏫',
    title: 'Espace Professeur',
    desc: 'Gérez vos classes, saisissez les notes, suivez les présences et communiquez avec les familles.',
    bg: 'linear-gradient(135deg, #1a4a2e 0%, #0d0d14 100%)',
    hover: 'linear-gradient(135deg, #1a5a3e 0%, #1a1a2e 100%)',
    features: ['Saisie des notes', 'Gestion des présences', 'Programme de cours', 'Statistiques classe'],
  },
  {
    emoji: '🏫',
    title: 'Administration',
    desc: 'Pilotez l\'établissement, gérez les inscriptions, les paiements et générez les rapports officiels.',
    bg: 'linear-gradient(135deg, #4a1a2e 0%, #0d0d14 100%)',
    hover: 'linear-gradient(135deg, #5a2a3e 0%, #1a1a2e 100%)',
    features: ['Gestion des inscriptions', 'Suivi financier', 'Rapports & statistiques', 'Gestion des utilisateurs'],
  },
]

const features = [
  { emoji: '📊', title: 'Bulletins de notes', desc: 'Générez automatiquement des bulletins détaillés par mois ou par année, avec mention et appréciation.', color: '#c9a84c', tags: ['PDF', 'Impression', 'Historique'] },
  { emoji: '💳', title: 'Gestion des paiements', desc: 'Suivez en temps réel les versements, échéances et soldes de chaque élève. Générez les reçus instantanément.', color: '#10b981', tags: ['Versements', 'Reçus', 'Bilan annuel'] },
  { emoji: '📚', title: 'Programme de cours', desc: 'Consultez les matières, les professeurs, l\'emploi du temps et les ressources pédagogiques partagées.', color: '#3b82f6', tags: ['Matières', 'Emploi du temps', 'Ressources'] },
  { emoji: '📋', title: 'Présences & Absences', desc: 'Enregistrez et consultez les présences par cours. Suivez les absences justifiées et non justifiées.', color: '#8b5cf6', tags: ['Suivi', 'Justificatifs', 'Alertes'] },
  { emoji: '🖨', title: 'Impression & PDF', desc: 'Imprimez ou téléchargez n\'importe quel document en un clic — bulletins, reçus, attestations.', color: '#f97316', tags: ['Bulletins', 'Reçus', 'Attestations'] },
  { emoji: '🔐', title: 'Sécurité & Accès', desc: 'Chaque utilisateur dispose d\'un espace sécurisé et d\'accès limités selon son rôle dans l\'établissement.', color: '#e74c3c', tags: ['Rôles', 'Permissions', 'Tokens'] },
]

const howItWorks = [
  { emoji: '🏫', title: 'L\'école s\'inscrit',         desc: 'L\'établissement configure sa structure : niveaux, classes, année académique et utilisateurs.',             color: '#c9a84c' },
  { emoji: '👤', title: 'Les utilisateurs accèdent',   desc: 'Chaque acteur — élève, professeur, administration — reçoit ses identifiants et accède à son espace.',      color: '#3b82f6' },
  { emoji: '📈', title: 'Les données s\'organisent',   desc: 'Notes, paiements, cours et présences sont centralisés et accessibles en temps réel depuis n\'importe où.', color: '#10b981' },
  { emoji: '📄', title: 'Les documents sont générés',  desc: 'Bulletins, reçus de paiement et rapports sont générés automatiquement et imprimables à la demande.',       color: '#8b5cf6' },
]

const testimonials = [
  { name: 'Marie-Carole J.', role: 'Directrice — École Sainte-Anne', initials: 'MC', color: '#c9a84c', text: 'Aplekol 360 a transformé notre gestion administrative. Les parents reçoivent les informations en temps réel et notre équipe gagne un temps précieux.' },
  { name: 'Jean-Baptiste P.', role: 'Professeur de Mathématiques', initials: 'JP', color: '#10b981', text: 'La saisie des notes est devenue intuitive. Je peux voir la progression de mes élèves et partager mes ressources facilement.' },
  { name: 'Sandra M.', role: 'Parent d\'élève — CPB', initials: 'SM', color: '#3b82f6', text: 'Je consulte les notes et les paiements de mon enfant depuis mon téléphone. C\'est simple, clair et très rassurant.' },
]

const footerLinks = ['Conditions', 'Confidentialité', 'Contact', 'Support']
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

.font-serif { font-family: 'Playfair Display', serif !important; }
.font-body  { font-family: 'DM Sans', sans-serif; }
* { font-family: 'DM Sans', sans-serif; }

html { scroll-behavior: smooth; }
</style>
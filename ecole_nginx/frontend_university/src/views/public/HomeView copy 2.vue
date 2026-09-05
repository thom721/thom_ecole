<template>
  <div>
    <div class="relative overflow-hidden" style="height:100vh;min-height:580px">
      <img
        src="https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=1800&q=80"
        alt="Élèves en classe"
        class="w-full h-full object-cover block"
      />
      <div class="absolute inset-0" style="background:linear-gradient(135deg,rgba(11,37,69,.88) 0%,rgba(26,122,74,.55) 60%,rgba(232,160,32,.2) 100%)"></div>

      <div class="absolute inset-0 flex flex-col items-start justify-center px-12 md:px-20">
        <div class="flex items-center gap-2 mb-6 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest" style="background:rgba(232,160,32,.2);border:1px solid rgba(232,160,32,.5);color:#fde68a">
          <span class="w-1.5 h-1.5 rounded-full bg-yellow-400 animate-pulse"></span>
          Inscriptions ouvertes 2025–2026
        </div>

        <h1 class="font-serif text-white mb-5 leading-tight" style="font-size:clamp(2.4rem,5vw,4rem);max-width:700px">
          Bâtir des esprits,<br />
          <span style="color:#E8A020">former des leaders</span>
        </h1>

        <p class="mb-8 max-w-lg leading-relaxed" style="color:rgba(255,255,255,.78);font-size:clamp(.95rem,1.8vw,1.12rem)">
          À Institution Le Mignon, chaque enfant est accompagné avec bienveillance vers l'excellence.
          Un cadre sécurisé, des enseignants passionnés, une pédagogie moderne.
        </p>

        <div class="flex flex-wrap gap-3">
          <router-link
            to="/admission"
            class="inline-flex items-center gap-2 px-8 py-3.5 rounded-full font-bold text-white no-underline"
            style="background:#E8A020;box-shadow:0 4px 20px rgba(232,160,32,.4)"
          >
            Inscrire mon enfant
            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </router-link>
          <router-link
            to="/formations"
            class="inline-flex items-center gap-2 px-7 py-3 rounded-full font-semibold text-white no-underline"
            style="background:rgba(255,255,255,.15);border:1.5px solid rgba(255,255,255,.4);backdrop-filter:blur(8px)"
          >
            Découvrir les cycles
          </router-link>
        </div>
      </div>
    </div>

    <!-- ══ STATS ══════════════════════════════════════════ -->
    <div class="bg-white" style="box-shadow:0 4px 30px rgba(11,37,69,.1)">
      <div class="max-w-4xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4">
        <div v-for="(s, i) in STATS" :key="i" class="text-center py-8 reveal" :style="i < 3 ? 'border-right:1px solid #E2E8F0' : ''">
          <div class="font-black leading-none mb-1" style="font-size:2.4rem;background:linear-gradient(135deg,#0B2545,#1A7A4A);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{{ s.n }}</div>
          <div class="text-xs text-gray-400 uppercase tracking-widest">{{ s.l }}</div>
        </div>
      </div>
    </div>

    <!-- ══ PRÉSENTATION ══════════════════════════════════ -->
    <section class="py-24 bg-gray-50">
      <div class="max-w-5xl mx-auto px-6 grid md:grid-cols-2 gap-20 items-center">
        <div class="relative reveal">
          <img
            src="https://images.unsplash.com/photo-1571260899304-425eee4c7efc?w=800&q=80"
            alt="Salle de classe"
            class="w-full rounded-2xl block"
            style="box-shadow:20px 20px 60px rgba(11,37,69,.15)"
          />
          <div class="absolute -bottom-5 -right-5 text-white text-center rounded-2xl px-6 py-4" style="background:#E8A020;box-shadow:0 8px 30px rgba(232,160,32,.3)">
            <div class="text-3xl font-black leading-none">20+</div>
            <div class="text-xs opacity-90 mt-1">ans d'expérience</div>
          </div>
        </div>

        <div class="reveal">
          <p class="text-xs font-extrabold tracking-widest uppercase mb-3" style="color:#E8A020">Notre école</p>
          <h2 class="font-serif mb-5 leading-snug" style="font-size:clamp(1.8rem,3vw,2.6rem);color:#0B2545">
            Un environnement pensé<br /><span style="color:#1A7A4A">pour votre enfant</span>
          </h2>
          <p class="text-gray-500 leading-relaxed mb-4 text-sm">
            Fondée avec la mission d'offrir une éducation de qualité accessible, Institution Le Mignon
            accompagne les élèves du préscolaire au secondaire dans un cadre chaleureux et stimulant.
          </p>
          <p class="text-gray-500 leading-relaxed mb-6 text-sm">
            Notre approche combine rigueur académique, épanouissement personnel et valeurs humaines
            pour préparer les élèves aux défis de demain.
          </p>
          <div class="flex flex-wrap gap-2">
            <span v-for="v in VALUES" :key="v.t" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold bg-white border border-gray-200" style="color:#0B2545">
              {{ v.i }} {{ v.t }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ CYCLES SCOLAIRES ══════════════════════════════ -->
    <section class="py-24 bg-white">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-14 reveal">
          <p class="text-xs font-extrabold tracking-widest uppercase mb-2" style="color:#E8A020">Nos cycles</p>
          <h2 class="font-serif" style="font-size:clamp(1.8rem,3vw,2.6rem);color:#0B2545">
            De la maternelle au <span style="color:#1A7A4A">baccalauréat</span>
          </h2>
        </div>
        <div class="grid md:grid-cols-3 gap-7">
          <div
            v-for="(c, i) in CYCLES"
            :key="i"
            class="relative rounded-2xl p-8 border-2 border-gray-100 overflow-hidden reveal transition-transform hover:-translate-y-1"
          >
            <div class="absolute top-0 left-0 right-0 h-1 rounded-t-2xl" :style="{ background: c.color }"></div>
            <div class="text-4xl mb-2">{{ c.i }}</div>
            <div class="text-xs font-bold uppercase tracking-widest mb-2" :style="{ color: c.color }">{{ c.age }}</div>
            <h3 class="font-serif text-xl mb-2" style="color:#0B2545">{{ c.t }}</h3>
            <p class="text-gray-400 text-sm leading-relaxed mb-4">{{ c.d }}</p>
            <ul class="space-y-1 mb-5 list-none p-0">
              <li v-for="item in c.items" :key="item" class="text-sm text-gray-600 flex items-start gap-2">
                <span class="font-bold mt-0.5" :style="{ color: c.color }">✓</span> {{ item }}
              </li>
            </ul>
            <router-link to="/formations" class="text-sm font-bold no-underline" :style="{ color: c.color }">En savoir plus →</router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ ATOUTS ═════════════════════════════════════════ -->
    <section class="py-24 bg-gray-50">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-14 reveal">
          <p class="text-xs font-extrabold tracking-widest uppercase mb-2" style="color:#E8A020">Nos atouts</p>
          <h2 class="font-serif" style="font-size:clamp(1.8rem,3vw,2.6rem);color:#0B2545">
            Pourquoi choisir <span style="color:#1A7A4A">Le Mignon ?</span>
          </h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="(f, i) in FEATURES"
            :key="i"
            class="rounded-2xl p-6 border border-gray-100 reveal transition-transform hover:-translate-y-1"
            :class="f.featured ? '' : 'bg-white'"
            :style="f.featured ? 'background:linear-gradient(135deg,#0B2545,#1A7A4A)' : ''"
          >
            <div class="text-3xl mb-3">{{ f.i }}</div>
            <h3 class="font-serif text-lg mb-2" :class="f.featured ? 'text-white' : 'text-gray-800'">{{ f.t }}</h3>
            <p class="text-sm leading-relaxed" :class="f.featured ? 'text-white opacity-70' : 'text-gray-400'">{{ f.d }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ VIE SCOLAIRE ══════════════════════════════════ -->
    <section class="py-24" style="background:#0B2545">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-12 reveal">
          <p class="text-xs font-extrabold tracking-widest uppercase mb-2" style="color:#E8A020">Vie scolaire</p>
          <h2 class="font-serif text-white mb-2" style="font-size:clamp(1.8rem,3vw,2.6rem)">Au-delà des cours</h2>
          <p class="text-sm" style="color:rgba(255,255,255,.6)">Des activités parascolaires pour révéler tous les talents</p>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div
            v-for="(a, i) in ACTIVITIES"
            :key="i"
            class="relative rounded-2xl overflow-hidden reveal"
            :class="i === 0 ? 'col-span-2' : ''"
            style="aspect-ratio:3/4"
          >
            <img :src="a.img" :alt="a.t" class="w-full h-full object-cover transition-transform duration-500 hover:scale-105" />
            <div class="absolute bottom-0 left-0 right-0 p-4" style="background:linear-gradient(to top,rgba(11,37,69,.9),transparent)">
              <span class="block text-xs font-bold uppercase tracking-widest mb-1" style="color:#E8A020">{{ a.tag }}</span>
              <h3 class="text-white text-sm font-semibold m-0">{{ a.t }}</h3>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ TÉMOIGNAGES ═══════════════════════════════════ -->
    <section class="py-24 bg-white">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-14 reveal">
          <p class="text-xs font-extrabold tracking-widest uppercase mb-2" style="color:#E8A020">Témoignages</p>
          <h2 class="font-serif" style="font-size:clamp(1.8rem,3vw,2.6rem);color:#0B2545">
            La parole aux <span style="color:#1A7A4A">familles</span>
          </h2>
        </div>
        <div class="grid md:grid-cols-3 gap-6">
          <div
            v-for="(t, i) in TESTIMONIALS"
            :key="i"
            class="bg-gray-50 rounded-2xl p-7 border border-gray-100 reveal transition-transform hover:-translate-y-1"
          >
            <div class="mb-3" style="color:#E8A020">★★★★★</div>
            <p class="text-sm text-gray-500 italic leading-relaxed mb-5">« {{ t.t }} »</p>
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0 text-sm" style="background:linear-gradient(135deg,#0B2545,#1A7A4A)">
                {{ t.n[0] }}
              </div>
              <div>
                <div class="text-sm font-bold" style="color:#0B2545">{{ t.n }}</div>
                <div class="text-xs text-gray-400">{{ t.r }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ CTA ════════════════════════════════════════════ -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-5xl mx-auto px-6">
        <div class="relative overflow-hidden rounded-3xl py-20 px-10 text-center reveal" style="background:linear-gradient(135deg,#0B2545,#1A7A4A)">
          <div class="absolute w-72 h-72 rounded-full -top-20 -right-16 opacity-10" style="background:#E8A020"></div>
          <p class="text-xs font-extrabold tracking-widest uppercase mb-3 relative" style="color:#fde68a">Rejoignez-nous</p>
          <h2 class="font-serif text-white mb-4 relative" style="font-size:clamp(1.8rem,3.5vw,2.8rem)">
            Offrez le meilleur<br />à votre enfant
          </h2>
          <p class="text-sm max-w-sm mx-auto mb-9 relative" style="color:rgba(255,255,255,.7)">
            Les inscriptions pour l'année 2025–2026 sont ouvertes. Ne manquez pas votre place.
          </p>
          <div class="flex flex-wrap gap-3 justify-center relative">
            <router-link
              to="/admission"
              class="inline-flex items-center gap-2 px-8 py-3.5 rounded-full font-bold text-white no-underline"
              style="background:#E8A020;box-shadow:0 4px 20px rgba(232,160,32,.4)"
            >
              Commencer l'inscription
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </router-link>
            <router-link
              to="/contact"
              class="inline-flex items-center gap-2 px-7 py-3 rounded-full font-semibold text-white no-underline"
              style="border:2px solid rgba(255,255,255,.5)"
            >
              Nous contacter
            </router-link>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { STATS, FEATURES, TESTIMONIALS } from '@/data/index.js'
import { initReveal } from '@/composables/useReveal.js'

const VALUES = [
  { i: '🎯', t: 'Excellence' },
  { i: '🤝', t: 'Bienveillance' },
  { i: '💡', t: 'Innovation' },
  { i: '🌍', t: 'Citoyenneté' },
]

const CYCLES = [
  {
    i: '🌱', age: '3 – 5 ans', t: 'Préscolaire', color: '#F59E0B',
    d: "L'éveil par le jeu et la découverte dans un cadre sécurisant.",
    items: ['Motricité fine & globale', 'Langage oral', 'Socialisation', 'Activités créatives'],
  },
  {
    i: '📖', age: '6 – 11 ans', t: 'Fondamental', color: '#10B981',
    d: 'Les bases solides en lecture, écriture, mathématiques et sciences.',
    items: ['Français & Créole', 'Mathématiques', 'Sciences naturelles', 'Histoire-Géographie'],
  },
  {
    i: '🎓', age: '12 – 18 ans', t: 'Secondaire', color: '#3B82F6',
    d: "Préparation rigoureuse au baccalauréat et à l'université.",
    items: ['Séries scientifique & littéraire', 'Langues vivantes', 'Informatique', 'Orientation universitaire'],
  },
]

const ACTIVITIES = [
  { t: 'Sport & EPS', tag: 'Parascolaire', img: 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&q=80' },
  { t: 'Arts plastiques', tag: 'Créativité', img: 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&q=80' },
  { t: 'Club de lecture', tag: 'Culture', img: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=600&q=80' },
  { t: 'Concours scolaires', tag: 'Excellence', img: 'https://images.unsplash.com/photo-1606761568499-6d2451b23c66?w=600&q=80' },
]

onMounted(() => {
  window.scrollTo(0, 0)
  initReveal()
})
</script>

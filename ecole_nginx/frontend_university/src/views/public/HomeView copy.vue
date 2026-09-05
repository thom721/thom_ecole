<template>
  <div>
    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:100vh;min-height:580px">
      <img
        src="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1800&q=80"
        alt="École"
        class="hero-img w-full h-full object-cover block"
      />
      <div
        class="absolute inset-0"
        style="background:linear-gradient(135deg,rgba(11,31,58,.85) 0%,rgba(26,122,110,.5) 60%,rgba(212,168,83,.3) 100%)"
      ></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">
          Bienvenue à EduSphere
        </p>
        <h1 class="font-serif text-white mb-5 leading-tight" style="font-size:clamp(2.2rem,5vw,4.2rem);max-width:800px">
          L'Excellence <span class="text-gold">Académique</span><br />au Service de l'Avenir
        </h1>
        <p class="mb-8 max-w-lg leading-relaxed" style="color:rgba(255,255,255,.8);font-size:clamp(.95rem,2vw,1.2rem)">
          Une plateforme complète pour gérer chaque aspect de la vie scolaire — élèves, enseignants, performances et événements.
        </p>
        <div class="flex flex-wrap gap-3 justify-center">
          <router-link to="/admission" class="btn-gold inline-flex items-center gap-2 px-8 py-3.5 rounded-full font-semibold tracking-wide no-underline">
            S'inscrire maintenant
          </router-link>
          <router-link to="/formations" class="btn-white inline-flex items-center gap-2 px-7 py-3 rounded-full font-semibold tracking-wide no-underline">
            Nos formations
          </router-link>
        </div>
      </div>
      <div class="scroll-hint flex flex-col items-center gap-1.5" style="color:rgba(255,255,255,.5)">
        <span class="text-xs tracking-widest uppercase">Défiler</span>
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    <!-- ══ STATS ══════════════════════════════════════════ -->
    <div class="bg-white py-7" style="box-shadow:0 4px 20px rgba(11,31,58,.08)">
      <div class="max-w-6xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6">
        <div v-for="(s, i) in STATS" :key="i" class="text-center reveal" :class="i ? 'd' + Math.min(i, 4) : ''">
          <div class="stat-gradient font-black leading-none" style="font-size:2.8rem">{{ s.n }}</div>
          <div class="text-xs text-gray-400 mt-1">{{ s.l }}</div>
        </div>
      </div>
    </div>

    <!-- ══ FEATURES ══════════════════════════════════════ -->
    <section class="py-20">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center reveal">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Nos Fonctionnalités</p>
          <div class="gold-line mx mt-3.5 mb-3.5"></div>
          <h2 class="font-serif text-4xl mb-3">Tout ce dont une école a besoin</h2>
          <p class="text-gray-400 max-w-sm mx-auto leading-relaxed">
            Une suite d'outils pour simplifier l'administration et booster les résultats.
          </p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7 mt-12">
          <div
            v-for="(f, i) in FEATURES"
            :key="i"
            class="bg-white rounded-2xl shadow-md card-hover reveal"
            :class="i % 3 ? 'd' + (i % 3) : ''"
          >
            <div class="p-7">
              <div
                class="rounded-2xl flex items-center justify-center text-2xl mb-5"
                :style="{ background: f.bg, width: '52px', height: '52px' }"
              >{{ f.i }}</div>
              <h3 class="font-serif text-lg mb-2.5 text-navy">{{ f.t }}</h3>
              <p class="text-gray-400 text-sm leading-relaxed">{{ f.d }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ CTA BANNER ════════════════════════════════════ -->
    <section class="py-12">
      <div class="max-w-6xl mx-auto px-6">
        <div
          class="relative overflow-hidden rounded-3xl py-20 px-10 text-center reveal"
          style="background:linear-gradient(135deg,#0B1F3A,#1A7A6E)"
        >
          <div class="blob" style="width:320px;height:320px;top:-80px;right:-80px;background:#D4A853"></div>
          <div class="relative">
            <h2 class="font-serif text-white mb-4" style="font-size:clamp(1.8rem,3.5vw,2.8rem)">
              Prêt à rejoindre EduSphere ?
            </h2>
            <p class="max-w-sm mx-auto mb-9" style="color:rgba(255,255,255,.7)">
              Rejoignez plus de 1 200 élèves qui bénéficient d'une éducation d'excellence.
            </p>
            <div class="flex flex-wrap gap-3 justify-center">
              <router-link to="/admission" class="btn-gold inline-flex items-center gap-2 px-8 py-3.5 rounded-full font-semibold no-underline">
                Demander une admission
              </router-link>
              <router-link to="/formations" class="btn-white inline-flex items-center gap-2 px-7 py-3 rounded-full font-semibold no-underline">
                Voir les formations
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ TÉMOIGNAGES ═══════════════════════════════════ -->
    <section class="py-20">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center reveal">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Témoignages</p>
          <div class="gold-line mx mt-3.5 mb-3"></div>
          <h2 class="font-serif text-3xl mt-1">Ce que disent nos utilisateurs</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-7 mt-12">
          <div
            v-for="(t, i) in TESTIMONIALS"
            :key="i"
            class="bg-white rounded-2xl shadow-md card-hover reveal"
            :class="i ? 'd' + i : ''"
          >
            <div class="p-7">
              <div class="text-gold text-base mb-3">★★★★★</div>
              <p class="italic text-gray-500 text-sm leading-relaxed mb-5">"{{ t.t }}"</p>
              <div class="flex items-center gap-3">
                <div
                  class="w-11 h-11 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0"
                  style="background:linear-gradient(135deg,#0B1F3A,#1A7A6E)"
                >{{ t.n[0] }}</div>
                <div>
                  <div class="font-semibold text-sm">{{ t.n }}</div>
                  <div class="text-gray-400 text-xs">{{ t.r }}</div>
                </div>
              </div>
            </div>
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

onMounted(() => {
  window.scrollTo(0, 0)
  initReveal()
})

</script>

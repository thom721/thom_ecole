<template>
  <div>
    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:65vh;min-height:400px">
      <img
        src="https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1800&q=80"
        alt="Événements"
        class="hero-img w-full h-full object-cover block"
      />
      <div class="absolute inset-0" style="background:linear-gradient(135deg,rgba(11,31,58,.86) 0%,rgba(26,122,110,.5) 60%,rgba(212,168,83,.28) 100%)"></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">Agenda Scolaire</p>
        <h1 class="font-serif text-white mb-4" style="font-size:clamp(2.2rem,5vw,4.2rem)">
          Nos <span class="text-gold">Événements</span>
        </h1>
        <p style="color:rgba(255,255,255,.8)" class="max-w-lg leading-relaxed">
          Restez informé de toutes les activités, cérémonies et manifestations de l'établissement.
        </p>
      </div>
    </div>

    <!-- ══ FILTRE ═════════════════════════════════════════ -->
    <div class="sticky top-16 z-40 bg-white/95 backdrop-blur-md" style="box-shadow:0 2px 12px rgba(11,31,58,.07)">
      <div class="flex gap-2.5 overflow-x-auto px-6 py-3.5">
        <button
          v-for="cat in CATS"
          :key="cat"
          class="ev-pill"
          :class="{ active: current === cat }"
          @click="current = cat"
        >{{ cat }}</button>
      </div>
    </div>

    <!-- ══ ÉVÉNEMENT VEDETTE ══════════════════════════════ -->
    <section class="py-16">
      <div class="max-w-6xl mx-auto px-6">
        <div class="reveal mb-6">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Prochain Grand Événement</p>
          <div class="gold-line mt-3.5"></div>
        </div>
        <div class="relative rounded-3xl overflow-hidden cursor-pointer reveal-s" style="height:380px">
          <img
            src="https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1400&q=80"
            alt="Remise des diplômes"
            class="ev-img-inner w-full h-full object-cover block"
          />
          <div class="absolute inset-0" style="background:linear-gradient(to top,rgba(11,31,58,.92) 0%,transparent 55%)"></div>
          <div class="absolute bottom-0 left-0 right-0 p-9">
            <span class="inline-block text-xs font-bold uppercase tracking-widest text-navy px-3 py-1 rounded-full mb-3.5" style="background:#D4A853">
              Cérémonie
            </span>
            <h2 class="font-serif text-white mb-2.5" style="font-size:clamp(1.6rem,3vw,2.4rem)">
              Remise des Diplômes 2025
            </h2>
            <div class="flex flex-wrap gap-5 text-sm" style="color:rgba(255,255,255,.75)">
              <span>📅 15 Juin 2025</span>
              <span>📍 Salle des Fêtes</span>
              <span>⏰ 10h00</span>
              <span>👥 Tous les élèves & familles</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ GRILLE ÉVÉNEMENTS ══════════════════════════════ -->
    <section class="pb-20">
      <div class="max-w-6xl mx-auto px-6">
        <h2 class="font-serif text-3xl mb-8 reveal">Tous les Événements</h2>

        <p v-if="filtered.length === 0" class="text-gray-400 text-center py-12">
          Aucun événement dans cette catégorie pour le moment.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7">
          <div
            v-for="(ev, i) in filtered"
            :key="ev.id"
            class="relative rounded-2xl overflow-hidden cursor-pointer ev-card reveal"
            :class="i % 3 ? 'd' + (i % 3) : ''"
          >
            <img :src="ev.img" :alt="ev.t" class="ev-img-inner w-full block object-cover" style="height:200px" />
            <div class="absolute inset-0" style="background:linear-gradient(to top,rgba(11,31,58,.9) 0%,transparent 55%)"></div>
            <div class="absolute bottom-0 left-0 right-0 p-5">
              <span
                class="inline-block text-xs font-bold text-white px-2.5 py-0.5 rounded-full mb-1.5"
                :style="{ background: ev.col }"
              >{{ ev.cat }}</span>
              <div class="text-white font-bold text-sm mb-1">{{ ev.t }}</div>
              <div class="text-xs" style="color:rgba(255,255,255,.65)">{{ ev.date }} — {{ ev.lieu }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ CTA NEWSLETTER ════════════════════════════════ -->
    <div style="background:linear-gradient(135deg,#0B1F3A,#1A7A6E);padding:64px 0">
      <div class="max-w-6xl mx-auto px-6 text-center reveal">
        <h2 class="font-serif text-white text-3xl mb-3">Ne ratez aucun événement</h2>
        <p class="max-w-sm mx-auto mb-8" style="color:rgba(255,255,255,.7)">
          Abonnez-vous aux notifications {{useSchoolInfo.school_info?.nom || 'Lekol 360'}} et recevez les alertes en temps réel.
        </p>
        <div class="flex flex-wrap gap-3 justify-center max-w-sm mx-auto">
          <input class="ifield flex-1" type="email" placeholder="votre@email.fr" v-model="newsletterEmail" />
          <button class="btn-gold px-6 py-3 rounded-full font-semibold flex-shrink-0" @click="subscribeNewsletter">
            {{ subscribed ? '✓ Inscrit !' : "S'abonner" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { EVENTS } from '@/data/index.js'
import { initReveal } from '@/composables/useReveal.js'
import { useSchoolStore, useSchoolStoreInfo } from '@/stores/schoolStore';
const useSchoolInfo = useSchoolStoreInfo();
const CATS = ['Tous', 'Sportif', 'Culturel', 'Académique', 'Cérémonie']
const current = ref('Tous')

const filtered = computed(() =>
  current.value === 'Tous' ? EVENTS : EVENTS.filter(e => e.cat === current.value)
)

const newsletterEmail = ref('')
const subscribed = ref(false)

function subscribeNewsletter() {
  if (!newsletterEmail.value.includes('@')) return
  subscribed.value = true
  setTimeout(() => { subscribed.value = false; newsletterEmail.value = '' }, 3000)
}

onMounted(() => { window.scrollTo(0, 0); initReveal() })
watch(current, () => initReveal())
</script>

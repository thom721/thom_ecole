<template>
  <div>
    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:65vh;min-height:400px">
      <img
        src="https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=1800&q=80"
        alt="À propos"
        class="hero-img w-full h-full object-cover block"
      />
      <div class="absolute inset-0" style="background:linear-gradient(135deg,rgba(26,122,110,.88),rgba(212,168,83,.35))"></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">Notre Histoire</p>
        <h1 class="font-serif text-white mb-4" style="font-size:clamp(2.2rem,5vw,4.2rem)">
          À Propos de Nous
        </h1>
        <p style="color:rgba(255,255,255,.8)" class="max-w-lg leading-relaxed">
          Depuis 1998, nous façonnons des générations d'élèves prêts à relever les défis du monde moderne.
        </p>
      </div>
    </div>

    <!-- ══ MISSION ════════════════════════════════════════ -->
    <section class="py-20">
      <div class="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <div class="reveal-l">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Notre Mission</p>
          <div class="gold-line mt-3.5 mb-3"></div>
          <h2 class="font-serif mb-4 leading-tight" style="font-size:clamp(1.6rem,2.8vw,2.4rem)">
            Former les leaders de demain
          </h2>
          <p class="text-gray-400 leading-relaxed mb-4">
            {{useSchoolInfo.school_info?.nom || 'Lekol 360'}} est né d'une vision : unir la tradition pédagogique et l'innovation technologique pour offrir à chaque élève une expérience d'apprentissage unique, inclusive et efficace.
          </p>
          <p class="text-gray-400 leading-relaxed mb-8">
            Notre plateforme centralise toutes les informations — notes, absences, événements, communication — pour que chaque acteur de la communauté éducative soit toujours informé et impliqué.
          </p>
          <router-link to="/admission" class="btn-gold px-8 py-3.5 rounded-full font-semibold no-underline inline-block">
            Rejoindre la communauté
          </router-link>
        </div>

        <div class="relative reveal-r">
          <div class="rounded-3xl overflow-hidden" style="box-shadow:0 16px 48px rgba(11,31,58,.18)">
            <img
              src="https://images.unsplash.com/photo-1509062522246-3755977927d7?w=900&q=80"
              alt="Classe"
              class="w-full object-cover block"
              style="height:340px"
            />
          </div>
          <div
            class="absolute bg-white rounded-2xl p-5"
            style="bottom:-24px;left:-24px;box-shadow:0 16px 48px rgba(11,31,58,.18)"
          >
            <div class="stat-gradient font-black leading-none" style="font-size:2.4rem">98%</div>
            <div class="text-gray-400 text-xs mt-0.5">Taux de satisfaction</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ CHIFFRES CLÉS ══════════════════════════════════ -->
    <div class="bg-white py-14">
      <div class="max-w-6xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6">
        <div v-for="(s, i) in KEY_STATS" :key="i" class="text-center reveal" :class="i ? 'd' + Math.min(i,4) : ''">
          <div class="stat-gradient font-black leading-none" style="font-size:2.6rem">{{ s.n }}</div>
          <div class="text-xs text-gray-400 mt-1.5">{{ s.l }}</div>
        </div>
      </div>
    </div>

    <!-- ══ VALEURS ════════════════════════════════════════ -->
    <div style="background:linear-gradient(135deg,#0B1F3A,#162d4a);padding:80px 0">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center reveal mb-12">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Nos Valeurs</p>
          <div class="gold-line mx mt-3.5 mb-3"></div>
          <h2 class="font-serif text-white text-3xl mt-1">Ce qui nous guide</h2>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-7">
          <div
            v-for="(v, i) in VALS"
            :key="v.t"
            class="text-center reveal"
            :class="i ? 'd' + Math.min(i, 4) : ''"
          >
            <div class="text-5xl mb-3.5">{{ v.i }}</div>
            <div class="font-serif text-xl text-gold mb-2">{{ v.t }}</div>
            <div class="text-xs leading-relaxed" style="color:rgba(255,255,255,.6)">{{ v.d }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ ÉQUIPE ═════════════════════════════════════════ -->
    <section class="py-20">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center reveal mb-12">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Notre Équipe</p>
          <div class="gold-line mx mt-3.5 mb-3"></div>
          <h2 class="font-serif text-3xl mt-1">Ceux qui font {{useSchoolInfo.school_info?.nom || 'Lekol 360'}}</h2>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-7">
          <div
            v-for="(m, i) in TEAM"
            :key="m.n"
            class="bg-white rounded-2xl shadow-md card-hover text-center reveal"
            :class="i ? 'd' + Math.min(i, 4) : ''"
          >
            <div class="p-6">
              <div
                class="w-16 h-16 rounded-2xl flex items-center justify-center text-white text-2xl font-black mx-auto mb-4"
                :style="{ background: m.bg }"
              >{{ m.n[0] }}</div>
              <div class="font-bold text-sm mb-0.5">{{ m.n }}</div>
              <div class="text-gold text-xs font-semibold mb-2">{{ m.r }}</div>
              <div class="text-gray-400 text-xs leading-relaxed">{{ m.d }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ TIMELINE ═══════════════════════════════════════ -->
    <section class="py-20" style="background:#FAF7F2">
      <div class="mx-auto px-6" style="max-width:680px">
        <div class="text-center reveal mb-12">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Notre Parcours</p>
          <div class="gold-line mx mt-3.5 mb-3"></div>
          <h2 class="font-serif text-3xl mt-1">Les grandes étapes</h2>
        </div>
        <div class="tl relative pl-11">
          <div
            v-for="(m, i) in MILESTONES"
            :key="m.y"
            class="relative mb-9 reveal"
            :class="i && i < 4 ? 'd' + i : ''"
          >
            <div
              class="absolute"
              style="left:-30px;top:6px;width:18px;height:18px;background:#D4A853;border-radius:50%;box-shadow:0 0 0 5px rgba(212,168,83,.15)"
            ></div>
            <div class="bg-white rounded-2xl px-6 py-5 ml-2" style="box-shadow:0 4px 24px rgba(11,31,58,.1)">
              <div class="text-xs font-bold text-gold tracking-widest mb-1">{{ m.y }}</div>
              <h3 class="font-serif text-sm mb-1.5">{{ m.t }}</h3>
              <p class="text-gray-400 text-xs leading-relaxed">{{ m.d }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ CTA ════════════════════════════════════════════ -->
    <div style="background:linear-gradient(135deg,#1A7A6E,#0B1F3A);padding:80px 0">
      <div class="max-w-6xl mx-auto px-6 text-center reveal">
        <h2 class="font-serif text-white text-3xl mb-3">Faites partie de l'aventure</h2>
        <p class="max-w-sm mx-auto mb-8" style="color:rgba(255,255,255,.7)">
          Rejoignez une communauté scolaire engagée, innovante et tournée vers l'avenir.
        </p>
        <div class="flex flex-wrap gap-3 justify-center">
          <router-link to="/admission" class="btn-gold inline-flex items-center gap-2 px-8 py-3.5 rounded-full font-semibold no-underline">
            Demander une admission
          </router-link>
          <router-link to="/contact" class="btn-white inline-flex items-center gap-2 px-7 py-3 rounded-full font-semibold no-underline">
            Nous contacter
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { VALS, MILESTONES } from '@/data/index.js'
import { initReveal } from '@/composables/useReveal.js'
import { useSchoolStore, useSchoolStoreInfo } from '@/stores/schoolStore';
const useSchoolInfo = useSchoolStoreInfo();

const KEY_STATS = [
  { n: '1 200+', l: 'Élèves inscrits' },
  { n: '85',     l: 'Enseignants certifiés' },
  { n: '27 ans', l: "D'expérience" },
  { n: '98%',    l: 'Taux de satisfaction' },
]

const TEAM = [
  { n: 'Amara Diallo',    r: 'Directeur général',     d: 'Visionnaire de l\'éducation moderne, 20 ans d\'expérience.', bg: 'linear-gradient(135deg,#0B1F3A,#1A7A6E)' },
  { n: 'Sophie Leclerc',  r: 'Directrice pédagogique', d: 'Spécialiste des méthodes actives et de la différenciation.', bg: 'linear-gradient(135deg,#D4A853,#B8860B)' },
  { n: 'Karim Benali',    r: 'Responsable technique',  d: 'Architecte de la plateforme numérique.',           bg: 'linear-gradient(135deg,#1A7A6E,#0f5e54)' },
  { n: 'Claire Nguyen',   r: 'Responsable admissions', d: 'Accompagne chaque famille dans son projet scolaire.',         bg: 'linear-gradient(135deg,#8b5cf6,#6d28d9)' },
]

onMounted(() => { window.scrollTo(0, 0); initReveal() })
</script>

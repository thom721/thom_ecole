<template>
  <div>
    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:58vh;min-height:380px">
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
          Depuis 2021, l'IUSTH forme des scientifiques, professionnels et techniciens compétents au service du développement durable d'Haïti.
        </p>
      </div>
    </div>

    <GenericSection v-for="gs in genericSectionsInZone(5)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="apropos"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <!-- ══ IUSTH EN BREF ══════════════════════════════════ -->
    <section class="py-20">
      <div class="max-w-3xl mx-auto px-6 text-center reveal">
        <p class="text-xs tracking-widest uppercase font-bold text-gold">Qui sommes-nous</p>
        <div class="gold-line mx mt-3.5 mb-3"></div>
        <h2 class="font-serif text-3xl mt-1 mb-6">IUSTH en bref</h2>
        <p v-for="(p, i) in IUSTH_EN_BREF" :key="i" class="text-gray-500 leading-relaxed mb-4 text-left">{{ p }}</p>
      </div>
    </section>

    <!-- ══ MISSION ════════════════════════════════════════ -->
    <section id="mission" class="py-20" style="background:#EFECE5;scroll-margin-top:100px">
      <div class="max-w-4xl mx-auto px-6 text-center reveal mb-12">
        <p class="text-xs tracking-widest uppercase font-bold text-gold">Notre Mission</p>
        <div class="gold-line mx mt-3.5 mb-3"></div>
        <h2 class="font-serif text-3xl mt-1 mb-5">Mission de l'IUSTH</h2>
        <p class="text-gray-500 leading-relaxed italic max-w-2xl mx-auto">
          L'objectif général vise à contribuer par l'amélioration de la qualité de la formation et de la
          recherche pour une Haïti meilleure. Selon ses propres statuts et règlements, l'IUSTH s'est donné
          pour mission de :
        </p>
      </div>
      <div class="max-w-6xl mx-auto px-6">
        <ul class="grid grid-cols-1 md:grid-cols-3 gap-x-8 gap-y-3 reveal">
          <li v-for="(m, i) in MISSION_ITEMS" :key="i" class="bg-white rounded-xl px-5 py-4 text-gray-500 text-sm leading-relaxed flex gap-2.5" style="box-shadow:0 2px 12px rgba(11,31,58,.05)">
            <span class="text-gold flex-shrink-0">▸</span>{{ m }}
          </li>
        </ul>
        <div class="text-center mt-10">
          <router-link to="/admission" class="btn-gold px-8 py-3.5 rounded-full font-semibold no-underline inline-block">
            Rejoindre la communauté
          </router-link>
        </div>
      </div>
    </section>

    <!-- ══ DEVISE ═════════════════════════════════════════ -->
    <section class="py-20">
      <div class="max-w-3xl mx-auto px-6 text-center reveal">
        <p class="text-xs tracking-widest uppercase font-bold text-gold">Notre Devise</p>
        <div class="gold-line mx mt-3.5 mb-3"></div>
        <h2 class="font-serif text-3xl mt-1 mb-5">Mens & Manus — Réfléchir et agir</h2>
        <p class="text-gray-500 leading-relaxed italic mb-5">
          La connaissance au service de la communauté a pour slogan « Mens & Manus ». La devise de l'Institut
          Universitaire des Sciences et des Technologies d'Haïti (IUSTH) est en latin « Mens & Manus », en
          français « Réfléchir et agir ».
        </p>
        <p class="text-gray-500 leading-relaxed mb-5">
          L'IUSTH œuvre avant tout pour que les étudiants qui sont formés puissent contribuer valablement au
          développement de leur pays.
        </p>
        <p class="text-gray-500 leading-relaxed mb-8 text-left">
          En effet, plus de 85 % des diplômés haïtiens vivent et travaillent à l'extérieur. Beaucoup de jeunes
          Haïtiens partent à l'étranger (Chili, Brésil, République Dominicaine, etc.). Consciente de sa
          responsabilité, l'IUSTH met la priorité sur les pratiques et stages de ses futurs diplômés, de façon
          à ce qu'ils puissent trouver rapidement un emploi sur place, faire carrière en Haïti et donc
          participer au développement d'Haïti.
        </p>
        <div class="bg-white rounded-2xl p-7" style="box-shadow:0 8px 32px rgba(11,31,58,.08)">
          <h3 class="font-serif text-lg mb-2" style="color:#0B1F3A">Vision</h3>
          <p class="text-gray-500 leading-relaxed text-sm">
            Être à l'avant-garde dans la proposition de programmes et d'actions pour le bien-être de la
            population, dans une ambiance de développement durable.
          </p>
        </div>
      </div>
    </section>

    <GenericSection v-for="gs in genericSectionsInZone(25)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="apropos"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <!-- ══ CHIFFRES CLÉS ══════════════════════════════════ -->
    <div class="py-14" style="background:#ffffff">
      <div class="max-w-6xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6">
        <div v-for="(s, i) in KEY_STATS" :key="i" class="text-center reveal" :class="i ? 'd' + Math.min(i,4) : ''">
          <div class="stat-gradient font-black leading-none" style="font-size:2.6rem">{{ s.n }}</div>
          <div class="text-xs text-gray-500 mt-1.5">{{ s.l }}</div>
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

    <!-- ══ MOT DU RECTEUR ═════════════════════════════════════ -->
    <section id="mot-recteur" class="py-20" style="background:#EFECE5;scroll-margin-top:100px">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center reveal mb-12">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Bienvenue</p>
          <div class="gold-line mx mt-3.5 mb-3"></div>
          <h2 class="font-serif text-3xl mt-1">Mot du Recteur</h2>
        </div>
        <div class="bg-white rounded-2xl shadow-md reveal p-8 md:p-10">
          <div class="grid md:grid-cols-[220px_1fr] gap-8 md:gap-10">
            <div class="text-center md:text-left">
              <img
                src="/images/iusth-recteur-beaubrun-portrait.webp"
                alt="Professeur Saint-Pierre BEAUBRUN, Recteur de l'IUSTH"
                class="w-40 h-40 md:w-full md:h-auto rounded-2xl object-cover mx-auto md:mx-0"
                style="box-shadow:0 8px 24px rgba(11,31,58,.15)"
                loading="lazy"
              />
              <p class="font-serif text-lg mt-4 mb-0.5">Pr. Saint-Pierre BEAUBRUN</p>
              <p class="text-gold text-xs uppercase tracking-widest font-bold">Recteur de l'IUSTH</p>
            </div>
            <div class="min-w-0">
              <p v-for="(p, i) in MOT_RECTEUR" :key="i" class="text-gray-500 text-sm leading-relaxed mb-4 last:mb-0">
                {{ p }}
              </p>
              <p class="font-serif text-lg mt-6 mb-1" style="color:#0B1F3A">Lux et Veritas !</p>
              <p class="text-gray-400 text-xs italic">
                — Professeur Saint-Pierre BEAUBRUN, Recteur, Institut Universitaire des Sciences et des Technologies d'Haïti
              </p>

              <button
                type="button"
                @click="showPresentationRecteur = !showPresentationRecteur"
                class="mt-7 inline-flex items-center gap-2 text-sm font-semibold text-gold cursor-pointer bg-transparent border-0 p-0 hover:underline"
              >
                {{ showPresentationRecteur ? 'Masquer la présentation complète' : 'Lire la présentation complète du Recteur' }}
                <svg class="w-4 h-4 transition-transform" :class="showPresentationRecteur ? 'rotate-180' : ''"
                  fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 16 16">
                  <polyline points="4 6 8 10 12 6"/>
                </svg>
              </button>

              <div v-if="showPresentationRecteur" class="mt-6 pt-6 border-t border-gray-100 flex flex-col gap-6">
                <p class="text-gray-500 text-sm leading-relaxed">{{ PRESENTATION_RECTEUR.intro }}</p>

                <div>
                  <h4 class="font-serif text-sm font-bold mb-2.5" style="color:#0B1F3A">Formation académique</h4>
                  <p class="text-gray-500 text-sm leading-relaxed">{{ PRESENTATION_RECTEUR.formation }}</p>
                </div>

                <div>
                  <h4 class="font-serif text-sm font-bold mb-2.5" style="color:#0B1F3A">Carrière professionnelle</h4>
                  <p v-for="(p, i) in PRESENTATION_RECTEUR.carriere" :key="i" class="text-gray-500 text-sm leading-relaxed mb-3 last:mb-0">
                    {{ p }}
                  </p>
                </div>

                <div>
                  <h4 class="font-serif text-sm font-bold mb-2.5" style="color:#0B1F3A">Engagement religieux, social et citoyen</h4>
                  <p class="text-gray-500 text-sm leading-relaxed">{{ PRESENTATION_RECTEUR.engagement }}</p>
                </div>

                <div>
                  <h4 class="font-serif text-sm font-bold mb-2.5" style="color:#0B1F3A">Publications</h4>
                  <ul class="space-y-1.5">
                    <li v-for="(p, i) in PRESENTATION_RECTEUR.publications" :key="i" class="text-gray-500 text-sm leading-relaxed flex gap-2">
                      <span class="flex-shrink-0" style="color:#1A7A6E">✓</span>{{ p }}
                    </li>
                  </ul>
                </div>

                <p class="text-gray-500 text-sm leading-relaxed">{{ PRESENTATION_RECTEUR.conclusion }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ PRÉSIDENT DU CA ═══════════════════════════════════ -->
    <section id="president" class="py-20" style="scroll-margin-top:100px">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center reveal mb-12">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Gouvernance</p>
          <div class="gold-line mx mt-3.5 mb-3"></div>
          <h2 class="font-serif text-3xl mt-1">Président du Conseil d'Administration</h2>
        </div>
        <div class="bg-white rounded-2xl shadow-md reveal p-8 md:p-10">
          <div class="grid md:grid-cols-[220px_1fr] gap-8 md:gap-10">
            <div class="text-center md:text-left">
              <img
                src="/images/iusth-president-horat.webp"
                alt="Rony Horat, Président du Conseil d'Administration de l'IUSTH"
                class="w-40 h-40 md:w-full md:h-auto rounded-2xl object-cover mx-auto md:mx-0"
                style="box-shadow:0 8px 24px rgba(11,31,58,.15)"
                loading="lazy"
              />
              <h3 class="font-serif text-lg mt-4 mb-0.5">Rony Horat</h3>
              <p class="text-gold text-xs uppercase tracking-widest font-bold">Ing. Agronome, Msc et Juriste</p>
              <p class="text-gray-400 text-xs mt-1">Originaire de Petite Rivière de l'Artibonite</p>
            </div>
            <div class="min-w-0">
              <ul class="space-y-1.5 mb-6">
                <li class="text-gray-500 text-sm leading-relaxed flex gap-2">
                  <span class="text-gold flex-shrink-0">▸</span>
                  Président du Conseil d'Administration de l'Institut Universitaire des Sciences et
                  des Technologies d'Haïti (IUSTH)
                </li>
                <li class="text-gray-500 text-sm leading-relaxed flex gap-2">
                  <span class="text-gold flex-shrink-0">▸</span>
                  Directeur de la Direction de l'Éducation Relative à l'Environnement (DERE) du
                  Ministère de l'Environnement
                </li>
              </ul>

              <h4 class="font-serif text-sm font-bold mb-2.5" style="color:#0B1F3A">Études universitaires</h4>
              <ul class="space-y-1.5 mb-6">
                <li v-for="(e, i) in ETUDES_HORAT" :key="i" class="text-gray-500 text-sm leading-relaxed flex gap-2">
                  <span class="flex-shrink-0" style="color:#1A7A6E">•</span>{{ e }}
                </li>
              </ul>

              <h4 class="font-serif text-sm font-bold mb-2.5" style="color:#0B1F3A">Expériences de travail</h4>
              <ul class="space-y-1.5">
                <li v-for="(e, i) in EXPERIENCES_HORAT" :key="i" class="text-gray-500 text-sm leading-relaxed flex gap-2">
                  <span class="flex-shrink-0" style="color:#1A7A6E">•</span>{{ e }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ CONSEIL D'ADMINISTRATION ═══════════════════════════ -->
    <section class="py-20" style="background:#EFECE5">
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center reveal mb-12">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Gouvernance</p>
          <div class="gold-line mx mt-3.5 mb-3"></div>
          <h2 class="font-serif text-3xl mt-1">Les membres du Conseil d'Administration de l'IUSTH</h2>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="(mb, i) in CONSEIL_MEMBERS" :key="mb.role"
            class="flex items-center gap-4 bg-white rounded-2xl px-5 py-5 reveal"
            style="box-shadow:0 4px 20px rgba(11,31,58,.06)"
            :class="i ? 'd' + (i % 3) : ''"
          >
            <img v-if="mb.photo" :src="mb.photo" :alt="mb.nom" class="w-16 h-16 rounded-full object-cover flex-shrink-0" loading="lazy" />
            <div v-else class="w-16 h-16 rounded-full flex items-center justify-center text-white text-lg font-black flex-shrink-0" style="background:linear-gradient(135deg,#0B1F3A,#1A7A6E)">{{ mb.initiales }}</div>
            <div class="min-w-0">
              <div class="font-serif text-base mb-0.5">{{ mb.role }}</div>
              <div class="text-gray-500 text-xs">{{ mb.nom }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ FONCTIONNEMENT ═════════════════════════════════════ -->
    <section id="fonctionnement" class="py-20" style="scroll-margin-top:100px">
      <div class="max-w-3xl mx-auto px-6 text-center reveal">
        <p class="text-xs tracking-widest uppercase font-bold text-gold">Gouvernance</p>
        <div class="gold-line mx mt-3.5 mb-3"></div>
        <h2 class="font-serif text-3xl mt-1 mb-4">Fonctionnement</h2>
        <p class="text-gray-500 leading-relaxed">
          Cette section, consacrée à la structure administrative et aux organes de gouvernance de l'IUSTH,
          sera bientôt disponible.
        </p>
      </div>
    </section>

    <!-- ══ TIMELINE ═══════════════════════════════════════ -->
    <section class="py-20" style="background:#EFECE5">
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
              <p class="text-gray-500 text-xs leading-relaxed">{{ m.d }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <GenericSection v-for="gs in genericSectionsInZone(65)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="apropos"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <!-- ══ CTA ════════════════════════════════════════════ -->
    <div style="background:linear-gradient(135deg,#1A7A6E,#0B1F3A);padding:80px 0">
      <div class="max-w-6xl mx-auto px-6 text-center reveal">
        <h2 class="font-serif text-white text-3xl mb-3">Faites partie de l'aventure</h2>
        <p class="max-w-sm mx-auto mb-8" style="color:rgba(255,255,255,.7)">
          Rejoignez une communauté universitaire engagée, innovante et tournée vers l'avenir.
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

    <GenericSection v-for="gs in genericSectionsInZone(95)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="apropos"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <div v-if="authStore.isAdmin" class="bg-gray-50 py-3 text-center">
      <button @click="showAddBlockModal = true" class="px-4 py-1.5 rounded-full bg-blue-500/10 text-blue-600 text-xs font-semibold hover:bg-blue-500/20">
        + Ajouter un bloc (n'importe où sur la page)
      </button>
    </div>

    <!-- Modal : ajouter un bloc générique -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showAddBlockModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="closeAddBlockModal">
        <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl">
          <div class="flex items-center gap-2 justify-between px-6 py-4 border-b">
            <h2 class="text-sm font-semibold text-gray-800 flex items-center gap-2">
              <button v-if="pendingZone" @click="pendingZone = null" class="text-gray-500 hover:text-gray-600">←</button>
              {{ pendingZone ? 'Choisir un modèle' : 'Où ajouter le bloc ?' }}
            </h2>
            <button @click="closeAddBlockModal" class="text-gray-500 hover:text-gray-600">✕</button>
          </div>
          <div class="px-6 py-5 space-y-3 max-h-[60vh] overflow-y-auto">
            <template v-if="!pendingZone">
              <button
                v-for="z in zones" :key="z.ordre"
                @click="pendingZone = z"
                class="w-full text-left border border-gray-200 rounded-xl px-4 py-3 hover:border-blue-400 hover:bg-blue-50/50 transition-colors"
              >
                <div class="font-semibold text-sm text-gray-800">{{ z.label }}</div>
              </button>
            </template>
            <template v-else>
              <button
                v-for="tpl in LAYOUT_TEMPLATES" :key="tpl.layout"
                @click="pickBlockTemplate(tpl)"
                class="w-full text-left border border-gray-200 rounded-xl px-4 py-3 hover:border-blue-400 hover:bg-blue-50/50 transition-colors"
              >
                <div class="font-semibold text-sm text-gray-800">{{ tpl.label }}</div>
                <div class="text-xs text-gray-500 mt-0.5">{{ tpl.desc }}</div>
              </button>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { VALS, MILESTONES } from '@/data/index.js'
import { initReveal } from '@/composables/useReveal.js'
import { useSchoolStore, useSchoolStoreInfo } from '@/stores/schoolStore';
import { useAuthStore } from '@/stores/auth'
import GenericSection from '@/components/GenericSection.vue'
import { usePageSections, LAYOUT_TEMPLATES } from '@/composables/usePageSections.js'
const route = useRoute()
const useSchoolInfo = useSchoolStoreInfo();
const authStore = useAuthStore()
const url = import.meta.env.VITE_APP_BASE_URL

// ── Blocs génériques ajoutés librement (voir HomeView.vue pour le détail) ──
const {
  genericSections, genericSectionsInZone, createGenericSection, fetchSections: fetchGenericSections,
  toggleSection: toggleGenericSection, deleteSection: deleteGenericSection, zones,
} = usePageSections('apropos')
const showAddBlockModal = ref(false)
const pendingZone = ref(null)
const closeAddBlockModal = () => { showAddBlockModal.value = false; pendingZone.value = null }
const pickBlockTemplate = async (tpl) => {
  const ok = await createGenericSection(tpl, pendingZone.value.ordre)
  if (ok) closeAddBlockModal()
}

// Chiffres réels et vérifiables (pas de nombre d'élèves/taux de satisfaction
// inventé — voir Audit_site_IUSTH_2026-08-27.pdf, point 2.5). Facultés et
// programmes comptés en direct depuis les mêmes endpoints publics que
// FacultesView.vue/FormationsView.vue, pas figés en dur : un ajout/retrait
// de faculté ou de programme se répercute automatiquement ici. "Institutions
// partenaires" reste éditorial (rien en base pour ça). Année de création
// lue depuis Profile.info_de_fondation (fallback 2021, valeur réelle IUSTH).
// Source : iusth/Les Facultés.docx (page "Mission de l'IUSTH")
const IUSTH_EN_BREF = [
  "Fondée en mai 2021, l'Institut Universitaire des Sciences et des Technologies d'Haïti (IUSTH) est une institution privée d'enseignement supérieur et de recherche, remplissant une mission de service au développement à la communauté, à but non lucratif, reconnue d'utilité publique par l'État haïtien, sans affiliation politique, ni appartenance religieuse.",
  "IUSTH est l'une des institutions de premier choix en Haïti, basée sur des pratiques en entreprise, réputée pour la qualité de sa formation et de sa recherche, son esprit d'ouverture, son dynamisme et le professionnalisme de son personnel de formation et d'enseignement. Elle s'est engagée à devenir une université d'excellence et de référence dans la recherche pour le développement d'Haïti.",
  "Vigilante aux besoins de sa communauté pour le choix de ses programmes d'enseignement supérieur et de recherche, l'IUSTH a mis en œuvre divers programmes et projets relatifs à la formation, à la recherche et au développement dans différents domaines, en coopération avec une dizaine d'institutions universitaires et non universitaires d'Amérique et des Caraïbes.",
  "IUSTH est placée sous la tutelle du Conseil d'Administration qui s'assure de son bon fonctionnement et de sa pérennité.",
]

const MISSION_ITEMS = [
  "Remplir toutes les exigences académiques et légales afin que nos étudiants soient bien formés.",
  "Former et perfectionner des scientifiques, professionnels et techniciens dotés d'une capacité de réflexion, d'un savoir et d'un savoir-faire susceptibles de répondre aux exigences du développement durable d'Haïti.",
  "Participer et contribuer, par des initiatives et actions appropriées, à la conservation, l'enrichissement et la promotion de la culture nationale et des valeurs morales, spirituelles et civiques de la communauté haïtienne.",
  "Pérenniser l'institution par la mise en place de règlements et d'une discipline sévère.",
  "Concevoir, exécuter et évaluer des programmes de recherche tendant à contribuer au développement de la science universelle et à l'amélioration des conditions de la société haïtienne.",
  "Agrandir l'institution sur le plan national en touchant certaines grandes villes du pays, en vue de répondre aux demandes.",
  "Développer chez ses membres, en plus des connaissances et compétences requises, une conscience citoyenne, le sens de l'éthique et les valeurs du partage.",
  "Assurer et promouvoir, par le moyen de la coopération universitaire, un système permanent d'informations et d'échanges avec les institutions qui poursuivent les mêmes fins, participant ainsi à un incessant et fécond dialogue national et international des cultures.",
  "Promouvoir au sein de la société haïtienne les idéaux d'excellence, de paix, de progrès, de respect des droits humains et de justice sociale.",
  "Développer chez ses communautés éducatives, en plus des connaissances et compétences requises, une conscience citoyenne, le sens de l'éthique et les valeurs au sens de la vulgarisation.",
  "Opérationnaliser l'institution conformément aux lois et règlements régissant la matière.",
]

const CONSEIL_MEMBERS = [
  { role: 'Le Recteur', nom: 'Me Saint-Pierre BEAUBRUN', initiales: 'SB', photo: '/images/iusth-recteur-beaubrun.webp' },
  { role: 'Président du Conseil', nom: 'Agr. Rony HORAT', initiales: 'RH', photo: '/images/iusth-president-horat.webp' },
  { role: 'Responsable IUSTH USA', nom: 'Mr. Canal FRANÇOIS', initiales: 'CF', photo: null },
  { role: 'Responsable Financière', nom: 'Mme Louna FRANÇOIS', initiales: 'LF', photo: null },
  { role: 'Responsable IT', nom: 'Ing. Jose BALTAZAR', initiales: 'JB', photo: '/images/iusth-responsable-it-baltazar.webp' },
]

const showPresentationRecteur = ref(false)

// Source : iusth/Mot du recteur de l'IUSTH.pdf
const MOT_RECTEUR = [
  "Au cœur des défis et des aspirations de notre nation, l'Institut Universitaire des Sciences et des Technologies d'Haïti (IUSTH) incarne un espoir tangible pour l'avenir de notre chère Haïti. Fondé en 2021, dans un contexte national complexe marqué par des défis sécuritaires et des incertitudes, notre institution symbolise un acte de courage, de patriotisme et de foi.",
  "En effet, il nécessite un courage certain de choisir de demeurer dans le pays en pareille période, alors que l'opportunité de partir est présente. Cela requiert un patriotisme authentique d'investir son temps, son argent et son énergie dans le pays en dépit des défis. Il est essentiel de garder espoir en un avenir meilleur et de croire en la renaissance d'Haïti, tel le Phénix, afin de poursuivre notre engagement envers l'éducation des jeunes qui, nous l'espérons, contribueront activement à la revitalisation de notre chère patrie.",
  "À l'IUSTH, nous croyons en l'enseignement des sciences et des technologies comme moteur du progrès. Nous sommes déterminés à offrir à nos étudiants et étudiantes un enseignement de qualité, ancré dans l'excellence académique et la pertinence sociale. Chaque jeune qui franchit nos portes est non seulement un apprenant, mais un futur leader, prêt à façonner un avenir meilleur pour notre pays.",
  "Notre mission dépasse les murs de nos salles de cours. Nous nous engageons à promouvoir la recherche novatrice qui répond aux besoins locaux et mondiaux, à cultiver un environnement d'apprentissage inclusif et à encourager la diversité des idées et des perspectives. Ensemble, nous construisons une communauté universitaire vibrante où la créativité et l'ambition trouvent leur plein épanouissement.",
  "À travers nos programmes académiques rigoureux, nos partenariats stratégiques et notre engagement envers l'intégrité et l'éthique, nous préparons nos étudiants et étudiantes à affronter les défis du XXIe siècle avec confiance et détermination. À l'IUSTH, nous croyons en une Haïti où le savoir sera la force motrice du développement durable, où chaque diplômé contribuera activement à la construction d'une société plus juste et prospère.",
  "Je vous invite à explorer notre université, à découvrir nos programmes innovants et à rejoindre une communauté passionnée de chercheurs, d'enseignants et d'étudiants engagés à faire une différence significative. Ensemble, nous écrivons l'histoire de l'IUSTH, une histoire d'excellence, d'audace et de succès.",
  "Bienvenue à l'IUSTH, où le savoir transforme des vies et forge un avenir brillant pour Haïti !",
]

// Source : iusth/Présentation du Recteur - version longue.pdf
const PRESENTATION_RECTEUR = {
  intro: "Me Saint-Pierre BEAUBRUN incarne une figure éminente alliant une carrière académique remarquable, un engagement passionné envers les droits humains, et une profonde implication dans la théologie et le service communautaire.",
  formation: "Après son baccalauréat au Lycée Louis Joseph Janvier de Carrefour en 1997, Saint-Pierre BEAUBRUN a obtenu une licence en sciences juridiques à la Faculté de Droit et des Sciences Économiques en 2001, puis une maîtrise en Criminologie au Programme de Maîtrise Interdisciplinaire en Sciences Sociales et Humaines de l'Université d'État d'Haïti en 2008. Il a également entrepris des études de premier cycle en théologie au Collège Universitaire de Christianville (CUC) de Gressier de 2004 à 2006 et obtenu une maîtrise à l'Indiana Wesleyan University (IWU) en 2018. BEAUBRUN a suivi des formations spécialisées en droits de l'homme à l'Institut International des Droits de l'Homme (IIDH) et au Centre International pour l'Enseignement des Droits de l'Homme dans les Universités (CIEDHU) de Strasbourg en 2011, puis au Centre International d'Éducation aux Droits Humains-EQUITAS du Québec en 2012. Cette formation est complétée par de nombreux séminaires, notamment des ateliers de formation de formateurs sur la Citoyenneté engagée et l'Action communautaire, le Coaching en droits humains, la Rédaction et gestion de projets, les Droits des femmes, les Droits des migrants, l'Équité de genre, les Garanties judiciaires et conditions de détention, l'Histoire des Religions et des sectes, la Théologie systématique, ainsi que la Bureautique.",
  carriere: [
    "Saint-Pierre BEAUBRUN a enseigné des cours de théologie biblique et historique au Tyrannus Séminaire de Théologie (TST) de Carrefour, dont il a été le directeur de 1997 à 2000, et à l'International Victory Bible Institute (annexe Haïti) de 2006 à 2011. Il a été professeur de droit à la Faculté des Sciences Appliquées (FDSA) de Port-au-Prince de 2009 à 2015. Il a prêté serment comme avocat du Barreau de Port-au-Prince en 2006. Il a occupé successivement les postes de Chargé d'assistance légale, Responsable de section des droits humains et migration, Responsable de programmes et Coordonnateur exécutif du Groupe d'Appui aux Rapatriés et Réfugiés (GARR) du 1er mars 2010 au 31 décembre 2019. Il a également été le premier responsable de la Commission d'Éthique au sein de cette institution des droits humains, élu pour un mandat de deux ans, de janvier 2013 à 2015.",
    "Il a donné de nombreuses consultations et mené plusieurs recherches appliquées : une évaluation du droit humain à la paix en Haïti pour la Finn Church Aid (2014), une étude sur la traite des femmes et des filles pour l'Organisation Internationale pour les Migrations (2009), une recherche sur le cadre juridique et institutionnel de l'état civil haïtien pour le GARR (2008-2009), une étude qualitative sur les obstacles culturels à l'utilisation de la contraception pour le MSPP et le FNUAP (2008), ainsi que plusieurs consultations sur la nationalité, la citoyenneté et la migration, et sur l'état civil et l'identification nationale, toujours pour le GARR (2007-2008).",
    "Il a également conçu et animé de nombreux ateliers de formation de formateurs à l'intention des leaders communautaires et religieux : en droit et droits humains (état civil, citoyenneté engagée, plaidoyer, démocratie, droit au logement, droit à la nationalité, droits des migrants, violence faite aux femmes, équité de genre), et en théologie (Réforme protestante, protestantisme haïtien, herméneutique, homilétique, apologétique chrétienne, ecclésiologie et missiologie).",
  ],
  engagement: "En parallèle à sa carrière académique et professionnelle, Saint-Pierre Beaubrun fait du bénévolat dans de nombreuses structures à caractère religieux et social. Membre du Mouvement d'Évangélisation Sans Frontière (MESF) depuis 1994, il a été ordonné Évangéliste en 2001. Il a fondé le Service d'Entraide Socio-Spirituelle (SENS) en 2003, où il enseigne hebdomadairement et en assure bénévolement la direction depuis cette date — SENS dispense des formations gratuites sur des thèmes religieux et sociaux (droits humains de base, droit à l'identité, droit à la paix, droits des femmes, équité de genre). Membre du conseil des anciens de son Église depuis 2016, il a également fondé l'Action citoyenne pour les droits de l'homme et la démocratie (ACDHD) en 2016, dont il occupe toujours la vice-présidence.",
  publications: [
    "Déclin Moral et Doctrinal de l'Église Médiévale : Aux Origines du Schisme Catholique et Protestant, Éd. Libres d'écrire, Marseille (à paraître, octobre 2024)",
    "La Réforme en réflexion : Fondements Historiques et Bibliques du Protestantisme, Éd. Libres d'écrire, Marseille (à paraître, octobre 2024)",
    "L'État civil en Haïti : Normes, Procédures et Pratiques, Éd. Média-Texte, Port-au-Prince, 2024",
    "L'Église en trois dimensions, Éd. Libres d'écrire, Marseille, 2023",
    "Mission Biblique de l'Église dans un monde en mutation, Éd. Libres d'écrire, Marseille, 2023",
    "La Réforme protestante en Haïti : Son difficile parcours et ses limites, Ed. Promociones & Publicidad la Fe, Santo-Domingo, 2020",
    "Coup d'œil Rétrospectif sur la Réforme protestante du XVIe siècle, Ed. Média-Texte, Port-au-Prince, 2005",
  ],
  conclusion: "Saint-Pierre Beaubrun incarne un exemple inspirant de leadership intellectuel, moral et communautaire en Haïti. Sa carrière remarquable, de l'enseignement à la recherche en passant par l'activisme pour les droits humains, reflète un engagement profond envers l'amélioration de la société haïtienne. À travers ses multiples contributions académiques, professionnelles et bénévoles, il continue de laisser une marque significative dans la promotion de la justice sociale, de l'éducation et du respect des droits fondamentaux.",
}

// Source : iusth/Biographie M.HORAT Rony.docx
const ETUDES_HORAT = [
  "Master en Bioressources à l'Université Paris 12, Créteil, 2006-2007",
  "Diplôme d'Ingénieur Agronome à l'Université Agraire de la Havane, Cuba, 1999-2004",
  "Maîtrise en Sciences de l'Environnement à l'Université Paris 7, Denis Diderot, 2004-2005",
  "Stage à l'INRA Paris-Grignon, formation de courte durée à l'INAPG-Agro-ParisTech, 2005-2006",
  "Licence en Droit, Université d'État d'Haïti, Faculté des Sciences Juridiques des Gonaïves, 2013-2017",
]
const EXPERIENCES_HORAT = [
  "Mai 2021 – à ce jour : Président du Conseil d'Administration de l'Institut Universitaire des Sciences et des Technologies d'Haïti (IUSTH)",
  "Septembre 2016 – Août 2020 : Recteur de l'Université Saint François d'Assise d'Haïti (USFAH)",
  "Septembre 2009 – à ce jour : Professeur et encadreur à l'Université de Port-au-Prince",
  "Coopération Allemagne, projet Binational (Haïti–République Dominicaine), septembre 2009-2010",
  "Coopération Espagnole – MdE, janvier 2011 – décembre 2011",
  "Care-Haïti, janvier 2012 – novembre 2012",
  "Consultant d'un programme d'Agroforesterie à Deschapelles, Département de l'Artibonite, décembre 2012-avril 2013",
  "Consultant au Secrétariat Technique de la Direction Générale (STDG)/MdE, mai 2013-octobre 2015",
  "Assistant Directeur au MdE, affecté à la Direction Forêts et des Énergies Renouvelables, 2015-octobre 2017",
  "Directeur de la Direction Inspection et Surveillance Environnementale (DEISE), novembre 2017-octobre 2020",
]

const facultesCount   = ref(null)
const formationsCount = ref(null)

const KEY_STATS = computed(() => [
  { n: facultesCount.value   != null ? String(facultesCount.value)   : '…', l: 'Facultés' },
  { n: formationsCount.value != null ? String(formationsCount.value) : '…', l: 'Programmes de formation' },
  { n: '10+', l: 'Institutions partenaires' },
  { n: useSchoolInfo.school_info?.info_de_fondation || '2021', l: 'Année de création' },
])

const fetchCounts = async () => {
  try {
    const [{ data: fac }, { data: form }] = await Promise.all([
      axios.get(`${url}/facultes-publiques`),
      axios.get(`${url}/formations/`),
    ])
    facultesCount.value   = fac?.data?.length ?? 0
    formationsCount.value = Array.isArray(form) ? form.length : 0
  } catch (e) { console.error('[À propos] chiffres clés', e) }
}

onMounted(() => {
  // Arrivée depuis un sous-menu (ex: /a-propos#president) : défiler vers la
  // section visée plutôt que de forcer le haut de page et perdre l'ancre.
  if (route.hash) {
    const el = document.querySelector(route.hash)
    if (el) el.scrollIntoView({ behavior: 'smooth' })
  } else {
    window.scrollTo(0, 0)
  }
  initReveal()
  fetchCounts()
  fetchGenericSections()
})
</script>

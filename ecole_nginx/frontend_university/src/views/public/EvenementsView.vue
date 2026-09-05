<template>
  <div>
    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:58vh;min-height:380px">
      <img
        src="https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1800&q=80"
        alt="Événements"
        class="hero-img w-full h-full object-cover block"
      />
      <div class="absolute inset-0" style="background:linear-gradient(135deg,rgba(11,31,58,.86) 0%,rgba(26,122,110,.5) 60%,rgba(212,168,83,.28) 100%)"></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">Agenda Universitaire</p>
        <h1 class="font-serif text-white mb-4" style="font-size:clamp(2.2rem,5vw,4.2rem)">
          Nos <span class="text-gold">Événements</span>
        </h1>
        <p style="color:rgba(255,255,255,.8)" class="max-w-lg leading-relaxed">
          Restez informé de toutes les activités, cérémonies et manifestations de l'établissement.
        </p>
      </div>
    </div>

    <GenericSection v-for="gs in genericSectionsInZone(5)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="evenements"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

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
    <!-- Retiré : aucun événement réel confirmé pour l'instant (voir
         EVENTS dans data/index.js) — la grille ci-dessous affiche déjà
         "Aucun événement pour le moment" tant qu'elle est vide, pas besoin
         d'un doublon statique et daté au-dessus. -->

    <!-- ══ GRILLE ÉVÉNEMENTS ══════════════════════════════ -->
    <section class="pb-20">
      <div class="max-w-6xl mx-auto px-6">
        <h2 class="font-serif text-3xl mb-8 reveal">Tous les Événements</h2>

        <p v-if="filtered.length === 0" class="text-gray-500 text-center py-12">
          Aucun événement dans cette catégorie pour le moment.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7">
          <div
            v-for="(ev, i) in filtered"
            :key="ev.id"
            class="relative rounded-2xl overflow-hidden cursor-pointer ev-card reveal"
            :class="i % 3 ? 'd' + (i % 3) : ''"
          >
            <img :src="ev.img" :alt="ev.t" class="ev-img-inner w-full block object-cover" style="height:200px" loading="lazy" />
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
          Abonnez-vous aux notifications {{useSchoolInfo.school_info?.nom || 'IUSTH'}} et recevez les alertes en temps réel.
        </p>
        <div class="flex flex-wrap gap-3 justify-center max-w-sm mx-auto">
          <input class="ifield flex-1" type="email" placeholder="votre@email.fr" v-model="newsletterEmail" />
          <button class="btn-gold px-6 py-3 rounded-full font-semibold flex-shrink-0" @click="subscribeNewsletter">
            {{ subscribed ? '✓ Inscrit !' : "S'abonner" }}
          </button>
        </div>
      </div>
    </div>

    <GenericSection v-for="gs in genericSectionsInZone(95)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="evenements"
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
import { ref, computed, watch, onMounted } from 'vue'
import { EVENTS } from '@/data/index.js'
import { initReveal } from '@/composables/useReveal.js'
import { useSchoolStore, useSchoolStoreInfo } from '@/stores/schoolStore';
import { useAuthStore } from '@/stores/auth'
import GenericSection from '@/components/GenericSection.vue'
import { usePageSections, LAYOUT_TEMPLATES } from '@/composables/usePageSections.js'
const useSchoolInfo = useSchoolStoreInfo();
const authStore = useAuthStore()

// ── Blocs génériques ajoutés librement (voir HomeView.vue pour le détail) ──
const {
  genericSections, genericSectionsInZone, createGenericSection, fetchSections: fetchGenericSections,
  toggleSection: toggleGenericSection, deleteSection: deleteGenericSection, zones,
} = usePageSections('evenements')
const showAddBlockModal = ref(false)
const pendingZone = ref(null)
const closeAddBlockModal = () => { showAddBlockModal.value = false; pendingZone.value = null }
const pickBlockTemplate = async (tpl) => {
  const ok = await createGenericSection(tpl, pendingZone.value.ordre)
  if (ok) closeAddBlockModal()
}

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

onMounted(() => { window.scrollTo(0, 0); initReveal(); fetchGenericSections() })
watch(current, () => initReveal())
</script>

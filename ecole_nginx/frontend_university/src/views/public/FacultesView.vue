<template>
  <div>
    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:58vh;min-height:380px">
      <img
        src="https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=1800&q=80"
        alt="Les facultés"
        class="hero-img w-full h-full object-cover block"
      />
      <div class="absolute inset-0" style="background:linear-gradient(135deg,rgba(11,31,58,.9),rgba(212,168,83,.3),rgba(26,122,110,.5))"></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">Nos filières</p>
        <h1 class="font-serif text-white mb-4" style="font-size:clamp(2.2rem,5vw,4.2rem)">
          Les <span class="text-gold">Facultés</span>
        </h1>
        <p style="color:rgba(255,255,255,.8)" class="max-w-lg leading-relaxed">
          Découvrez nos filières ouvertes et les programmes qui y sont rattachés.
        </p>
      </div>
    </div>

    <!-- ══ GRILLE DES FACULTÉS ══════════════════════════════ -->
    <section class="py-16" style="background:#EFECE5">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-14 reveal">
          <h2 class="font-serif" style="font-size:clamp(1.8rem,3vw,2.6rem);color:#0B2545">Explorez nos programmes<br/>d'études</h2>
        </div>

        <div v-if="loading" class="text-center text-gray-500 py-16">Chargement…</div>

        <div v-else-if="facultes.length === 0" class="text-center text-gray-500 py-16">
          Aucune faculté n'est ouverte pour le moment.
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          <div
            v-for="(f, i) in facultes"
            :key="f.id"
            class="rounded-3xl overflow-hidden reveal"
            style="background:#fdfbf6;box-shadow:0 4px 20px rgba(11,31,58,.06)"
            :class="i ? 'd' + (i % 3) : ''"
          >
            <div class="p-5 pb-6">
              <div class="rounded-2xl overflow-hidden mb-4" style="aspect-ratio:1/1">
                <img v-if="f.image_url" :src="toAbsoluteUrl(f.image_url)" :alt="f.nom" class="w-full h-full object-cover block" loading="lazy"/>
                <div v-else class="w-full h-full flex items-center justify-center text-5xl" style="background:rgba(212,168,83,.12)">🎓</div>
              </div>
              <div class="text-center">
                <span class="inline-block px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wide text-white mb-3"
                      style="background:#1A7A6E">{{ f.nom }}</span>
                <p v-if="f.description" class="text-gray-500 text-xs leading-relaxed mb-4" :class="{ 'line-clamp-3': !expanded[f.id] }">{{ f.description }}</p>
                <button
                  v-if="f.description"
                  type="button"
                  @click="expanded[f.id] = !expanded[f.id]"
                  class="btn-outline inline-block px-5 py-1.5 rounded-full text-xs font-semibold"
                >{{ expanded[f.id] ? 'Voir moins' : 'Voir plus' }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { initReveal } from '@/composables/useReveal.js'

const url = import.meta.env.VITE_APP_BASE_URL

// f.image_url stocké par l'API est un chemin relatif ("/static/uploads/...")
// — se résoudrait contre l'origine du frontend, pas celle de l'API (voir
// même correctif dans FormationsView.vue et usePageSections.js).
const apiOrigin = url.replace(/\/api\/v1\/?$/, '')
const toAbsoluteUrl = (path) => {
  if (!path) return null
  return path.startsWith('http') ? path : `${apiOrigin}${path}`
}

const facultes = ref([])
const loading  = ref(false)
// "Voir plus" déplie la description sur place plutôt que de naviguer vers
// /formations?faculte_id=... — cette page ne filtre plus rien depuis que la
// grille de cartes y a été remplacée par "Programmes Offerts" (le lien
// n'aurait plus rien fait), et évite un UUID visible dans l'URL.
const expanded = ref({})

const fetchFacultes = async () => {
  loading.value = true
  try {
    // Publique et déjà filtrée côté serveur (status=True) : une faculté
    // annoncée mais pas encore ouverte n'apparaît jamais ici (voir
    // Audit_site_IUSTH_2026-08-27.pdf, point 2.4 : lien mort vers une
    // filière inexistante).
    const { data } = await axios.get(`${url}/facultes-publiques`)
    facultes.value = data.data ?? []
  } catch (e) { console.error('[Facultés]', e) }
  finally { loading.value = false }
}

onMounted(async () => {
  await fetchFacultes()
  initReveal()
})
</script>

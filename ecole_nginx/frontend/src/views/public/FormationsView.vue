<template>
  <div>
    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:72vh;min-height:460px">
      <img
        src="https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?w=1800&q=80"
        alt="Formations"
        class="hero-img w-full h-full object-cover block"
      />
      <div class="absolute inset-0" style="background:linear-gradient(135deg,rgba(11,31,58,.9) 0%,rgba(26,122,110,.55) 55%,rgba(212,168,83,.3) 100%)"></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">Cursus & Programmes</p>
        <h1 class="font-serif text-white mb-4 leading-tight" style="font-size:clamp(2.2rem,5vw,4.2rem)">
          Nos <span class="text-gold">Formations</span>
        </h1>
        <p class="mb-8 max-w-lg leading-relaxed" style="color:rgba(255,255,255,.8)">
          Des programmes rigoureux et innovants, conçus pour préparer chaque élève à un avenir brillant.
        </p>
        <!-- Filter pills -->
        <div class="flex flex-wrap gap-2.5 justify-center">
          <button v-for="lv in F_LEVELS" :key="lv"
            class="filter-pill" :class="{ active: currentLevel === lv }"
            @click="currentLevel = lv">{{ lv }}</button>
        </div>
      </div>
    </div>

    <!-- ══ ATOUTS ═════════════════════════════════════════ -->
    <section v-if="showingAtouts" class="py-12 relative">
      <!-- Overlay masqué -->
      <div v-if="authStore.isAdmin && atoutsSection?.is_visible === false"
        class="absolute inset-0 bg-red-500/5 border-2 border-dashed border-red-300/40 z-10 pointer-events-none"></div>

      <!-- Barre admin -->
      <div v-if="authStore.isAdmin" class="absolute top-2 right-4 flex items-center gap-1 z-20">
        <span :class="['text-[10px] px-2 py-0.5 rounded-full font-medium',
          atoutsSection?.is_visible !== false ? 'bg-emerald-500/20 text-emerald-600' : 'bg-red-500/20 text-red-500']">
          {{ atoutsSection?.is_visible !== false ? 'Visible' : 'Masqué' }}
        </span>
        <button @click="openAtoutItemEdit()" class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 text-xs hover:bg-amber-500/20">+ Atout</button>
        <button @click="toggleAtouts()" class="p-1 rounded bg-gray-100 text-gray-500 text-xs hover:bg-gray-200" title="Masquer/Afficher">👁</button>
      </div>

      <div class="max-w-6xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6">
        <div v-for="(a, i) in ATOUTS" :key="i"
          class="bg-white rounded-2xl shadow-md card-hover reveal relative group"
          :class="i ? 'd' + Math.min(i, 4) : ''">
          <div class="p-6 flex gap-3.5 items-start">
            <div class="text-3xl flex-shrink-0">{{ a.i }}</div>
            <div>
              <div class="font-bold text-sm mb-1">{{ a.t }}</div>
              <div class="text-gray-400 text-xs leading-relaxed">{{ a.d }}</div>
            </div>
          </div>
          <!-- Boutons admin par carte -->
          <div v-if="authStore.isAdmin" class="absolute top-2 right-2 hidden group-hover:flex gap-1">
            <button @click="openAtoutItemEdit(i)" class="w-6 h-6 rounded bg-blue-500/15 text-blue-600 text-xs flex items-center justify-center hover:bg-blue-500/25">✎</button>
            <button @click="deleteAtoutItem(i)" class="w-6 h-6 rounded bg-red-500/15 text-red-500 text-xs flex items-center justify-center hover:bg-red-500/25">✕</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ GRILLE FORMATIONS ══════════════════════════════ -->
    <section v-if="formations.length > 0 || authStore.isAdmin" class="py-10">
      <div class="max-w-6xl mx-auto px-6">
        <div class="flex items-center justify-between mb-9">
          <h2 class="font-serif text-3xl reveal">Toutes nos formations</h2>
          <!-- Bouton Ajouter — admin seulement -->
          <button v-if="authStore.isAdmin" @click="openModal()"
            class="flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold text-white"
            style="background:var(--gold,#D4A853)">
            + Ajouter une formation
          </button>
        </div>

        <div v-if="loadingFormations" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7">
          <div v-for="i in 4" :key="i" class="bg-white rounded-2xl shadow-md overflow-hidden animate-pulse">
            <div class="h-48 bg-gray-200"></div>
            <div class="p-7 space-y-3">
              <div class="h-4 bg-gray-200 rounded w-3/4"></div>
              <div class="h-3 bg-gray-100 rounded w-full"></div>
            </div>
          </div>
        </div>

        <div v-else-if="filteredFormations.length === 0" class="text-center py-16 text-gray-400">
          Aucune formation disponible pour ce niveau.
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7">
          <div v-for="(f, i) in filteredFormations" :key="f.id"
            class="bg-white rounded-2xl shadow-md card-hover overflow-hidden reveal relative"
            :class="i % 3 ? 'd' + (i % 3) : ''">

            <!-- Boutons admin -->
            <div v-if="authStore.isAdmin" class="absolute top-2 right-2 z-10 flex gap-1.5">
              <button @click.stop="openModal(f)"
                class="w-7 h-7 rounded-full bg-white/90 flex items-center justify-center shadow hover:bg-blue-50 transition" title="Modifier">
                <svg class="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931z"/>
                </svg>
              </button>
              <button @click.stop="deleteFormation(f.id)"
                class="w-7 h-7 rounded-full bg-white/90 flex items-center justify-center shadow hover:bg-red-50 transition" title="Supprimer">
                <svg class="w-3.5 h-3.5 text-red-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/>
                </svg>
              </button>
            </div>

            <div class="relative overflow-hidden" style="height:192px">
              <img :src="f.image_url || 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=700&q=75'"
                   :alt="f.titre" class="f-img-inner w-full h-full object-cover"/>
              <div class="absolute inset-0" style="background:linear-gradient(to bottom,transparent 40%,rgba(11,31,58,.6))"></div>
              <span class="absolute top-3.5 left-3.5 px-3 py-1 rounded-full text-xs font-bold tracking-wider text-white uppercase"
                    :style="{ background: f.couleur }">{{ f.niveau }}</span>
              <span v-if="f.duree" class="absolute bottom-3 right-3 text-white font-bold text-xs bg-black/30 px-2.5 py-0.5 rounded-full">{{ f.duree }}</span>
            </div>
            <div class="p-7">
              <h3 class="font-serif text-base mb-2">{{ f.titre }}</h3>
              <p class="text-gray-400 text-xs leading-relaxed mb-3.5">{{ f.description }}</p>
              <div class="flex flex-wrap gap-1.5 mb-3.5">
                <span v-for="p in (f.matieres || [])" :key="p"
                  class="px-2.5 py-1 rounded-full text-xs font-medium" style="background:rgba(212,168,83,.1)">{{ p }}</span>
              </div>
              <div v-if="f.nb_eleves_classe || f.taux_reussite || f.nb_debouches"
                class="grid grid-cols-3 rounded-xl text-center py-3.5 mb-3.5" style="background:#FAF7F2">
                <div>
                  <div class="text-base font-black text-gold">{{ f.nb_eleves_classe || '–' }}</div>
                  <div class="text-xs text-gray-400 mt-0.5">Élèves/cl.</div>
                </div>
                <div class="border-x border-gray-200">
                  <div class="text-base font-black text-teal">{{ f.taux_reussite || '–' }}</div>
                  <div class="text-xs text-gray-400 mt-0.5">Réussite</div>
                </div>
                <div>
                  <div class="text-base font-black text-navy">{{ f.nb_debouches || '–' }}</div>
                  <div class="text-xs text-gray-400 mt-0.5">Débouchés</div>
                </div>
              </div>
              <div v-if="(f.debouches || []).length" class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Débouchés</div>
              <ul class="mb-5">
                <li v-for="d in (f.debouches || [])" :key="d" class="flex items-center gap-2 text-xs text-gray-500 mb-1.5">
                  <span class="text-teal font-bold flex-shrink-0">✓</span> {{ d }}
                </li>
              </ul>
              <div class="flex gap-2.5">
                <router-link to="/admission" class="btn-gold flex-1 py-2 rounded-full text-xs font-semibold text-center no-underline">S'inscrire</router-link>
                <button class="btn-outline flex-1 py-2 rounded-full text-xs font-semibold">En savoir +</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ MODAL Admin ════════════════════════════════════ -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="showModal = false">
        <div class="bg-white rounded-2xl w-full max-w-2xl shadow-2xl max-h-[90vh] overflow-y-auto">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h2 class="text-base font-serif font-semibold text-gray-800">{{ editing ? 'Modifier la formation' : 'Nouvelle formation' }}</h2>
            <button @click="showModal = false" class="text-gray-400 hover:text-gray-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="px-6 py-5 space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Niveau *</label>
                <select v-model="form.niveau_id" @change="onNiveauChange"
                  class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition">
                  <option value="">-- Choisir --</option>
                  <option v-for="n in niveau_global" :key="n.id" :value="n.id">{{ n.name }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Titre *</label>
                <input v-model="form.titre" type="text" placeholder="Ex: Cycle Fondamental" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition"/>
              </div>
            </div>

            <!-- Faculté — visible seulement si niveau = Universitaire -->
            <div v-if="isUniversitaire">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Faculté *</label>
              <select v-model="form.faculte_id"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition">
                <option value="">-- Choisir une faculté --</option>
                <option v-for="f in faculte" :key="f.id" :value="f.id">{{ f.nom }}</option>
              </select>
            </div>
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Durée</label>
                <input v-model="form.duree" type="text" placeholder="Ex: 6 ans" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition"/>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Couleur</label>
                <input v-model="form.couleur" type="color" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition h-10 p-1"/>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Ordre</label>
                <input v-model.number="form.ordre" type="number" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition"/>
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Description</label>
              <textarea v-model="form.description" rows="3" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition resize-none" placeholder="Description de la formation..."/>
            </div>
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Élèves/classe</label>
                <input v-model="form.nb_eleves_classe" type="text" placeholder="25" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition"/>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Taux réussite</label>
                <input v-model="form.taux_reussite" type="text" placeholder="98%" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition"/>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Nb débouchés</label>
                <input v-model="form.nb_debouches" type="text" placeholder="15+" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition"/>
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Matières (une par ligne)</label>
              <textarea v-model="matieresText" rows="3" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition resize-none font-mono text-xs" placeholder="Français&#10;Mathématiques&#10;Sciences"/>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Débouchés (un par ligne)</label>
              <textarea v-model="debouchesText" rows="3" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition resize-none font-mono text-xs" placeholder="Entrée en 6ème&#10;Maîtrise du français"/>
            </div>
            <!-- Image -->
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Image</label>
              <div v-if="imagePreview" class="mb-2 rounded-xl overflow-hidden h-32">
                <img :src="imagePreview" class="w-full h-full object-cover"/>
              </div>
              <label class="flex items-center gap-2 cursor-pointer px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg hover:border-amber-400 transition">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
                </svg>
                <span class="text-xs text-gray-500">{{ imageFile ? imageFile.name : 'Choisir une image' }}</span>
                <input type="file" accept="image/*" class="hidden" @change="handleImage"/>
              </label>
              <div class="mt-1">
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Ou URL d'image</label>
                <input v-model="form.image_url" type="text" placeholder="https://…" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:border-amber-400 transition"/>
              </div>
            </div>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="form.is_published" class="w-4 h-4"/>
              <span class="text-sm text-gray-700">Publier</span>
            </label>
          </div>
          <div class="flex items-center justify-end gap-3 px-6 py-4 border-t">
            <button @click="showModal = false" class="px-4 py-2 text-sm text-gray-500 hover:text-gray-800 transition">Annuler</button>
            <button @click="save" :disabled="saving"
              class="px-5 py-2 text-sm font-semibold text-white rounded-full disabled:opacity-50 transition"
              style="background:#D4A853">
              {{ saving ? 'Enregistrement…' : (editing ? 'Modifier' : 'Créer') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ══ PÉDAGOGIE ══════════════════════════════════════ -->
    <div style="background:linear-gradient(135deg,#0B1F3A,#1a3a5c);padding:80px 0">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center reveal mb-12">
          <p class="text-xs tracking-widest uppercase font-bold text-gold">Notre Pédagogie</p>
          <div class="gold-line mx mt-3.5 mb-3"></div>
          <h2 class="font-serif text-white text-3xl mt-1">Une approche qui fait la différence</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div class="reveal-l">
            <div v-for="p in PEDA" :key="p.t" class="flex gap-4 items-start mb-7">
              <div
                class="rounded-2xl flex items-center justify-center text-xl flex-shrink-0"
                :style="{ background: p.bg, width: '48px', height: '48px' }"
              >{{ p.i }}</div>
              <div>
                <h3 class="text-white text-sm font-bold mb-1.5 font-serif">{{ p.t }}</h3>
                <p class="text-xs leading-relaxed" style="color:rgba(255,255,255,.55)">{{ p.d }}</p>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3 reveal-r">
            <div
              v-for="s in PEDA_STATS"
              :key="s.n"
              class="text-center rounded-2xl p-6"
              style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1)"
            >
              <span class="text-gold text-2xl font-black block mb-1">{{ s.n }}</span>
              <span class="text-xs" style="color:rgba(255,255,255,.6)">{{ s.l }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ CTA ════════════════════════════════════════════ -->
    <section class="py-20 text-center">
      <div class="max-w-6xl mx-auto px-6 reveal">
        <p class="text-xs tracking-widest uppercase font-bold text-gold">Prêt à commencer ?</p>
        <div class="gold-line mx mt-3.5 mb-3"></div>
        <h2 class="font-serif text-3xl my-2">Rejoignez-nous dès cette année</h2>
        <p class="text-gray-400 mb-8">Inscriptions 2025–2026 ouvertes. Déposez votre dossier en 10 minutes.</p>
        <router-link to="/admission" class="btn-gold inline-flex items-center gap-2 px-8 py-3.5 rounded-full font-semibold no-underline">
          Déposer ma candidature →
        </router-link>
      </div>
    </section>

    <!-- ══ MODAL atout ════════════════════════════════════ -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showAtoutItemModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="showAtoutItemModal = false">
        <div class="bg-white rounded-2xl w-full max-w-sm shadow-2xl">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h2 class="text-sm font-semibold text-gray-800">{{ editingAtoutIdx !== null ? 'Modifier l\'atout' : 'Nouvel atout' }}</h2>
            <button @click="showAtoutItemModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
          <div class="px-6 py-5 space-y-3">
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Icône</label>
              <input v-model="atoutItemForm.i" type="text" placeholder="👨‍🏫"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"/>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Titre</label>
              <input v-model="atoutItemForm.t" type="text" placeholder="Enseignants certifiés"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"/>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Description</label>
              <textarea v-model="atoutItemForm.d" rows="2" placeholder="100% titulaires d'un Master…"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400 resize-none"/>
            </div>
          </div>
          <div class="flex justify-end gap-3 px-6 py-4 border-t">
            <button @click="showAtoutItemModal = false" class="px-4 py-2 text-sm text-gray-500 hover:text-gray-800">Annuler</button>
            <button @click="saveAtoutItem" :disabled="savingAtout"
              class="px-5 py-2 text-sm font-semibold text-white rounded-full disabled:opacity-50"
              style="background:#D4A853">
              {{ savingAtout ? '…' : (editingAtoutIdx !== null ? 'Modifier' : 'Ajouter') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { initReveal } from '@/composables/useReveal.js'
import { useAuthStore } from '@/stores/auth'
import { useSchoolStore, useSchoolStoreInfo } from '@/stores/schoolStore'
import { storeToRefs } from 'pinia'
import axios from 'axios'
import Swal from 'sweetalert2'

const url = import.meta.env.VITE_APP_BASE_URL
const authStore  = useAuthStore()
const schoolInfo = useSchoolStoreInfo()
const { niveau_global, faculte } = storeToRefs(schoolInfo)

// ── Formations dynamiques ─────────────────────────────────────────────────
const formations       = ref([])
const loadingFormations= ref(false)
const showModal        = ref(false)
const editing          = ref(null)
const saving           = ref(false)
const imageFile        = ref(null)
const imagePreview     = ref(null)
const matieresText     = ref('')
const debouchesText    = ref('')

const emptyForm = () => ({
  niveau: '', niveau_id: '', faculte_id: '',
  titre: '', duree: '', couleur: '#3b82f6', image_url: '',
  description: '', nb_eleves_classe: '', taux_reussite: '', nb_debouches: '',
  matieres: [], debouches: [], ordre: 0, is_published: true
})
const form = ref(emptyForm())

// Niveaux qui nécessitent une faculté
const NEED_FACULTE = ['universitaire', 'technique']
const isUniversitaire = computed(() => {
  if (!form.value.niveau_id) return false
  const n = niveau_global.value.find(n => n.id === form.value.niveau_id)
  return NEED_FACULTE.some(k => n?.name?.toLowerCase().includes(k))
})

const onNiveauChange = () => {
  const n = niveau_global.value.find(n => n.id === form.value.niveau_id)
  form.value.niveau = n?.name ?? ''
  if (!isUniversitaire.value) form.value.faculte_id = ''
}

const fetchFormations = async () => {
  loadingFormations.value = true
  try {
    const endpoint = authStore.isAdmin ? `${url}/formations/all` : `${url}/formations/`
    const { data } = await axios.get(endpoint)
    formations.value = data
  } catch (e) { console.error('[Formations]', e) }
  finally { loadingFormations.value = false }
}

// ── Filtres ───────────────────────────────────────────────────────────────
const F_LEVELS    = computed(() => ['Tous', ...new Set(formations.value.map(f => f.niveau))])
const currentLevel= ref('Tous')

const filteredFormations = computed(() =>
  currentLevel.value === 'Tous'
    ? formations.value
    : formations.value.filter(f => f.niveau === currentLevel.value)
)

// ── Modal ─────────────────────────────────────────────────────────────────
const openModal = (f = null) => {
  editing.value    = f
  imageFile.value  = null
  imagePreview.value = f?.image_url ?? null
  matieresText.value = (f?.matieres  ?? []).join('\n')
  debouchesText.value= (f?.debouches ?? []).join('\n')
  form.value = f
    ? { niveau: f.niveau, niveau_id: f.niveau_id ?? '', faculte_id: f.faculte_id ?? '',
        titre: f.titre, duree: f.duree ?? '', couleur: f.couleur ?? '#3b82f6',
        image_url: f.image_url ?? '', description: f.description ?? '',
        nb_eleves_classe: f.nb_eleves_classe ?? '', taux_reussite: f.taux_reussite ?? '',
        nb_debouches: f.nb_debouches ?? '', matieres: f.matieres ?? [],
        debouches: f.debouches ?? [], ordre: f.ordre ?? 0, is_published: f.is_published }
    : emptyForm()
  showModal.value = true
}

const handleImage = (e) => {
  const file = e.target.files[0]
  if (!file) return
  imageFile.value    = file
  imagePreview.value = URL.createObjectURL(file)
}

const save = async () => {
  if (!form.value.niveau_id || !form.value.titre) {
    Swal.fire({ icon: 'warning', title: 'Niveau et titre requis', background: '#fff' }); return
  }
  if (isUniversitaire.value && !form.value.faculte_id) {
    Swal.fire({ icon: 'warning', title: 'Faculté requise pour un niveau universitaire', background: '#fff' }); return
  }
  form.value.matieres  = matieresText.value.split('\n').map(s => s.trim()).filter(Boolean)
  form.value.debouches = debouchesText.value.split('\n').map(s => s.trim()).filter(Boolean)
  saving.value = true
  try {
    let id
    if (editing.value) {
      await axios.put(`${url}/formations/${editing.value.id}`, form.value)
      id = editing.value.id
    } else {
      const { data } = await axios.post(`${url}/formations/`, form.value)
      id = data.id
    }
    if (imageFile.value && id) {
      const fd = new FormData()
      fd.append('file', imageFile.value)
      await axios.post(`${url}/formations/${id}/upload-image`, fd)
    }
    showModal.value = false
    await fetchFormations()
  } catch (e) {
    const detail = e.response?.data?.detail
    Swal.fire({ icon: 'error', title: 'Erreur', text: Array.isArray(detail) ? detail.map(d=>d.msg).join(', ') : (detail||'Erreur') })
  } finally { saving.value = false }
}

const deleteFormation = async (id) => {
  const res = await Swal.fire({ title: 'Supprimer cette formation ?', icon: 'warning', showCancelButton: true,
    confirmButtonColor: '#ef4444', cancelButtonColor: '#6b7280',
    confirmButtonText: 'Supprimer', cancelButtonText: 'Annuler' })
  if (!res.isConfirmed) return
  try { await axios.delete(`${url}/formations/${id}`); await fetchFormations() }
  catch (e) { Swal.fire({ icon: 'error', title: 'Erreur', text: e.response?.data?.detail || 'Erreur' }) }
}

// ── Atouts dynamiques ─────────────────────────────────────────────────────
const ATOUTS_DEFAULT = [
  { i: '👨‍🏫', t: 'Enseignants certifiés',  d: "100% titulaires d'un Master ou d'une agrégation." },
  { i: '🏫',  t: 'Petits groupes',          d: '25 élèves max pour un suivi individualisé.' },
  { i: '💻',  t: 'Équipements modernes',    d: 'Salles numériques, labos, bibliothèque, coworking.' },
  { i: '🤝',  t: 'Réseau alumni',           d: "3 500+ anciens dans les meilleures entreprises." },
]
const atoutsSection = ref(null)
// Fallback sur les données statiques si l'API n'a rien retourné
const ATOUTS = computed(() => atoutsSection.value?.items?.length ? atoutsSection.value.items : ATOUTS_DEFAULT)
// Visible par défaut — masquée SEULEMENT si l'admin l'a explicitement cachée
const showingAtouts = computed(() => {
  if (!atoutsSection.value) return true               // pas encore chargé → visible
  return atoutsSection.value.is_visible !== false || authStore.isAdmin
})

const fetchAtouts = async () => {
  try {
    const endpoint = authStore.isAdmin
      ? `${url}/page-sections/formations/all`
      : `${url}/page-sections/formations`
    const { data } = await axios.get(endpoint)
    atoutsSection.value = data.find(s => s.section_key === 'formation_atouts') ?? null
  } catch (e) { console.error('[Formations] atouts:', e) }
}

const openAtoutItemEdit = (idx = null) => {
  editingAtoutIdx.value = idx
  atoutItemForm.value = idx !== null
    ? { ...atoutsSection.value.items[idx] }
    : { i: '', t: '', d: '' }
  showAtoutItemModal.value = true
}

const saveAtoutItem = async () => {
  if (!atoutsSection.value) return
  savingAtout.value = true
  try {
    const items = [...(atoutsSection.value.items || [])]
    if (editingAtoutIdx.value !== null) items[editingAtoutIdx.value] = atoutItemForm.value
    else items.push(atoutItemForm.value)
    await axios.put(`${url}/page-sections/${atoutsSection.value.id}`, { items })
    showAtoutItemModal.value = false
    await fetchAtouts()
  } catch (e) { console.error(e) }
  finally { savingAtout.value = false }
}

const deleteAtoutItem = async (idx) => {
  const items = [...atoutsSection.value.items]
  items.splice(idx, 1)
  await axios.put(`${url}/page-sections/${atoutsSection.value.id}`, { items })
  await fetchAtouts()
}

const toggleAtouts = async () => {
  await axios.patch(`${url}/page-sections/${atoutsSection.value.id}/toggle`)
  await fetchAtouts()
}

const showAtoutItemModal = ref(false)
const atoutItemForm      = ref({ i: '', t: '', d: '' })
const editingAtoutIdx    = ref(null)
const savingAtout        = ref(false)
const PEDA = [
  { i: '🔬', t: 'Apprentissage par projets',    d: "Des projets interdisciplinaires ancrent les savoirs dans des contextes réels.",    bg: 'rgba(212,168,83,.2)' },
  { i: '🧠', t: 'Différenciation pédagogique', d: "L'enseignement est adapté au profil d'apprentissage de chaque élève.",             bg: 'rgba(26,122,110,.2)' },
  { i: '📱', t: 'Outils numériques intégrés',  d: 'Tablettes, logiciels éducatifs et classes hybrides au quotidien.',                  bg: 'rgba(59,130,246,.2)' },
  { i: '🎯', t: 'Suivi individualisé',         d: 'Entretiens trimestriels élève-prof-parent pour garantir la progression.',           bg: 'rgba(139,92,246,.2)' },
]
const PEDA_STATS = [
  { n: '20 min', l: 'Suivi indiv./sem./élève' },
  { n: '3×',     l: 'Entretiens bilan/an' },
  { n: '100%',   l: 'Profs certifiés/agrégés' },
  { n: '4.9/5',  l: 'Satisfaction parents 2024' },
]

onMounted(() => { window.scrollTo(0, 0); Promise.all([fetchFormations(), fetchAtouts()]).then(() => initReveal()) })
watch(currentLevel, () => initReveal())
</script>


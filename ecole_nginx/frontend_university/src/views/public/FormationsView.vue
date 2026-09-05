<template>
  <div>
    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:58vh;min-height:380px">
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
          Des programmes rigoureux et innovants, conçus pour préparer chaque étudiant à un avenir brillant.
        </p>
      </div>
    </div>

    <GenericSection v-for="gs in genericSectionsInZone(5)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="formations"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

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
              <div class="text-gray-500 text-xs leading-relaxed">{{ a.d }}</div>
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

    <GenericSection v-for="gs in genericSectionsInZone(45)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="formations"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <!-- ══ PROGRAMMES OFFERTS ══════════════════════════════ -->
    <section class="py-10">
      <div class="max-w-6xl mx-auto px-6">
        <h2 class="font-serif text-3xl text-center mb-14 reveal" style="color:#D4A853">Programmes Offerts.</h2>

        <!-- Premier cycle -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-10 items-start mb-20 reveal">
          <img src="/images/iusth-sciences-infirmieres.webp" alt="Étudiantes de l'IUSTH en sciences infirmières"
               class="w-full rounded-2xl object-cover" style="max-height:420px;box-shadow:0 16px 48px rgba(11,31,58,.15)" loading="lazy"/>
          <div>
            <p class="text-sm font-bold mb-4" style="color:#E8A020">Premier cycle : diplôme universitaire, licence et diplôme ingénieur.</p>
            <ul class="space-y-2 mb-6">
              <li v-for="f in facultesPremierCycle" :key="f.id" class="text-sm text-gray-700 underline underline-offset-2">{{ f.nom }}</li>
              <li v-if="!facultesPremierCycle.length" class="text-sm text-gray-500 italic">Facultés à renseigner dans l'admin.</li>
            </ul>
            <router-link to="/contact" class="btn-gold inline-block px-6 py-2.5 rounded-full text-sm font-semibold no-underline">Contactez-nous</router-link>
          </div>
        </div>

        <!-- Cycles courts -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-10 items-start reveal">
          <div class="relative w-full rounded-2xl overflow-hidden" style="aspect-ratio:4/3;max-height:420px;box-shadow:0 16px 48px rgba(11,31,58,.15)">
            <Transition name="carousel-fade">
              <img :key="cyclesCourtsIndex"
                   :src="CYCLES_COURTS_CAROUSEL[cyclesCourtsIndex].img"
                   :alt="CYCLES_COURTS_CAROUSEL[cyclesCourtsIndex].label"
                   class="absolute inset-0 w-full h-full object-cover" loading="lazy"/>
            </Transition>
            <div class="absolute bottom-0 left-0 right-0 px-4 pt-8 pb-3" style="background:linear-gradient(to top,rgba(11,31,58,.85),transparent)">
              <p class="text-white text-sm font-semibold m-0">{{ CYCLES_COURTS_CAROUSEL[cyclesCourtsIndex].label }}</p>
            </div>
            <div class="absolute bottom-3 right-4 flex gap-1.5">
              <button v-for="(item, i) in CYCLES_COURTS_CAROUSEL" :key="i"
                      @click="cyclesCourtsIndex = i"
                      :aria-label="`Voir ${item.label}`"
                      class="h-1.5 rounded-full transition-all duration-300"
                      :class="i === cyclesCourtsIndex ? 'w-5 bg-white' : 'w-1.5 bg-white/40 hover:bg-white/70'"></button>
            </div>
          </div>
          <div>
            <p class="text-sm font-bold mb-4" style="color:#E8A020">Cycles courts : diplôme technique</p>
            <ul class="space-y-2 mb-6">
              <li v-for="c in CYCLES_COURTS" :key="c" class="text-sm text-gray-700 underline underline-offset-2">{{ c }}</li>
            </ul>
            <router-link to="/admission" class="btn-gold inline-block px-6 py-2.5 rounded-full text-sm font-semibold no-underline">Admission</router-link>
          </div>
        </div>

        <!-- Gestion admin des fiches formation (images, descriptions détaillées)
             — reste disponible même si la grille publique en cartes a laissé
             place à la présentation ci-dessus. -->
        <div v-if="authStore.isAdmin" class="text-center mt-14">
          <button @click="openModal()"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold text-white"
            style="background:var(--gold,#D4A853)">
            + Gérer les fiches formation ({{ formations.length }})
          </button>
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
            <button @click="showModal = false" class="text-gray-500 hover:text-gray-600">
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
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Élèves/session-année</label>
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
                <img :src="imagePreview" alt="Aperçu de l'image de la formation" class="w-full h-full object-cover"/>
              </div>
              <label class="flex items-center gap-2 cursor-pointer px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg hover:border-amber-400 transition">
                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
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
        <div class="reveal mb-8">
          <h2 class="font-serif text-white text-2xl mb-2" style="color:#8fd694">Premier cycle</h2>
        </div>
        <div class="overflow-x-auto mb-14 reveal">
          <table class="w-full text-sm text-left text-white" style="border-collapse:collapse">
            <thead>
              <tr style="border-bottom:2px solid rgba(255,255,255,.25)">
                <th class="py-3 pr-4 font-semibold" style="color:rgba(255,255,255,.6)">Domaine d'études</th>
                <th class="py-3 pr-4 font-semibold" style="color:rgba(255,255,255,.6)">Libellé du diplôme</th>
                <th class="py-3 font-semibold" style="color:rgba(255,255,255,.6)">Durée des études (Ans)</th>
              </tr>
            </thead>
            <tbody>
              <tr style="border-bottom:1px solid rgba(255,255,255,.12)">
                <td rowspan="2" class="py-3 pr-4 align-top">Sciences</td>
                <td class="py-3 pr-4">Licence en sciences infirmières</td>
                <td class="py-3">4</td>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,.12)">
                <td class="py-3 pr-4">Licence en sciences administratives, comptabilité et de gestion</td>
                <td class="py-3">4</td>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,.12)">
                <td rowspan="3" class="py-3 pr-4 align-top">Génie</td>
                <td class="py-3 pr-4">Diplôme d'ingénieur Agronome</td>
                <td class="py-3">5</td>
              </tr>
              <tr style="border-bottom:1px solid rgba(255,255,255,.12)">
                <td class="py-3 pr-4">Diplôme d'ingénieur civil</td>
                <td class="py-3">5</td>
              </tr>
              <tr>
                <td class="py-3 pr-4">Diplôme d'ingénieur en informatique</td>
                <td class="py-3">4</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="reveal mb-8">
          <h2 class="font-serif text-white text-2xl mb-2" style="color:#8fd694">Cycles courts : Diplôme ou attestation</h2>
        </div>
        <div class="overflow-x-auto reveal">
          <table class="w-full text-sm text-left text-white" style="border-collapse:collapse">
            <thead>
              <tr style="border-bottom:2px solid rgba(255,255,255,.25)">
                <th class="py-3 pr-4 font-semibold" style="color:rgba(255,255,255,.6)">Domaine</th>
                <th class="py-3 pr-4 font-semibold" style="color:rgba(255,255,255,.6)">Spécialisation</th>
                <th class="py-3 font-semibold" style="color:rgba(255,255,255,.6)">Grade offerts (ans) ou mois</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(c, i) in CYCLES_COURTS_TABLE" :key="c.spec" style="border-bottom:1px solid rgba(255,255,255,.12)">
                <td v-if="i === 0" :rowspan="CYCLES_COURTS_TABLE.length" class="py-2.5 pr-4 align-top">Technique</td>
                <td class="py-2.5 pr-4">{{ c.spec }}</td>
                <td class="py-2.5">{{ c.duree }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ══ CTA ════════════════════════════════════════════ -->
    <section class="py-20 text-center">
      <div class="max-w-6xl mx-auto px-6 reveal">
        <p class="text-xs tracking-widest uppercase font-bold text-gold">Prêt à commencer ?</p>
        <div class="gold-line mx mt-3.5 mb-3"></div>
        <h2 class="font-serif text-3xl my-2">Rejoignez-nous dès cette année</h2>
        <p class="text-gray-500 mb-8">Inscriptions 2026–2027 ouvertes. Déposez votre dossier en 10 minutes.</p>
        <router-link to="/admission" class="btn-gold inline-flex items-center gap-2 px-8 py-3.5 rounded-full font-semibold no-underline">
          Déposer ma candidature →
        </router-link>
      </div>
    </section>

    <GenericSection v-for="gs in genericSectionsInZone(95)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="formations"
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

    <!-- ══ MODAL atout ════════════════════════════════════ -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showAtoutItemModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="showAtoutItemModal = false">
        <div class="bg-white rounded-2xl w-full max-w-sm shadow-2xl">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h2 class="text-sm font-semibold text-gray-800">{{ editingAtoutIdx !== null ? 'Modifier l\'atout' : 'Nouvel atout' }}</h2>
            <button @click="showAtoutItemModal = false" class="text-gray-500 hover:text-gray-600">✕</button>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { initReveal } from '@/composables/useReveal.js'
import { useAuthStore } from '@/stores/auth'
import { useSchoolStore, useSchoolStoreInfo } from '@/stores/schoolStore'
import { storeToRefs } from 'pinia'
import axios from 'axios'
import Swal from 'sweetalert2'
import GenericSection from '@/components/GenericSection.vue'
import { usePageSections, LAYOUT_TEMPLATES } from '@/composables/usePageSections.js'

const url = import.meta.env.VITE_APP_BASE_URL
const authStore  = useAuthStore()
const schoolInfo = useSchoolStoreInfo()
const { niveau_global, faculte } = storeToRefs(schoolInfo)

// f.image_url stocké par l'API est un chemin relatif ("/static/uploads/...")
// — se résoudrait contre l'origine du frontend, pas celle de l'API (deux
// domaines différents en déploiement web), d'où l'image cassée sinon.
const apiOrigin = url.replace(/\/api\/v1\/?$/, '')
const toAbsoluteUrl = (path) => {
  if (!path) return null
  return path.startsWith('http') ? path : `${apiOrigin}${path}`
}

// ── Blocs génériques ajoutés librement (voir HomeView.vue pour le détail) ──
const {
  genericSections, genericSectionsInZone, createGenericSection, fetchSections: fetchGenericSections,
  toggleSection: toggleGenericSection, deleteSection: deleteGenericSection, zones,
} = usePageSections('formations')
const showAddBlockModal = ref(false)
const pendingZone = ref(null)
const closeAddBlockModal = () => { showAddBlockModal.value = false; pendingZone.value = null }
const pickBlockTemplate = async (tpl) => {
  const ok = await createGenericSection(tpl, pendingZone.value.ordre)
  if (ok) closeAddBlockModal()
}

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

// ── Modal ─────────────────────────────────────────────────────────────────
const openModal = (f = null) => {
  editing.value    = f
  imageFile.value  = null
  imagePreview.value = toAbsoluteUrl(f?.image_url) ?? null
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
// Facultés "Premier cycle" — depuis la table Faculte (mêmes données réelles
// que FacultesView.vue), pas une liste figée : reflète les vraies facultés
// actives saisies par l'admin (voir /facultes-publiques, filtré status=True).
const facultesPremierCycle = ref([])
const fetchFacultesPremierCycle = async () => {
  try {
    const { data } = await axios.get(`${url}/facultes-publiques`)
    facultesPremierCycle.value = data?.data ?? []
  } catch (e) { console.error('[Formations] facultés', e) }
}

// Cycles courts : spécialisations techniques (pas des Facultés à part
// entière — aucune table dédiée pour ça), voir iusth/Programmes offerts.docx.
const CYCLES_COURTS = [
  'Auxiliaire pharmacie', 'Technologie médicale', 'Technique agricole', 'Secourisme',
  'Assistance administrative', 'Informatique bureautique', 'Comptabilité Informatisée',
  'Elaboration et gestion de projet', 'Logiciels : Word, Excel et PowerPoint',
  "Outils technologiques et d'enquêtes", 'Langues : espagnol, Anglais et français',
]
// Même liste, avec la durée réelle par spécialisation (voir
// iusth/Programmes offerts.docx) — pour le tableau de "Notre Pédagogie".
const CYCLES_COURTS_TABLE = [
  { spec: 'Auxiliaire pharmacie',                        duree: '2 ans' },
  { spec: 'Technologie médicale',                        duree: '2 ans' },
  { spec: 'Technique agricole',                          duree: '3 ans' },
  { spec: 'Secourisme',                                  duree: '2 ans' },
  { spec: 'Assistance administrative',                   duree: '2 ans' },
  { spec: 'Informatique bureautique',                    duree: '2 ans' },
  { spec: 'Comptabilité Informatisée',                   duree: '2 ans' },
  { spec: 'Elaboration et gestion de projet',             duree: '6 mois' },
  { spec: 'Logiciels : Word, Excel et PowerPoint',        duree: '3 mois' },
  { spec: "Outils technologiques et d'enquêtes",          duree: '3 mois' },
  { spec: 'Langues : espagnol, Anglais et français',      duree: '6 mois' },
]

// Une image par spécialisation (aucune photo IUSTH dédiée par métier pour
// l'instant) — remplace l'unique image statique "Cycles courts" par un
// carrousel qui illustre chaque intitulé tour à tour.
const CYCLES_COURTS_CAROUSEL = [
  { label: 'Auxiliaire pharmacie', img: 'https://upload.wikimedia.org/wikipedia/commons/7/7b/Pharmacy_Technician_-_DPLA_-_bcbedfb68c26b09b38a75658488f3387.jpg' },
  { label: 'Technologie médicale', img: 'https://images.unsplash.com/photo-1748261348213-62f4c399bb72?w=1200&q=80&auto=format&fit=crop' },
  { label: 'Technique agricole', img: 'https://images.unsplash.com/photo-1759261158814-e5c651e30714?w=1200&q=80&auto=format&fit=crop' },
  { label: 'Secourisme', img: 'https://upload.wikimedia.org/wikipedia/commons/5/5a/CPR_training-01.jpg' },
  { label: 'Assistance administrative', img: 'https://images.unsplash.com/photo-1758874384556-cc2b9dcbb6e0?w=1200&q=80&auto=format&fit=crop' },
  { label: 'Informatique bureautique', img: 'https://images.unsplash.com/photo-1743834147172-37c12011b321?w=1200&q=80&auto=format&fit=crop' },
  { label: 'Comptabilité Informatisée', img: 'https://images.unsplash.com/photo-1709880945165-d2208c6ad2ec?w=1200&q=80&auto=format&fit=crop' },
  { label: 'Elaboration et gestion de projet', img: 'https://images.unsplash.com/photo-1677506048148-0c914dd8197b?w=1200&q=80&auto=format&fit=crop' },
  { label: 'Logiciels : Word, Excel et PowerPoint', img: 'https://images.unsplash.com/photo-1759752393975-7ca7b302fcc6?w=1200&q=80&auto=format&fit=crop' },
  { label: "Outils technologiques et d'enquêtes", img: 'https://images.unsplash.com/photo-1759661966728-4a02e3c6ed91?w=1200&q=80&auto=format&fit=crop' },
  { label: 'Langues : espagnol, Anglais et français', img: 'https://images.unsplash.com/photo-1758270704080-e3556e6794a7?w=1200&q=80&auto=format&fit=crop' },
]
const cyclesCourtsIndex = ref(0)
let cyclesCourtsTimer = null

onMounted(() => { window.scrollTo(0, 0); Promise.all([fetchFormations(), fetchAtouts(), fetchGenericSections(), fetchFacultesPremierCycle()]).then(() => initReveal())
  cyclesCourtsTimer = setInterval(() => {
    cyclesCourtsIndex.value = (cyclesCourtsIndex.value + 1) % CYCLES_COURTS_CAROUSEL.length
  }, 4000)
})
onUnmounted(() => clearInterval(cyclesCourtsTimer))
</script>

<style scoped>
.carousel-fade-enter-active,
.carousel-fade-leave-active {
  transition: opacity .6s ease;
}
.carousel-fade-enter-from,
.carousel-fade-leave-to {
  opacity: 0;
}
</style>


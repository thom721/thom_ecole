<template>
  <div>

    <!-- ══ HERO ══════════════════════════════════════════ -->
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
    <div v-if="sec('stats')?.is_visible !== false || authStore.isAdmin" class="bg-white relative" style="box-shadow:0 4px 30px rgba(11,37,69,.1)">
      <!-- overlay masqué -->
      <div v-if="authStore.isAdmin && !sec('stats')?.is_visible" class="absolute inset-0 bg-red-500/5 border-2 border-dashed border-red-300/40 z-10 pointer-events-none rounded"></div>
      <div v-if="authStore.isAdmin" class="absolute top-1 right-2 flex items-center gap-1 z-20">
        <span :class="['text-[10px] px-2 py-0.5 rounded-full font-medium', sectionBadgeClass(sec('stats'))]">{{ sec('stats')?.is_visible ? 'Visible' : 'Masqué' }}</span>
        <button @click="openItemEdit(sec('stats'))" class="p-1 rounded bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 text-xs" title="Ajouter stat">+</button>
        <button @click="toggleSection(sec('stats'))" class="p-1 rounded bg-gray-100 text-gray-500 hover:bg-gray-200 text-xs" title="Masquer/Afficher">👁</button>
        <button @click="deleteSection(sec('stats'))" class="p-1 rounded bg-red-50 text-red-400 hover:bg-red-100 text-xs" title="Supprimer">✕</button>
      </div>
      <div class="max-w-4xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4">
        <div v-for="(s, i) in STATS" :key="i" class="text-center py-8 reveal relative group" :style="i < 3 ? 'border-right:1px solid #E2E8F0' : ''">
          <div class="font-black leading-none mb-1" style="font-size:2.4rem;background:linear-gradient(135deg,#0B2545,#1A7A4A);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{{ s.n }}</div>
          <div class="text-xs text-gray-400 uppercase tracking-widest">{{ s.l }}</div>
          <div v-if="authStore.isAdmin" class="absolute top-1 right-1 hidden group-hover:flex gap-1">
            <button @click="openItemEdit(sec('stats'), i)" class="w-5 h-5 rounded bg-blue-500/15 text-blue-600 text-xs flex items-center justify-center hover:bg-blue-500/30">✎</button>
            <button @click="deleteItem(sec('stats'), i)" class="w-5 h-5 rounded bg-red-500/15 text-red-500 text-xs flex items-center justify-center hover:bg-red-500/30">✕</button>
          </div>
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
    <section v-if="sec('cycles')?.is_visible !== false || authStore.isAdmin" class="py-24 bg-white relative">
      <div v-if="authStore.isAdmin && !sec('cycles')?.is_visible" class="absolute inset-0 bg-red-500/5 border-2 border-dashed border-red-300/40 z-10 pointer-events-none"></div>
      <div v-if="authStore.isAdmin" class="absolute top-2 right-4 flex items-center gap-1 z-20">
        <span :class="['text-[10px] px-2 py-0.5 rounded-full font-medium', sectionBadgeClass(sec('cycles'))]">{{ sec('cycles')?.is_visible ? 'Visible' : 'Masqué' }}</span>
        <button @click="openItemEdit(sec('cycles'))" class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 text-xs">+ Cycle</button>
        <button @click="openSectionEdit(sec('cycles'))" class="px-2 py-0.5 rounded bg-blue-500/10 text-blue-600 hover:bg-blue-500/20 text-xs">Titres</button>
        <button @click="toggleSection(sec('cycles'))" class="p-1 rounded bg-gray-100 text-gray-500 text-xs">👁</button>
        <button @click="deleteSection(sec('cycles'))" class="p-1 rounded bg-red-50 text-red-400 text-xs">✕</button>
      </div>
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-14 reveal">
          <p class="text-xs font-extrabold tracking-widest uppercase mb-2" style="color:#E8A020">{{ sec('cycles')?.titre || 'Nos cycles' }}</p>
          <h2 class="font-serif" style="font-size:clamp(1.8rem,3vw,2.6rem);color:#0B2545">
            {{ sec('cycles')?.sous_titre || 'De la maternelle au baccalauréat' }}
          </h2>
        </div>
        <div class="grid md:grid-cols-3 gap-7">
          <div v-for="(c, i) in CYCLES" :key="i"
            class="relative rounded-2xl p-8 border-2 border-gray-100 overflow-hidden reveal transition-transform hover:-translate-y-1 group">
            <div class="absolute top-0 left-0 right-0 h-1 rounded-t-2xl" :style="{ background: c.color }"></div>
            <div class="text-4xl mb-2">{{ c.i }}</div>
            <div class="text-xs font-bold uppercase tracking-widest mb-2" :style="{ color: c.color }">{{ c.age }}</div>
            <h3 class="font-serif text-xl mb-2" style="color:#0B2545">{{ c.t }}</h3>
            <p class="text-gray-400 text-sm leading-relaxed mb-4">{{ c.d }}</p>
            <router-link to="/formations" class="text-sm font-bold no-underline" :style="{ color: c.color }">En savoir plus →</router-link>
            <div v-if="authStore.isAdmin" class="absolute top-2 right-2 hidden group-hover:flex gap-1">
              <button @click="openItemEdit(sec('cycles'), i)" class="w-6 h-6 rounded bg-blue-500/15 text-blue-600 text-xs flex items-center justify-center">✎</button>
              <button @click="deleteItem(sec('cycles'), i)" class="w-6 h-6 rounded bg-red-500/15 text-red-500 text-xs flex items-center justify-center">✕</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ ATOUTS ═════════════════════════════════════════ -->
    <section v-if="sec('features')?.is_visible !== false || authStore.isAdmin" class="py-24 bg-gray-50 relative">
      <div v-if="authStore.isAdmin && !sec('features')?.is_visible" class="absolute inset-0 bg-red-500/5 border-2 border-dashed border-red-300/40 z-10 pointer-events-none"></div>
      <div v-if="authStore.isAdmin" class="absolute top-2 right-4 flex items-center gap-1 z-20">
        <span :class="['text-[10px] px-2 py-0.5 rounded-full font-medium', sectionBadgeClass(sec('features'))]">{{ sec('features')?.is_visible ? 'Visible' : 'Masqué' }}</span>
        <button @click="openItemEdit(sec('features'))" class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 text-xs">+ Atout</button>
        <button @click="openSectionEdit(sec('features'))" class="px-2 py-0.5 rounded bg-blue-500/10 text-blue-600 text-xs">Titres</button>
        <button @click="toggleSection(sec('features'))" class="p-1 rounded bg-gray-200 text-gray-500 text-xs">👁</button>
        <button @click="deleteSection(sec('features'))" class="p-1 rounded bg-red-100 text-red-400 text-xs">✕</button>
      </div>
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-14 reveal">
          <p class="text-xs font-extrabold tracking-widest uppercase mb-2" style="color:#E8A020">{{ sec('features')?.titre || 'Nos atouts' }}</p>
          <h2 class="font-serif" style="font-size:clamp(1.8rem,3vw,2.6rem);color:#0B2545">{{ sec('features')?.sous_titre || 'Pourquoi choisir Le Mignon ?' }}</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="(f, i) in FEATURES" :key="i"
            class="rounded-2xl p-6 border border-gray-100 reveal transition-transform hover:-translate-y-1 relative group bg-white">
            <div class="text-3xl mb-3">{{ f.i }}</div>
            <h3 class="font-serif text-lg mb-2 text-gray-800">{{ f.t }}</h3>
            <p class="text-sm leading-relaxed text-gray-400">{{ f.d }}</p>
            <div v-if="authStore.isAdmin" class="absolute top-2 right-2 hidden group-hover:flex gap-1">
              <button @click="openItemEdit(sec('features'), i)" class="w-6 h-6 rounded bg-blue-500/15 text-blue-600 text-xs flex items-center justify-center">✎</button>
              <button @click="deleteItem(sec('features'), i)" class="w-6 h-6 rounded bg-red-500/15 text-red-500 text-xs flex items-center justify-center">✕</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ VIE SCOLAIRE ══════════════════════════════════ -->
    <section v-if="sec('activities')?.is_visible !== false || authStore.isAdmin" class="py-24 relative" style="background:#0B2545">
      <div v-if="authStore.isAdmin && !sec('activities')?.is_visible" class="absolute inset-0 border-2 border-dashed border-red-300/40 z-10 pointer-events-none" style="background:rgba(239,68,68,0.05)"></div>
      <div v-if="authStore.isAdmin" class="absolute top-2 right-4 flex items-center gap-1 z-20">
        <span :class="['text-[10px] px-2 py-0.5 rounded-full font-medium', sectionBadgeClass(sec('activities'))]">{{ sec('activities')?.is_visible ? 'Visible' : 'Masqué' }}</span>
        <button @click="openItemEdit(sec('activities'))" class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 text-xs">+ Activité</button>
        <button @click="openSectionEdit(sec('activities'))" class="px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 text-xs">Titres</button>
        <button @click="toggleSection(sec('activities'))" class="p-1 rounded bg-white/10 text-white/70 text-xs">👁</button>
        <button @click="deleteSection(sec('activities'))" class="p-1 rounded bg-red-500/20 text-red-300 text-xs">✕</button>
      </div>
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-12 reveal">
          <p class="text-xs font-extrabold tracking-widest uppercase mb-2" style="color:#E8A020">{{ sec('activities')?.titre || 'Vie scolaire' }}</p>
          <h2 class="font-serif text-white mb-2" style="font-size:clamp(1.8rem,3vw,2.6rem)">{{ sec('activities')?.sous_titre || "L'école, au-delà des cours" }}</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="(a, i) in ACTIVITIES" :key="i" class="relative rounded-2xl overflow-hidden reveal group" style="aspect-ratio:16/9">
            <img :src="a.img" :alt="a.t" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
            <div class="absolute inset-0" style="background:linear-gradient(to top,rgba(11,37,69,.85) 0%,transparent 60%)"></div>
            <div class="absolute bottom-0 left-0 right-0 p-5">
              <span class="inline-block mb-1.5 px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-widest" style="background:#E8A020;color:#fff">{{ a.tag }}</span>
              <h3 class="text-white font-serif text-lg m-0 leading-snug">{{ a.t }}</h3>
            </div>
            <div v-if="authStore.isAdmin" class="absolute top-2 right-2 hidden group-hover:flex gap-1 z-10">
              <button @click="openItemEdit(sec('activities'), i)" class="w-6 h-6 rounded bg-white/20 text-white text-xs flex items-center justify-center hover:bg-white/40">✎</button>
              <button @click="deleteItem(sec('activities'), i)" class="w-6 h-6 rounded bg-red-500/40 text-white text-xs flex items-center justify-center hover:bg-red-500/60">✕</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ TÉMOIGNAGES ═══════════════════════════════════ -->
    <section v-if="sec('testimonials')?.is_visible !== false || authStore.isAdmin" class="py-24 bg-white relative">
      <div v-if="authStore.isAdmin && !sec('testimonials')?.is_visible" class="absolute inset-0 bg-red-500/5 border-2 border-dashed border-red-300/40 z-10 pointer-events-none"></div>
      <div v-if="authStore.isAdmin" class="absolute top-2 right-4 flex items-center gap-1 z-20">
        <span :class="['text-[10px] px-2 py-0.5 rounded-full font-medium', sectionBadgeClass(sec('testimonials'))]">{{ sec('testimonials')?.is_visible ? 'Visible' : 'Masqué' }}</span>
        <button @click="openItemEdit(sec('testimonials'))" class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 text-xs">+ Témoignage</button>
        <button @click="openSectionEdit(sec('testimonials'))" class="px-2 py-0.5 rounded bg-blue-500/10 text-blue-600 text-xs">Titres</button>
        <button @click="toggleSection(sec('testimonials'))" class="p-1 rounded bg-gray-100 text-gray-500 text-xs">👁</button>
        <button @click="deleteSection(sec('testimonials'))" class="p-1 rounded bg-red-50 text-red-400 text-xs">✕</button>
      </div>
      <div class="max-w-5xl mx-auto px-6">
        <div class="text-center mb-14 reveal">
          <p class="text-xs font-extrabold tracking-widest uppercase mb-2" style="color:#E8A020">{{ sec('testimonials')?.titre || 'Témoignages' }}</p>
          <h2 class="font-serif" style="font-size:clamp(1.8rem,3vw,2.6rem);color:#0B2545">{{ sec('testimonials')?.sous_titre || 'Ce que disent les familles' }}</h2>
        </div>
        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="(t, i) in TESTIMONIALS" :key="i" class="bg-gray-50 rounded-2xl p-7 border border-gray-100 reveal transition-transform hover:-translate-y-1 relative group">
            <div class="text-5xl font-serif leading-none mb-2" style="color:#E8A020;line-height:1">"</div>
            <p class="text-sm text-gray-500 italic leading-relaxed mb-5">{{ t.t }}</p>
            <div class="flex items-center gap-3 pt-4 border-t border-gray-200">
              <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0 text-sm" style="background:linear-gradient(135deg,#0B2545,#1A7A4A)">
                {{ (t.n || '?').split(' ').map(w => w[0]).join('') }}
              </div>
              <div>
                <div class="text-sm font-bold" style="color:#0B2545">{{ t.n }}</div>
                <div class="text-xs text-gray-400">{{ t.r }}</div>
              </div>
              <div class="ml-auto text-xs" style="color:#E8A020">★★★★★</div>
            </div>
            <div v-if="authStore.isAdmin" class="absolute top-2 right-2 hidden group-hover:flex gap-1">
              <button @click="openItemEdit(sec('testimonials'), i)" class="w-6 h-6 rounded bg-blue-500/15 text-blue-600 text-xs flex items-center justify-center">✎</button>
              <button @click="deleteItem(sec('testimonials'), i)" class="w-6 h-6 rounded bg-red-500/15 text-red-500 text-xs flex items-center justify-center">✕</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ ACTUALITÉS ════════════════════════════════════ -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-5xl mx-auto px-6">
        <div class="flex items-center justify-between mb-8 reveal">
          <div>
            <p class="text-xs font-extrabold tracking-widest uppercase mb-1" style="color:#E8A020">Actualités</p>
            <h2 class="font-serif text-2xl" style="color:#0B2545">Vie de l'établissement</h2>
          </div>
          <router-link to="/evenements" class="text-sm font-semibold no-underline" style="color:#1A7A4A">Voir tout →</router-link>
        </div>
        <div class="grid md:grid-cols-3 gap-5">
          <div v-for="n in NEWS" :key="n.t" class="bg-white rounded-xl p-5 border border-gray-100 reveal hover:-translate-y-1 transition-transform">
            <div class="text-xs font-bold uppercase tracking-widest mb-2" style="color:#E8A020">{{ n.cat }}</div>
            <h4 class="text-sm font-semibold mb-2 leading-snug" style="color:#0B2545">{{ n.t }}</h4>
            <p class="text-xs text-gray-400">{{ n.date }}</p>
          </div>
        </div>
      </div>
    </section>

        <!-- ══ CTA ════════════════════════════════════════════ -->
    <section class="py-16 bg-white">
      <div class="max-w-5xl mx-auto px-6">
        <div class="relative overflow-hidden rounded-3xl py-20 px-10 reveal" style="background:linear-gradient(135deg,#0B2545,#1A7A4A)">
          <div class="absolute w-72 h-72 rounded-full -top-20 -right-16 opacity-10" style="background:#E8A020"></div>
          <div class="grid md:grid-cols-2 gap-10 items-center relative">
            <div>
              <p class="text-xs font-extrabold tracking-widest uppercase mb-3" style="color:#fde68a">Candidature 2025–2026</p>
              <h2 class="font-serif text-white mb-4" style="font-size:clamp(1.6rem,3vw,2.4rem)">
                Rejoindre<br />{{useSchoolInfo.school_info?.nom || 'Lekol 360'}}
              </h2>
              <p class="text-sm mb-0 leading-relaxed" style="color:rgba(255,255,255,.7)">
                Les dossiers de candidature pour l'année scolaire 2025–2026 sont ouverts.
                Consultez les conditions d'admission et déposez votre dossier en ligne.
              </p>
            </div>
            <div class="flex flex-col gap-3">
              <router-link to="/admission" class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-bold text-white no-underline text-center" style="background:#E8A020;box-shadow:0 4px 20px rgba(232,160,32,.4)">
                Déposer un dossier d'admission
                <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </router-link>
              <router-link to="/contact" class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-semibold text-white no-underline text-center" style="border:2px solid rgba(255,255,255,.4)">
                📞 Contacter l'administration
              </router-link>
              <p class="text-xs text-center mt-1" style="color:rgba(255,255,255,.4)">
                Du lundi au vendredi · {{ useSchoolInfo.school_info?.horaires || '8h00 – 16h00' }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ MODALS ADMIN ═══════════════════════════════════ -->

    <!-- Modal : titres de section -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showSectionModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="showSectionModal = false">
        <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h2 class="text-sm font-semibold text-gray-800">Modifier les titres — {{ editingSection?.section_key }}</h2>
            <button @click="showSectionModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
          <div class="px-6 py-5 space-y-4">
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Titre</label>
              <input v-model="sectionForm.titre" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"/>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Sous-titre</label>
              <input v-model="sectionForm.sous_titre" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"/>
            </div>
          </div>
          <div class="flex justify-end gap-3 px-6 py-4 border-t">
            <button @click="showSectionModal = false" class="px-4 py-2 text-sm text-gray-500 hover:text-gray-800">Annuler</button>
            <button @click="saveSectionMeta" :disabled="savingSection"
              class="px-5 py-2 text-sm font-semibold text-white rounded-full disabled:opacity-50" style="background:#D4A853">
              {{ savingSection ? '…' : 'Enregistrer' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal : éditeur d'item -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showItemModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="showItemModal = false">
        <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h2 class="text-sm font-semibold text-gray-800">
              {{ editingItemIdx !== null ? 'Modifier' : 'Ajouter' }} — {{ editingSection?.section_key }}
            </h2>
            <button @click="showItemModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
          <div class="px-6 py-5 space-y-4">
            <div v-for="f in currentFields" :key="f.k">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">{{ f.l }}</label>
              <textarea v-if="f.k === 't' && editingSection?.section_key === 'testimonials'"
                v-model="itemForm[f.k]" rows="3" :placeholder="f.p"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400 resize-none"/>
              <input v-else v-model="itemForm[f.k]" type="text" :placeholder="f.p"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"/>
            </div>
          </div>
          <div class="flex justify-end gap-3 px-6 py-4 border-t">
            <button @click="showItemModal = false" class="px-4 py-2 text-sm text-gray-500 hover:text-gray-800">Annuler</button>
            <button @click="saveItem" :disabled="savingItem"
              class="px-5 py-2 text-sm font-semibold text-white rounded-full disabled:opacity-50" style="background:#D4A853">
              {{ savingItem ? '…' : (editingItemIdx !== null ? 'Modifier' : 'Ajouter') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { onMounted, ref, computed, nextTick } from 'vue'
import { initReveal } from '@/composables/useReveal.js'
import { useSchoolStoreInfo } from '@/stores/schoolStore'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import Swal from 'sweetalert2'

const url          = import.meta.env.VITE_APP_BASE_URL
const useSchoolInfo= useSchoolStoreInfo()
const authStore    = useAuthStore()

// ── Actualités récentes ───────────────────────────────────────────────────
const NEWS = ref([])
const fetchNews = async () => {
  try {
    const { data } = await axios.get(`${url}/news/`)
    NEWS.value = data
      .filter(n => n.is_published)
      .slice(0, 3)
      .map(n => ({
        t: n.title,
        cat: n.category?.name ?? 'Actualité',
        date: n.published_at
          ? new Date(n.published_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
          : new Date(n.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
      }))
  } catch { /* silencieux — section reste vide */ }
}

// ── Sections chargées depuis l'API ────────────────────────────────────────
const sections     = ref([])
const loading      = ref(false)

const sec = (key) => sections.value.find(s => s.section_key === key)

const STATS       = computed(() => sec('stats')?.items        ?? [])
const CYCLES      = computed(() => sec('cycles')?.items       ?? [])
const FEATURES    = computed(() => sec('features')?.items     ?? [])
const ACTIVITIES  = computed(() => sec('activities')?.items   ?? [])
const TESTIMONIALS= computed(() => sec('testimonials')?.items ?? [])
const VALUES      = computed(() => sec('values')?.items       ?? [])

const fetchSections = async () => {
  loading.value = true
  try {
    const endpoint = authStore.isAdmin
      ? `${url}/page-sections/home/all`
      : `${url}/page-sections/home`
    const { data } = await axios.get(endpoint)
    sections.value = data
  } catch (e) { console.error('[Home] sections:', e) }
  finally {
    loading.value = false
    await nextTick(); initReveal()
  }
}

// ── CRUD sections ─────────────────────────────────────────────────────────
const editingSection = ref(null)
const showSectionModal = ref(false)
const sectionForm    = ref({ items: [] })
const savingSection  = ref(false)
const editingItemIdx = ref(null)
const itemForm       = ref({})
const showItemModal  = ref(false)
const savingItem     = ref(false)

const openSectionEdit = (s) => {
  editingSection.value  = s
  sectionForm.value     = { titre: s.titre, sous_titre: s.sous_titre, items: JSON.parse(JSON.stringify(s.items || [])) }
  showSectionModal.value = true
}

const toggleSection = async (s) => {
  try {
    await axios.patch(`${url}/page-sections/${s.id}/toggle`)
    await fetchSections()
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Erreur', text: e.response?.data?.detail || 'Erreur', background: '#0f1117', color: '#e8eaf0' })
  }
}

const deleteSection = async (s) => {
  const res = await Swal.fire({
    title: `Supprimer la section "${s.titre || s.section_key}" ?`,
    text: 'Cette action est irréversible.',
    icon: 'warning', showCancelButton: true,
    confirmButtonColor: '#ef4444', cancelButtonColor: '#374151',
    confirmButtonText: 'Supprimer', cancelButtonText: 'Annuler',
    background: '#0f1117', color: '#e8eaf0'
  })
  if (!res.isConfirmed) return
  try {
    await axios.delete(`${url}/page-sections/${s.id}`)
    await fetchSections()
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Erreur', text: e.response?.data?.detail || 'Erreur', background: '#0f1117', color: '#e8eaf0' })
  }
}

const saveSectionMeta = async () => {
  if (!editingSection.value) return
  savingSection.value = true
  try {
    await axios.put(`${url}/page-sections/${editingSection.value.id}`, {
      titre: sectionForm.value.titre,
      sous_titre: sectionForm.value.sous_titre,
    })
    showSectionModal.value = false
    await fetchSections()
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Erreur', text: e.response?.data?.detail || 'Erreur', background: '#0f1117', color: '#e8eaf0' })
  } finally { savingSection.value = false }
}

// ── CRUD items ────────────────────────────────────────────────────────────
const openItemEdit = (s, idx = null) => {
  editingSection.value = s
  editingItemIdx.value = idx
  itemForm.value = idx !== null
    ? JSON.parse(JSON.stringify(s.items[idx]))
    : {}
  showItemModal.value = true
}

const saveItem = async () => {
  if (!editingSection.value) return
  savingItem.value = true
  try {
    const items = JSON.parse(JSON.stringify(editingSection.value.items || []))
    if (editingItemIdx.value !== null) {
      items[editingItemIdx.value] = itemForm.value
    } else {
      items.push(itemForm.value)
    }
    await axios.put(`${url}/page-sections/${editingSection.value.id}`, { items })
    showItemModal.value = false
    await fetchSections()
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Erreur', text: e.response?.data?.detail || 'Erreur', background: '#0f1117', color: '#e8eaf0' })
  } finally { savingItem.value = false }
}

const deleteItem = async (s, idx) => {
  const res = await Swal.fire({
    title: 'Supprimer cet élément ?', icon: 'warning', showCancelButton: true,
    confirmButtonColor: '#ef4444', cancelButtonColor: '#374151',
    confirmButtonText: 'Supprimer', cancelButtonText: 'Annuler',
    background: '#0f1117', color: '#e8eaf0'
  })
  if (!res.isConfirmed) return
  const items = [...s.items]
  items.splice(idx, 1)
  await axios.put(`${url}/page-sections/${s.id}`, { items })
  await fetchSections()
}

// Champs disponibles par type de section
const FIELDS = {
  stats:        [{ k:'n', l:'Valeur', p:'1 200+' }, { k:'l', l:'Label', p:'Élèves inscrits' }],
  cycles:       [{ k:'i', l:'Icône', p:'🌱' }, { k:'t', l:'Titre', p:'Préscolaire' }, { k:'age', l:'Tranche d\'âge', p:'3-5 ans' }, { k:'color', l:'Couleur', p:'#10B981' }, { k:'d', l:'Description', p:'...' }],
  features:     [{ k:'i', l:'Icône', p:'👨‍🏫' }, { k:'t', l:'Titre', p:'...' }, { k:'d', l:'Description', p:'...' }],
  activities:   [{ k:'t', l:'Titre', p:'Sport & EPS' }, { k:'tag', l:'Tag', p:'Parascolaire' }, { k:'img', l:'URL image', p:'https://...' }, { k:'desc', l:'Description', p:'...' }],
  testimonials: [{ k:'n', l:'Nom', p:'Jean Dupont' }, { k:'r', l:'Rôle', p:'Parent d\'élève' }, { k:'t', l:'Témoignage', p:'...' }],
  values:       [{ k:'i', l:'Icône', p:'🎯' }, { k:'t', l:'Valeur', p:'Excellence' }],
}

const currentFields = computed(() => FIELDS[editingSection.value?.section_key] ?? [])

// ── Admin bar helper ──────────────────────────────────────────────────────
const sectionBadgeClass = (s) => s?.is_visible ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'

onMounted(async () => {
  window.scrollTo(0, 0)
  await Promise.all([fetchSections(), fetchNews()])
})
</script>

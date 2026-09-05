<template>
  <div>

    <!-- ══ HERO ══════════════════════════════════════════ -->
    <div class="relative overflow-hidden" style="height:100vh;min-height:580px">
      <img
        src="/images/iusth-sciences-infirmieres.webp"
        alt="Étudiants de l'IUSTH lors d'une cérémonie de fin de cycle"
        class="w-full h-full object-cover block"
      />
      <div class="absolute inset-0" style="background:linear-gradient(135deg,rgba(11,37,69,.88) 0%,rgba(26,122,74,.55) 60%,rgba(232,160,32,.2) 100%)"></div>

      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6 md:px-12">
        <div v-if="useSchoolInfo.school_info?.inscription" class="flex items-center gap-2 mb-6 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest" style="background:rgba(232,160,32,.2);border:1px solid rgba(232,160,32,.5);color:#fde68a">
          <span class="w-1.5 h-1.5 rounded-full bg-yellow-400 animate-pulse"></span>
          Inscriptions ouvertes 2026–2027
        </div>

        <h1 class="font-sans font-bold text-white mb-5 leading-tight mx-auto" style="font-size:clamp(1.8rem,4.2vw,3.2rem);max-width:900px">
          Bienvenue à IUSTH, où nous nous engageons à libérer le potentiel de chaque étudiant.
        </h1>

        <p class="font-sans mb-8 max-w-xl mx-auto leading-relaxed" style="color:rgba(255,255,255,.78);font-size:clamp(.95rem,1.8vw,1.12rem)">
          Découvrez l'excellence académique et l'innovation à IUSTH. Rejoignez-nous pour un avenir brillant !
        </p>

        <div class="flex justify-center">
          <router-link
            to="/facultes"
            class="inline-flex items-center gap-2 px-8 py-3.5 rounded-full font-bold uppercase tracking-wide no-underline"
            style="background:#E8A020;color:#0B2545;box-shadow:0 4px 20px rgba(232,160,32,.4)"
          >
            Explorez maintenant
          </router-link>
        </div>
      </div>
    </div>

    <!-- ══ AJOUTER (admin) ═══════════════════════ -->
    <div v-if="authStore.isAdmin" class="bg-gray-50 py-3 text-center flex items-center justify-center gap-2">
      <button v-if="missingTemplates.length" @click="showAddSectionModal = true" class="px-4 py-1.5 rounded-full bg-amber-500/10 text-amber-600 text-xs font-semibold hover:bg-amber-500/20">
        + Ajouter une section
      </button>
      <button @click="showAddBlockModal = true" class="px-4 py-1.5 rounded-full bg-blue-500/10 text-blue-600 text-xs font-semibold hover:bg-blue-500/20">
        + Ajouter un bloc (n'importe où sur la page)
      </button>
    </div>

    <GenericSection v-for="gs in genericSectionsInZone(5)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="home"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

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
      <div class="max-w-6xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4">
        <div v-for="(s, i) in STATS" :key="i" class="text-center py-8 reveal relative group" :style="i < 3 ? 'border-right:1px solid #E2E8F0' : ''">
          <div class="font-black leading-none mb-1" style="font-size:2.4rem;background:linear-gradient(135deg,#0B2545,#1A7A4A);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{{ s.n }}</div>
          <div class="text-xs text-gray-500 uppercase tracking-widest">{{ s.l }}</div>
          <div v-if="authStore.isAdmin" class="absolute top-1 right-1 hidden group-hover:flex gap-1">
            <button @click="openItemEdit(sec('stats'), i)" class="w-5 h-5 rounded bg-blue-500/15 text-blue-600 text-xs flex items-center justify-center hover:bg-blue-500/30">✎</button>
            <button @click="deleteItem(sec('stats'), i)" class="w-5 h-5 rounded bg-red-500/15 text-red-500 text-xs flex items-center justify-center hover:bg-red-500/30">✕</button>
          </div>
        </div>
      </div>
    </div>

    <GenericSection v-for="gs in genericSectionsInZone(15)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="home"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <!-- ══ PRÉSENTATION ══════════════════════════════════ -->
    <section class="py-24 bg-gray-50">
      <div class="max-w-6xl mx-auto px-6 grid md:grid-cols-2 gap-20 items-center">
        <div class="relative reveal">
          <img
            src="/images/iusth-institution-salle-classe.webp"
            alt="Salle de classe"
            class="w-full rounded-2xl block"
            style="box-shadow:20px 20px 60px rgba(11,37,69,.15)"
            loading="lazy"
          />
          <div class="absolute -bottom-5 -right-5 text-white text-center rounded-2xl px-6 py-4" style="background:#E8A020;box-shadow:0 8px 30px rgba(232,160,32,.3)">
            <div class="text-3xl font-black leading-none">{{ facultesCount != null ? facultesCount : '…' }}</div>
            <div class="text-xs opacity-90 mt-1">facultés</div>
          </div>
        </div>

        <div class="reveal">
          <p class="text-xs font-extrabold tracking-widest uppercase mb-3" style="color:#E8A020">Notre institution</p>
          <h2 class="font-serif mb-5 leading-snug" style="font-size:clamp(1.8rem,3vw,2.6rem);color:#0B2545">
            Une formation pensée<br /><span style="color:#1A7A4A">pour votre avenir</span>
          </h2>
          <p class="text-gray-500 leading-relaxed mb-4 text-sm">
            Créé en mai 2021, l'IUSTH est une institution privée d'enseignement supérieur et de
            recherche, à but non lucratif, reconnue d'utilité publique par l'État haïtien.
          </p>
          <p class="text-gray-500 leading-relaxed mb-6 text-sm">
            Elle coopère avec une dizaine d'institutions universitaires des Amériques et des Caraïbes,
            et prépare ses étudiants aux exigences du développement durable en Haïti.
          </p>
          <div class="flex flex-wrap gap-2">
            <span v-for="v in VALUES" :key="v.t" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold bg-white border border-gray-200" style="color:#0B2545">
              {{ v.i }} {{ v.t }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <GenericSection v-for="gs in genericSectionsInZone(25)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="home"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <!-- ══ OFFRES ACADÉMIQUES ════════════════════════════ -->
    <section v-if="sec('cycles')?.is_visible !== false || authStore.isAdmin" class="py-24 relative" style="background:#EFECE5">
      <div v-if="authStore.isAdmin && !sec('cycles')?.is_visible" class="absolute inset-0 bg-red-500/5 border-2 border-dashed border-red-300/40 z-10 pointer-events-none"></div>
      <div v-if="authStore.isAdmin" class="absolute top-2 right-4 flex items-center gap-1 z-20">
        <span :class="['text-[10px] px-2 py-0.5 rounded-full font-medium', sectionBadgeClass(sec('cycles'))]">{{ sec('cycles')?.is_visible ? 'Visible' : 'Masqué' }}</span>
        <button @click="openItemEdit(sec('cycles'))" class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 text-xs">+ Carte</button>
        <button @click="openSectionEdit(sec('cycles'))" class="px-2 py-0.5 rounded bg-blue-500/10 text-blue-600 hover:bg-blue-500/20 text-xs">Titres</button>
        <button @click="toggleSection(sec('cycles'))" class="p-1 rounded bg-gray-100 text-gray-500 text-xs">👁</button>
        <button @click="deleteSection(sec('cycles'))" class="p-1 rounded bg-red-50 text-red-400 text-xs">✕</button>
      </div>
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-14 reveal">
          <h2 class="font-serif" style="font-size:clamp(1.8rem,3.2vw,2.8rem);color:#0B2545">
            {{ sec('cycles')?.titre || 'Nos Offres Académiques' }}
          </h2>
        </div>
        <div class="grid md:grid-cols-3 gap-7">
          <div v-for="(c, i) in CYCLES" :key="i"
            class="relative rounded-2xl overflow-hidden bg-white reveal transition-transform hover:-translate-y-1 group"
            style="box-shadow:0 4px 20px rgba(11,37,69,.08)">
            <div style="aspect-ratio:4/3">
              <img v-if="c.img" :src="c.img" :alt="c.t" class="w-full h-full object-cover block" loading="lazy"/>
              <div v-else class="w-full h-full flex items-center justify-center text-5xl" style="background:rgba(212,168,83,.12)">🎓</div>
            </div>
            <div class="p-6 text-center">
              <p v-if="c.badge" class="text-xs font-bold uppercase tracking-widest text-gold mb-1.5">{{ c.badge }}</p>
              <h3 class="font-serif text-xl mb-4" style="color:#0B2545">{{ c.t }}</h3>
              <router-link :to="c.lien || '/formations'" class="inline-flex items-center gap-1.5 px-6 py-2.5 rounded-full font-bold text-xs uppercase tracking-wide no-underline" style="background:#E8A020;color:#0B2545">
                {{ c.bouton || 'En savoir plus' }}
              </router-link>
            </div>
            <div v-if="authStore.isAdmin" class="absolute top-2 right-2 hidden group-hover:flex gap-1">
              <button @click="openItemEdit(sec('cycles'), i)" class="w-6 h-6 rounded bg-blue-500/15 text-blue-600 text-xs flex items-center justify-center">✎</button>
              <button @click="deleteItem(sec('cycles'), i)" class="w-6 h-6 rounded bg-red-500/15 text-red-500 text-xs flex items-center justify-center">✕</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <GenericSection v-for="gs in genericSectionsInZone(35)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="home"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <!-- ══ POURQUOI NOUS REJOINDRE ════════════════════════ -->
    <section v-if="sec('features')?.is_visible !== false || authStore.isAdmin" class="py-24 relative" style="background:linear-gradient(135deg,#0B1F3A,#162d4a)">
      <div v-if="authStore.isAdmin && !sec('features')?.is_visible" class="absolute inset-0 border-2 border-dashed border-red-300/40 z-10 pointer-events-none" style="background:rgba(239,68,68,0.05)"></div>
      <div v-if="authStore.isAdmin" class="absolute top-2 right-4 flex items-center gap-1 z-20">
        <span :class="['text-[10px] px-2 py-0.5 rounded-full font-medium', sectionBadgeClass(sec('features'))]">{{ sec('features')?.is_visible ? 'Visible' : 'Masqué' }}</span>
        <button @click="openItemEdit(sec('features'))" class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 text-xs">+ Atout</button>
        <button @click="openSectionEdit(sec('features'))" class="px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 text-xs">Titres</button>
        <button @click="toggleSection(sec('features'))" class="p-1 rounded bg-white/10 text-white/70 text-xs">👁</button>
        <button @click="deleteSection(sec('features'))" class="p-1 rounded bg-red-500/20 text-red-300 text-xs">✕</button>
      </div>
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-16 reveal">
          <h2 class="font-serif text-white" style="font-size:clamp(1.8rem,3.2vw,2.8rem)">{{ sec('features')?.titre || 'Pourquoi nous rejoindre ?' }}</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-x-10 gap-y-10">
          <div v-for="(f, i) in FEATURES" :key="i" class="reveal relative group"
            :class="[i % 3 !== 2 ? 'md:border-r md:pr-8' : '', i >= 3 ? 'md:border-t md:pt-9' : '']"
            style="border-color:rgba(255,255,255,.12)">
            <h3 class="font-serif text-lg text-white mb-2.5">{{ f.t }}</h3>
            <p class="text-sm leading-relaxed mb-4" style="color:rgba(255,255,255,.6)">{{ f.d }}</p>
            <router-link :to="f.lien || '/contact'" class="inline-block px-3 py-1 rounded text-xs font-semibold no-underline" style="background:rgba(212,168,83,.18);color:#D4A853">
              {{ f.lien_texte || 'En savoir plus' }}
            </router-link>
            <div v-if="authStore.isAdmin" class="absolute top-0 right-0 hidden group-hover:flex gap-1">
              <button @click="openItemEdit(sec('features'), i)" class="w-6 h-6 rounded bg-white/20 text-white text-xs flex items-center justify-center hover:bg-white/40">✎</button>
              <button @click="deleteItem(sec('features'), i)" class="w-6 h-6 rounded bg-red-500/40 text-white text-xs flex items-center justify-center hover:bg-red-500/60">✕</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <GenericSection v-for="gs in genericSectionsInZone(45)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="home"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <GenericSection v-for="gs in genericSectionsInZone(55)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="home"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <GenericSection v-for="gs in genericSectionsInZone(65)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="home"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <!-- ══ ACTUALITÉS ════════════════════════════════════ -->
    <section class="py-16 bg-gray-50">
      <div class="max-w-6xl mx-auto px-6">
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
            <p class="text-xs text-gray-500">{{ n.date }}</p>
          </div>
        </div>
      </div>
    </section>

    <GenericSection v-for="gs in genericSectionsInZone(75)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="home"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

        <!-- ══ CTA ════════════════════════════════════════════ -->
    <section class="py-16 bg-white">
      <div>
        <div class="relative overflow-hidden py-20 px-10 reveal" style="background:linear-gradient(135deg,#0B2545,#1A7A4A)">
          <div class="absolute w-72 h-72 rounded-full -top-20 -right-16 opacity-10" style="background:#E8A020"></div>
          <div class="max-w-6xl mx-auto relative">
          <div class="grid md:grid-cols-2 gap-10 items-start">
            <div>
              <p class="text-xs font-extrabold tracking-widest uppercase mb-3" style="color:#fde68a">Candidature 2026–2027</p>
              <h2 class="font-serif text-white mb-4" style="font-size:clamp(1.6rem,3vw,2.4rem)">
                Rejoindre<br />{{useSchoolInfo.school_info?.nom || 'IUSTH'}}
              </h2>
              <p class="text-sm mb-0 leading-relaxed" style="color:rgba(255,255,255,.7)">
                <template v-if="useSchoolInfo.school_info?.inscription">Les dossiers de candidature pour l'année 2026–2027 sont ouverts. </template>
                Consultez les conditions d'admission et déposez votre dossier en ligne.
              </p>
            </div>
            <div class="grid justify-end gap-3">
              <router-link to="/admission" class="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-full font-bold text-white no-underline text-center whitespace-nowrap" style="background:#E8A020;border:2px solid transparent;box-shadow:0 4px 20px rgba(232,160,32,.4)">
                Déposer un dossier d'admission
                <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" class="shrink-0"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </router-link>
              <router-link to="/contact" class="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-full font-semibold text-white no-underline text-center whitespace-nowrap" style="border:2px solid rgba(255,255,255,.4)">
                📞 Contacter l'administration
              </router-link>
              <p class="text-xs mt-1" style="color:rgba(255,255,255,.4)">
                {{ premierHoraire.jour }} · {{ premierHoraire.horaire }}
              </p>
            </div>
          </div>
          </div>
        </div>
      </div>
    </section>

    <GenericSection v-for="gs in genericSectionsInZone(95)" :key="gs.id" :section="gs" :is-admin="authStore.isAdmin" page="home"
      @toggle="toggleGenericSection" @delete="deleteGenericSection" @changed="fetchGenericSections" />

    <!-- ══ MÉDIAS (VIDÉOS & ARTICLES) ═════════════════════ -->
    <section v-if="VIDEOS.length || ARTICLES.length" class="py-20 bg-white">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-12 reveal">
          <p class="text-xs font-extrabold tracking-widest uppercase mb-2" style="color:#E8A020">Presse & Médias</p>
          <h2 class="font-serif" style="font-size:clamp(1.8rem,3vw,2.6rem);color:#0B2545">IUSTH dans les médias</h2>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-[280px_1fr_280px] gap-8">
          <!-- Nos Vidéos -->
          <div class="border border-gray-200 rounded-2xl overflow-hidden reveal flex flex-col">
            <div class="px-4 py-3 border-b border-gray-200 bg-gray-50">
              <h3 class="font-serif text-sm" style="color:#0B2545">Nos Vidéos</h3>
            </div>
            <div class="flex-1">
              <div v-if="videosPage.length === 0" class="p-5 text-center text-xs text-gray-500">Aucune vidéo pour le moment.</div>
              <button v-for="v in videosPage" :key="v.id" type="button" @click="playVideo(v)"
                class="w-full text-left block border-b border-gray-100 last:border-b-0 hover:bg-gray-50 transition-colors"
                :class="currentVideo?.id === v.id ? 'bg-amber-50/60' : ''">
                <div class="relative bg-gray-100" style="aspect-ratio:16/9">
                  <img :src="youtubeThumb(v.youtube_url)" :alt="v.titre" class="w-full h-full object-cover block" loading="lazy"/>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <div class="w-9 h-9 rounded-full flex items-center justify-center" style="background:rgba(220,38,38,.9)">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"/></svg>
                    </div>
                  </div>
                </div>
                <div class="px-3 py-2.5">
                  <div class="text-xs font-semibold leading-snug mb-0.5" style="color:#0B2545">{{ v.titre }}</div>
                  <div class="text-[11px] text-gray-500">{{ v.source }}</div>
                </div>
              </button>
            </div>
            <div v-if="videoPageCount > 1" class="flex items-center justify-center gap-1 py-3 border-t border-gray-100">
              <button v-for="p in videoPageCount" :key="p" type="button" @click="videoPage = p"
                class="w-6 h-6 rounded-full text-[11px] font-semibold transition-colors"
                :class="videoPage === p ? 'text-white' : 'text-gray-500 hover:bg-gray-100'"
                :style="videoPage === p ? { background: '#E8A020' } : {}">{{ p }}</button>
            </div>
          </div>

          <!-- Lecteur central -->
          <div class="reveal self-start">
            <div class="rounded-2xl overflow-hidden bg-black relative" style="aspect-ratio:16/9;box-shadow:0 8px 32px rgba(11,37,69,.15)">
              <iframe v-if="currentVideo && videoPlaying" :key="currentVideo.id" :src="youtubeEmbed(currentVideo.youtube_url)" class="w-full h-full"
                frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
              <button v-else-if="currentVideo" type="button" @click="videoPlaying = true"
                class="relative w-full h-full block group cursor-pointer">
                <img :src="youtubeThumb(currentVideo.youtube_url)" :alt="currentVideo.titre" class="w-full h-full object-cover block" loading="lazy"/>
                <div class="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/35 transition-colors">
                  <div class="w-16 h-16 rounded-full flex items-center justify-center" style="background:rgba(220,38,38,.9)">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"/></svg>
                  </div>
                </div>
              </button>
              <div v-else class="w-full h-full flex items-center justify-center text-white/40 text-sm">Aucune vidéo disponible</div>
            </div>
            <div v-if="currentVideo" class="mt-4 text-center">
              <h3 class="font-serif text-lg mb-1" style="color:#0B2545">{{ currentVideo.titre }}</h3>
              <p class="text-xs text-gray-500">{{ currentVideo.source }}</p>
            </div>
          </div>

          <!-- Articles -->
          <div class="border border-gray-200 rounded-2xl overflow-hidden reveal flex flex-col">
            <div class="px-4 py-3 border-b border-gray-200 bg-gray-50">
              <h3 class="font-serif text-sm" style="color:#0B2545">Articles</h3>
            </div>
            <div class="flex-1">
              <div v-if="articlesPage.length === 0" class="p-5 text-center text-xs text-gray-500">Aucun article pour le moment.</div>
              <div v-for="a in articlesPage" :key="a.id" class="flex gap-3 px-4 py-3.5 border-b border-gray-100 last:border-b-0">
                <img v-if="a.image_url" :src="toAbsoluteUrl(a.image_url)" :alt="a.title" class="w-14 h-14 rounded-lg object-cover flex-shrink-0" loading="lazy"/>
                <p class="text-xs leading-relaxed" style="color:#0B2545">
                  {{ a.title }}
                  <router-link :to="`/actualites/${a.id}`" class="font-semibold no-underline whitespace-nowrap" style="color:#1A7A4A">Lire la suite…</router-link>
                </p>
              </div>
            </div>
            <div v-if="articlePageCount > 1" class="flex items-center justify-center gap-1 py-3 border-t border-gray-100">
              <button v-for="p in articlePageCount" :key="p" type="button" @click="articlePage = p"
                class="w-6 h-6 rounded-full text-[11px] font-semibold transition-colors"
                :class="articlePage === p ? 'text-white' : 'text-gray-500 hover:bg-gray-100'"
                :style="articlePage === p ? { background: '#1A7A4A' } : {}">{{ p }}</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══ MODALS ADMIN ═══════════════════════════════════ -->

    <!-- Modal : ajouter une section (templates existants manquants) -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showAddSectionModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="showAddSectionModal = false">
        <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h2 class="text-sm font-semibold text-gray-800">Ajouter une section</h2>
            <button @click="showAddSectionModal = false" class="text-gray-500 hover:text-gray-600">✕</button>
          </div>
          <div class="px-6 py-5 space-y-3 max-h-[60vh] overflow-y-auto">
            <button
              v-for="tpl in missingTemplates" :key="tpl.key"
              @click="createSection(tpl)" :disabled="creatingSection"
              class="w-full text-left border border-gray-200 rounded-xl px-4 py-3 hover:border-amber-400 hover:bg-amber-50/50 transition-colors disabled:opacity-50"
            >
              <div class="font-semibold text-sm text-gray-800">{{ tpl.label }}</div>
              <div class="text-xs text-gray-500 mt-0.5">{{ tpl.desc }}</div>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal : ajouter un bloc générique (mise en page libre) -->
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

    <!-- Modal : titres de section -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showSectionModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="showSectionModal = false">
        <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h2 class="text-sm font-semibold text-gray-800">Modifier les titres — {{ editingSection?.section_key }}</h2>
            <button @click="showSectionModal = false" class="text-gray-500 hover:text-gray-600">✕</button>
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
            <button @click="showItemModal = false" class="text-gray-500 hover:text-gray-600">✕</button>
          </div>
          <div class="px-6 py-5 space-y-4">
            <div v-for="f in currentFields" :key="f.k">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">{{ f.l }}</label>
              <template v-if="f.type === 'image'">
                <img v-if="itemForm[f.k]" :src="itemForm[f.k]" alt="Aperçu" class="w-full h-28 object-cover rounded-lg mb-2 border border-gray-200"/>
                <input type="file" accept="image/*" @change="onItemImageChange($event, f.k)"
                  class="w-full text-xs text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-amber-50 file:text-amber-600 hover:file:bg-amber-100"/>
                <p v-if="uploadingImage" class="text-xs text-gray-500 mt-1">Envoi en cours…</p>
              </template>
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
import GenericSection from '@/components/GenericSection.vue'
import { usePageSections, LAYOUT_TEMPLATES } from '@/composables/usePageSections.js'

const url          = import.meta.env.VITE_APP_BASE_URL
// image_url renvoyé par l'API est un chemin relatif ("/static/uploads/...")
// — même correctif que FacultesView.vue / FormationsView.vue / usePageSections.js.
const apiOrigin    = url.replace(/\/api\/v1\/?$/, '')
const toAbsoluteUrl = (path) => (!path ? null : path.startsWith('http') ? path : `${apiOrigin}${path}`)
const useSchoolInfo= useSchoolStoreInfo()
const authStore    = useAuthStore()

// ── Blocs génériques (image_left/right, texte centré, bannière, grille de
// cartes, ligne de chiffres) — distincts des 6 sections historiques
// ci-dessus, qui gardent leur logique locale (sections/sec/fetchSections…)
// inchangée pour ne rien casser. Alias sur toggle/delete pour éviter toute
// collision avec les fonctions homonymes déjà définies plus bas.
const {
  genericSections, genericSectionsInZone, createGenericSection, fetchSections: fetchGenericSections,
  toggleSection: toggleGenericSection, deleteSection: deleteGenericSection,
  uploadImage, zones,
} = usePageSections('home')
const showAddBlockModal = ref(false)
const pendingZone = ref(null)
const closeAddBlockModal = () => { showAddBlockModal.value = false; pendingZone.value = null }
const pickBlockTemplate = async (tpl) => {
  const ok = await createGenericSection(tpl, pendingZone.value.ordre)
  if (ok) closeAddBlockModal()
}

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

// Première ligne d'horaires (voir Profile.horaires, RProfile.py) pour le
// bandeau CTA — ContactView.vue affiche la liste complète.
const premierHoraire = computed(() => {
  const h = useSchoolInfo.school_info?.horaires
  return (h && h.length) ? h[0] : { jour: 'Vendredi et samedi', horaire: '8h00 – 17h00' }
})

const STATS       = computed(() => sec('stats')?.items        ?? [])
const CYCLES      = computed(() => sec('cycles')?.items       ?? [])
const FEATURES    = computed(() => sec('features')?.items     ?? [])
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

// ── Ajouter une section (templates existants) ──────────────────────────────
// Chaque section_key a déjà son propre rendu visuel sur mesure et responsive
// (grille de chiffres, cartes avec icône, galerie avec image...) — "ajouter"
// propose de recréer l'un de ces templates s'il a été masqué/supprimé,
// plutôt qu'un éditeur de mise en page libre (pas dans l'architecture
// actuelle : chaque type de section a son propre bloc de template ci-dessus).
const SECTION_TEMPLATES = [
  { key: 'stats',        label: 'Chiffres clés',  desc: 'Grille de statistiques (nombre + libellé), sans image.', titre: 'Chiffres clés' },
  { key: 'cycles',       label: 'Offres académiques', desc: 'Cartes avec photo, texte et bouton.', titre: 'Nos Offres Académiques' },
  { key: 'features',     label: 'Pourquoi nous rejoindre', desc: 'Grille de 6 avantages, sans image, fond sombre.', titre: 'Pourquoi nous rejoindre ?' },
  { key: 'values',       label: 'Nos valeurs',    desc: 'Icône + titre, compact, sans image.', titre: 'Nos valeurs' },
]
const showAddSectionModal = ref(false)
const missingTemplates = computed(() =>
  SECTION_TEMPLATES.filter(t => !sec(t.key))
)
const creatingSection = ref(false)
const createSection = async (tpl) => {
  creatingSection.value = true
  try {
    await axios.post(`${url}/page-sections/`, {
      page: 'home', section_key: tpl.key, titre: tpl.titre, sous_titre: null, items: [],
    })
    showAddSectionModal.value = false
    await fetchSections()
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Erreur', text: e.response?.data?.detail || 'Erreur', background: '#0f1117', color: '#e8eaf0' })
  } finally { creatingSection.value = false }
}

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

// Upload d'image pour un item (ex: activities.img) — remplace le champ
// texte "coller une URL" par un vrai envoi de fichier (voir
// /page-sections/upload-image côté API).
const uploadingImage = ref(false)
const onItemImageChange = async (event, fieldKey) => {
  const file = event.target.files?.[0]
  if (!file) return
  uploadingImage.value = true
  try {
    itemForm.value[fieldKey] = await uploadImage(file)
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Erreur', text: e.response?.data?.detail || "Échec de l'envoi de l'image", background: '#0f1117', color: '#e8eaf0' })
  } finally { uploadingImage.value = false }
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
  cycles:       [{ k:'img', l:'Image', type:'image' }, { k:'badge', l:'Texte au-dessus du titre', p:'Vaste sélection de' }, { k:'t', l:'Titre', p:'Programmes diversifiés' }, { k:'bouton', l:'Texte du bouton', p:'EXPLORER' }, { k:'lien', l:'Lien (route)', p:'/formations' }],
  features:     [{ k:'t', l:'Titre', p:'Environnement Innovant' }, { k:'d', l:'Description', p:'...' }, { k:'lien_texte', l:'Texte du lien', p:'En savoir plus' }, { k:'lien', l:'Lien (route)', p:'/contact' }],
  values:       [{ k:'i', l:'Icône', p:'🎯' }, { k:'t', l:'Valeur', p:'Excellence' }],
}

const currentFields = computed(() => FIELDS[editingSection.value?.section_key] ?? [])

// ── Admin bar helper ──────────────────────────────────────────────────────
const sectionBadgeClass = (s) => s?.is_visible ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'

// Nombre de facultés actives — même endpoint public que FacultesView.vue,
// pas figé en dur (voir Audit_site_IUSTH_2026-08-27.pdf, point 2.5).
const facultesCount = ref(null)
const fetchFacultesCount = async () => {
  try {
    const { data } = await axios.get(`${url}/facultes-publiques`)
    facultesCount.value = data?.data?.length ?? 0
  } catch (e) { console.error('[Accueil] facultés', e) }
}

// ── Médias (vidéos & articles de presse) ──────────────────────────────────
const VIDEOS      = ref([])
const ARTICLES    = ref([])
const currentVideo = ref(null)
// L'iframe YouTube n'est montée qu'après un clic explicite (audit CCA, P1-7 —
// "trois lecteurs YouTube intégrés directement sur la page d'accueil ... à
// remplacer par des vignettes cliquables (chargement différé)") : par défaut
// on affiche une simple vignette, jamais l'iframe au chargement de la page.
const videoPlaying = ref(false)
const videoPage    = ref(1)
const articlePage  = ref(1)
const MEDIA_PAGE_SIZE = 3

const playVideo = (v) => {
  currentVideo.value = v
  videoPlaying.value = true
}

const fetchVideos = async () => {
  try {
    const { data } = await axios.get(`${url}/videos/`, { params: { published_only: true } })
    VIDEOS.value = data
    // La plus récente (déjà triée desc côté API) reste toujours prête à lire par défaut.
    currentVideo.value = data[0] ?? null
  } catch (e) { console.error('[Home] videos:', e) }
}
const fetchArticles = async () => {
  try {
    const { data } = await axios.get(`${url}/news/`, { params: { published_only: true } })
    ARTICLES.value = data
  } catch (e) { console.error('[Home] articles:', e) }
}

const videoPageCount = computed(() => Math.max(1, Math.ceil(VIDEOS.value.length / MEDIA_PAGE_SIZE)))
const videosPage     = computed(() => VIDEOS.value.slice((videoPage.value - 1) * MEDIA_PAGE_SIZE, videoPage.value * MEDIA_PAGE_SIZE))
const articlePageCount = computed(() => Math.max(1, Math.ceil(ARTICLES.value.length / MEDIA_PAGE_SIZE)))
const articlesPage     = computed(() => ARTICLES.value.slice((articlePage.value - 1) * MEDIA_PAGE_SIZE, articlePage.value * MEDIA_PAGE_SIZE))

const youtubeId = (u) => {
  const m = u?.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|shorts\/))([\w-]{11})/)
  return m ? m[1] : null
}
const youtubeEmbed = (u) => { const id = youtubeId(u); return id ? `https://www.youtube.com/embed/${id}` : '' }
const youtubeThumb = (u) => { const id = youtubeId(u); return id ? `https://img.youtube.com/vi/${id}/hqdefault.jpg` : '' }

onMounted(async () => {
  window.scrollTo(0, 0)
  await Promise.all([fetchSections(), fetchNews(), fetchFacultesCount(), fetchGenericSections(), fetchVideos(), fetchArticles()])
})
</script>

<template>
  <div class="animate-[fadeUp_0.3s_ease_both]">

    <!-- Tabs -->
    <div class="flex border-b border-white/[0.07] mb-6">
      <button v-for="t in tabs" :key="t.key" @click="activeSub = t.key"
        :class="['px-4 py-2.5 text-[13.5px] font-medium border-b-2 -mb-px transition-colors',
          activeSub === t.key ? 'border-[var(--accent)] text-[var(--accent)]' : 'border-transparent text-[#7c83a0] hover:text-[#e8eaf0]']">
        {{ t.label }}
        <span v-if="t.count > 0" class="ml-1.5 text-[11px] px-1.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-medium">
          {{ t.count }}
        </span>
      </button>
    </div>

    <!-- ── Événements ── -->
    <div v-if="activeSub === 'evenement'">
      <div class="flex items-center justify-between mb-4 gap-3 flex-wrap">
        <!-- Filtres audience -->
        <div class="flex items-center gap-2">
          <button v-for="f in [{k:'',l:'Tous'},{k:'public',l:'Public'},{k:'classe',l:'Classes'},{k:'professeurs',l:'Professeurs'}]"
            :key="f.k" @click="audienceFilter = f.k"
            :class="['px-3 py-1 rounded-full text-[12px] font-medium border transition-colors',
              audienceFilter === f.k ? 'bg-[var(--accent)]/15 text-[var(--accent)] border-[var(--accent)]/30' : 'border-white/[0.1] text-[#7c83a0] hover:text-[#e8eaf0]']">
            {{ f.l }}
            <span v-if="f.k" class="ml-1 opacity-60">
              ({{ evenements.filter(e => e.audience === f.k).length }})
            </span>
          </button>
        </div>
        <button @click="openEventModal()" class="text-xs font-medium text-white px-3 py-1.5 rounded-lg hover:opacity-80 transition-opacity shrink-0" :style="{ background: 'var(--accent)' }">
          + Nouvel événement
        </button>
      </div>

      <div v-if="loadingEvents" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div v-for="i in 4" :key="i" class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5 animate-pulse">
          <div class="h-3 w-24 bg-white/[0.06] rounded mb-4"></div>
          <div class="h-4 w-3/4 bg-white/[0.06] rounded mb-2"></div>
          <div class="h-3 w-full bg-white/[0.04] rounded"></div>
        </div>
      </div>

      <div v-else-if="evenementsFiltres.length === 0" class="text-center py-16 text-[#7c83a0] text-[13px]">
        Aucun événement pour cette audience.
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div v-for="ev in evenementsFiltres" :key="ev.id"
          class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5 hover:border-white/[0.12] transition-colors">
          <div class="flex items-start justify-between mb-3">
            <span :class="['inline-flex items-center px-2 py-0.5 rounded-md text-[11.5px] font-medium', categoryBadge(ev.category?.name)]">
              {{ ev.category?.name ?? 'Général' }}
            </span>
            <div class="flex items-center gap-2">
              <span class="text-xs font-mono text-[#7c83a0]">{{ formatDate(ev.start_date) }}</span>
              <button @click="openEventModal(ev)" class="text-[#7c83a0] hover:text-[var(--accent)] transition-colors" title="Modifier">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931z"/>
                </svg>
              </button>
              <button @click="deleteEvent(ev.id)" class="text-[#7c83a0] hover:text-red-400 transition-colors" title="Supprimer">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/>
                </svg>
              </button>
            </div>
          </div>
          <h3 class="text-[13.5px] font-semibold text-[#e8eaf0] mb-1 leading-snug">{{ ev.title }}</h3>
          <p class="text-xs text-[#7c83a0] mb-3 leading-relaxed line-clamp-2">{{ ev.description }}</p>
          <div v-if="ev.location" class="flex items-center gap-1.5 mb-2">
            <svg class="w-3.5 h-3.5 text-[#7c83a0]/50 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z"/>
            </svg>
            <span class="text-xs text-[#7c83a0]">{{ ev.location }}</span>
          </div>
          <span :class="['text-[10px] px-1.5 py-0.5 rounded font-medium', ev.is_published ? 'bg-emerald-500/15 text-emerald-400' : 'bg-white/[0.06] text-[#7c83a0]']">
            {{ ev.is_published ? 'Publié' : 'Brouillon' }}
          </span>
        </div>
      </div>
    </div>

    <!-- ── Actualités ── -->
    <div v-if="activeSub === 'actualite'">
      <div class="flex items-center justify-between mb-4 gap-3 flex-wrap">
        <div class="flex items-center gap-2">
          <button v-for="f in [{k:'',l:'Tous'},{k:'public',l:'Public'},{k:'classe',l:'Classes'},{k:'professeurs',l:'Professeurs'}]"
            :key="f.k" @click="newsAudienceFilter = f.k"
            :class="['px-3 py-1 rounded-full text-[12px] font-medium border transition-colors',
              newsAudienceFilter === f.k ? 'bg-[var(--accent)]/15 text-[var(--accent)] border-[var(--accent)]/30' : 'border-white/[0.1] text-[#7c83a0] hover:text-[#e8eaf0]']">
            {{ f.l }}
            <span v-if="f.k" class="ml-1 opacity-60">({{ actualites.filter(a => a.audience === f.k).length }})</span>
          </button>
        </div>
        <button @click="openNewsModal()" class="text-xs font-medium text-white px-3 py-1.5 rounded-lg hover:opacity-80 transition-opacity shrink-0" :style="{ background: 'var(--accent)' }">
          + Nouvelle actualité
        </button>
      </div>

      <div v-if="loadingNews" class="space-y-3">
        <div v-for="i in 3" :key="i" class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5 animate-pulse">
          <div class="h-3 w-32 bg-white/[0.06] rounded mb-3"></div>
          <div class="h-4 w-2/3 bg-white/[0.06] rounded mb-2"></div>
          <div class="h-3 w-full bg-white/[0.04] rounded"></div>
        </div>
      </div>

      <div v-else-if="actualitesFiltrees.length === 0" class="text-center py-16 text-[#7c83a0] text-[13px]">
        Aucune actualité pour cette audience.
      </div>

      <div v-else class="space-y-3">
        <div v-for="a in actualitesFiltrees" :key="a.id"
          class="bg-[#171b26] border border-white/[0.07] rounded-xl p-5 hover:border-white/[0.12] transition-colors">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="w-1.5 h-1.5 rounded-full shrink-0" :style="{ background: 'var(--accent)' }"></span>
              <span class="font-mono text-xs text-[#7c83a0]">{{ formatDate(a.published_at ?? a.created_at) }}</span>
              <span class="inline-flex items-center px-2 py-0.5 rounded-md text-[11.5px] font-medium bg-white/[0.06] text-[#a0a8c0]">
                {{ a.category?.name ?? 'Général' }}
              </span>
              <span :class="['text-[10px] px-1.5 py-0.5 rounded font-medium', a.is_published ? 'bg-emerald-500/15 text-emerald-400' : 'bg-white/[0.06] text-[#7c83a0]']">
                {{ a.is_published ? 'Publié' : 'Brouillon' }}
              </span>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <button @click="openNewsModal(a)" class="text-[#7c83a0] hover:text-[var(--accent)] transition-colors">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931z"/>
                </svg>
              </button>
              <button @click="deleteNews(a.id)" class="text-[#7c83a0] hover:text-red-400 transition-colors">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/>
                </svg>
              </button>
            </div>
          </div>
          <h3 class="text-[13.5px] font-semibold text-[#e8eaf0] mb-1.5 leading-snug">{{ a.title }}</h3>
          <p class="text-xs text-[#7c83a0] leading-relaxed line-clamp-3">{{ a.content }}</p>
        </div>
      </div>
    </div>

    <!-- ── Annonces ── -->
    <div v-if="activeSub === 'annonce'">
      <div class="flex justify-end mb-4">
        <button class="text-xs font-medium text-white px-3 py-1.5 rounded-lg hover:opacity-80 transition-opacity" :style="{ background: 'var(--accent)' }">
          + Nouvelle annonce
        </button>
      </div>
      <div class="space-y-3">
        <div v-for="an in annonces" :key="an.id"
          :class="['rounded-xl border p-5 transition-colors', an.priorite === 'haute' ? 'border-amber-500/30 bg-amber-500/[0.05]' : 'bg-[#171b26] border-white/[0.07] hover:border-white/[0.12]']">
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-2">
              <span :class="['inline-flex items-center px-2 py-0.5 rounded-full text-[11.5px] font-medium',
                an.priorite === 'haute' ? 'bg-amber-500/20 text-amber-400' : 'bg-white/[0.07] text-[#a0a8c0]']">
                {{ an.priorite === 'haute' ? '⚠ Urgent' : 'Info' }}
              </span>
              <span class="text-xs text-[#7c83a0]">{{ an.cible }}</span>
            </div>
            <span class="font-mono text-xs text-[#7c83a0] shrink-0">{{ an.date }}</span>
          </div>
          <h3 class="text-[13.5px] font-semibold text-[#e8eaf0] mb-1 leading-snug">{{ an.titre }}</h3>
          <p class="text-xs text-[#7c83a0] leading-relaxed">{{ an.message }}</p>
        </div>
      </div>
    </div>

    <!-- ══ Modal Événement ══ -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showEventModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="showEventModal = false">
        <div class="bg-[#0f1117] border border-white/[0.1] rounded-2xl w-full max-w-lg shadow-2xl">
          <div class="flex items-center justify-between px-6 py-4 border-b border-white/[0.07]">
            <h2 class="text-[14px] font-semibold text-[#e8eaf0]">{{ editingEvent ? "Modifier l'événement" : 'Nouvel événement' }}</h2>
            <button @click="showEventModal = false" class="text-[#7c83a0] hover:text-[#e8eaf0] transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="px-6 py-5 space-y-4 max-h-[70vh] overflow-y-auto">
            <div>
              <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Titre *</label>
              <input v-model="eventForm.title" type="text" placeholder="Titre de l'événement"
                class="w-full bg-[#171b26] border border-white/[0.1] rounded-lg px-3 py-2 text-[13px] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition"/>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Date début *</label>
                <input v-model="eventForm.start_date" type="datetime-local"
                  class="w-full bg-[#171b26] border border-white/[0.1] rounded-lg px-3 py-2 text-[13px] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition"/>
              </div>
              <div>
                <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Date fin</label>
                <input v-model="eventForm.end_date" type="datetime-local"
                  class="w-full bg-[#171b26] border border-white/[0.1] rounded-lg px-3 py-2 text-[13px] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition"/>
              </div>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Lieu</label>
              <input v-model="eventForm.location" type="text" placeholder="Ex: Salle polyvalente"
                class="w-full bg-[#171b26] border border-white/[0.1] rounded-lg px-3 py-2 text-[13px] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition"/>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Description</label>
              <textarea v-model="eventForm.description" rows="3" placeholder="Description..."
                class="w-full bg-[#171b26] border border-white/[0.1] rounded-lg px-3 py-2 text-[13px] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition resize-none"/>
            </div>
            <!-- Image -->
            <div>
              <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Image</label>
              <div v-if="eventImagePreview" class="mb-2 rounded-lg overflow-hidden h-32 bg-[#171b26] border border-white/[0.07]">
                <img :src="eventImagePreview" class="w-full h-full object-cover"/>
              </div>
              <label class="flex items-center gap-2 cursor-pointer px-3 py-2 bg-[#171b26] border border-white/[0.1] rounded-lg hover:border-[var(--accent)]/50 transition-colors">
                <svg class="w-4 h-4 text-[#7c83a0]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
                </svg>
                <span class="text-[12px] text-[#7c83a0]">{{ eventImageFile ? eventImageFile.name : 'Choisir une image' }}</span>
                <input type="file" accept="image/*" class="hidden" @change="handleEventImage"/>
              </label>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Audience</label>
                <select v-model="eventForm.audience"
                  class="w-full bg-[#171b26] border border-white/[0.1] rounded-lg px-3 py-2 text-[13px] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition">
                  <option value="public">Public</option>
                  <option value="classe">Classes</option>
                  <option value="professeurs">Professeurs</option>
                </select>
              </div>
              <div class="flex items-end pb-1">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" v-model="eventForm.is_published" class="w-4 h-4 accent-[var(--accent)]"/>
                  <span class="text-[13px] text-[#e8eaf0]">Publier</span>
                </label>
              </div>
            </div>
            <!-- Note audience -->
            <div v-if="eventForm.audience !== 'public'"
              class="text-[11.5px] text-[#7c83a0] bg-[var(--accent)]/5 border border-[var(--accent)]/20 rounded-lg px-3 py-2">
              {{ eventForm.audience === 'classe' ? 'Visible uniquement pour les étudiants et leurs classes.' : 'Visible uniquement pour les professeurs.' }}
            </div>
          </div>
          <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-white/[0.07]">
            <button @click="showEventModal = false" class="px-4 py-2 text-[13px] text-[#7c83a0] hover:text-[#e8eaf0] transition-colors">Annuler</button>
            <button @click="saveEvent" :disabled="savingEvent"
              class="px-4 py-2 text-[13px] font-medium text-white rounded-lg disabled:opacity-50 hover:opacity-90 transition-opacity"
              :style="{ background: 'var(--accent)' }">
              {{ savingEvent ? 'Enregistrement...' : (editingEvent ? 'Modifier' : 'Créer') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ══ Modal Actualité ══ -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showNewsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="showNewsModal = false">
        <div class="bg-[#0f1117] border border-white/[0.1] rounded-2xl w-full max-w-lg shadow-2xl">
          <div class="flex items-center justify-between px-6 py-4 border-b border-white/[0.07]">
            <h2 class="text-[14px] font-semibold text-[#e8eaf0]">{{ editingNews ? "Modifier l'actualité" : 'Nouvelle actualité' }}</h2>
            <button @click="showNewsModal = false" class="text-[#7c83a0] hover:text-[#e8eaf0] transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="px-6 py-5 space-y-4">
            <div>
              <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Titre *</label>
              <input v-model="newsForm.title" type="text" placeholder="Titre de l'actualité"
                class="w-full bg-[#171b26] border border-white/[0.1] rounded-lg px-3 py-2 text-[13px] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition"/>
            </div>
            <div>
              <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Contenu</label>
              <textarea v-model="newsForm.content" rows="4" placeholder="Contenu..."
                class="w-full bg-[#171b26] border border-white/[0.1] rounded-lg px-3 py-2 text-[13px] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition resize-none"/>
            </div>
            <!-- Image -->
            <div>
              <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Image</label>
              <div v-if="newsImagePreview" class="mb-2 rounded-lg overflow-hidden h-32 bg-[#171b26] border border-white/[0.07]">
                <img :src="newsImagePreview" class="w-full h-full object-cover"/>
              </div>
              <label class="flex items-center gap-2 cursor-pointer px-3 py-2 bg-[#171b26] border border-white/[0.1] rounded-lg hover:border-[var(--accent)]/50 transition-colors">
                <svg class="w-4 h-4 text-[#7c83a0]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
                </svg>
                <span class="text-[12px] text-[#7c83a0]">{{ newsImageFile ? newsImageFile.name : 'Choisir une image' }}</span>
                <input type="file" accept="image/*" class="hidden" @change="handleNewsImage"/>
              </label>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-[11px] font-medium text-[#7c83a0] uppercase tracking-wider mb-1.5">Audience</label>
                <select v-model="newsForm.audience"
                  class="w-full bg-[#171b26] border border-white/[0.1] rounded-lg px-3 py-2 text-[13px] text-[#e8eaf0] focus:outline-none focus:border-[var(--accent)]/50 transition">
                  <option value="public">Public</option>
                  <option value="classe">Classes</option>
                  <option value="professeurs">Professeurs</option>
                </select>
              </div>
              <div class="flex items-end pb-1">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" v-model="newsForm.is_published" class="w-4 h-4 accent-[var(--accent)]"/>
                  <span class="text-[13px] text-[#e8eaf0]">Publier</span>
                </label>
              </div>
            </div>
            <div v-if="newsForm.audience !== 'public'"
              class="text-[11.5px] text-[#7c83a0] bg-[var(--accent)]/5 border border-[var(--accent)]/20 rounded-lg px-3 py-2">
              {{ newsForm.audience === 'classe' ? 'Visible uniquement pour les étudiants et leurs classes.' : 'Visible uniquement pour les professeurs.' }}
            </div>
          </div>
          <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-white/[0.07]">
            <button @click="showNewsModal = false" class="px-4 py-2 text-[13px] text-[#7c83a0] hover:text-[#e8eaf0] transition-colors">Annuler</button>
            <button @click="saveNews" :disabled="savingNews"
              class="px-4 py-2 text-[13px] font-medium text-white rounded-lg disabled:opacity-50 hover:opacity-90 transition-opacity"
              :style="{ background: 'var(--accent)' }">
              {{ savingNews ? 'Enregistrement...' : (editingNews ? 'Modifier' : 'Créer') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { useSchoolStore } from '@/stores/schoolStore'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const url = import.meta.env.VITE_APP_BASE_URL
const schoolStore = useSchoolStore()
const authStore = useAuthStore()
const { classes, niveau } = storeToRefs(schoolStore)

const activeSub      = ref('evenement')
const evenements     = ref([])
const actualites     = ref([])
const loadingEvents  = ref(false)
const loadingNews    = ref(false)
const audienceFilter = ref('')  // '' | 'public' | 'classe' | 'professeurs'
const newsAudienceFilter = ref('')

const showEventModal = ref(false)
const showNewsModal  = ref(false)
const editingEvent   = ref(null)
const editingNews    = ref(null)
const savingEvent    = ref(false)
const savingNews     = ref(false)

// Image upload
const eventImageFile    = ref(null)
const eventImagePreview = ref(null)
const newsImageFile     = ref(null)
const newsImagePreview  = ref(null)

const eventForm = ref({ title: '', description: '', location: '', start_date: '', end_date: '', audience: 'public', is_published: false })
const newsForm  = ref({ title: '', content: '', audience: 'public', is_published: false })

const ALL_COMMUNITY_TABS = [
  { key: 'evenement', subId: 'communaute.evenements', label: 'Événements' },
  { key: 'actualite', subId: 'communaute.actualites', label: 'Actualités' },
  { key: 'annonce',   subId: 'communaute.annonces',   label: 'Annonces' },
]
const tabs = computed(() => {
  const tabIds = authStore.user?.tab_ids ?? null
  const base = tabIds === null ? ALL_COMMUNITY_TABS : ALL_COMMUNITY_TABS.filter(t => tabIds.includes(t.subId))
  return base.map(t => ({
    ...t,
    count: t.key === 'evenement' ? evenements.value.length : t.key === 'actualite' ? actualites.value.length : 0
  }))
})
watch(tabs, (vt) => {
  if (vt.length && !vt.find(t => t.key === activeSub.value)) {
    activeSub.value = vt[0]?.key ?? 'evenement'
  }
}, { immediate: true })

// Listes filtrées par audience
const evenementsFiltres = computed(() => {
  if (!audienceFilter.value) return evenements.value
  return evenements.value.filter(ev => ev.audience === audienceFilter.value)
})
const actualitesFiltrees = computed(() => {
  if (!newsAudienceFilter.value) return actualites.value
  return actualites.value.filter(a => a.audience === newsAudienceFilter.value)
})

const annonces = [
  { id:1, titre:'Fermeture exceptionnelle – Lundi 3 mars',    priorite:'haute',   cible:'Tous',        date:'24/02/25', message:"L'école sera fermée le lundi 3 mars pour travaux d'urgence." },
  { id:2, titre:'Réunion parents-professeurs – 6ème et 5ème', priorite:'normale', cible:'6ème & 5ème', date:'22/02/25', message:"Une réunion est organisée le jeudi 6 mars à 18h." },
  { id:3, titre:'Rappel: paiement frais 2e trimestre',         priorite:'haute',   cible:'Parents',     date:'18/02/25', message:"Le délai de paiement des frais expire le 28 février." },
]

const BADGE_MAP = {
  'Culturel':   'bg-purple-500/15 text-purple-400',
  'Sport':      'bg-emerald-500/15 text-emerald-400',
  'Réunion':    'bg-blue-500/15 text-[var(--accent)]',
  'Académique': 'bg-orange-500/15 text-orange-400',
  'Examens':    'bg-red-500/15 text-red-400',
}
const categoryBadge = (name) => BADGE_MAP[name] ?? 'bg-white/[0.06] text-[#a0a8c0]'
const formatDate = (dt) => {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

// ── API ────────────────────────────────────────────────────────────────────
const fetchEvents = async () => {
  loadingEvents.value = true
  try {
    const { data } = await axios.get(`${url}/events/`)
    evenements.value = data
  } catch (e) { console.error('[Communaute] events:', e) }
  finally { loadingEvents.value = false }
}

const fetchNews = async () => {
  loadingNews.value = true
  try {
    const { data } = await axios.get(`${url}/news/`)
    actualites.value = data
  } catch (e) { console.error('[Communaute] news:', e) }
  finally { loadingNews.value = false }
}

// Ajoute les secondes manquantes pour FastAPI
const toISO = (dt) => dt ? (dt.length === 16 ? dt + ':00' : dt) : null

// ── CRUD Événements ────────────────────────────────────────────────────────
const openEventModal = (ev = null) => {
  editingEvent.value = ev
  eventImageFile.value = null
  eventImagePreview.value = ev?.image_url ?? null
  eventForm.value = ev
    ? { title: ev.title, description: ev.description ?? '', location: ev.location ?? '',
        start_date: ev.start_date?.slice(0, 16) ?? '', end_date: ev.end_date?.slice(0, 16) ?? '',
        audience: ev.audience, is_published: ev.is_published }
    : { title: '', description: '', location: '', start_date: '', end_date: '', audience: 'public', is_published: false }
  showEventModal.value = true
}

const handleEventImage = (e) => {
  const file = e.target.files[0]
  if (!file) return
  eventImageFile.value = file
  eventImagePreview.value = URL.createObjectURL(file)
}

const saveEvent = async () => {
  if (!eventForm.value.title) { Swal.fire({ icon: 'warning', title: 'Titre requis', background: '#0f1117', color: '#e8eaf0' }); return }
  if (!eventForm.value.start_date) { Swal.fire({ icon: 'warning', title: 'Date de début requise', background: '#0f1117', color: '#e8eaf0' }); return }
  savingEvent.value = true
  try {
    const payload = {
      ...eventForm.value,
      start_date: toISO(eventForm.value.start_date),
      end_date: toISO(eventForm.value.end_date) || null,
    }
    let eventId
    if (editingEvent.value) {
      await axios.put(`${url}/events/${editingEvent.value.id}`, payload)
      eventId = editingEvent.value.id
    } else {
      const { data } = await axios.post(`${url}/events/`, payload)
      eventId = data.id
    }
    // Upload image si sélectionnée
    if (eventImageFile.value && eventId) {
      const form = new FormData()
      form.append('file', eventImageFile.value)
      await axios.post(`${url}/events/${eventId}/upload-image`, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    showEventModal.value = false
    await fetchEvents()
  } catch (e) {
    const detail = e.response?.data?.detail
    Swal.fire({ icon: 'error', title: 'Erreur', text: Array.isArray(detail) ? detail.map(d => d.msg).join(', ') : (detail || 'Erreur inconnue'), background: '#0f1117', color: '#e8eaf0' })
  } finally { savingEvent.value = false }
}

const deleteEvent = async (id) => {
  const res = await Swal.fire({ title: 'Supprimer cet événement ?', icon: 'warning', showCancelButton: true,
    confirmButtonColor: '#ef4444', cancelButtonColor: '#374151', confirmButtonText: 'Supprimer', cancelButtonText: 'Annuler',
    background: '#0f1117', color: '#e8eaf0' })
  if (!res.isConfirmed) return
  try { await axios.delete(`${url}/events/${id}`); await fetchEvents() }
  catch (e) { Swal.fire({ icon: 'error', title: 'Erreur', text: e.response?.data?.detail || 'Erreur', background: '#0f1117', color: '#e8eaf0' }) }
}

// ── CRUD Actualités ────────────────────────────────────────────────────────
const openNewsModal = (a = null) => {
  editingNews.value = a
  newsImageFile.value = null
  newsImagePreview.value = a?.image_url ?? null
  newsForm.value = a
    ? { title: a.title, content: a.content ?? '', audience: a.audience, is_published: a.is_published }
    : { title: '', content: '', audience: 'public', is_published: false }
  showNewsModal.value = true
}

const handleNewsImage = (e) => {
  const file = e.target.files[0]
  if (!file) return
  newsImageFile.value = file
  newsImagePreview.value = URL.createObjectURL(file)
}

const saveNews = async () => {
  if (!newsForm.value.title) { Swal.fire({ icon: 'warning', title: 'Titre requis', background: '#0f1117', color: '#e8eaf0' }); return }
  savingNews.value = true
  try {
    let newsId
    if (editingNews.value) {
      await axios.put(`${url}/news/${editingNews.value.id}`, newsForm.value)
      newsId = editingNews.value.id
    } else {
      const { data } = await axios.post(`${url}/news/`, newsForm.value)
      newsId = data.id
    }
    if (newsImageFile.value && newsId) {
      const form = new FormData()
      form.append('file', newsImageFile.value)
      await axios.post(`${url}/news/${newsId}/upload-image`, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    showNewsModal.value = false
    await fetchNews()
  } catch (e) {
    const detail = e.response?.data?.detail
    Swal.fire({ icon: 'error', title: 'Erreur', text: Array.isArray(detail) ? detail.map(d => d.msg).join(', ') : (detail || 'Erreur inconnue'), background: '#0f1117', color: '#e8eaf0' })
  } finally { savingNews.value = false }
}

const deleteNews = async (id) => {
  const res = await Swal.fire({ title: 'Supprimer cette actualité ?', icon: 'warning', showCancelButton: true,
    confirmButtonColor: '#ef4444', cancelButtonColor: '#374151', confirmButtonText: 'Supprimer', cancelButtonText: 'Annuler',
    background: '#0f1117', color: '#e8eaf0' })
  if (!res.isConfirmed) return
  try { await axios.delete(`${url}/news/${id}`); await fetchNews() }
  catch (e) { Swal.fire({ icon: 'error', title: 'Erreur', text: e.response?.data?.detail || 'Erreur', background: '#0f1117', color: '#e8eaf0' }) }
}

onMounted(() => { fetchEvents(); fetchNews() })
</script>

<style scoped>
@keyframes fadeUp { from { opacity:0; transform:translateY(8px) } to { opacity:1; transform:translateY(0) } }
.line-clamp-2 { display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden }
.line-clamp-3 { display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden }
</style>

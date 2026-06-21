<template>
  <div class="min-h-screen bg-[#f4f6f9] font-sans animate-[fadeUp_0.4s_ease_both]">
    <div class=" mx-auto px-4 -mt-8 pb-16">

      <!-- STUDENT HERO -->
      <div class="bg-[#0d0d14] rounded-2xl p-7 flex flex-col sm:flex-row items-start sm:items-center gap-5 mb-6 relative overflow-hidden">

            <div class="absolute inset-0 opacity-20">
        <svg width="100%" height="100%"><defs><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="white" stroke-width="1"/></pattern></defs><rect width="100%" height="100%" fill="url(#grid)"/></svg>
      </div>

        <div class="absolute -top-12 -right-12 w-64 h-64 rounded-full bg-[#c9a84c]/10 blur-3xl pointer-events-none"></div>
        <div class="absolute bottom-2 right-6 font-serif text-6xl font-black text-white/[0.03] select-none pointer-events-none leading-none">"Savoir"</div>

        <div class="w-14 h-14 rounded-full bg-gradient-to-br from-[#c9a84c] to-[#8a6520] flex items-center justify-center font-serif text-xl font-bold text-white shrink-0 border-2 border-[#c9a84c]/40">
          {{ initials }}
        </div>
        <div class="flex-1 py-8">
          <h1 class="font-serif text-2xl font-bold text-white">{{ student.nom }}</h1>
          <p class="text-[#888] text-sm mt-1">{{ student.classe }} &nbsp;·&nbsp; {{ student.niveau }} &nbsp;·&nbsp; {{ student.annee }}</p>
          <div class="flex gap-2 mt-3 flex-wrap">
            <span class="bg-[#c9a84c]/20 text-[#c9a84c] border border-[#c9a84c]/30 px-3 py-1 rounded-full text-xs font-semibold">
              📚 {{ totalCours }} cours au programme
            </span>
            <span class="bg-[#1a7a4a]/20 text-[#4ade80] border border-[#1a7a4a]/30 px-3 py-1 rounded-full text-xs font-semibold">
              ✓ {{ coursReussis }} réussis
            </span>
            <!-- v-if="coursReprise > 0" -->
            <span  class="bg-[#e74c3c]/20 text-[#f87171] border border-[#e74c3c]/30 px-3 py-1 rounded-full text-xs font-semibold">
              ↺ {{ coursReprise || 0 }} en reprise
            </span>
          </div>
        </div>

        <!-- GLOBAL PROGRESS -->
        <div class="shrink-0 text-center">
          <div class="relative w-20 h-20">
            <svg class="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
              <circle cx="40" cy="40" r="32" fill="none" stroke="#1a1a2e" stroke-width="8"/>
              <circle cx="40" cy="40" r="32" fill="none" stroke="#c9a84c" stroke-width="8"
                stroke-dasharray="201"
                :stroke-dashoffset="201 - (201 * progressGlobal / 100)"
                stroke-linecap="round" class="transition-all duration-700"/>
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <span class="font-serif text-lg font-bold text-white">{{ progressGlobal }}%</span>
            </div>
          </div>
          <div class="text-[0.65rem] text-[#555] mt-1 tracking-widest uppercase">Progression</div>
        </div>
      </div>

      <!-- TABS -->
      <div class="flex gap-1 bg-white rounded-xl p-1.5 border border-[#e0dbd0] shadow-sm mb-5 overflow-x-auto scrollbar-hide">
        <button v-for="tab in tabs" :key="tab.key"
          @click="currentTab = tab.key"
          :class="currentTab === tab.key
            ? 'bg-[#0d0d14] text-white shadow-md'
            : 'text-[#777] hover:text-[#0d0d14] hover:bg-[#f5f5f0]'"
          class="shrink-0 flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer">
          <span>{{ tab.icon }}</span>{{ tab.label }}
          <span v-if="tab.count !== undefined"
            :class="currentTab === tab.key ? 'bg-[#c9a84c] text-[#0d0d14]' : 'bg-[#f0ece0] text-[#888]'"
            class="px-1.5 py-0.5 rounded-full text-[0.6rem] font-bold">
            {{ tab.count }}
          </span>
        </button>
      </div>

      <!-- ══════════ TAB: MATIÈRES ══════════ -->
      <template v-if="currentTab === 'matieres'">

        <!-- Search + Filter -->
        <div class="flex gap-3 mb-5 flex-wrap">
          <div class="relative flex-1 min-w-48">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[#bbb] text-sm">🔍</span>
            <input v-model="search" placeholder="Rechercher une matière..."
              class="w-full pl-9 pr-4 py-2.5 rounded-lg border border-[#e0dbd0] bg-white text-sm outline-none focus:border-[#c9a84c] shadow-sm"/>
          </div>
          <select v-model="filtreStatut"
            class="px-3 py-2.5 rounded-lg border border-[#e0dbd0] bg-white text-sm outline-none focus:border-[#c9a84c] cursor-pointer shadow-sm">
            <option value="tous">Tous les statuts</option>
            <option value="en_cours">En cours</option>
            <option value="reussi">Réussi</option>
            <option value="reprise">Reprise</option>
            <option value="non_commence">Non commencé</option>
          </select>
        </div>

        <!-- COURS GRID -->
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <div v-for="cours in filteredCours" :key="cours.id"
            @click="openDetail(cours)"
            class="bg-white rounded-xl border border-[#e8e4d8] shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all cursor-pointer overflow-hidden group">

            <!-- Color bar -->
            <div class="h-1.5 w-full" :style="{ background: cours.couleur }"></div>

            <div class="p-5">
              <div class="flex items-start justify-between gap-3 mb-3">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0"
                  :style="{ background: cours.couleur + '20' }">
                  {{ cours.emoji }}
                </div>
                <span :class="statutClass(cours.statut).pill" class="px-2.5 py-1 rounded-full text-[0.65rem] font-bold shrink-0">
                  {{ statutClass(cours.statut).label }}
                </span>
              </div>

              <h3 class="font-semibold text-[#0d0d14] text-sm leading-snug mb-1">{{ cours.nom }}</h3>
              <p class="text-[#aaa] text-xs mb-3">{{ cours.professeur }}</p>

              <!-- Progress -->
              <div class="mb-3">
                <div class="flex justify-between text-[0.65rem] text-[#bbb] mb-1">
                  <span>{{ cours.seances_faites }}/{{ cours.seances_total }} séances</span>
                  <span class="font-bold" :style="{ color: cours.couleur }">{{ cours.progression }}%</span>
                </div>
                <div class="bg-[#f0ece0] rounded-full h-1.5 overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-700"
                    :style="{ width: cours.progression + '%', background: cours.couleur }"></div>
                </div>
              </div>

              <!-- Footer -->
              <div class="flex items-center justify-between pt-3 border-t border-[#f5f5f0]">
                <div class="flex items-center gap-2">
                  <span class="text-[0.65rem] text-[#bbb]">Coef. {{ cours.coefficient }}</span>
                  <span class="text-[#e0dbd0]">·</span>
                  <span class="text-[0.65rem]" :class="cours.absences > 2 ? 'text-[#e74c3c]' : 'text-[#bbb]'">
                    {{ cours.absences }} abs.
                  </span>
                </div>
                <span v-if="cours.note !== null"
                  class="font-serif text-base font-bold"
                  :class="cours.note >= 10 ? 'text-[#1a7a4a]' : 'text-[#e74c3c]'">
                  {{ cours.note }}/20
                </span>
                <span v-else class="text-[0.68rem] text-[#c9a84c] font-semibold group-hover:underline">Voir →</span>
              </div>
            </div>
          </div>

          <div v-if="!filteredCours.length"
            class="col-span-3 py-16 text-center text-[#bbb] text-sm">
            Aucun cours trouvé
          </div>
        </div>
      </template>

      <!-- ══════════ TAB: EMPLOI DU TEMPS ══════════ -->
      <template v-if="currentTab === 'emploi'">
        <div class="bg-white rounded-xl border border-[#e8e4d8] shadow-sm overflow-hidden">
          <!-- Day tabs -->
          <div class="flex border-b border-[#f0ece0] overflow-x-auto scrollbar-hide">
            <button v-for="jour in joursActifs" :key="jour.key"
              @click="currentJour = jour.key"
              :class="currentJour === jour.key
                ? 'border-b-2 border-[#c9a84c] text-[#0d0d14] bg-[#fdfcf8]'
                : 'text-[#aaa] hover:text-[#0d0d14]'"
              class="shrink-0 px-5 py-3.5 text-xs font-semibold transition-all cursor-pointer">
              <div>{{ jour.label }}</div>
              <div class="text-[0.6rem] mt-0.5 font-normal" :class="currentJour === jour.key ? 'text-[#c9a84c]' : 'text-[#ddd]'">
                {{ emploiDuTemps[jour.key]?.length || 0 }} cours
              </div>
            </button>
          </div>

          <div class="p-5">
            <div v-if="emploiDuTemps[currentJour]?.length" class="space-y-3">
              <div v-for="(seance, i) in emploiDuTemps[currentJour]" :key="i"
                class="flex gap-4 items-stretch">
                <!-- Time -->
                <div class="text-right shrink-0 w-16 pt-1">
                  <div class="text-xs font-bold text-[#0d0d14]">{{ seance.heure_debut }}</div>
                  <div class="text-[0.65rem] text-[#bbb]">{{ seance.heure_fin }}</div>
                </div>
                <!-- Line -->
                <div class="flex flex-col items-center shrink-0">
                  <div class="w-2.5 h-2.5 rounded-full mt-1.5" :style="{ background: seance.couleur }"></div>
                  <div v-if="i < emploiDuTemps[currentJour].length - 1" class="w-px flex-1 bg-[#f0ece0] my-1"></div>
                </div>
                <!-- Card -->
                <div class="flex-1 rounded-xl p-4 mb-1 border transition-all hover:shadow-sm"
                  :style="{ borderLeftColor: seance.couleur, borderLeftWidth: '3px', borderColor: '#f0ece0', borderLeftColor: seance.couleur }">
                  <div class="flex justify-between items-start">
                    <div>
                      <div class="font-semibold text-sm text-[#0d0d14]">{{ seance.matiere }}</div>
                      <div class="text-xs text-[#aaa] mt-0.5">{{ seance.professeur }} · Salle {{ seance.salle }}</div>
                    </div>
                    <span class="text-lg">{{ seance.emoji }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="py-12 text-center text-[#bbb] text-sm">
              Aucun cours ce jour
            </div>
          </div>
        </div>
      </template>

      <!-- ══════════ TAB: RESSOURCES ══════════ -->
      <template v-if="currentTab === 'ressources'">
        <!-- {{ ressourcesParMatiere ==null }} -->
        <div v-if="ressourcesParMatiere ==null" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="(groupe, matiere) in ressourcesParMatiere" :key="matiere"
            class="bg-white rounded-xl border border-[#e8e4d8] shadow-sm overflow-hidden">
            <div class="px-5 py-3.5 border-b border-[#f0ece0] flex items-center gap-3">
              <span class="text-lg">{{ groupe.emoji }}</span>
              <span class="font-semibold text-sm text-[#0d0d14]">{{ matiere }}</span>
              <span class="ml-auto bg-[#f0ece0] text-[#888] text-[0.65rem] font-bold px-2 py-0.5 rounded-full">
                {{ groupe.fichiers.length }}
              </span>
            </div>
            <div class="divide-y divide-[#f5f5f0]">
              <div v-for="(f, i) in groupe.fichiers" :key="i"
                class="px-5 py-3 flex items-center gap-3 hover:bg-[#faf8f3] transition-colors group cursor-pointer">
                <div class="w-8 h-8 rounded-lg flex items-center justify-center text-sm shrink-0"
                  :class="f.type === 'pdf' ? 'bg-[#fdecea] text-[#e74c3c]' : f.type === 'doc' ? 'bg-[#e8eef8] text-[#1a3a6b]' : 'bg-[#fdf6e3] text-[#c9a84c]'">
                  {{ f.type === 'pdf' ? '📄' : f.type === 'doc' ? '📝' : '🖼' }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-[#0d0d14] truncate">{{ f.nom }}</div>
                  <div class="text-[0.65rem] text-[#bbb]">{{ f.taille }} · {{ f.date }}</div>
                </div>
                <span class="text-[0.68rem] font-semibold text-[#c9a84c] opacity-0 group-hover:opacity-100 transition-opacity">⬇</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="py-2 rounded-md bg-red-100">
          <p class="text-center text-red-500 text-xl">Aucune ressources enregistrée</p>
        </div>
      </template>

      <!-- ══════════ TAB: ABSENCES ══════════ -->
      <template v-if="currentTab === 'absences'">
        <!-- Stats -->
        <div class="grid grid-cols-3 gap-4 mb-5">
          <div class="bg-white rounded-xl p-5 border border-[#e8e4d8] shadow-sm relative overflow-hidden">
            <div class="absolute top-0 left-0 right-0 h-[3px] bg-[#e74c3c]"></div>
            <div class="text-[0.65rem] font-semibold tracking-widest uppercase text-[#999] mb-1.5">Total absences</div>
            <div class="font-serif text-3xl font-bold text-[#e74c3c]">{{ totalAbsences }}</div>
            <div class="text-xs text-[#bbb] mt-1">toutes matières</div>
          </div>
          <div class="bg-white rounded-xl p-5 border border-[#e8e4d8] shadow-sm relative overflow-hidden">
            <div class="absolute top-0 left-0 right-0 h-[3px] bg-[#c9a84c]"></div>
            <div class="text-[0.65rem] font-semibold tracking-widest uppercase text-[#999] mb-1.5">Justifiées</div>
            <div class="font-serif text-3xl font-bold text-[#c9a84c]">{{ absencesJustifiees }}</div>
            <div class="text-xs text-[#bbb] mt-1">avec justificatif</div>
          </div>
          <div class="bg-white rounded-xl p-5 border border-[#e8e4d8] shadow-sm relative overflow-hidden">
            <div class="absolute top-0 left-0 right-0 h-[3px] bg-[#1a3a6b]"></div>
            <div class="text-[0.65rem] font-semibold tracking-widest uppercase text-[#999] mb-1.5">Non justifiées</div>
            <div class="font-serif text-3xl font-bold text-[#1a3a6b]">{{ totalAbsences - absencesJustifiees }}</div>
            <div class="text-xs text-[#bbb] mt-1">sans justificatif</div>
          </div>
        </div>

        <div class="bg-white rounded-xl border border-[#e8e4d8] shadow-sm overflow-hidden">
          <table class="w-full border-collapse">
            <thead>
              <tr class="bg-[#0d0d14]">
                <th class="px-5 py-3.5 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#c9a84c]">Matière</th>
                <th class="px-5 py-3.5 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#888]">Date</th>
                <th class="px-5 py-3.5 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#888] hidden sm:table-cell">Séance</th>
                <th class="px-5 py-3.5 text-left text-[0.68rem] font-semibold tracking-widest uppercase text-[#888]">Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(abs, i) in listeAbsences" :key="i"
                class="border-t border-[#f0ece0] hover:bg-[#faf8f3] transition-colors">
                <td class="px-5 py-3.5 text-sm font-semibold text-[#0d0d14]">{{ abs.matiere }}</td>
                <td class="px-5 py-3.5 text-sm text-[#888]">{{ abs.date }}</td>
                <td class="px-5 py-3.5 text-sm text-[#aaa] hidden sm:table-cell">{{ abs.seance }}</td>
                <td class="px-5 py-3.5">
                  <span :class="abs.justifie ? 'bg-[#fdf6e3] text-[#9a7a20]' : 'bg-[#fdecea] text-[#e74c3c]'"
                    class="px-2.5 py-1 rounded-full text-[0.65rem] font-bold">
                    {{ abs.justifie ? '✓ Justifiée' : '✗ Non justifiée' }}
                  </span>
                </td>
              </tr>
              <tr v-if="!listeAbsences.length">
                <td colspan="4" class="px-5 py-10 text-center text-[#bbb] text-sm">Aucune absence enregistrée</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <!-- ══════════ TAB: SUIVI (réussi / reprise) ══════════ -->
      <template v-if="currentTab === 'suivi'">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <!-- RÉUSSIS -->
          <div>
            <div class="flex items-center gap-3 mb-3">
              <span class="font-serif text-base font-bold text-[#0d0d14]">Cours réussis</span>
              <div class="flex-1 h-px bg-[#e0dbd0]"></div>
              <span class="bg-[#e8f5ee] text-[#1a7a4a] text-xs font-bold px-2.5 py-1 rounded-full">{{ coursReussisList.length }}</span>
            </div>
            <div class="space-y-3">
              <div v-for="c in coursReussisList" :key="c.id"
                class="bg-white rounded-xl p-4 border border-[#e8e4d8] shadow-sm flex items-center gap-4 hover:-translate-y-0.5 hover:shadow-md transition-all">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0"
                  :style="{ background: c.couleur + '20' }">{{ c.emoji }}</div>
                <div class="flex-1 min-w-0">
                  <div class="font-semibold text-sm text-[#0d0d14] truncate">{{ c.nom }}</div>
                  <div class="text-xs text-[#aaa]">{{ c.professeur }}</div>
                </div>
                <div class="text-right shrink-0">
                  <div class="font-serif text-xl font-bold text-[#1a7a4a]">{{ c.note }}/20</div>
                  <div class="text-[0.65rem] text-[#1a7a4a] font-semibold">✓ Réussi</div>
                </div>
              </div>
              <div v-if="!coursReussisList.length" class="py-8 text-center text-[#bbb] text-sm bg-white rounded-xl border border-[#e8e4d8]">
                Aucun cours réussi pour l'instant
              </div>
            </div>
          </div>

          <!-- REPRISES -->
          <div>
            <div class="flex items-center gap-3 mb-3">
              <span class="font-serif text-base font-bold text-[#0d0d14]">Cours en reprise</span>
              <div class="flex-1 h-px bg-[#e0dbd0]"></div>
              <span class="bg-[#fdecea] text-[#e74c3c] text-xs font-bold px-2.5 py-1 rounded-full">{{ coursRepriseList.length }}</span>
            </div>
            <div class="space-y-3">
              <div v-for="c in coursRepriseList" :key="c.id"
                class="bg-white rounded-xl p-4 border border-[#fde8e8] shadow-sm flex items-center gap-4 hover:-translate-y-0.5 hover:shadow-md transition-all">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0 bg-[#fdecea]">{{ c.emoji }}</div>
                <div class="flex-1 min-w-0">
                  <div class="font-semibold text-sm text-[#0d0d14] truncate">{{ c.nom }}</div>
                  <div class="text-xs text-[#aaa]">{{ c.professeur }}</div>
                  <div class="text-[0.65rem] text-[#e74c3c] mt-0.5 font-semibold">↺ Reprise — {{ c.date_reprise }}</div>
                </div>
                <div class="text-right shrink-0">
                  <div class="font-serif text-xl font-bold text-[#e74c3c]">{{ c.note }}/20</div>
                  <div class="text-[0.65rem] text-[#e74c3c] font-semibold">✗ Échec</div>
                </div>
              </div>
              <div v-if="!coursRepriseList.length" class="py-8 text-center text-[#bbb] text-sm bg-white rounded-xl border border-[#e8e4d8]">
                Aucune reprise 🎉
              </div>
            </div>
          </div>
        </div>
      </template>

    </div>

    <!-- ══════════ MODAL DÉTAIL COURS ══════════ -->
    <Transition name="modal">
      <div v-if="selectedCours"
        class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4"
        @click.self="selectedCours = null">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="selectedCours = null"></div>
        <div class="relative bg-white w-full sm:max-w-lg rounded-t-2xl sm:rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] overflow-y-auto z-10">

          <!-- Header -->
          <div class="h-2 w-full" :style="{ background: selectedCours.couleur }"></div>
          <div class="p-6 border-b border-[#f0ece0]">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shrink-0"
                :style="{ background: selectedCours.couleur + '20' }">
                {{ selectedCours.emoji }}
              </div>
              <div class="flex-1">
                <h2 class="font-serif text-xl font-bold text-[#0d0d14]">{{ selectedCours.nom }}</h2>
                <p class="text-[#aaa] text-sm mt-0.5">{{ selectedCours.professeur }}</p>
              </div>
              <button @click="selectedCours = null"
                class="w-8 h-8 rounded-full bg-[#f0ece0] flex items-center justify-center text-[#888] hover:bg-[#e0dbd0] transition-colors cursor-pointer text-lg">
                ×
              </button>
            </div>
          </div>

          <div class="p-6 space-y-5">

            <!-- Stats row -->
            <div class="grid grid-cols-3 gap-3">
              <div class="bg-[#faf8f3] rounded-xl p-3 text-center">
                <div class="font-serif text-xl font-bold" :style="{ color: selectedCours.couleur }">{{ selectedCours.progression }}%</div>
                <div class="text-[0.65rem] text-[#aaa] mt-0.5">Progression</div>
              </div>
              <div class="bg-[#faf8f3] rounded-xl p-3 text-center">
                <div class="font-serif text-xl font-bold text-[#0d0d14]">{{ selectedCours.seances_faites }}/{{ selectedCours.seances_total }}</div>
                <div class="text-[0.65rem] text-[#aaa] mt-0.5">Séances</div>
              </div>
              <div class="bg-[#faf8f3] rounded-xl p-3 text-center">
                <div class="font-serif text-xl font-bold" :class="selectedCours.absences > 2 ? 'text-[#e74c3c]' : 'text-[#0d0d14]'">{{ selectedCours.absences }}</div>
                <div class="text-[0.65rem] text-[#aaa] mt-0.5">Absences</div>
              </div>
            </div>

            <!-- Progress bar -->
            <div>
              <div class="flex justify-between text-xs text-[#aaa] mb-2">
                <span>Avancement du programme</span>
                <span class="font-bold" :style="{ color: selectedCours.couleur }">{{ selectedCours.progression }}%</span>
              </div>
              <div class="bg-[#f0ece0] rounded-full h-2.5 overflow-hidden">
                <div class="h-full rounded-full transition-all duration-700"
                  :style="{ width: selectedCours.progression + '%', background: selectedCours.couleur }"></div>
              </div>
            </div>

            <!-- Note -->
            <div v-if="selectedCours.note !== null"
              class="flex items-center justify-between p-4 rounded-xl"
              :class="selectedCours.note >= 10 ? 'bg-[#e8f5ee]' : 'bg-[#fdecea]'">
              <div>
                <div class="text-xs font-semibold" :class="selectedCours.note >= 10 ? 'text-[#1a7a4a]' : 'text-[#e74c3c]'">
                  Note obtenue
                </div>
                <div class="text-[0.68rem]" :class="selectedCours.note >= 10 ? 'text-[#1a7a4a]/70' : 'text-[#e74c3c]/70'">
                  {{ selectedCours.note >= 10 ? 'Cours réussi ✓' : 'Reprise requise ↺' }}
                </div>
              </div>
              <div class="font-serif text-3xl font-bold"
                :class="selectedCours.note >= 10 ? 'text-[#1a7a4a]' : 'text-[#e74c3c]'">
                {{ selectedCours.note }}/20
              </div>
            </div>

            <!-- Infos -->
            <div class="space-y-2.5">
              <div class="flex items-center justify-between py-2.5 border-b border-[#f5f5f0]">
                <span class="text-xs text-[#aaa]">Coefficient</span>
                <span class="text-sm font-semibold text-[#0d0d14]">{{ selectedCours.coefficient }}</span>
              </div>
              <div class="flex items-center justify-between py-2.5 border-b border-[#f5f5f0]">
                <span class="text-xs text-[#aaa]">Horaire hebdo</span>
                <span class="text-sm font-semibold text-[#0d0d14]">{{ selectedCours.heures_semaine }}h / semaine</span>
              </div>
              <div class="flex items-center justify-between py-2.5 border-b border-[#f5f5f0]">
                <span class="text-xs text-[#aaa]">Statut</span>
                <span :class="statutClass(selectedCours.statut).pill" class="px-2.5 py-1 rounded-full text-[0.65rem] font-bold">
                  {{ statutClass(selectedCours.statut).label }}
                </span>
              </div>
              <div v-if="selectedCours.description" class="pt-1">
                <div class="text-xs text-[#aaa] mb-1.5">Description</div>
                <p class="text-sm text-[#555] leading-relaxed">{{ selectedCours.description }}</p>
              </div>
            </div>
 

          </div>
 

        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup> 
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia';
import axios from 'axios';
 

const authStore = useAuthStore(); 
/* ══════════════════════════════════════════
   PROPS — brancher vos données API ici
   ══════════════════════════════════════════ */
const props = defineProps({
  coursData: { type: Object, default: null }
})
const localData = ref(props.coursData)
/* ── STUDENT ── */
const student = ref({
  nom: 'Jean-David Pierre',
  classe: 'Terminale A',
  niveau: 'Secondaire',
  annee: '2024–2025',
})
const initials = computed(() => {
  const p = student.value.nom?.split(' ') || []
  return (p[0]?.[0] || '') + (p[1]?.[0] || '')
})

// Mapping emoji par nom de cours
const emojiMap = {
  'Sport': '⚽', 'Poésie': '✍️', 'Histoire': '🏛', 'Sciences': '🔬',
  'Calcul Mental': '🧮', 'Grammaire': '📝', 'Orthographe': '🔤',
  'Lecture': '📖', 'Opération / Numération': '➕', 'Problème': '🧩',
  'Géographie': '🌍', 'Anglais': '🇬🇧', 'Civisme': '🏛', 'Géometrie': '📐',
  'Bible': '✝️', 'Ecriture': '✏️', 'Travaux Manuels': '🔨',
}

const couleurMap = [
  '#8b5cf6','#3b82f6','#ef4444','#f59e0b','#10b981',
  '#f97316','#06b6d4','#84cc16','#ec4899','#6366f1',
  '#14b8a6','#a855f7','#e11d48','#0ea5e9','#22c55e',
  '#f43f5e','#8b5cf6',
]

const coursList = computed(() => {
  const raw = props.coursData?.data || localData.value

  // Si données API disponibles → mapper
  if (Array.isArray(raw) && raw.length && raw[0].cours) {
    return raw.map((c, i) => ({
      id:             c.id,
      nom:            c.cours,
      professeur:     `${c.prof_nom} ${c.prenom}`,
      emoji:          emojiMap[c.cours] || '📚',
      couleur:        couleurMap[i % couleurMap.length],
      coefficient:    c.coefficients,
      seances_faites: 0,       // pas dans l'API → 0 par défaut
      seances_total:  0,       // pas dans l'API → 0 par défaut
      absences:       0,       // pas dans l'API → 0 par défaut
      note:           null,    // pas dans l'API → null
      statut:         'en_cours',
      heures_semaine: c.heure || 0,
      description:    `${c.cours}  —  ${c.niveau_name}`, //— Session ${c.session}`,
      progression:    0,
      jours:          c.jours,
      session:        c.session,
      classe:         c.classe,
      niveau:         c.niveau_name,
    }))
  }

  // Sinon → données démo
  return [
  { id: 1,  nom: 'Philosophie',      professeur: 'Prof. Descartes',  emoji: '🧠', couleur: '#8b5cf6', coefficient: 4, seances_faites: 22, seances_total: 24, absences: 0, note: 18,   statut: 'reussi',       heures_semaine: 4, description: 'Étude des grandes pensées philosophiques occidentales et haïtiennes.', progression: 92 },
  { id: 2,  nom: 'Français',         professeur: 'Prof. Leconte',    emoji: '✍️', couleur: '#3b82f6', coefficient: 4, seances_faites: 20, seances_total: 24, absences: 1, note: 16,   statut: 'reussi',       heures_semaine: 4, description: 'Littérature, grammaire et expression écrite.',                          progression: 83 },
  { id: 3,  nom: 'Mathématiques',    professeur: 'Prof. Euler',      emoji: '📐', couleur: '#ef4444', coefficient: 3, seances_faites: 16, seances_total: 24, absences: 3, note: 8,    statut: 'reprise',      heures_semaine: 3, description: 'Algèbre, géométrie et analyse mathématique.',                           progression: 67 },
  { id: 4,  nom: 'Histoire-Géo',     professeur: 'Prof. Toussaint',  emoji: '🌍', couleur: '#f59e0b', coefficient: 3, seances_faites: 18, seances_total: 24, absences: 1, note: 15,   statut: 'reussi',       heures_semaine: 3, description: 'Histoire d\'Haïti, des Amériques et géographie mondiale.',            progression: 75 },
  { id: 5,  nom: 'Anglais',          professeur: 'Prof. Shakespeare', emoji: '🇬🇧', couleur: '#10b981', coefficient: 3, seances_faites: 21, seances_total: 24, absences: 0, note: 17,  statut: 'reussi',       heures_semaine: 3, description: 'Langue anglaise : oral, écrit et compréhension.',                        progression: 88 },
  { id: 6,  nom: 'Espagnol',         professeur: 'Prof. Cervantes',  emoji: '🇪🇸', couleur: '#f97316', coefficient: 2, seances_faites: 14, seances_total: 20, absences: 2, note: null, statut: 'en_cours',     heures_semaine: 2, description: 'Introduction à la langue et culture hispanophone.',                      progression: 70 },
  { id: 7,  nom: 'Sciences Nat.',    professeur: 'Prof. Darwin',     emoji: '🔬', couleur: '#06b6d4', coefficient: 2, seances_faites: 10, seances_total: 20, absences: 2, note: null, statut: 'en_cours',     heures_semaine: 2, description: 'Biologie, chimie et sciences de la nature.',                            progression: 50 },
  { id: 8,  nom: 'Éd. Physique',     professeur: 'Prof. Usain',      emoji: '⚽', couleur: '#84cc16', coefficient: 1, seances_faites: 12, seances_total: 16, absences: 1, note: 17,   statut: 'reussi',       heures_semaine: 2, description: 'Sport, santé et développement physique.',                               progression: 75 },
  { id: 9,  nom: 'Créole',           professeur: 'Prof. Morisseau',  emoji: '🏝', couleur: '#ec4899', coefficient: 2, seances_faites: 8,  seances_total: 20, absences: 0, note: null, statut: 'non_commence', heures_semaine: 2, description: 'Langue et culture créole haïtienne.',                                    progression: 40 },
  { id: 10, nom: 'Informatique',     professeur: 'Prof. Turing',     emoji: '💻', couleur: '#6366f1', coefficient: 2, seances_faites: 15, seances_total: 20, absences: 0, note: null, statut: 'en_cours',     heures_semaine: 2, description: 'Initiation à l\'algorithmique et aux outils numériques.',              progression: 75 },
]
})
 

/* ── TABS ── */
const currentTab = ref('matieres')
const totalCours    = computed(() => coursList.value.length)
const coursReussis  = computed(() => coursList.value.filter(c => c.statut === 'reussi').length)
const coursReprise  = computed(() => coursList.value.filter(c => c.statut === 'reprise').length)
const totalAbsences = computed(() => coursList.value.reduce((a, c) => a + c.absences, 0))
const progressGlobal = computed(() => {
  const total = coursList.value.reduce((a, c) => a + c.progression, 0)
  return Math.round(total / coursList.value.length)
})

const tabs = computed(() => [
  { key: 'matieres',  icon: '📚', label: 'Matières',     count: totalCours.value },
  { key: 'emploi',    icon: '🗓', label: 'Emploi du temps' },
  { key: 'ressources',icon: '📁', label: 'Ressources' },
  { key: 'absences',  icon: '📋', label: 'Absences',     count: totalAbsences.value },
  { key: 'suivi',     icon: '📊', label: 'Suivi' },
])

/* ── FILTERS ── */
const search = ref('')
const filtreStatut = ref('tous')
const filteredCours = computed(() =>
  coursList.value.filter(c => {
    const matchSearch = c.nom.toLowerCase().includes(search.value.toLowerCase()) ||
                        c.professeur.toLowerCase().includes(search.value.toLowerCase())
    const matchStatut = filtreStatut.value === 'tous' || c.statut === filtreStatut.value
    return matchSearch && matchStatut
  })
)

/* ── SUIVI LISTS ── */
const coursReussisList  = computed(() => coursList.value.filter(c => c.statut === 'reussi'))
const coursRepriseList  = computed(() => coursList.value.filter(c => c.statut === 'reprise').map(c => ({ ...c, date_reprise: 'Mar 2025' })))

/* ── MODAL ── */
const selectedCours = ref(null)
function openDetail(cours) { selectedCours.value = cours }

/* ── STATUT HELPER ── */
function statutClass(statut) {
  const map = {
    reussi:        { pill: 'bg-[#e8f5ee] text-[#1a7a4a]',  label: '✓ Réussi' },
    en_cours:      { pill: 'bg-[#e8eef8] text-[#1a3a6b]',  label: '▶ En cours' },
    reprise:       { pill: 'bg-[#fdecea] text-[#e74c3c]',  label: '↺ Reprise' },
    non_commence:  { pill: 'bg-[#f0ece0] text-[#aaa]',      label: '○ À venir' },
  }
  return map[statut] || map.non_commence
}

/* ── EMPLOI DU TEMPS ── */
const jours = [
  { key: 'lundi',    label: 'Lundi' },
  { key: 'mardi',    label: 'Mardi' },
  { key: 'mercredi', label: 'Mercredi' },
  { key: 'jeudi',    label: 'Jeudi' },
  { key: 'vendredi', label: 'Vendredi' },
  { key: 'samedi', label: 'Samedi' },
  { key: 'dimanche', label: 'Dimanche' },
]
const currentJour = ref('lundi')

const joursMap = {
  'Lundi': 'lundi', 'Mardi': 'mardi', 'Mercredi': 'mercredi',
  'Jeudi': 'jeudi', 'Vendredi': 'vendredi', 'Samedi': 'samedi'
}

const joursActifs = computed(() =>
  jours.filter(j => emploiDuTemps.value[j.key]?.length > 0)
)

const emploiDuTemps = computed(() => {
  const result = {
    lundi: [], mardi: [], mercredi: [], jeudi: [], vendredi: [], samedi: []
  }

  coursList.value.forEach(c => {
    const key = joursMap[c.jours]
    if (!key) return

    result[key].push({
      heure_debut: c.heure?.split('-')[0]?.trim() || '08:00',
      heure_fin:   c.heure?.split('-')[1]?.trim() || '09:00',
      matiere:     c.nom,
      professeur:  c.professeur,
      salle:       '—',
      emoji:       c.emoji,
      couleur:     c.couleur,
    })
  })

  return result
})

// const emploiDuTemps = {
//   lundi:    [
//     { heure_debut: '08:00', heure_fin: '09:30', matiere: 'Philosophie',    professeur: 'Prof. Descartes',  salle: '12', emoji: '🧠', couleur: '#8b5cf6' },
//     { heure_debut: '09:45', heure_fin: '11:15', matiere: 'Mathématiques',  professeur: 'Prof. Euler',      salle: '08', emoji: '📐', couleur: '#ef4444' },
//     { heure_debut: '13:00', heure_fin: '14:30', matiere: 'Anglais',        professeur: 'Prof. Shakespeare',salle: '05', emoji: '🇬🇧', couleur: '#10b981' },
//   ],
//   mardi:    [
//     { heure_debut: '08:00', heure_fin: '09:30', matiere: 'Français',       professeur: 'Prof. Leconte',    salle: '10', emoji: '✍️', couleur: '#3b82f6' },
//     { heure_debut: '09:45', heure_fin: '11:15', matiere: 'Histoire-Géo',   professeur: 'Prof. Toussaint',  salle: '14', emoji: '🌍', couleur: '#f59e0b' },
//     { heure_debut: '14:00', heure_fin: '15:30', matiere: 'Informatique',   professeur: 'Prof. Turing',     salle: 'Lab', emoji: '💻', couleur: '#6366f1' },
//   ],
//   mercredi: [
//     { heure_debut: '08:00', heure_fin: '09:30', matiere: 'Sciences Nat.',  professeur: 'Prof. Darwin',     salle: 'Lab', emoji: '🔬', couleur: '#06b6d4' },
//     { heure_debut: '10:00', heure_fin: '11:00', matiere: 'Éd. Physique',   professeur: 'Prof. Usain',      salle: 'Gym', emoji: '⚽', couleur: '#84cc16' },
//   ],
//   jeudi:    [
//     { heure_debut: '08:00', heure_fin: '09:30', matiere: 'Mathématiques',  professeur: 'Prof. Euler',      salle: '08', emoji: '📐', couleur: '#ef4444' },
//     { heure_debut: '09:45', heure_fin: '11:15', matiere: 'Espagnol',       professeur: 'Prof. Cervantes',  salle: '06', emoji: '🇪🇸', couleur: '#f97316' },
//     { heure_debut: '13:00', heure_fin: '14:30', matiere: 'Créole',         professeur: 'Prof. Morisseau',  salle: '11', emoji: '🏝', couleur: '#ec4899' },
//   ],
//   vendredi: [
//     { heure_debut: '08:00', heure_fin: '09:30', matiere: 'Français',       professeur: 'Prof. Leconte',    salle: '10', emoji: '✍️', couleur: '#3b82f6' },
//     { heure_debut: '09:45', heure_fin: '11:15', matiere: 'Philosophie',    professeur: 'Prof. Descartes',  salle: '12', emoji: '🧠', couleur: '#8b5cf6' },
//     { heure_debut: '13:00', heure_fin: '14:00', matiere: 'Éd. Physique',   professeur: 'Prof. Usain',      salle: 'Gym', emoji: '⚽', couleur: '#84cc16' },
//   ],
// }

/* ── RESSOURCES ── */
const ressourcesParMatiere = {
  // 'Philosophie': {
  //   emoji: '🧠',
  //   fichiers: [
  //     { nom: 'Introduction à Descartes.pdf',  type: 'pdf', taille: '2.3 MB', date: '10 jan.' },
  //     { nom: 'Dissertation modèle.pdf',        type: 'pdf', taille: '1.1 MB', date: '18 jan.' },
  //   ]
  // },
  // 'Mathématiques': {
  //   emoji: '📐',
  //   fichiers: [
  //     { nom: 'Cours algèbre ch.3.pdf',         type: 'pdf', taille: '3.8 MB', date: '5 nov.' },
  //     { nom: 'Exercices corrigés.pdf',          type: 'pdf', taille: '1.5 MB', date: '12 nov.' },
  //     { nom: 'Formules bac.doc',                type: 'doc', taille: '0.4 MB', date: '20 nov.' },
  //   ]
  // },
  // 'Histoire-Géo': {
  //   emoji: '🌍',
  //   fichiers: [
  //     { nom: 'Carte Haïti coloniale.png',       type: 'img', taille: '1.2 MB', date: '8 déc.' },
  //     { nom: 'Chronologie indépendance.pdf',    type: 'pdf', taille: '0.8 MB', date: '15 déc.' },
  //   ]
  // },
  // 'Anglais': {
  //   emoji: '🇬🇧',
  //   fichiers: [
  //     { nom: 'Vocabulary list unit 4.pdf',      type: 'pdf', taille: '0.6 MB', date: '3 jan.' },
  //     { nom: 'Grammar exercises.pdf',           type: 'pdf', taille: '1.0 MB', date: '17 jan.' },
  //   ]
  // },
}

/* ── ABSENCES ── */
const listeAbsences = computed(() => {
  const abs = []
  coursList.value.forEach(c => {
    for (let i = 0; i < c.absences; i++) {
      abs.push({
        matiere: c.nom,
        date: `${10 + i} nov. 2024`,
        seance: `${8 + i * 2}:00 – ${9 + i * 2}:30`,
        justifie: i === 0,
      })
    }
  })
  return abs
})
const programme = ref({
  annee_academique_id: '',
  class_id: ''
});
const absencesJustifiees = computed(() => listeAbsences.value.filter(a => a.justifie).length)

onMounted(async () => {
    if (!authStore.user) await authStore.initializeAuth();
  // setTimeout(() => { animated.value = true }, 100)
  const { data } = await axios.get(`/etudiant/${authStore.user.user.userable_id}`)
  console.log(data);
  const etudiant = data.data
  const dernierClasseEtudiant = etudiant.classes_etudiant?.at(-1);  
  const dernierEtudiantFaculte = etudiant.etudiant_facultes?.at(-1);
  const last_year = dernierClasseEtudiant?.annee_academiques?.annee_academique || "Non definie"

  student.value = {
  nom: `${etudiant.prenom} ${etudiant.nom}`,
  classe: dernierClasseEtudiant.classes.nom_classe,
  niveau: dernierClasseEtudiant.niveaux.name,
  annee: dernierClasseEtudiant.annee_academiques.annee_academique,
}

  programme.value={
    annee_academique_id: dernierClasseEtudiant.annee_academiques.id,
    class_id: dernierClasseEtudiant.classes.id
  }

  reload_data_programme()
})

const reload_data_programme = async ()=>  {  
    
    try {      
  const response = await axios.post('/programme-and-student-cours', {
    ...programme.value
  });
  
  const data = response.data 
  localData.value = response.data
  console.log('Données reçues response:', data); 
  
} catch (error) {
  console.log('Erreur:', error.response?.data || error.message);
}
  
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

.font-serif { font-family: 'Playfair Display', serif; }
.font-sans  { font-family: 'DM Sans', sans-serif; }

.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
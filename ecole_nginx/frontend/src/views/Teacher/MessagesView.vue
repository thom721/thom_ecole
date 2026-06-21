<!-- src/views/MessagesView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Messages</h1>
        <p class="text-[#7c83a0] text-sm">3 messages non lus</p>
      </div>
      <button class="px-4 py-2 text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">+ Nouveau message</button>
    </div>

    <div class="grid md:grid-cols-[300px_1fr] bg-[#171b26] border border-white/[0.07] rounded-2xl overflow-hidden min-h-[500px]">

      <!-- List -->
      <div class="border-b md:border-b-0 md:border-r border-white/[0.07] overflow-y-auto">
        <div
          v-for="m in messages" :key="m.id"
          @click="selected = m.id"
          class="flex items-start gap-3 p-4 border-b border-white/[0.05] cursor-pointer transition-colors last:border-0"
          :class="selected===m.id ? 'bg-[rgba(79,142,247,0.08)]' : 'hover:bg-white/[0.03]'"
          :style="selected===m.id ? { background: 'color-mix(in srgb, var(--accent,#4f8ef7) 8%, transparent)' } : {}"
        >
          <div class="w-9 h-9 rounded-full flex items-center justify-center text-[12px] font-bold text-[#0f1117] flex-shrink-0" :style="{ background: m.color }">{{ m.initials }}</div>
          <div class="flex-1 min-w-0">
            <p class="text-[13px] text-[#b0b5cc] truncate" :class="!m.read ? 'font-bold text-[#e8eaf0]' : ''">{{ m.from }}</p>
            <p class="text-[11.5px] text-[#7c83a0] truncate mt-0.5">{{ m.snippet }}</p>
          </div>
          <div class="flex flex-col items-end gap-1.5 flex-shrink-0">
            <span class="text-[11px] text-[#7c83a0]">{{ m.time }}</span>
            <span v-if="!m.read" class="w-2 h-2 rounded-full" :style="{ background: 'var(--accent,#4f8ef7)' }" />
          </div>
        </div>
      </div>

      <!-- Detail -->
      <div class="p-6 flex flex-col gap-4">
        <template v-if="active">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full flex items-center justify-center text-[14px] font-bold text-[#0f1117]" :style="{ background: active.color }">{{ active.initials }}</div>
            <div>
              <p class="text-[15px] font-semibold text-[#e8eaf0]">{{ active.from }}</p>
              <p class="text-[12px] text-[#7c83a0]">{{ active.time }}</p>
            </div>
          </div>
          <p class="text-[18px] font-semibold text-[#e8eaf0]" style="font-family:'Playfair Display',serif">{{ active.subject }}</p>
          <p class="text-[13.5px] text-[#b0b5cc] leading-relaxed whitespace-pre-line flex-1">{{ active.body }}</p>
          <div class="flex flex-col gap-2.5 pt-4 border-t border-white/[0.07]">
            <textarea
              class="w-full bg-[#1e2335] border border-white/10 rounded-xl px-4 py-3 text-[#e8eaf0] text-sm resize-none outline-none focus:border-white/20 transition-colors"
              placeholder="Écrire une réponse…" rows="3"
            />
            <button class="self-end px-5 py-2 text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">Envoyer</button>
          </div>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
const selected = ref(1)
const messages = [
  { id:1, from:'Léa Aubert',      initials:'LA', color:'linear-gradient(135deg,#6ee7b7,#4f8ef7)',  time:'10:32', read:false, subject:'Question sur le chapitre 4',  snippet:'Bonjour madame, j\'avais une question…', body:'Bonjour Madame,\n\nJ\'avais une question concernant l\'exercice 3 du chapitre 4 sur l\'intégration. Je ne comprends pas pourquoi on change les bornes lors d\'un changement de variable.\n\nPourriez-vous me réexpliquer ?\n\nMerci,\nLéa Aubert' },
  { id:2, from:'M. Directeur',    initials:'MD', color:'linear-gradient(135deg,#f59e0b,#f87171)',  time:'09:15', read:false, subject:'Réunion pédagogique Vendredi', snippet:'Rappel : réunion vendredi 14h…',           body:'Bonjour,\n\nJe vous rappelle la réunion pédagogique de ce vendredi 21 Février à 14h00 en salle des professeurs.\n\nOrdre du jour : résultats du 2e trimestre, projet numérique.\n\nCordialement,\nM. Le Directeur' },
  { id:3, from:'Thomas Morin',    initials:'TM', color:'linear-gradient(135deg,#a78bfa,#4f8ef7)',  time:'Hier',  read:false, subject:'Absence mercredi',            snippet:'Je serai absent mercredi…',               body:'Bonjour Madame,\n\nJe vous informe que je serai absent le mercredi 19 Février pour une consultation médicale. Pourriez-vous me transmettre les exercices ?\n\nCordialement,\nThomas Morin' },
  { id:4, from:'Mme. Fontaine',   initials:'MF', color:'linear-gradient(135deg,#22d3ee,#6ee7b7)',  time:'Lun',   read:true,  subject:'Échange emploi du temps',     snippet:'Serait-il possible d\'échanger…',         body:'Bonjour Marie,\n\nSerait-il possible d\'échanger nos salles pour jeudi prochain ? La salle A3 est plus adaptée pour mon TP.\n\nMerci,\nMme Fontaine' },
  { id:5, from:'Parent d\'élève', initials:'PA', color:'linear-gradient(135deg,#f87171,#f59e0b)',  time:'Sam',   read:true,  subject:'RDV concernant Clément',      snippet:'Je souhaiterais prendre RDV…',            body:'Bonjour Madame,\n\nJe suis le père de Clément Aubert en Terminale S1. Je souhaiterais prendre rendez-vous pour discuter de ses résultats.\n\nCordialement,\nM. Aubert' },
]
const active = computed(() => messages.find(m => m.id === selected.value))
</script>

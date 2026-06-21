<template>
  <main class="pt-28 pb-24">
    <div class="max-w-6xl mx-auto px-6">

      <div class="text-center mb-14 reveal reveal-hidden">
        <div class="section-label justify-center mb-4">Parlons-en</div>
        <h1 class="font-syne text-5xl font-extrabold tracking-tight mb-4">Contactez-nous</h1>
        <p class="text-[#64748b] max-w-md mx-auto">Une question, un projet, une démo ? Notre équipe répond dans les 24h.</p>
      </div>

      <div class="grid md:grid-cols-5 gap-10">
        <!-- Form -->
        <div class="md:col-span-3 card p-8 reveal reveal-hidden">
          <h2 class="font-syne text-xl font-bold mb-6">Envoyer un message</h2>
          <div class="space-y-4">
            <div class="grid sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-[#64748b] mb-1.5">Nom *</label>
                <input class="inp" type="text" placeholder="Jean Dupont" v-model="form.nom"/>
              </div>
              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-[#64748b] mb-1.5">Email *</label>
                <input class="inp" type="email" placeholder="jean@entreprise.com" v-model="form.email"/>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-[#64748b] mb-1.5">Sujet *</label>
              <select class="inp" v-model="form.sujet" style="appearance:none">
                <option value="">Choisir un sujet…</option>
                <option>Demande de démo</option>
                <option>Projet sur mesure</option>
                <option>Support technique</option>
                <option>Partenariat</option>
                <option>Autre</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-[#64748b] mb-1.5">Message *</label>
              <textarea class="inp resize-none" rows="5"
                placeholder="Décrivez votre projet ou votre demande…" v-model="form.message"/>
            </div>
            <button class="btn-primary w-full justify-center py-3 text-base" @click="submit">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
              {{ sent ? 'Message envoyé !' : 'Envoyer le message' }}
            </button>
          </div>
        </div>

        <!-- Info sidebar -->
        <div class="md:col-span-2 space-y-4 reveal reveal-hidden">
          <div v-for="info in infos" :key="info.label" class="card p-5">
            <div class="flex items-start gap-4">
              <div class="w-9 h-9 rounded-lg bg-[#06b6d4]/10 border border-[#06b6d4]/20 flex items-center justify-center flex-shrink-0">{{ info.icon }}</div>
              <div>
                <div class="text-xs font-bold uppercase tracking-wider text-[#64748b] mb-1">{{ info.label }}</div>
                <div class="text-sm font-medium">{{ info.value }}</div>
              </div>
            </div>
          </div>
          <div class="card p-5">
            <div class="text-xs font-bold uppercase tracking-wider text-[#64748b] mb-4">Réseaux sociaux</div>
            <div class="flex gap-3">
              <a v-for="s in socials" :key="s.name" href="#"
                class="w-9 h-9 rounded-lg bg-[#111820] border border-[#1e2a38] flex items-center justify-center text-[#64748b] hover:text-[#06b6d4] hover:border-[#06b6d4]/30 transition-colors text-xs font-bold">
                {{ s.icon }}
              </a>
            </div>
          </div>
          <div class="card p-5">
            <div class="text-xs font-bold uppercase tracking-wider text-[#64748b] mb-3">Disponibilité</div>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between"><span class="text-[#64748b]">Lun — Ven</span><span class="font-medium">8h — 18h</span></div>
              <div class="flex justify-between"><span class="text-[#64748b]">Samedi</span><span class="font-medium">9h — 13h</span></div>
              <div class="flex justify-between"><span class="text-[#64748b]">Dimanche</span><span class="text-[#ef4444]">Fermé</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useReveal } from '@/composables/useReveal.js'
useReveal()

const sent = ref(false)
const form = ref({ nom:'', email:'', sujet:'', message:'' })

function submit() {
  if (!form.value.nom || !form.value.email || !form.value.message) return
  sent.value = true
  setTimeout(() => { sent.value = false; form.value = { nom:'', email:'', sujet:'', message:'' } }, 3000)
}

const infos = [
  { icon:'📧', label:'Email',    value:'contact@infini-software.com' },
  { icon:'📞', label:'Téléphone', value:'+509 00 00 0000' },
  { icon:'📍', label:'Adresse',  value:'Port-au-Prince, Haïti' },
]
const socials = [
  { name:'LinkedIn', icon:'in' }, { name:'Twitter', icon:'𝕏' },
  { name:'GitHub',   icon:'⌥' }, { name:'Facebook', icon:'f' },
]
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-6 py-24" style="background:#FAF7F2">
    <div class="max-w-lg text-center reveal">
      <p class="text-xs tracking-widest uppercase font-bold text-gold mb-3">Erreur 404</p>
      <h1 class="font-serif text-4xl mb-4" style="color:#0B1F3A">Page introuvable</h1>
      <p class="text-gray-500 leading-relaxed mb-10">
        La page que vous cherchez n'existe pas ou plus. Elle a peut-être été déplacée —
        voici les sections principales du site.
      </p>

      <div class="grid grid-cols-2 gap-3 mb-10 text-left">
        <router-link v-for="l in LINKS" :key="l.to" :to="l.to"
          class="bg-white rounded-xl px-4 py-3 text-sm font-semibold no-underline hover:-translate-y-0.5 transition-transform"
          style="color:#0B1F3A;box-shadow:0 2px 12px rgba(11,31,58,.06)">
          {{ l.label }}
        </router-link>
      </div>

      <router-link to="/" class="btn-gold inline-flex items-center gap-2 px-8 py-3.5 rounded-full font-semibold no-underline">
        ← Retour à l'accueil
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { initReveal } from '@/composables/useReveal.js'

const LINKS = [
  { to: '/facultes',   label: 'Les Facultés' },
  { to: '/formations', label: 'Formations' },
  { to: '/admission',  label: 'Admission' },
  { to: '/contact',    label: 'Contact' },
]

onMounted(() => { window.scrollTo(0, 0); initReveal() })
</script>

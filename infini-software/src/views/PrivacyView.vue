<template>
  <main class="pt-28 pb-24">
    <div class="max-w-3xl mx-auto px-6">
      <div class="mb-12 reveal reveal-hidden">
        <div class="section-label mb-4">Légal</div>
        <h1 class="font-syne text-4xl font-extrabold mb-2">Politique de confidentialité</h1>
        <p class="text-[#64748b] text-sm">Dernière mise à jour : Mars 2026</p>
      </div>
      <div class="space-y-6">
        <div v-for="(s,i) in sections" :key="s.title"
          class="card p-7 reveal reveal-hidden" :style="`transition-delay:${i*.05}s`">
          <h2 class="font-syne font-bold text-lg mb-4 flex items-center gap-3">
            <span class="badge-cyan font-mono">{{ String(i+1).padStart(2,'0') }}</span>
            {{ s.title }}
          </h2>
          <p class="text-sm text-[#94a3b8] leading-relaxed">{{ s.content }}</p>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { useReveal } from '@/composables/useReveal.js'
useReveal()
const sections = [
  { title:'Collecte des données',      content:"Infini Software collecte uniquement les données nécessaires à la fourniture de ses services : nom, email, entreprise et données d'utilisation anonymisées. Nous ne collectons jamais de données sensibles sans consentement explicite." },
  { title:'Utilisation des informations', content:"Les données collectées sont utilisées exclusivement pour vous fournir nos services, améliorer nos applications, vous contacter concernant votre compte, et vous envoyer des mises à jour si vous y avez consenti." },
  { title:'Partage des données',       content:"Infini Software ne vend, ne loue et ne partage jamais vos données personnelles avec des tiers à des fins commerciales. Des données peuvent être partagées avec des sous-traitants techniques liés par des accords de confidentialité stricts." },
  { title:'Droits des utilisateurs',   content:"Vous disposez du droit d'accès, de rectification, de suppression et de portabilité de vos données. Pour exercer ces droits, contactez-nous à privacy@infini-software.com. Nous répondons dans les 30 jours." },
  { title:'Sécurité des données',      content:"Toutes les données sont chiffrées en transit (TLS 1.3) et au repos (AES-256). Nos systèmes font l'objet d'audits de sécurité réguliers. En cas de violation, nous vous notifions dans les 72 heures." },
  { title:'Cookies',                   content:"Notre site utilise uniquement des cookies techniques essentiels au fonctionnement. Aucun cookie de tracking ou publicitaire n'est utilisé. Vous pouvez configurer votre navigateur pour les refuser sans impact sur votre expérience." },
]
</script>

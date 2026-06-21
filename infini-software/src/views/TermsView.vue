<template>
  <main class="pt-28 pb-24">
    <div class="max-w-3xl mx-auto px-6">
      <div class="mb-12 reveal reveal-hidden">
        <div class="section-label mb-4">Légal</div>
        <h1 class="font-syne text-4xl font-extrabold mb-2">Conditions générales d'utilisation</h1>
        <p class="text-[#64748b] text-sm">Dernière mise à jour : Mars 2026</p>
      </div>
      <div class="space-y-6">
        <div v-for="(s,i) in sections" :key="s.title"
          class="card p-7 reveal reveal-hidden" :style="`transition-delay:${i*.05}s`">
          <h2 class="font-syne font-bold text-lg mb-4 flex items-center gap-3">
            <span class="badge-gold font-mono">{{ String(i+1).padStart(2,'0') }}</span>
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
  { title:"Acceptation des conditions",      content:"En accédant au site ou en utilisant nos logiciels, vous acceptez les présentes conditions générales dans leur intégralité. Si vous n'acceptez pas ces conditions, veuillez ne pas utiliser nos services." },
  { title:"Licence d'utilisation",           content:"Infini Software accorde une licence non exclusive, non transférable et révocable pour utiliser nos logiciels conformément à leur destination. Toute reproduction ou distribution non autorisée est strictement interdite." },
  { title:"Propriété intellectuelle",        content:"Tous les logiciels, codes sources, designs et contenus créés par Infini Software restent notre propriété exclusive. Les clients bénéficient d'une licence d'utilisation mais ne peuvent revendiquer aucun droit de propriété." },
  { title:"Responsabilités et limitations",  content:"Infini Software s'engage à fournir des services de qualité mais ne peut garantir l'absence de bugs ou interruptions. Notre responsabilité est limitée au montant payé pour le service concerné." },
  { title:"Conditions liées aux logiciels",  content:"Nos logiciels sont fournis tels quels. Des mises à jour régulières sont fournies pendant la durée du contrat de maintenance. L'utilisation des logiciels à des fins illégales est strictement interdite." },
  { title:"Résiliation",                     content:"Infini Software se réserve le droit de résilier l'accès aux services en cas de violation des présentes conditions, sans préavis ni remboursement. Le client peut résilier son contrat conformément aux modalités prévues." },
]
</script>

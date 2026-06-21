<template>
  <main class="pt-28 pb-24">
    <div class="max-w-7xl mx-auto px-6">
    <div class="img">
        <div style="position: relative; z-index: 1;">
           
        </div>
    </div>
      <!-- Hero -->
      <div class="max-w-3xl mb-20 reveal reveal-hidden">
        <div class="section-label mb-4">Notre histoire</div>
        <h1 class="font-syne text-5xl md:text-6xl font-extrabold tracking-tight mb-6">
          Nous construisons le<br>
          <span style="background:linear-gradient(135deg,#06b6d4,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent">
            futur digital
          </span>
        </h1>
        <p class="text-lg text-[#94a3b8] leading-relaxed">
          Infini Software est née d'une conviction : chaque entreprise mérite des outils technologiques
          à la hauteur de ses ambitions. Fondée par des passionnés du logiciel, nous combinons
          créativité et rigueur technique pour livrer des solutions qui durent.
        </p>
      </div>

      <!-- Mission / Vision / Valeurs -->
      <div class="grid md:grid-cols-3 gap-6 mb-20">
        <div v-for="(mv,i) in mvv" :key="mv.title"
          class="card p-7 reveal reveal-hidden" :style="`transition-delay:${i*.1}s`">
          <div class="text-3xl mb-4">{{ mv.icon }}</div>
          <h3 class="font-syne font-bold text-lg mb-2 text-[#06b6d4]">{{ mv.title }}</h3>
          <p class="text-sm text-[#94a3b8] leading-relaxed">{{ mv.desc }}</p>
        </div>
      </div>

      <!-- Timeline -->
      <div class="mb-20">
        <div class="section-label mb-8 reveal reveal-hidden">Notre parcours</div>
        <div class="space-y-8">
          <div v-for="(t,i) in timeline" :key="t.year"
            class="flex gap-6 reveal reveal-hidden" :style="`transition-delay:${i*.08}s`">
            <div class="flex flex-col items-center">
              <div class="w-2.5 h-2.5 rounded-full bg-[#06b6d4] flex-shrink-0 mt-1.5" style="box-shadow:0 0 10px rgba(6,182,212,.5)"/>
              <div v-if="i < timeline.length-1" class="w-px flex-1 bg-[#1e2a38] mt-1"/>
            </div>
            <div class="pb-8">
              <span class="badge-cyan mb-2 inline-block">{{ t.year }}</span>
              <h4 class="font-syne font-bold mb-1">{{ t.title }}</h4>
              <p class="text-sm text-[#64748b]">{{ t.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Valeurs -->
      <div class="mb-20">
        <div class="text-center mb-12 reveal reveal-hidden">
          <div class="section-label justify-center mb-4">Ce qui nous guide</div>
          <h2 class="font-syne text-4xl font-extrabold">Nos valeurs</h2>
        </div>
        <div class="grid sm:grid-cols-2 md:grid-cols-4 gap-5">
          <div v-for="(v,i) in values" :key="v.title"
            class="card p-6 text-center reveal reveal-hidden" :style="`transition-delay:${i*.08}s`">
            <div class="text-4xl mb-3">{{ v.icon }}</div>
            <h4 class="font-syne font-bold mb-2">{{ v.title }}</h4>
            <p class="text-xs text-[#64748b] leading-relaxed">{{ v.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Team -->
      <div>
        <div class="text-center mb-12 reveal reveal-hidden">
          <div class="section-label justify-center mb-4">Les gens derrière</div>
          <h2 class="font-syne text-4xl font-extrabold">L'équipe</h2>
        </div>
        <div class="grid sm:grid-cols-2 md:grid-cols-3 gap-6">
          <div v-for="(m,i) in team" :key="m.name"
            class="card p-6 text-center reveal reveal-hidden" :style="`transition-delay:${i*.1}s`">
            <div class="w-16 h-16 rounded-full flex items-center justify-center text-2xl mx-auto mb-4"
              :style="`background:linear-gradient(135deg,${m.c1},${m.c2})`">{{ m.avatar }}</div>
            <h4 class="font-syne font-bold mb-1">{{ m.name }}</h4>
            <p class="text-xs text-[#06b6d4] mb-2">{{ m.role }}</p>
            <p class="text-xs text-[#64748b]">{{ m.bio }}</p>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { useReveal } from '@/composables/useReveal.js'
useReveal()

const mvv = [
  { icon:'🎯', title:'Notre mission', desc:"Rendre la technologie accessible à toutes les entreprises en livrant des logiciels fiables, performants et abordables qui résolvent de vrais problèmes métier." },
  { icon:'🔭', title:'Notre vision',  desc:"Devenir la référence caribéenne et francophone en développement logiciel sur mesure, reconnue pour la qualité et l'innovation de ses solutions." },
  { icon:'💎', title:'Nos valeurs',   desc:"Excellence, transparence, engagement client et amélioration continue. Nous livrons ce que nous promettons, quand nous le promettons." },
]
const timeline = [
  { year:'2018', title:'Fondation',     desc:"Création d'Infini Software avec une première équipe de 2 développeurs passionnés." },
  { year:'2020', title:'Premier grand projet', desc:"Livraison d'ÉcoleServ, notre système de gestion scolaire, à notre premier client institutionnel." },
  { year:'2022', title:'Expansion',     desc:"Passage à 6 développeurs, élargissement au marché régional et lancement de 3 nouvelles applications." },
  { year:'2024', title:'Consolidation', desc:"15+ applications livrées, 50+ clients actifs, partenariats régionaux établis." },
  { year:'2026', title:"Aujourd'hui",   desc:"Lancement de notre store officiel et ouverture à de nouveaux marchés internationaux." },
]
const values = [
  { icon:'💡', title:'Innovation',  desc:"Toujours à la pointe des technologies pour livrer ce qu'il y a de mieux." },
  { icon:'🤝', title:'Engagement', desc:"Nous traitons chaque projet comme si c'était le nôtre." },
  { icon:'🎯', title:'Précision',  desc:"Chaque détail compte. Nous livrons du code propre et maintenable." },
  { icon:'🌱', title:'Croissance', desc:"Nous grandissons avec nos clients sur le long terme." },
]
const team = [
  { name:'Fritz Occean',   role:'CEO & Lead Developer', avatar:'👨‍💻', c1:'#0d1f2a', c2:'#06b6d4', bio:"Architecte logiciel avec 10 ans d'expérience en développement full-stack et gestion de projets." },
  { name:'Marie Jean-Louis', role:'Frontend Lead',     avatar:'👩‍🎨', c1:'#1a0d2a', c2:'#8b5cf6', bio:"Spécialiste UX/UI et Vue.js, passionnée par les interfaces qui font la différence." },
  { name:'Karl Pierre',    role:'Backend & DevOps',     avatar:'👨‍🔧', c1:'#0a1f14', c2:'#10b981', bio:"Expert Python/FastAPI et infrastructure, garant de la fiabilité et sécurité des systèmes." },
]
</script>

<template>
  <main>

    <!-- ── Hero ── -->
    <section class="relative min-h-[640px] flex flex-col justify-center pt-16 overflow-hidden"
      style="background: radial-gradient(ellipse 60% 50% at 80% 20%, rgba(6,182,212,.1) 0%,transparent 60%), radial-gradient(ellipse 40% 60% at 10% 80%, rgba(245,158,11,.06) 0%,transparent 60%), #080c10">
      <!-- Grid -->
      <div class="absolute inset-0 opacity-[.04]"
        style="background-image:linear-gradient(#1e2a38 1px,transparent 1px),linear-gradient(90deg,#1e2a38 1px,transparent 1px);background-size:60px 60px"/>
      <!-- Orb -->
      <div class="absolute top-1/3 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-10"
        style="background:radial-gradient(circle,#06b6d4,transparent)"/>

      <div class="max-w-7xl mx-auto px-6 py-20 relative z-10">
        <div class="max-w-3xl">
          <div class="section-label mb-6 reveal reveal-hidden">Solutions Logicielles</div>
          <h1 class="text-4xl md:text-6xl font-syne font-extrabold leading-[1.08] tracking-tight mb-6 reveal reveal-hidden" style="transition-delay:.1s">
            Des logiciels qui<br>
            <span style="background:linear-gradient(135deg,#06b6d4,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent">
              transforment
            </span>
            votre entreprise
          </h1>
          <p class="text-lg text-[#94a3b8] leading-relaxed max-w-xl mb-10 reveal reveal-hidden" style="transition-delay:.15s">
            Infini Software conçoit des applications sur mesure, des systèmes de gestion
            et des solutions digitales adaptées à vos besoins réels.
          </p>
          <div class="flex flex-wrap gap-4 reveal reveal-hidden" style="transition-delay:.2s">
            <router-link to="/store" class="btn-primary text-base px-7 py-3">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              Voir nos applications
            </router-link>
            <router-link to="/contact" class="btn-outline text-base px-7 py-3">
              Demander une démo
            </router-link>
          </div>
        </div>
      </div>

      <!-- Scroll indicator -->
      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 text-[#374151] animate-[bounceY_1.8s_ease-in-out_infinite]">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
      </div>
    </section>

    <!-- ── Stats ── -->
    <section ref="statsSection" class="py-16 border-y border-[#1e2a38]">
      <div class="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
        <div v-for="(s, i) in stats" :key="s.label" class="text-center reveal reveal-hidden">
          <div class="font-syne font-extrabold text-[2.5rem] leading-none"
            style="background:linear-gradient(135deg,#06b6d4,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent">
            {{ counts[i] }}{{ s.suffix }}
          </div>
          <div class="text-sm text-[#64748b] mt-1 font-medium">{{ s.label }}</div>
        </div>
      </div>
    </section>

    <!-- ── Services ── -->
    <section class="py-24">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16 reveal reveal-hidden">
          <div class="section-label justify-center mb-4">Ce que nous faisons</div>
          <h2 class="font-syne text-4xl md:text-5xl font-extrabold tracking-tight">Nos services</h2>
          <p class="text-[#64748b] mt-4 max-w-lg mx-auto">De la conception à la livraison, nous couvrons tout le cycle de développement logiciel.</p>
        </div>
        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="(s,i) in services" :key="s.title"
            class="card p-7 reveal reveal-hidden" :style="`transition-delay:${i*.08}s`">
            <div class="w-11 h-11 rounded-xl flex items-center justify-center mb-5 text-xl"
              :style="`background:${s.bg};color:${s.color}`">{{ s.icon }}</div>
            <h3 class="font-syne font-bold text-lg mb-2">{{ s.title }}</h3>
            <p class="text-sm text-[#64748b] leading-relaxed">{{ s.desc }}</p>
            <div class="flex flex-wrap gap-1.5 mt-4">
              <span v-for="t in s.tags" :key="t" class="tech-tag">{{ t }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Featured Apps ── -->
    <section class="py-24 bg-[#0d1219]">
      <div class="max-w-7xl mx-auto px-6">
        <div class="flex flex-col md:flex-row md:items-end justify-between mb-14 gap-4">
          <div class="reveal reveal-hidden">
            <div class="section-label mb-4">Applications phares</div>
            <h2 class="font-syne text-4xl md:text-5xl font-extrabold tracking-tight">Nos créations</h2>
          </div>
          <router-link to="/store" class="btn-outline reveal reveal-hidden">Voir tout le store →</router-link>
        </div>
        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="(app,i) in featured" :key="app.slug"
            class="card overflow-hidden cursor-pointer reveal reveal-hidden" :style="`transition-delay:${i*.1}s`"
            @click="$router.push('/store')">
            <div class="h-36 flex items-center justify-center text-5xl"
              :style="`background:linear-gradient(135deg,${app.bg1},${app.bg2})`">{{ app.icon }}</div>
            <div class="p-5">
              <div class="flex items-center justify-between mb-2">
                <h3 class="font-syne font-bold">{{ app.name }}</h3>
                <span :class="app.badgeClass" class="inline-flex items-center gap-1">
                  <span v-if="app.badge === 'Nouveau'" class="relative flex h-1.5 w-1.5">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#06b6d4] opacity-75"/>
                    <span class="relative inline-flex h-1.5 w-1.5 rounded-full bg-[#06b6d4]"/>
                  </span>
                  {{ app.badge }}
                </span>
              </div>
              <p class="text-xs text-[#64748b] leading-relaxed mb-4">{{ app.desc }}</p>
              <div class="flex gap-2">
                <div class="group relative flex-1">
                  <button disabled class="btn-primary w-full justify-center text-xs px-4 py-2 !opacity-40 !cursor-not-allowed pointer-events-none">Télécharger</button>
                  <div class="absolute -top-9 left-1/2 -translate-x-1/2 whitespace-nowrap text-[10px] bg-[#0d1219] border border-[#253040] text-[#94a3b8] px-2.5 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                    Bientôt disponible
                  </div>
                </div>
                <div class="group relative">
                  <button disabled class="btn-gold text-xs px-4 py-2 !opacity-40 !cursor-not-allowed pointer-events-none">Démo</button>
                  <div class="absolute -top-9 left-1/2 -translate-x-1/2 whitespace-nowrap text-[10px] bg-[#0d1219] border border-[#253040] text-[#94a3b8] px-2.5 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                    Bientôt disponible
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Why Us ── -->
    <section class="py-24">
      <div class="max-w-7xl mx-auto px-6">
        <div class="grid md:grid-cols-2 gap-16 items-center">
          <div class="reveal reveal-hidden">
            <div class="section-label mb-4">Notre différence</div>
            <h2 class="font-syne text-4xl md:text-5xl font-extrabold tracking-tight mb-6">
              Pourquoi choisir<br><span class="text-[#06b6d4]">Infini Software</span> ?
            </h2>
            <p class="text-[#94a3b8] leading-relaxed mb-8">
              Nous combinons expertise technique et compréhension métier pour livrer des solutions
              qui fonctionnent vraiment — pas juste des produits, mais des outils qui font avancer votre activité.
            </p>
            <div class="space-y-5">
              <div v-for="w in whyUs" :key="w.title" class="flex items-start gap-4">
                <div class="w-9 h-9 rounded-xl bg-[#06b6d4]/10 border border-[#06b6d4]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  {{ w.icon }}
                </div>
                <div>
                  <div class="font-semibold text-sm mb-1">{{ w.title }}</div>
                  <div class="text-sm text-[#64748b]">{{ w.desc }}</div>
                </div>
              </div>
            </div>
          </div>
          <!-- Terminal card -->
          <div class="hidden md:block reveal reveal-hidden">
            <div class="card p-6" style="box-shadow:0 0 40px rgba(6,182,212,.12)">
              <div class="flex items-center gap-2 mb-4">
                <div class="w-2.5 h-2.5 rounded-full bg-[#10b981] animate-pulse"></div>
                <span class="font-mono text-xs text-[#64748b]">infini-deploy — production</span>
              </div>
              <div class="font-mono text-xs space-y-2">
                <div><span class="text-[#10b981]">✓</span> <span class="text-[#64748b]">Build completed in</span> <span class="text-[#f59e0b]">2.4s</span></div>
                <div><span class="text-[#10b981]">✓</span> <span class="text-[#64748b]">Tests passed</span> <span class="text-[#06b6d4]">128/128</span></div>
                <div><span class="text-[#10b981]">✓</span> <span class="text-[#64748b]">Security scan</span> <span class="text-[#10b981]">clean</span></div>
                <div><span class="text-[#10b981]">✓</span> <span class="text-[#64748b]">Deployed to</span> <span class="text-white">production</span></div>
                <div class="mt-3 text-[#374151]">$ <span class="text-[#06b6d4]">infini</span> <span class="text-white">status</span></div>
                <div class="text-[#10b981]">→ All systems operational ✓</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA ── -->
    <section class="py-20">
      <div class="max-w-7xl mx-auto px-6">
        <div class="rounded-2xl p-12 text-center relative overflow-hidden reveal reveal-hidden"
          style="background:linear-gradient(135deg,#0d1f2a,#0a1a14);border:1px solid rgba(6,182,212,.2)">
          <div class="absolute top-0 left-1/2 -translate-x-1/2 w-80 h-0.5 blur-sm"
            style="background:linear-gradient(90deg,transparent,#06b6d4,#f59e0b,transparent)"/>
          <div class="section-label justify-center mb-4">Passons à l'action</div>
          <h2 class="font-syne text-4xl font-extrabold mb-4">Votre projet commence ici</h2>
          <p class="text-[#94a3b8] max-w-md mx-auto mb-8">
            Discutons de vos besoins et construisons ensemble la solution idéale pour votre entreprise.
          </p>
          <div class="flex flex-wrap gap-4 justify-center">
            <router-link to="/contact" class="btn-primary text-base px-8 py-3">Démarrer un projet</router-link>
            <router-link to="/about"   class="btn-outline  text-base px-8 py-3">En savoir plus</router-link>
          </div>
        </div>
      </div>
    </section>

  </main>
</template>

<script setup>
import { ref, onMounted }  from 'vue'
import { useReveal }       from '@/composables/useReveal.js'
import { useDemoStore }    from '@/stores/demo.js'
import { apps }            from '@/stores/apps.js'

useReveal()
const demoStore = useDemoStore()
const featured  = apps.slice(0, 3)

const stats = [
  { num: 15, suffix: '+', label: "Applications livrées" },
  { num: 50, suffix: '+', label: "Clients satisfaits" },
  { num:  8, suffix: '+', label: "Années d'expérience" },
  { num: 99, suffix: '%', label: "Satisfaction client" },
]
const counts      = ref(stats.map(() => 0))
const statsSection = ref(null)

onMounted(() => {
  const obs = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return
    obs.disconnect()
    stats.forEach((s, i) => {
      const totalFrames = 90
      let frame = 0
      const timer = setInterval(() => {
        frame++
        const p = 1 - Math.pow(1 - frame / totalFrames, 3)
        counts.value[i] = Math.round(s.num * p)
        if (frame >= totalFrames) { counts.value[i] = s.num; clearInterval(timer) }
      }, 1000 / 60)
    })
  }, { threshold: 0.5 })
  if (statsSection.value) obs.observe(statsSection.value)
})
const services = [
  { icon:'🖥️', title:'Applications de bureau', bg:'rgba(6,182,212,.1)',  color:'#06b6d4', desc:"Logiciels Windows/Linux robustes, packagés et distribués facilement.",             tags:['Python','Electron','C#','Nuitka'] },
  { icon:'🌐', title:'Applications web',        bg:'rgba(245,158,11,.1)', color:'#f59e0b', desc:"Sites web et SaaS modernes, rapides et accessibles depuis n'importe quel appareil.", tags:['Vue.js','FastAPI','React','PostgreSQL'] },
  { icon:'📱', title:'Applications mobiles',    bg:'rgba(16,185,129,.1)', color:'#10b981', desc:"Apps iOS et Android natives ou cross-platform pour accompagner vos équipes.",         tags:['Flutter','React Native','Swift'] },
  { icon:'🗄️', title:'Systèmes de gestion',    bg:'rgba(139,92,246,.1)', color:'#8b5cf6', desc:"ERP, CRM, systèmes scolaires, RH — solutions métier complètes sur mesure.",           tags:['MySQL','SQLAlchemy','Docker'] },
  { icon:'☁️', title:'Cloud & DevOps',          bg:'rgba(6,182,212,.1)',  color:'#06b6d4', desc:"Hébergement, CI/CD, monitoring et déploiement automatisé.",                           tags:['Docker','Nginx','GitHub Actions'] },
  { icon:'🔐', title:'Sécurité & Licences',     bg:'rgba(239,68,68,.1)',  color:'#ef4444', desc:"Protection du code, systèmes de licences, chiffrement et gestion des accès.",         tags:['Fernet','JWT','WireGuard'] },
]
const whyUs = [
  { icon:'⚡', title:'Livraison rapide',   desc:"Méthodes agiles pour des délais respectés et une mise en production rapide." },
  { icon:'🔧', title:'Support continu',    desc:"Nous restons disponibles après livraison pour maintenance et évolutions." },
  { icon:'🎯', title:'Sur mesure',         desc:"Chaque solution est conçue selon vos besoins réels, pas un template générique." },
  { icon:'🔒', title:'Sécurisé by design', desc:"Sécurité intégrée dès la conception, pas ajoutée après coup." },
]
</script>

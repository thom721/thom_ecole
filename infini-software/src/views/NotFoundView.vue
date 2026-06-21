<template>
  <main class="relative min-h-screen flex items-center justify-center pt-16 overflow-hidden"
    style="background:radial-gradient(ellipse 50% 60% at 50% 30%, rgba(6,182,212,.07) 0%,transparent 60%),#080c10">

    <!-- Grid -->
    <div class="absolute inset-0 opacity-[.03]"
      style="background-image:linear-gradient(#1e2a38 1px,transparent 1px),linear-gradient(90deg,#1e2a38 1px,transparent 1px);background-size:60px 60px"/>

    <div class="relative z-10 text-center px-6">
      <!-- 404 number -->
      <div class="font-syne font-extrabold leading-none select-none mb-6"
        style="font-size:clamp(6rem,20vw,12rem);background:linear-gradient(135deg,#06b6d4,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent">
        404
      </div>

      <!-- Terminal card -->
      <div class="inline-block text-left mb-10 card px-6 py-4 font-mono text-xs space-y-1.5"
        style="box-shadow:0 0 40px rgba(6,182,212,.1)">
        <div><span class="text-[#ef4444]">✗</span> <span class="text-[#64748b]">Route not found:</span> <span class="text-[#f59e0b]">{{ $route.path }}</span></div>
        <div><span class="text-[#10b981]">→</span> <span class="text-[#64748b]">Suggestion:</span> <span class="text-[#06b6d4]">cd /</span></div>
      </div>

      <h1 class="font-syne text-2xl md:text-3xl font-extrabold mb-3">Page introuvable</h1>
      <p class="text-[#64748b] max-w-sm mx-auto mb-10 leading-relaxed">
        Cette page n'existe pas ou a été déplacée. Retournez à l'accueil pour continuer.
      </p>

      <div class="flex flex-wrap gap-4 justify-center">
        <router-link to="/" class="btn-primary text-base px-7 py-3">← Retour à l'accueil</router-link>
        <router-link to="/store" class="btn-outline text-base px-7 py-3">Voir le store</router-link>
      </div>
    </div>
  </main>
</template>

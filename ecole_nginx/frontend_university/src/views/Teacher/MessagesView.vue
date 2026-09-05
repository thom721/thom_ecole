<!-- src/views/MessagesView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Messages</h1>
        <p class="text-[#7c83a0] text-sm">Messagerie interne</p>
      </div>
    </div>

    <div class="bg-[#171b26] border border-white/[0.07] rounded-2xl min-h-[400px] flex flex-col items-center justify-center gap-3 p-10 text-center">
      <div class="w-14 h-14 rounded-2xl bg-white/[0.04] flex items-center justify-center text-2xl">✉️</div>
      <p class="text-[15px] font-semibold text-[#e8eaf0]">Messagerie pas encore disponible</p>
      <p class="text-[13px] text-[#7c83a0] max-w-sm">Cette fonctionnalité nécessite un système de messagerie côté serveur qui n'existe pas encore dans l'application.</p>
    </div>
  </div>
</template>

<script setup>
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[100] flex items-center justify-center p-4"
      style="background:rgba(8,12,16,.85);backdrop-filter:blur(12px)"
      @click.self="store.closeDemo()">
      <div class="card p-8 w-full max-w-md">
        <div class="flex items-center justify-between mb-5">
          <h3 class="font-syne font-bold text-xl">Demander une démo</h3>
          <button class="text-[#64748b] hover:text-white transition-colors text-lg"
            @click="store.closeDemo()">✕</button>
        </div>
        <p class="text-sm text-[#94a3b8] mb-6">
          Application : <strong class="text-[#06b6d4]">{{ store.app?.name }}</strong>
        </p>
        <div class="space-y-4">
          <input class="inp" type="text"  placeholder="Votre nom"           v-model="store.form.nom"/>
          <input class="inp" type="email" placeholder="Email professionnel" v-model="store.form.email"/>
          <input class="inp" type="text"  placeholder="Votre entreprise"    v-model="store.form.entreprise"/>
          <textarea class="inp resize-none" rows="3"
            placeholder="Vos besoins spécifiques…" v-model="store.form.message"/>
          <button class="btn-primary w-full justify-center py-3" @click="submit">
            Envoyer la demande
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useDemoStore } from '@/stores/demo.js'
const store = useDemoStore()
function submit() { store.closeDemo() }
</script>

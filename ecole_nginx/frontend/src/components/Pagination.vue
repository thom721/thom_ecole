<template>
  <div v-if="meta && meta.last_page > 1" class="mt-4 flex items-center justify-between px-4 rounded-lg shadow-sm">
    
    <div class="hidden sm:flex flex-1 items-center justify-between">
      <!-- <p class="text-sm text-sky-600">
        Page <span class="font-semibold text-sky-900">{{ meta.current_page }}</span> sur <span class="font-semibold text-sky-900">{{ meta.last_page }}</span>
      </p> -->

      <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm bg-[#1e2335]">
        <button @click="updatePage(meta.current_page - 1)" :disabled="meta.current_page === 1"
          class="relative inline-flex items-center rounded-l-md px-2 py-2 text-sky-400 ring-1 ring-inset ring-sky-300 hover:bg-white/[0.02] disabled:opacity-40 disabled:cursor-not-allowed transition-all">
          <i class="ri-arrow-left-s-line text-xl"></i>
        </button>

        <template v-for="(page, index) in displayedPages" :key="index">
          <button v-if="typeof page === 'number'" 
            @click="updatePage(page)"
            class="relative inline-flex items-center px-4 py-2 text-sm font-semibold ring-1 ring-inset ring-sky-300 transition-all"
            :class="page === meta.current_page ? 'z-10 bg-sky-600 text-white ring-sky-600' : 'text-sky-900 hover:bg-white/[0.02]'">
            {{ page }}
          </button>
          
          <span v-else class="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-sky-400 ring-1 ring-inset ring-sky-300 bg-sky-50">
            {{ page }}
          </span>
        </template>

        <button @click="updatePage(meta.current_page + 1)" :disabled="meta.current_page === meta.last_page"
          class="relative inline-flex items-center rounded-r-md px-2 py-2 text-sky-400 ring-1 ring-inset ring-sky-300 hover:bg-white/[0.02] disabled:opacity-40 disabled:cursor-not-allowed transition-all">
          <i class="ri-arrow-right-s-line text-xl cursor-pointer"></i>
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  meta: { type: Object, required: true }
});

const emit = defineEmits(['changePage']);

const displayedPages = computed(() => {
  const current = props.meta.current_page;
  const last = props.meta.last_page;
  const delta = 2; // Nombre de pages à afficher autour de la page actuelle
  const range = [];
  const rangeWithDots = [];
  let l;

  // 1. Définir les pages à inclure
  for (let i = 1; i <= last; i++) {
    if (i === 1 || i === last || (i >= current - delta && i <= current + delta)) {
      range.push(i);
    }
  }

  // 2. Ajouter les ellipses (...)
  for (let i of range) {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1);
      } else if (i - l !== 1) {
        rangeWithDots.push('...');
      }
    }
    rangeWithDots.push(i);
    l = i;
  }

  return rangeWithDots;
});

const updatePage = (page) => {
     console.log(page);
     
  if (typeof page === 'number' && page !== props.meta.current_page) {
    emit('changePage', page);
  }
};
</script>
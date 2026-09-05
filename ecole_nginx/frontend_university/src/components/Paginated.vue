<script setup>
defineProps({
  links: Array, // Les liens fournis par Laravel (data.links)
});

const emit = defineEmits(["change-page"]);

const updatePage = (url) => {
  if (url) {
    const urlParams = new URLSearchParams(url.split('?')[1]);
    const page = urlParams.get('page');
    emit("change-page", page);
  }
};
</script>

<template>
  <div v-if="links && links.length > 3" class="flex flex-wrap justify-center mt-4 gap-1">
    <button
      v-for="(link, key) in links"
      :key="key"
      @click="updatePage(link.url)"
      :disabled="!link.url || link.active"
      class="px-3 py-2 text-sm rounded-md transition-colors border"
      :class="{
        'bg-sky-600 text-white border-sky-600': link.active,
        'bg-white text-slate-600 border-slate-200 hover:bg-slate-50': !link.active && link.url,
        'opacity-50 cursor-not-allowed bg-slate-100 text-slate-400': !link.url
      }"
      v-html="link.label"
    ></button>
  </div>
</template>
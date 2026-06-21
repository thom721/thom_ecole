<template>
  <div v-if="show" class="fixed inset-0 z-[100] overflow-y-auto">
    <div class="fixed inset-0 bg-black/50 transition-opacity" @click="$emit('close')"></div>

    <div class="flex min-h-full items-center justify-center p-4">
      <div 
        class="relative transform overflow-hidden rounded-2xl bg-white shadow-2xl transition-all sm:w-full"
        :class="maxWidthClass"
      >
        <div class="px-6 py-4 border-b flex justify-between items-center bg-gray-50">
          <h3 class="text-lg font-bold text-gray-800">
            <slot name="title" />
          </h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <div class="px-6 py-6">
          <slot name="content" />
        </div>

        <div v-if="$slots.footer" class="px-6 py-4 bg-gray-50 border-t text-right">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  show: Boolean,
  maxWidth: { default: '2xl' }
});

defineEmits(['close']);

const maxWidthClass = computed(() => {
  return {
    'sm': 'max-w-sm',
    'md': 'max-w-md',
    'lg': 'max-w-lg',
    'xl': 'max-w-xl',
    '2xl': 'max-w-2xl',
    '3xl': 'max-w-3xl',
  }[props.maxWidth];
});
</script>
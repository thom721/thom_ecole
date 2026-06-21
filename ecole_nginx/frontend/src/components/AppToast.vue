<script setup>
defineProps({
  show:    { type: Boolean, default: false },
  message: { type: String,  default: '' },
  ok:      { type: Boolean, default: true },
});
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0 translate-y-4">
      <div
        v-if="show"
        class="fixed top-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-xl text-[13px] font-medium"
        :class="ok
          ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/25'
          : 'bg-red-500/15 text-red-300 border border-red-500/25'"
      >
        <span>{{ ok ? '✅' : '❌' }}</span>
        <span>{{ message }}</span>
      </div>
    </Transition>
  </Teleport>
</template>
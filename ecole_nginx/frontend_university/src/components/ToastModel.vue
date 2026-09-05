<template>
         <Teleport to="body">
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0 translate-y-4">
        <div v-if="toast.show"
          class="fixed top-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-2xl text-sm font-medium text-white max-w-sm"
          :class="toast.type === 'success' ? 'bg-emerald-600' : 'bg-red-600'">
          <span class="text-xl">{{ toast.type === 'success' ? '✅' : '❌' }}</span>
          <span>{{ toast.msg }}</span>
        </div>
      </Transition>
    </Teleport>
</template>

<script setup>
const toast = ref({ show: false, msg: '', type: 'success' })
const notify = (msg, type = 'success') => {
  toast.value = { show: true, msg, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}
</script>
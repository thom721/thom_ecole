<script setup>
defineProps({
    type: {
        type: String,
        default: 'button',
    },
});
</script>

<template>
    <button :type="type" class="inline-flex items-center gap-2 px-4 py-2 bg-red-500/10 text-red-400 border border-red-500/20 rounded-md text-[12px] font-medium hover:bg-red-500/20 hover:border-red-500/35 cursor-pointer transition-colors">
        <slot />
    </button>
</template>

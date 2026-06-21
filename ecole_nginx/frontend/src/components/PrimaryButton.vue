<script setup>
defineProps({
    type: {
        type: String,
        default: 'submit',
    },
});
</script>

<template>
    <button :type="type"
        class="inline-flex items-center gap-2 px-4 py-2 bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-md text-[12px] font-medium hover:bg-sky-500/20 hover:border-sky-500/35 cursor-pointer transition-colors">
        <slot />
    </button>
</template>

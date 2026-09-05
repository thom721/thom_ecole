<script setup>
import { onMounted, ref } from 'vue';

defineProps({
    modelValue: String,
});

defineEmits(['update:modelValue']);

const input = ref(null);

onMounted(() => {
    if (input.value.hasAttribute('autofocus')) {
        input.value.focus();
    }
});

defineExpose({ focus: () => input.value.focus() });
</script>

<template>
    <input ref="input"
        class="w-full mt-1 bg-white border-1 border-slate-300 rounded-md px-2 py-2.5 text-sm focus:border-sky-500 transition-all outline-none focus:ring-0 transition duration-300 text-slate-700"
        :value="modelValue" @input="$emit('update:modelValue', $event.target.value)">
</template>

<script setup>
defineProps({
    message: {
        type: [String, Array],
        default: null,
    },
});
</script>

<template>
    <div v-if="message && message.length">
        <p
            v-for="(msg, index) in (Array.isArray(message) ? message : [message])"
            :key="index"
            class="text-sm text-red-500"
        >
            {{ msg }}
        </p>
    </div>
</template>

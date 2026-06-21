<script setup>
import { Head, Link } from '@inertiajs/vue3';
import HomePage from './HomePage.vue';

defineProps({
    canLogin: {
        type: Boolean,
    },
    canRegister: {
        type: Boolean,
    },
    laravelVersion: {
        type: String,
        required: true,
    },
    phpVersion: {
        type: String,
        required: true,
    },
});

// import HomePage from '/components/HomePage.vue'
// import HomePage from '/HomePage.vue'
</script>


<template>

    <Head title="Welcome" />
    <HomePage />
</template>

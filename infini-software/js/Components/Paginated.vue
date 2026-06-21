<script setup>
import { Link } from '@inertiajs/vue3';

defineProps({
    links: Array
})
</script>

<template>
    <div>
        <Link v-for="link in links" :key="link" :href="link.url ? link.url : ''" v-html="link.label"
            class="me-2 text-lg text-md"
            :class="{ 'text-slate-400 disabled': !link.url, 'font-bold text-sky-500': link.active }" />
    </div>

</template>
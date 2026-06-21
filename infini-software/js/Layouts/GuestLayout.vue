<template>

  <Head :title="title" />


  <Navbar />
  <!-- <div class="max-w-7xl px-4 mx-auto sm:px-6 lg:px-8 pt-4"> -->
  <!-- <div class="max-w-7xl px-4 mx-auto sm:px-6 lg:px-8 pt-4" v-else> -->
  <div class="h-screen mb-32">
    <slot />
  </div>

  <!-- <div class="w-full content-end mt-auto">
    <footer class="bg-slate-300 absolute right-0 left-0 bottom-0">
      <p class="text-center mb-0 py-4">my school © Tous
        droits réservés 2024</p>
    </footer>
  </div> -->
  <!-- <footer class="fixed left-0 bottom-0 w-full">
    <div class="border-t border-gray-400 shadow bg-gray-100 py-2">
      <p class="flex justify-center text-lg text-slate-700 items-center transition-all duration-300 py-1"><span
          class="text-medium me-2" v-if="$page.props.school">{{ $page.props.school.nom ??
            'Myschool'
          }}</span> . © Tous
        droits réservés</p>
    </div>
  </footer> -->
</template>

<script setup>
import { Head, Link, router, useForm, usePage } from '@inertiajs/vue3';
import Navbar from '@/Components/Navbar.vue'
import { ref } from 'vue';
defineProps({
  title: String,
});

const openModalPrivacy = ref(false)
const openModalCertificat = ref(false)
const openModalterms = ref(false)
const openModalRefund = ref(false)

const setLoading = ref(false);

const openModalDonate = ref(false)
const closeModalDonate = ref(false)

const donation = () => {
  openModalDonate.value = true
  // formDonate.reset()
}

const closeModal = () => {
  openModalDonate.value = false
}

// const showSwalInfo = (text, color) => {
//   Swal.fire({
//     position: "top-end",
//     text: text,
//     showConfirmButton: false,
//     timer: 2000,
//     color: color,
//   });
// }
// if (usePage().props.flash.message != null) {
//   showSwalInfo(usePage().props.flash.message, '#e94335')
// }


</script>

<style>
.containers {
  --uib-size: 180px;
  --uib-color: rgb(34, 89, 240);
  --uib-speed: 1.3s;
  --uib-bg-opacity: .1;
  height: calc(var(--uib-size) * (2.1 / 5));
  width: var(--uib-size);
  transform-origin: center;
  overflow: visible;
}

.car {
  fill: none;
  stroke: var(--uib-color);
  stroke-dasharray: 15, 85;
  stroke-dashoffset: 0;
  stroke-linecap: round;
  animation: travel var(--uib-speed) linear infinite;
  will-change: stroke-dasharray, stroke-dashoffset;
  transition: stroke 0.5s ease;
}

.track {
  stroke: var(--uib-color);
  opacity: var(--uib-bg-opacity);
}

@keyframes travel {
  0% {
    stroke-dashoffset: 0;
  }

  100% {
    stroke-dashoffset: 100;
  }
}
</style>

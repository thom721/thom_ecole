<template>

    <nav class="w-full bg-white shadow-lg fixed transition-all duration-500 ease-in-out z-40"
        :class="[!showNavBackgground ? 'md:bg-transparent md:shadow-none md:py-5' : 'md:py-1.5']">


        <div class=" flex justify-between items-center relative sm:text-nowrap md:px-16 lg:px-24"
            :class="{ 'py-1 ': !showNavBackgground }">

            <div class="w-full flex justify-between md:justify-start items-center px-8 md:px-0">

                <div class="flex flex-col justify-start items-center">
                    <Link class="font-bold text-sky-500" :href="route('accueil')">

                    <img class="d-none display-img h-12 rounded-full w-12" style="border-radius: 50%;"
                        src="./../../../public/images/logo.png" alt="" srcset="">
                    </Link>

                </div>


                <div>
                    <button v-show="!isVisible"
                        class="md:hidden h-8 w-8 flex justify-center items-center rounded-full border bg-slate-50 transition-all duration-300 ease-in-out"
                        @click="toggle">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                            stroke="currentColor" class="w-6 h-6 text-sky-500">
                            <path stroke-linecap="round" stroke-linejoin="round"
                                d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                        </svg>
                    </button>

                    <button v-show="isVisible"
                        class="md:hidden h-8 w-8 flex justify-center items-center rounded-full border border-red-100 bg-red-50  transition-all duration-300 ease-in-out"
                        @click="toggle">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                            stroke="currentColor" class="w-6 h-6 text-red-500">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            </div>

            <div @click="hideNavOnSm"
                class="flex flex-col items-center space-y-3 md:space-y-0 md:flex-row space-x-2 lg:space-x-4 md:block text-[#0f705d] w-full justify-center absolute top-[60px] md:sticky md:top-0 sm:text-nowrap itim"
                :class="{ 'hidden': !isVisible, 'md:text-[#fff]': !showNavBackgground && $page.component !== 'FrontEnd/Contact', 'bg-white pb-2': isVisible }">

                <!-- text-[#0f705d] -->
                <Link
                    :class="{ 'text-[#ff9e37] text-md font-bold transition-all duration-500 p-1.5 ': $page.component == 'FrontEnd/Acceuil' }"
                    :href="route('accueil')"
                    class="hover:text-[#ff9e37] rounded-b-md  transition-all duration-300 text-md Itim">
                Accueil
                </Link>

                <Link
                    :class="{ 'text-[#ff9e37] text-md font-bold transition-all duration-500 p-1.5 ': $page.component == 'FrontEnd/Politique' }"
                    :href="route('politique')"
                    class="hover:text-[#ff9e37] rounded-b-md  transition-all duration-300 text-md">
                politique de confidentialité
                </Link>
                <Link
                    :class="{ 'text-[#ff9e37] text-md font-bold transition-all duration-500 p-1.5 ': $page.component == 'FrontEnd/Condition' }"
                    :href="route('condition')"
                    class="hover:text-[#ff9e37] rounded-b-md  transition-all duration-300 text-md">
                Conditions générales

                </Link>



                <Link
                    :class="{ 'text-[#ff9e37] text-md font-bold transition-all duration-500 p-1.5 ': $page.component == 'FrontEnd/About' }"
                    :href="route('about')"
                    class="hover:text-[#ff9e37] rounded-b-md  transition-all duration-300 text-md">

                À propos de nous

                </Link>


                <Link
                    :class="{ 'text-[#ff9e37] text-md font-bold transition-all duration-500 p-1.5 ': $page.component == 'FrontEnd/Contact' }"
                    :href="route('contact')"
                    class="hover:text-[#ff9e37] rounded-b-md  transition-all duration-300 text-md">
                Contact
                </Link>

            </div>

        </div>
    </nav>
    <!-- </div> -->
</template>
<script setup>
import { Link } from '@inertiajs/vue3';
import { computed, onMounted, ref, onUnmounted } from 'vue';

const isVisible = ref(false)
const showConnect = ref(true)
const logo = ref(null)

const show = () => {
    isVisible.value = true
}

const hide = () => {
    isVisible.value = false
}

const toggle = () => {
    return isVisible.value === false ? show() : hide()
}

const showNavBackgground = ref(false)
onMounted(() => {

    document.addEventListener('scroll', () => {
        let topClient = document.body.getBoundingClientRect().top
        // console.log(topClient);

        if (topClient < -30) {
            // console.log(topClient);
            showNavBackgground.value = true
        } else {
            showNavBackgground.value = false

        }
    })
})

const hideNavOnSm = () => {
    if (window.innerWidth < 767) {
        hide()
    }
}


const handleResize = () => {
    // Mettez à jour la valeur de showConnect en fonction de la largeur intérieure de la fenêtre
    showConnect.value = window.innerWidth < 767;
};

// Écoutez l'événement de redimensionnement de la fenêtre lors du montage du composant
onMounted(() => {
    window.addEventListener('resize', handleResize);
    handleResize();
});

// Arrêtez d'écouter l'événement de redimensionnement lorsque le composant est démonté
onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
});



</script>
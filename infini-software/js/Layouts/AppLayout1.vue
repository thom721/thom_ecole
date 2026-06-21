<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { Head, Link, router, usePage } from '@inertiajs/vue3';
import AuthenticationCardLogo from '@/Components/AuthenticationCardLogo.vue';

// import Banner from '@/Components/Banner.vue';
import Dropdown from '@/Components/Dropdown.vue';
import DropdownLink from '@/Components/DropdownLink.vue';
// import Swal from 'sweetalert2'
import DialogModal from '@/Components/DialogModal.vue';
// import NProgress from 'nprogress'
// import Cookies from 'js-cookie';


defineProps({
    title: String,
});

const cart = computed(() => usePage().props.cart.data.count)
const showPromo = ref(false)

const menuIsVisible = ref(false)

const menu = ref(null)
const collapse_admin = ref(null)
const collapse_admin_finance = ref(null)

const admin = ref(false)
const finance = ref(false)

const collapse = () => {
    return admin.value ? admin.value = false : admin.value = true
}

const collapse_finance = () => {
    return finance.value ? finance.value = false : finance.value = true
}

const showingNavigationDropdown = ref(false);

const switchToTeam = (team) => {
    router.put(route('current-team.update'), {
        team_id: team.id,
    }, {
        preserveState: false,
    });
};

const logout = () => {
    router.post(route('logout'));
};

const show = () => {
    menuIsVisible.value = true
}

const hide = () => {
    menuIsVisible.value = false
    admin.value = false
}

const toggle = () => {
    // var element = document.querySelector('.sidebar-menu');

    // if (element && element.classList.add('hidden')) {
    //     element.classList.add('hidden');

    //     // Optionnel : attendre la fin de la transition pour changer display
    //     setTimeout(function () {
    //         element.style.display = 'none';
    //     }, 300);
    // }

    return menuIsVisible.value ? hide() : show()
}

const handleResize = () => {
    // Mettez à jour la valeur de showConnect en fonction de la largeur intérieure de la fenêtre
    if (window.innerWidth < 992) {
        hide()
    } else {
        show()
    }
};

const hides = (event) => {
    if (window.innerWidth < 540) {

        let tag = document.getElementsByTagName(event.target.id)
        if (!event.target.id) {
            hide()
        }
        // console.log(tag);

        // if (menu.value && !menu.value.contains(event.target) && collapse_admin.value && !collapse_admin.value.contains(event.target) && collapse_admin_finance.value && !collapse_admin_finance.value.contains(event.target)) {
        //     hide()
        // }

    }
};




onMounted(() => {
    // setTimeout(() => {

    //     showPromo.value = true
    //     if (usePage().props.auth.user.promo == 1) {
    //         window.scrollTo(0, 0);
    //         document.body.style.overflow = 'hidden';
    //     }
    // }, 2000);


    window.addEventListener('resize', handleResize);
    window.addEventListener('click', hides);
    handleResize();


});




// Arrêtez d'écouter l'événement de redimensionnement lorsque le composant est démonté
onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
});

const openAddressModal = ref(false)
const closeAddressModal = ref(false)


const setLoading = ref(false);
const setPostLoading = ref(false)


router.on('start', (event) => {

    if (event.detail.visit.method !== 'post') {
        setLoading.value = true
        window.scrollTo(0, 0);
        document.body.style.overflow = 'hidden';
    } else {
        window.scrollTo(0, 0);
        document.body.style.overflow = 'hidden';
        setPostLoading.value = true
    }
})

router.on('finish', (event) => {
    if (event.detail.visit.method !== 'post') {
        setLoading.value = false
        document.body.style.overflow = 'scroll';
    } else {
        setPostLoading.value = false
        document.body.style.overflow = 'scroll';
    }
})

const promo = ref(false)



// const hidePromo = () => {
//     axios.post('/session-data')
//         .then(response => {
//             console.log(response);
//             usePage().props.auth.user.promo = 0
//             document.body.style.overflow = 'scroll';
//         })
//         .catch(error => {
//             console.error('Erreur lors de la récupération de la session:', error);
//         });
// }
</script>

<template>
    <div>

        <Head :title="title" />
        <!-- start: Sidebar -->
        <div class="fixed left-0 top-0 h-full bg-gray-900 z-50 transition-all duration-300  ease-in-out overflow-y-auto"
            :class="{ 'w-0 sidebar-menu': !menuIsVisible, 'w-56 ': menuIsVisible }">

            <div class="flex justify-center items-center h-[52px] bg-gray-800 border-b border-b-gray-700 transition-all duration-300  ease-in-out"
                :class="{ 'fixed': admin == true }">
                <img src="./../../../public/images/logo.png" class="object-cover h-10 w-10 rounded-full" alt="" sizes=""
                    srcset="">
                <!-- <AuthenticationCardLogo :route="route('dashboard')" /> -->
            </div>

            <ul class="mt-4 pb-10"
                :class="{ 'hidden': !menuIsVisible, 'show shows': menuIsVisible, 'pt-16': admin == true }">
                <Link :href="route('dashboard')"
                    class="flex items-center py-2 px-6 text-gray-400 transition-all duration-500 hover:bg-gray-800 hover:text-gray-100 text-lg border-b-gray-600 border-b"
                    :class="{ 'bg-gray-800 text-gray-50 font-bold': $page.component == 'BackEnd/Dashboard' }">
                <i class="ri-dashboard-3-line text-white me-2"></i>
                Dashboard
                </Link>

                <Link :href="route('dashboard')"
                    class="flex items-center py-2 px-6 text-gray-400 transition-all duration-500 hover:bg-gray-800 hover:text-gray-100 text-lg border-b-gray-600 border-b"
                    :class="{ 'bg-gray-800 text-gray-50 font-bold': $page.component == 'BackEnd/Dashboard' }">
                <i class="ri-dashboard-3-line text-white me-2"></i>
                Administration
                </Link>

                <Link :href="route('chauffeur')"
                    class="flex items-center py-2 px-6 text-gray-400 transition-all duration-500 hover:bg-gray-800 hover:text-gray-100 text-lg border-b-gray-600 border-b"
                    :class="{ 'bg-gray-800 text-gray-50 font-bold': $page.component == 'BackEnd/Drivers' }">
                <i class="ri-dashboard-3-line text-white me-2"></i>
                Chauffeur
                </Link>

                <Link :href="route('client')"
                    class="flex items-center py-2 px-6 text-gray-400 transition-all duration-500 hover:bg-gray-800 hover:text-gray-100 text-lg border-b-gray-600 border-b"
                    :class="{ 'bg-gray-800 text-gray-50 font-bold': $page.component == 'BackEnd/Customers' }">
                <i class="ri-dashboard-3-line text-white me-2"></i>
                Passager
                </Link>

                <Link :href="route('course')"
                    class="flex items-center py-2 px-6 text-gray-400 transition-all duration-500 hover:bg-gray-800 hover:text-gray-100 text-lg border-b-gray-600 border-b"
                    :class="{ 'bg-gray-800 text-gray-50 font-bold': $page.component == 'BackEnd/Course' }">
                <i class="ri-folder-video-line text-white me-2"></i>
                Course </Link>



                <Link :href="route('dashboard')"
                    class="flex items-center py-2 px-6 text-gray-400 transition-all duration-500 hover:bg-gray-800 hover:text-gray-100 text-lg border-b-gray-600 border-b"
                    :class="{ 'bg-gray-800 text-gray-50 font-bold': $page.component == 'BackEnd/Dashboard' }">
                <i class="ri-history-line text-white me-2"></i>
                Historique </Link>

                <Link :href="route('parametre')"
                    class="flex items-center py-2 px-6 text-gray-400 transition-all duration-500 hover:bg-gray-800 hover:text-gray-100 text-lg border-b-gray-600 border-b"
                    :class="{ 'bg-gray-800 text-gray-50 font-bold': $page.component == 'BackEnd/Settings' }">
                <i class="ri-history-line text-white me-2"></i>
                Param&egrave;tre </Link>


                <!-- <div v-if="$page.props.auth.user && $page.props.auth.user.roles.length > 0 && $page.props.auth.user.roles[0].role == 'super admin'"
                    class="text-gray-400 text-lg px-6 py-2 flex justify-between items-center cursor-pointer transition-all duration-500 hover:bg-gray-800 hover:text-gray-50 border-b-gray-600 border-b"
                    :class="{ 'bg-sky-800 text-white font-bold': $page.component.startsWith('BackEnd/Admin') }"
                    @click="collapse" ref="collapse_admin" id="collapse_admin"> <i
                        class="ri-admin-line text-yellow-400 me-2"></i> Admin
                    <i class=" text-lg flex items-center"
                        :class="[admin == true ? 'ri-arrow-down-s-line text-yellow-400 text-xl' : 'ri-arrow-right-s-line text-slate-300']"></i>
                </div> -->


            </ul>
        </div>
        <!-- <div class="fixed top-0 left-0 w-full h-full bg-black/50 z-40 md:hidden sidebar-overlay"></div> -->
        <!-- end: Sidebar -->

        <!-- start: Main -->
        <main class="w-full">
            <div class="h-[50px] px-6 bg-white flex items-center shadow-sm border-b  shadow-black/5 sticky top-0 left-0 z-30  transition-all duration-300"
                :class="{ 'ml-0': !menuIsVisible, 'sm:ml-56': menuIsVisible }">
                <button ref="menu" type="button" class="text-lg text-gray-600" id="sidebar-toggle" @click="toggle">
                    <i class="ri-menu-line me-4" id="menu"></i>
                </button>

                <div class="flex ml-auto justify-end items-center">
                    <!--Start  Section for Order And Community Order -->


                    <!-- Settings Dropdown -->
                    <div class="ms-3 relative">
                        <Dropdown align="right" width="48">
                            <template #trigger>
                                <i v-if="$page.props.auth && $page.props.auth.user.isverfied == 1"
                                    class="ri-verified-badge-fill text-sky-600 absolute -right-1 z-50 top-3"></i>
                                <div v-if="$page.props.jetstream.managesProfilePhotos"
                                    class="flex items-center md:gap-4">
                                    <p class="text-slate-600 text-lg hidden md:block" v-if="$page.props.auth.user">{{
                                        $page.props.auth.user.username }}</p>
                                    <button
                                        class="flex text-sm border-2 border-transparent rounded-full focus:outline-none focus:border-gray-300 transition z-30">
                                        <img v-if="$page.props.auth.profile_photo_path != null"
                                            class="h-8 w-8 rounded-full border object-cover"
                                            :src="$page.props.auth.user.profile_photo_url">
                                        <span v-else>
                                            <i
                                                class="ri-user-2-fill text-2xl text-slate-500 h-8 w-8 border-sky-500 rounded-full border p-1"></i>
                                        </span>
                                    </button>
                                </div>

                                <span v-else class="inline-flex rounded-md">
                                    <button type="button"
                                        class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-gray-500 bg-white hover:text-gray-700 focus:outline-none focus:bg-gray-50 active:bg-gray-50 transition ease-in-out duration-150 z-30">
                                        {{ $page.props.auth.user.username }}

                                        <svg class="ms-2 -me-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none"
                                            viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round"
                                                d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                                        </svg>
                                    </button>
                                </span>
                            </template>

                            <template #content>
                                <!-- Account Management -->
                                <div class="block px-4 py-2 text-xs text-gray-400">
                                    Manage Account
                                </div>

                                <DropdownLink :href="route('profile.show')">
                                    Profile
                                </DropdownLink>

                                <DropdownLink v-if="$page.props.jetstream.hasApiFeatures"
                                    :href="route('api-tokens.index')">
                                    API Tokens
                                </DropdownLink>

                                <div class="border-t border-gray-200" />

                                <!-- Authentication -->
                                <form @submit.prevent="logout">
                                    <DropdownLink as="button">
                                        Log Out
                                    </DropdownLink>
                                </form>
                            </template>
                        </Dropdown>
                    </div>
                </div>
            </div>

            <div class="transition-all duration-300 pb-16"
                :class="{ 'ml-0': !menuIsVisible, 'md:ml-56': menuIsVisible }">

                <div v-if="setLoading" class="max-w-7xl px-4 mx-auto sm:px-6 lg:px-8 pt-4">

                    <div class="flex justify-center items-center h-screen">

                        <svg class="containers" x="0px" y="0px" viewBox="0 0 50.10 23.1" height="23.1" width="50"
                            preserveAspectRatio='xMidYMid meet'>
                            <path class="track" fill="none" stroke-width="2" pathlength="100"
                                d="M26.7,12.2c3.5,3.4,7.4,7.8,12.7,7.8c5.5,0,9.6-4.4,9.6-9.5C49,5,45.1,1,39.8,1c-5.5,0-9.5,4.2-13.1,7.8l-3.4,3.3c-3.6,3.6-7.6,7.8-13.1,7.8C4.9,20,1,16,1,10.5C1,5.4,5.1,1,10.6,1c5.3,0,9.2,4.5,12.7,7.8L26.7,12.2z" />
                            <path class="car" fill="none" stroke-width="2" pathlength="100"
                                d="M26.7,12.2c3.5,3.4,7.4,7.8,12.7,7.8c5.5,0,9.6-4.4,9.6-9.5C49,5,45.1,1,39.8,1c-5.5,0-9.5,4.2-13.1,7.8l-3.4,3.3c-3.6,3.6-7.6,7.8-13.1,7.8C4.9,20,1,16,1,10.5C1,5.4,5.1,1,10.6,1c5.3,0,9.2,4.5,12.7,7.8L26.7,12.2z" />
                        </svg>
                    </div>


                </div>

                <div v-else>

                    <div style="backdrop-filter: blur(2px);
" v-if="setPostLoading" class=" absolute inset-0 h-screen backdrop-blur-s bg-white/15 z-40">
                    </div>
                    <div v-if="setPostLoading"
                        class="flex inset-0 justify-center items-center h-full absolute z-50 top-10 left-10">

                        <svg class="containersP" x="0px" y="0px" viewBox="0 0 50.10 23.1" height="23.1" width="50"
                            preserveAspectRatio='xMidYMid meet'>
                            <path class="track" fill="none" stroke-width="2" pathlength="100"
                                d="M26.7,12.2c3.5,3.4,7.4,7.8,12.7,7.8c5.5,0,9.6-4.4,9.6-9.5C49,5,45.1,1,39.8,1c-5.5,0-9.5,4.2-13.1,7.8l-3.4,3.3c-3.6,3.6-7.6,7.8-13.1,7.8C4.9,20,1,16,1,10.5C1,5.4,5.1,1,10.6,1c5.3,0,9.2,4.5,12.7,7.8L26.7,12.2z" />
                            <path class="car" fill="none" stroke-width="2" pathlength="100"
                                d="M26.7,12.2c3.5,3.4,7.4,7.8,12.7,7.8c5.5,0,9.6-4.4,9.6-9.5C49,5,45.1,1,39.8,1c-5.5,0-9.5,4.2-13.1,7.8l-3.4,3.3c-3.6,3.6-7.6,7.8-13.1,7.8C4.9,20,1,16,1,10.5C1,5.4,5.1,1,10.6,1c5.3,0,9.2,4.5,12.7,7.8L26.7,12.2z" />
                        </svg>
                    </div>
                    <!-- <div style="backdrop-filter: blur(1px);"
                        v-if="$page.props.auth.user && $page.props.auth.user.promo && showPromo"
                        class="animate__animated animate__fadeIn absolute inset-0 bg-black/60 z-50 transition-all duration-700 opacity-0 hover:opacity-100 min-h-full min-w-full">
                        <div class="flex justify-center items-center absolute inset-0 z-40 h-full" scroll-region>
                            <div
                                class="flex max-w-2xl bg-white border border-yellow-200 rounded-xl h-[32rem] justify-center overflow-hidden relative">

                                <img src="./../../../public/images/promo.png" class="rounded-xl" alt="" sizes=""
                                    srcset="">
                                <span @click="hidePromo"
                                    class="text-red-500 text-xl absolute top-4 right-4 z-50 w-8 h-8 rounded-full cursor-pointer flex hover:border-none transition-all duration-300 spin">
                                    <svg class="flex justify-center items-center" xmlns="http://www.w3.org/2000/svg"
                                        viewBox="0 0 32 32" fill="currentColor">
                                        <path fill="none" d="M0 0h24v24H0z"></path>
                                        <path
                                            d="M10.5859 12L2.79297 4.20706L4.20718 2.79285L12.0001 10.5857L19.793 2.79285L21.2072 4.20706L13.4143 12L21.2072 19.7928L19.793 21.2071L12.0001 13.4142L4.20718 21.2071L2.79297 19.7928L10.5859 12Z">
                                        </path>
                                    </svg>
                                </span>
                            </div>
                        </div>
                    </div> -->


                    <!-- <div class="overflow-hidden"> -->
                    <slot />
                    <!-- </div> -->

                </div>

            </div>

            <!-- <footer class="fixed left-0 bottom-0 w-full">
                <div class="border-t border-gray-300 shadow bg-gray-100 py-2">
                    <p class="flex justify-center text-md items-center transition-all duration-300 text-sm"
                        :class="{ 'ml-0': !menuIsVisible, 'sm:ml-56': menuIsVisible }">
                        Copyright © 2024 Equitechlink All rights reserved.</p>
                </div>
            </footer> -->
        </main>
        <!-- end: Main -->
    </div>
</template>
<style scoped>
html,
body {
    overflow: hidden;
    height: 100%;
    margin: 0;
}

.sidebar-menu {
    opacity: 1;
    transition: opacity 0.2s ease;
    /* Transition de 0.3 secondes, fluide */
}

.sidebar-menu.hidden {
    opacity: 0;
}

.show.shows {
    opacity: 1;

}

.show {
    opacity: 0;
    transition: opacity 0.2s ease;
    /* Transition de 0.3 secondes, fluide */
}

.containers {
    --uib-size: 200px;
    --uib-color: rgb(44, 119, 218);
    --uib-speed: 1.3s;
    --uib-bg-opacity: .1;
    height: calc(var(--uib-size) * (2.1 / 5));
    width: var(--uib-size);
    transform-origin: center;
    overflow: visible;
}

.containersP {
    --uib-size: 200px;
    --uib-color: rgb(255, 196, 0);
    --uib-speed: 1.3s;
    --uib-bg-opacity: .3;
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

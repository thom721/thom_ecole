<script setup>
import Paginated from "@/Components/Paginated.vue";
import { onMounted, ref, watch } from "vue";
import AppLayout1 from '@/Layouts/AppLayout1.vue';
import axios from "axios";


defineOptions({
    layout: AppLayout1,
});
const props = defineProps({
    customerDetails: Object
})




</script>

<template>
    <div class="max-w-6xl px-4 mx-auto sm:px-6 lg:px-16 pt-4">

        {{ customerDetails }}
        <div class="grid md:grid-cols-2">
            <div class="text-xl gap-6 items-center">
                <h1 class="text-3xl py-2 text-center font-semibold">Information personnelle</h1>

                <!-- 
                <table class="text-slate-700 text-xl">
                    <tbody>
                        <tr>
                            <td class="w-56 py-2">Profile</td>
                            <td class="text-xl font-semibold">
                                <a :href="driverDetails[0].profile_image_url" target="_blank">
                                    <img :src="driverDetails[0].profile_image_url || '/default-avatar.png'" alt="Profil"
                                        class="w-20 h-20 rounded-full border shadow object-cover">
                                </a>
                            </td>
                        </tr>
                        <tr>
                            <td class="w-56 py-2">Nom</td>
                            <td class="text-xl font-semibold">{{ driverDetails[0].firstName }}</td>
                        </tr>
                        <tr>
                            <td class="w-56 py-2">Prénom</td>
                            <td class="text-xl font-semibold">{{ driverDetails[0].lastName }}</td>
                        </tr>
                        <tr>
                            <td class="w-56 py-2">Téléphone</td>
                            <td class="text-xl font-semibold">{{ driverDetails[0].phoneNumber }}</td>
                        </tr>
                        <tr>
                            <td class="w-56 py-2">Statut</td>
                            <td class="text-xl font-semibold">{{ driverDetails[0].status }}</td>
                        </tr>

                        <tr>
                            <td class="w-56 py-2">Date d'entrée</td>
                            <td class="text-xl font-semibold"> {{ new
                                Date(driverDetails[0].created_at).toLocaleDateString('fr-FR') }}</td>
                        </tr>
                    </tbody>
                </table> -->

            </div>



        </div>


    </div>
</template>
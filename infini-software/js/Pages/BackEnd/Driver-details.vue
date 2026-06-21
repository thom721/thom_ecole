<script setup>
import Paginated from "@/Components/Paginated.vue";
import { onMounted, ref, watch } from "vue";
import AppLayout1 from '@/Layouts/AppLayout1.vue';
import axios from "axios";


defineOptions({
    layout: AppLayout1,
});
const props = defineProps({
    driverDetails: Object
})




</script>

<template>
    <div class="max-w-6xl px-4 mx-auto sm:px-6 lg:px-16 pt-4">

        <!-- {{ driverDetails }} -->
        <div class="grid md:grid-cols-2">
            <div class="text-xl gap-6 items-center">
                <h1 class="text-3xl py-2 text-center font-semibold">Information personnelle</h1>


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
                </table>

            </div>


            <!-- ====================================================================================================== -->

            <div class="text-xl gap-6 items-center">
                <h1 class="text-3xl py-2 text-center font-semibold">Information sur le v&eacute;hicule</h1>


                <table class="text-slate-700 text-xl">
                    <tbody>
                        <tr>
                            <td class="w-56 py-2">Licence</td>
                            <td class="text-xl font-semibold">{{ driverDetails[0].vehicle.licenseNumber }}</td>
                        </tr>
                        <tr>
                            <td class="w-56 py-2">Mod&egrave;l</td>
                            <td class="text-xl font-semibold">{{ driverDetails[0].vehicle.carModel }}</td>
                        </tr>
                        <tr>
                            <td class="w-56 py-2">Couleur</td>
                            <td class="text-xl font-semibold">{{ driverDetails[0].vehicle.car_color }}</td>
                        </tr>
                        <tr>
                            <td class="w-56 py-2">Ann&eacute;</td>
                            <td class="text-xl font-semibold">{{ driverDetails[0].vehicle.car_annee }}</td>
                        </tr>
                    </tbody>
                </table>

                <di class="flex flex-col md:flex-row justify-between gap-4">
                    <div class=" ">
                        <p class=" text-xl text-slate-500 py-2">Image du licence</p>
                        <a :href="driverDetails[0].vehicle.license_image_url" target="_blank">
                            <img :src="driverDetails[0].vehicle.license_image_url" alt="licence"
                                class="w-56 h-28 border object-cover shadow-lg rounded-lg">
                        </a>
                    </div>

                    <div class=" ">
                        <p class=" text-xl text-slate-500 py-2">Image de la voiture</p>
                        <a :href="driverDetails[0].vehicle.car_image_url" target="_blank">
                            <img :src="driverDetails[0].vehicle.car_image_url" alt="licence"
                                class="w-56 h-28 border object-cover shadow-lg rounded-lg">
                        </a>
                    </div>
                </di>
            </div>
        </div>


    </div>
</template>
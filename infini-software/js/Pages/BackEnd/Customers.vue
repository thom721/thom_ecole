<script setup>
import Paginated from "@/Components/Paginated.vue";
import { onMounted, ref, watch } from "vue";
import AppLayout1 from '@/Layouts/AppLayout1.vue';
import axios from "axios";
import { Link } from "@inertiajs/vue3";


defineOptions({
    layotu: AppLayout1,
});
const props = defineProps({
    filters: Object,
})

const customersData = ref([])

const fetchcustomersData = async () => {
    try {
        const response = await axios.get('api/customer');
        if (response.status === 200) {
            customersData.value = response.data.data
            console.log(response.data);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération des données :", error);
    }
}

onMounted(() => {
    fetchcustomersData();
})

let search = ''// ref(props.filters.search);

watch(search, (value) => {
    searchCustomers()
});

const searchCustomers = async (searchTerm) => {
    try {
        const response = await axios.get('/api/customer', {
            params: { search: search.value },
        });
        if (response.data) {
            customersData.value = response.data.data
        }
    } catch (error) {
        console.error('Erreur lors de la recherche :', error);
    }
};
</script>

<template>
    <div class="max-w-7xl px-4 mx-auto sm:px-6 lg:px-8 pt-4">

        <div class="flex justify-end me-4 mb-2">

            <input type="text"
                class="border-gray-300 focus:border-sky-600 focus:ring-sky-600 py-1 rounded-md shadow-sm  text-lg text-gray-600 w-full md:w-5/12"
                name="" v-model="search" placeholder="Rechercher un client.." id="" />

        </div>


        <div class=" overflow-x-auto mt-2">
            <table class="w-full text-sm text-center text-gray-500  ">
                <thead class="text-md text-slate-100 uppercase bg-gray-600  dark:text-gray-100 px-2">
                    <tr>
                        <th class="th p-2">Profile</th>
                        <th class="th p-2">Nom</th>
                        <th class="th p-2">Pr&eacute;nom</th>
                        <th class="th p-2">T&eacute;l&eacute;phone</th>
                        <!-- <th class="th p-2">Courriel</th>
                        <th class="th p-2">Adresse</th> -->
                        <th class="th p-2">Status</th>
                        <th class="th p-2">Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="cursor-pointer hover:bg-sky-100" :class="{ 'bg-slate-100': index % 2 == 1 }"
                        v-for="(customerData, index) in customersData.data" :key="customerData.id">

                        <td class="td py-2 flex justify-center">
                            <img :src="customerData.profile_image_url"
                                class="w-10 h-10 rounded-full object-cover flex justify-center" alt="" sizes=""
                                srcset="">
                        </td>
                        <td class="td"> {{ customerData.first_name }} </td>
                        <td class="td">{{ customerData.last_name }} </td>
                        <td class="td">{{ customerData.phoneNumber }}</td>
                        <td class="td">
                            <span v-if="customerData.isPhoneVerified == 1" class="text-green-500">Active</span>
                            <span v-else class="text-red-500">Inactive</span>
                        </td>
                        <td class="td">
                            <!-- <i class="fa fa-edit text-yellow-500 me-3 cursor-pointer" @click="editProf(customerData)"></i> -->
                            <i class="fa fa-trash text-red-500 cursor-pointer px-4"></i>
                            <Link :href="route('client.detail', customerData.firebase_uid)">Voir</Link>

                        </td>
                    </tr>
                </tbody>
            </table>
            <!-- <div v-if="customersData && customersData.data && customersData.data.length > 9" class="mt-2 flex justify-end">
          <Paginated :links="customersData.meta.links" />
        </div> -->

        </div>
    </div>
</template>
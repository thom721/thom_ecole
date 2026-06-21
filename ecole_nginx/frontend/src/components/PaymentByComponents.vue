<script setup>
const props = defineProps({
    payBy: Object,
    indexPayMont: Array,
    chekedIndex: Number,
    payDevise: String,
    // @pay by session controle and other
    pay_by: String,
    payDetail: Object,
    avance: Number,
    balance: Number,
    balances_montant: String,
    accessoires: Object,
    already_pay_accessoire: String


})

const emit = defineEmits(['checkForControle'])

const change = (index) => {
    emit('checkForControle', index, props.pay_by)
}

const versement = [
    '1 er Versement', '2 ème Versement', '3 ème Versement', '4 ème Versement'
]

const getFormattedPayBy = (obj) => {
    if (!obj || typeof obj !== 'object') {
        return []; // Retourne un tableau vide si obj est invalide
    }

    return Object.keys(obj).map((key, index) => {
        const parts = key.split('_');
        if (parts.length < 3) return key;

        const versementNumber = parseInt(parts[1], 10);

        const suffix = (versementNumber === 1)
            ? (parts[0] === 'Session' ? 'ère' : 'er')
            : 'ème';


        return `${versementNumber} ${suffix} ${parts[0]}`;
    });
};

</script>

<template>
    <div class=" py-2">
        <!-- <div class="grid grid-cols-4 py-2"> -->
        <!-- <div v-for="(value, key, index) in props.payBy " :key="index" class="col-3">

            <div class="flex flex-col items-center">
                <label class="text-slate-500" :for="key" :class="{ 'text-success': props.indexPayMont.includes(key) }">
                    {{
                        key.substring(0, 4) }}.
                    <span>{{ index + 1 }}</span>
                    <span style="font-size: 13px;" class="px-1">(<span class="pe-2 font-bold">{{ value }} </span>{{
                        props.payDevise }})</span> </label>
                <input v-if="!props.indexPayMont.includes(key)" type="checkbox"
                    :checked="props.indexPayMont.includes(key)" :disabled="index != props.chekedIndex" :id="key" name=""
                    :value="key" @change="change(index, props.pay_by)" v-model="props.payDetail.mois[key]"
                    class="cursor-pointer transition-all appearance-none rounded shadow hover:shadow-md border border-slate-300 checked:bg-sky-600 checked:border-sky-600">
                <span v-else class="bg-sky-200 px-2 rounded-md"> <strong class="text-sky-500"> Pay&eacute;
                    </strong></span>
            </div>
        </div> -->


        <!-- {{ props.indexPayMont.length }} -->

        <!-- <div v-for="(value, key, index) in props.payBy " :key="index"> -->

        <div class="py-2 pb-4">

            <div class="flex justify-between px-4">
                <p class="text-slate-500 text-md font-bold">Avance {{
                    getFormattedPayBy(props.payBy)[props.indexPayMont.length] }}</p>

                <p class="text-slate-500 text-md font-bold"><span class="text-sky-500">{{ props.avance }}</span> {{
                    props.payDevise
                    }}
                </p>
            </div>

            <div class="flex justify-between px-4 border-b">
                <p class="text-slate-500 text-md font-bold">Balance</p>
                <p class="text-slate-500 text-md font-bold"><span v-if="avance == 0 && balance == 0"
                        class="text-sky-500">{{ balance }}</span><span v-else class="text-sky-500">{{ balance
                        }}</span> {{
                            props.payDevise
                        }}

                </p>
            </div>

            <!-- <div class="flex justify-between px-4">
                <p class="text-slate-500 text-md font-bold">Total a payer</p>
                <p class="text-slate-500 text-md font-bold"><span class="text-sky-500">{{ balance }}</span> {{
                    props.payDevise
                }}
                </p>
            </div> -->
        </div>
        <div class="py-2 px-4" v-if="props.accessoires && props.accessoires.length > 0">
            <div v-for="(accessoire, index) in accessoires" :key="index" class=" flex justify-between">
                <div class="flex justify-between items-center gap-4 w-full">
                    <p class="text-slate-500 font-semibold text-nowrap">{{ accessoire.type_daccessoire }} </p>

                    <p class="text-sky-500 font-semibold text-nowrap"> {{ accessoire.prix }} {{ props.payDevise }}</p>
                </div>

                <div class="w-full flex justify-end ">
                    <input
                        v-if="already_pay_accessoire && !already_pay_accessoire.includes(accessoire.type_daccessoire)"
                        type="checkbox" :id="accessoire.type_daccessoire" name="" :value="accessoire.type_daccessoire"
                        v-model="props.payDetail.accessoires[accessoire.type_daccessoire]"
                        :checked="already_pay_accessoire.includes(accessoire.type_daccessoire)"
                        :disabled="already_pay_accessoire.includes(accessoire.type_daccessoire)"
                        class="cursor-pointer transition-all appearance-none ring-0 offset-0 shadow hover:shadow-md border border-slate-600 checked:bg-sky-600 rounded-full checked:border-sky-600">

                    <span v-else class=" px-2 rounded-md"> <strong class="text-green-500">
                            Pay&eacute;
                        </strong></span>

                </div>
            </div>
        </div>

        <div
            class="relative flex flex-col w-full h-full overflow-x-auto text-gray-700 bg-white border rounded-lg bg-clip-border shadow">

            <table id="productTable" class="w-full text-left table-auto min-w-max">

                <tbody>
                    <tr class="hover:bg-slate-50" v-for="(value, key, index) in props.payBy " :key="index"
                        :class="{ 'bg-slate-100': index % 2 == 0 }">

                        <td class="px-4 py-2 border-b border-slate-200">
                            <p v-if="key.startsWith('Versement')" class="block text-md text-slate-800">
                                {{ index + 1 }} <span v-if="index == 0">er</span> <span v-else>&egrave;me</span> <span
                                    class="ms-2">{{ key.substring(0, 9) }}</span>
                            </p>
                            <p v-if="key.startsWith('Session')" class="block text-md text-slate-800">
                                {{ index + 1 }} <span v-if="index == 0">&egrave;re</span> <span v-else>&egrave;me</span>
                                <span class="ms-2">{{ key.substring(0, 7) }}</span>
                            </p>

                            <p v-if="key.startsWith('Controle')" class="block text-md text-slate-800">
                                {{ index + 1 }} <span v-if="index == 0">er</span> <span v-else>&egrave;me</span>
                                <span class="ms-2">{{ key.substring(0, 8) }}</span>
                            </p>
                        </td>

                        <td class="px-4 py-2 border-b border-slate-200">
                            <p class="block text-md text-slate-800">
                                <span style="font-size: 13px;" class="px-1"><span class="pe-2 font-bold">{{ value }}
                                    </span>{{ props.payDevise }}</span>

                            </p>
                        </td>

                        <td>
                            <input v-if="!props.indexPayMont.includes(key)" type="checkbox"
                                :checked="props.indexPayMont.includes(key)" :disabled="index != props.chekedIndex"
                                :id="key" name="" :value="key" @change="change(index, props.pay_by)"
                                v-model="props.payDetail.mois[key]"
                                class="cursor-pointer transition-all appearance-none rounded-full shadow hover:shadow-md border border-slate-600 checked:bg-sky-600 checked:border-sky-600">
                            <span v-else class="bg-green-200 px-2 py-0.5 rounded-md"> <strong class="text-green-500">
                                    Pay&eacute;
                                </strong></span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
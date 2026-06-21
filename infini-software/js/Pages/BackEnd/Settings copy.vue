<template>
    <div class="max-w-7xl px-4 mx-auto sm:px-6 lg:px-8 pt-4">
        <h1 class="text-2xl font-bold mb-6">Paramètres Généraux</h1>

        <form @submit.prevent="saveSettings" class="space-y-6">

            <div v-for="setting in settings" :key="setting.key" class="grid md:grid-cols-2 gap-4 items-center">

                <label class="block font-semibold text-sm md:text-base">
                    {{ setting.label }}
                </label>

                <!-- TYPE MULTISELECT -->
                <template v-if="setting.type === 'multiselect'">
                    <div class="flex flex-wrap gap-4">
                        <label v-for="opt in setting.options" :key="opt" class="inline-flex items-center space-x-2">
                            <input type="checkbox" :value="opt" :checked="setting.value.includes(opt)"
                                @change="toggleMultiSelect(setting, opt)" class="form-checkbox" />
                            <span>{{ opt }}</span>
                        </label>
                    </div>
                </template>

                <!-- TYPE SELECT SIMPLE -->
                <template v-else-if="setting.type === 'select'">
                    <select v-model="setting.value" class="w-full border px-3 py-2 rounded">
                        <option disabled value="">-- Choisir --</option>
                        <option v-for="opt in setting.options" :key="opt" :value="opt">
                            {{ opt }}
                        </option>
                    </select>
                </template>

                <!-- TYPE NUMBER -->
                <template v-else-if="setting.type === 'number'">
                    <input type="number" v-model.number="setting.value" class="w-full border px-3 py-2 rounded" />
                </template>

                <!-- TYPE TEXT (par défaut) -->
                <template v-else>
                    <input type="text" v-model="setting.value" class="w-full border px-3 py-2 rounded" />
                </template>
            </div>

            <div class="pt-6">
                <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
                    Enregistrer
                </button>
            </div>

        </form>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AppLayout1 from '@/Layouts/AppLayout1.vue'

defineOptions({
    layout: AppLayout1,
})

const settings = ref([
    // ton tableau complet ici (comme tu as mis dans ton code)
    { group: 'general', key: 'app_name', label: "Nom de l'application", value: '' },
    { group: 'general', key: 'logo_url', label: 'URL du logo', value: '' },
    { group: 'general', key: 'favicon_url', label: 'URL du favicon', value: '' },
    { group: 'general', key: 'available_languages', label: 'Langues disponibles', value: [], type: 'multiselect', options: ['fr', 'en', 'es', 'ht'] },
    { group: 'general', key: 'timezone', label: 'Fuseau horaire', value: '', type: 'select', options: ['UTC', 'America/New_York', 'Europe/Paris'] },
    { group: 'general', key: 'date_format', label: 'Format de date/heure', value: '', type: 'select', options: ['YYYY-MM-DD HH:mm', 'DD/MM/YYYY HH:mm', 'MM-DD-YYYY hh:mm A'] },
    { group: 'general', key: 'currency', label: 'Devise principale', value: '', type: 'select', options: ['USD', 'EUR', 'HTG'] },

    // ... reste des paramètres (inchangés)

    { group: 'trip', key: 'base_fare', label: 'Tarif de base', value: 0, type: 'number' },
    { group: 'trip', key: 'price_per_km', label: 'Prix par kilomètre', value: 0, type: 'number' },

    { group: 'trip', key: 'vehicle_types', label: 'Types de véhicules disponibles', value: [], type: 'multiselect', options: ['eco', 'suv', 'lux', 'van'] },

    { group: 'payment', key: 'payment_gateway', label: 'Gateway de paiement', value: [], type: 'multiselect', options: ['stripe', 'paypal', 'coinpayment', 'flutterwave'] },

    // etc.
])

// Charger les settings depuis l'API
onMounted(async () => {
    try {
        const res = await axios.get('/api/admin/settings')
        const data = res.data.general || []

        // On met à jour les valeurs avec celles venant de l'API
        data.forEach(s => {
            const found = settings.value.find(item => item.key === s.key)
            if (found) {
                if (found.type === 'multiselect' && Array.isArray(s.value)) {
                    found.value = s.value
                } else if (found.type === 'number') {
                    found.value = Number(s.value) || 0
                } else {
                    found.value = s.value
                }
            }
        })
    } catch (e) {
        console.error("Erreur chargement settings:", e)
    }
})

// Gestion toggle checkbox multiselect
function toggleMultiSelect(setting, option) {
    const idx = setting.value.indexOf(option)
    if (idx === -1) {
        setting.value.push(option)
    } else {
        setting.value.splice(idx, 1)
    }
}

const saveSettings = async () => {
    try {
        await axios.post('/api/admin/settings', {
            settings: settings.value.map(s => ({
                group: s.group,
                key: s.key,
                value: s.value
            }))
        })
        alert('Paramètres enregistrés.')
    } catch (e) {
        alert('Erreur lors de l\'enregistrement.')
        console.error(e)
    }
}
</script>
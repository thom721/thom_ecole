<!-- resources/js/Pages/Admin/Settings.vue -->
<template>
    <div class="max-w-7xl px-4 mx-auto sm:px-6 lg:px-8 pt-4">
        <h1 class="text-2xl font-bold mb-6">Paramètres Généraux</h1>

        <form @submit.prevent="saveSettings" class="space-y-6">
            <div v-for="(setting, index) in settings" :key="index">
                <div class="grid md:grid-cols-2 gap-4 items-center">


                    <div>
                        <label class="block font-semibold text-sm md:text-base">
                            {{ setting.label }}
                        </label>
                        <template v-if="setting.type === 'select'">
                            <select v-model="setting.value" class="w-full border px-3 py-2 rounded">
                                <option disabled value="">-- Choisir --</option>
                                <option v-for="opt in setting.options" :key="opt" :value="opt">
                                    {{ opt }}
                                </option>
                            </select>
                        </template>

                        <template v-else>
                            <input v-model="setting.value" class="w-full border px-3 py-2 rounded"
                                :type="setting.type || 'text'" />
                        </template>
                    </div>
                </div>
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
import AppLayout1 from '@/Layouts/AppLayout1.vue';
defineOptions({
    layout: AppLayout1,
});
const settings = ref([
    // 🔧 Paramètres Généraux
    { group: 'general', key: 'app_name', label: "Nom de l'application", value: '' },
    { group: 'general', key: 'logo_url', label: 'URL du logo', value: '' },
    { group: 'general', key: 'favicon_url', label: 'URL du favicon', value: '' },
    { group: 'general', key: 'available_languages', label: 'Langues disponibles', value: '', type: 'multiselect', options: ['fr', 'en', 'es', 'ht'] },
    { group: 'general', key: 'timezone', label: 'Fuseau horaire', value: '', type: 'select', options: ['UTC', 'America/New_York', 'Europe/Paris'] },
    { group: 'general', key: 'date_format', label: 'Format de date/heure', value: '', type: 'select', options: ['YYYY-MM-DD HH:mm', 'DD/MM/YYYY HH:mm', 'MM-DD-YYYY hh:mm A'] },
    { group: 'general', key: 'currency', label: 'Devise principale', value: '', type: 'select', options: ['USD', 'EUR', 'HTG'] },

    // 🌍 Localisation & Zones
    { group: 'location', key: 'map_provider', label: 'Fournisseur de carte', value: '', type: 'select', options: ['google', 'mapbox'] },
    { group: 'location', key: 'zone_activation_enabled', label: 'Activation des zones dynamiques', value: '', type: 'select', options: ['on', 'off'] },

    // 🚗 Courses
    { group: 'trip', key: 'pricing_type', label: 'Type de tarification', value: '', type: 'select', options: ['km', 'minute', 'fixe'] },
    { group: 'trip', key: 'base_fare', label: 'Tarif de base', value: '', type: 'number' },
    { group: 'trip', key: 'price_per_km', label: 'Prix par kilomètre', value: '', type: 'number' },
    { group: 'trip', key: 'price_per_minute', label: 'Prix par minute', value: '', type: 'number' },
    { group: 'trip', key: 'min_fare', label: 'Tarif minimum', value: '', type: 'number' },
    { group: 'trip', key: 'vehicle_types', label: 'Types de véhicules disponibles', value: '', type: 'multiselect', options: ['eco', 'suv', 'lux', 'van'] },
    { group: 'trip', key: 'realtime_tracking_enabled', label: 'Suivi en temps réel', value: '', type: 'select', options: ['on', 'off'] },

    // 👤 Utilisateurs - Passagers
    { group: 'user', key: 'passenger_phone_verification', label: 'Vérif. téléphone passager', value: '', type: 'select', options: ['on', 'off'] },
    { group: 'user', key: 'payment_methods_passenger', label: 'Méthodes de paiement passager', value: '', type: 'multiselect', options: ['card', 'cash', 'wallet'] },

    // 👤 Chauffeurs
    { group: 'driver', key: 'auto_approval_driver', label: 'Approbation automatique chauffeur', value: '', type: 'select', options: ['on', 'off'] },

    // 💰 Paiements
    { group: 'payment', key: 'accepted_methods', label: 'Modes de paiement acceptés', value: '', type: 'multiselect', options: ['card', 'cash', 'wallet'] },
    { group: 'payment', key: 'wallet_enabled', label: 'Portefeuille activé', value: '', type: 'select', options: ['on', 'off'] },
    { group: 'payment', key: 'commission_mode', label: 'Type de commission', value: '', type: 'select', options: ['fixe', 'variable'] },
    { group: 'payment', key: 'payout_frequency', label: 'Cycle de paiement chauffeur', value: '', type: 'select', options: ['daily', 'weekly', 'manual'] },
    { group: 'payment', key: 'payment_gateway', label: 'Gateway de paiement', value: '', type: 'multiselect', options: ['stripe', 'paypal', 'coinpayment', 'flutterwave'] },

    // 📱 Notifications
    { group: 'notification', key: 'enable_sms', label: 'Activer notifications SMS', value: '', type: 'select', options: ['on', 'off'] },
    { group: 'notification', key: 'enable_email', label: 'Activer notifications email', value: '', type: 'select', options: ['on', 'off'] },
    { group: 'notification', key: 'enable_push', label: 'Activer notifications Push', value: '', type: 'select', options: ['on', 'off'] },
    { group: 'notification', key: 'chat_enabled', label: 'Chat passager-chauffeur', value: '', type: 'select', options: ['on', 'off'] },
    { group: 'notification', key: 'support_ticket_enabled', label: 'Assistance via ticket', value: '', type: 'select', options: ['on', 'off'] },

    // 🛑 Sécurité
    { group: 'security', key: 'enable_2fa', label: 'Authentification 2FA', value: '', type: 'select', options: ['on', 'off'] },
    { group: 'security', key: 'fraud_detection_enabled', label: 'Détection de fraude', value: '', type: 'select', options: ['on', 'off'] },

    // 📊 Rapports
    { group: 'report', key: 'enable_exports', label: 'Export des données', value: '', type: 'select', options: ['on', 'off'] },
    { group: 'report', key: 'default_export_format', label: 'Format export par défaut', value: '', type: 'select', options: ['csv', 'xlsx', 'pdf'] },

    // 🧩 Intégrations
    { group: 'integration', key: 'map_api_provider', label: 'API Map', value: '', type: 'select', options: ['google', 'mapbox'] },
    { group: 'integration', key: 'email_service_provider', label: 'Email provider', value: '', type: 'select', options: ['sendgrid', 'mailchimp'] },
    { group: 'integration', key: 'crm_integration', label: 'CRM intégré', value: '', type: 'select', options: ['zendesk', 'hubspot'] },
])


onMounted(async () => {
    const res = await axios.get('/api/admin/settings')
    const data = res.data.general || []
    data.forEach(s => {
        const found = settings.value.find(item => item.key === s.key)
        if (found) found.value = s.value
    })
})

const saveSettings = async () => {
    await axios.post('/api/admin/settings', {
        settings: settings.value.map(s => ({
            group: s.group,
            key: s.key,
            value: s.value
        }))
    })

    alert('Paramètres enregistrés.')
}
</script>
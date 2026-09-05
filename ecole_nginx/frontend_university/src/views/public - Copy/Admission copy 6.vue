<script setup>
import { ref } from 'vue'
import api from '../../services/api'

const form = ref({ nom: '', prenom: '', telephone: '' })
const message = ref('')

const submitAdmission = async () => {
  try {
    // Appel à ton API FastAPI (post.admission)
    await api.post('/admission', form.value)
    message.value = "✅ Votre demande d'admission a été envoyée !"
  } catch (error) {
    message.value = "❌ Erreur lors de l'envoi."
  }
}
</script>

<template>
admission
</template>
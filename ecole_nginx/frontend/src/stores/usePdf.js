// composables/usePdf.js
import axios from 'axios'
import { ref } from 'vue'
import Swal from 'sweetalert2'
import { useAuthStore } from '@/stores/auth'

// Portage web de canPrintNonReceipt() (flutter_version/lib/core/print_gate.dart)
// — jamais reproduit ici jusqu'ici, d'où les impressions non bloquées malgré
// une licence expirée (voir isLicenseAuthorized, stores/auth.js). Les reçus
// (paiement/vente/inscription) restent exclus, comme côté Flutter
// (`endpoint.startswith('v1/print-recu')`).
export function canPrintNonReceipt(endpoint) {
  if (endpoint.startsWith('/print-recu')) return true
  const authStore = useAuthStore()
  if (authStore.isLicenseAuthorized) return true
  Swal.fire({
    icon: 'error',
    title: 'Impression bloquée',
    text: "La clé d'activation est invalide. Vous ne pouvez pas imprimer. Veuillez contacter l'administrateur ou l'équipe de développement.",
  })
  return false
}

export function usePdf() {
  const baseUrl = import.meta.env.VITE_APP_BASE_URL

  const submitPdf = async (endpoint, data) => {
    if (!canPrintNonReceipt(endpoint)) return
    try {
      const token = localStorage.getItem('auth-token')
      const response = await axios.post(`${baseUrl}${endpoint}`, data, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/pdf',
        },
        responseType: 'blob',
      })

      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      window.open(url, '_blank')
      setTimeout(() => window.URL.revokeObjectURL(url), 100)

    } catch (error) {
      console.error('Erreur Impression:', error)
      alert('Erreur lors de la génération du document.')
    }
  }

  return { submitPdf }
}



export function usePdfWithLoading() {
  const baseUrl  = import.meta.env.VITE_APP_BASE_URL
  const loading  = ref(false)
  const error    = ref({})
  const rowErrors = ref({})
  const loadingMap = ref({})
 

const submitPdf = async (endpoint, data, key = 0) => {
  if (!canPrintNonReceipt(endpoint)) return

  loadingMap.value = { ...loadingMap.value, [key]: true }
    error.value[key] = null
    try {
      const token = localStorage.getItem('auth-token')
      const response = await axios.post(`${baseUrl}${endpoint}`, data, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/pdf',
        },
        responseType: 'blob',
      })
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url  = window.URL.createObjectURL(blob)
      window.open(url, '_blank')
      setTimeout(() => window.URL.revokeObjectURL(url), 100)
    } catch (e) {
      let message = 'Erreur lors de la génération du document.'
      if (e.response?.data instanceof Blob) {
        try {
          const text = await e.response.data.text()
          const json = JSON.parse(text)
          message = json.errors
            ? Object.values(json.errors).flat().join('\n')
            : (json.detail ?? json.message ?? message)
        } catch {
          // Le blob n'était pas du JSON (ex: PDF partiel) — garde le message par défaut.
        }
      } else {
        message = e.response?.data?.detail ?? e.response?.data?.message ?? message
      }
      error.value[key] = message
      Swal.fire({ icon: 'error', text: message })
    } finally {
     loadingMap.value = { ...loadingMap.value, [key]: false }
     //  loadingMap.value[key] = false
    }
  }

  return { submitPdf, loading, error, loadingMap }
}
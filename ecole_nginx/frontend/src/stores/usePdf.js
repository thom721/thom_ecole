// composables/usePdf.js
import axios from 'axios'
import { ref } from 'vue'

export function usePdf() {
  const baseUrl = import.meta.env.VITE_APP_BASE_URL

  const submitPdf = async (endpoint, data) => {
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
        if (e.response?.data instanceof Blob) {
        const text = await e.response.data.text()
        const json = JSON.parse(text)

        if (json.errors) {
          // Boucle sur les erreurs et affiche chacune
          const messages = Object.values(json.errors).flat().join("\n")
          error(messages,false) // ton toast/notification d'erreur
        } else {
          error(json.message ?? 'Une erreur est survenue.',false)
        }
      }
       error.value[key] = e.response?.data?.message || 'Erreur lors de la génération.'
    } finally {
     loadingMap.value = { ...loadingMap.value, [key]: false }
     //  loadingMap.value[key] = false
    }
  }

  return { submitPdf, loading, error, loadingMap }
}
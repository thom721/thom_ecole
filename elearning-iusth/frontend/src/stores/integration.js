import { defineStore } from 'pinia'
import axios from 'axios'

export const useIntegrationStore = defineStore('integration', {
  actions: {
    async fetchEcoleNginxAnnees() {
      const { data } = await axios.get('/integration/ecole-nginx/annees-academiques')
      return data
    },

    async importFromEcoleNginx(anneeAcademiqueId) {
      const { data } = await axios.post('/integration/ecole-nginx/import', null, {
        params: { annee_academique_id: anneeAcademiqueId },
      })
      return data
    },

    async fetchEcoleNginxClasses(anneeAcademiqueId) {
      const { data } = await axios.get('/integration/ecole-nginx/classes', {
        params: { annee_academique_id: anneeAcademiqueId },
      })
      return data
    },

    async fetchEcoleNginxClasseStudents(classeId, anneeAcademiqueId) {
      const { data } = await axios.get(`/integration/ecole-nginx/classes/${classeId}/students`, {
        params: { annee_academique_id: anneeAcademiqueId },
      })
      return data
    },

    async activateStudent(payload) {
      const { data } = await axios.post('/integration/ecole-nginx/activate-student', payload)
      return data
    },

    async syncStaffCredentials() {
      const { data } = await axios.post('/integration/ecole-nginx/sync-credentials')
      return data
    },
  },
})

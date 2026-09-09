import { defineStore } from 'pinia'
import axios from 'axios'

export const useCohortsStore = defineStore('cohorts', {
  actions: {
    async fetchCohorts() {
      const { data } = await axios.get('/cohorts')
      return data
    },

    async createCohort(payload) {
      const { data } = await axios.post('/cohorts', payload)
      return data
    },

    async deleteCohort(id) {
      await axios.delete(`/cohorts/${id}`)
    },

    async addMember(cohortId, userId) {
      const { data } = await axios.post(`/cohorts/${cohortId}/members`, { user_id: userId })
      return data
    },

    async removeMember(cohortId, userId) {
      const { data } = await axios.delete(`/cohorts/${cohortId}/members/${userId}`)
      return data
    },
  },
})

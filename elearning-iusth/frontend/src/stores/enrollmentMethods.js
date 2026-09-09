import { defineStore } from 'pinia'
import axios from 'axios'

export const useEnrollmentMethodsStore = defineStore('enrollmentMethods', {
  actions: {
    async fetchSettings(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/enrollment-settings`)
      return data
    },

    async updateSettings(courseId, payload) {
      const { data } = await axios.patch(`/courses/${courseId}/enrollment-settings`, payload)
      return data
    },

    async enrollSelf(courseId, key) {
      const { data } = await axios.post(`/courses/${courseId}/enroll-self`, { key: key || null })
      return data
    },

    async enrollGuest(courseId, key) {
      const { data } = await axios.post(`/courses/${courseId}/enroll-guest`, { key: key || null })
      return data
    },

    async fetchCohortSyncs(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/cohort-syncs`)
      return data
    },

    async createCohortSync(courseId, cohortId, role = 'student') {
      const { data } = await axios.post(`/courses/${courseId}/cohort-syncs`, { cohort_id: cohortId, role })
      return data
    },

    async deleteCohortSync(id) {
      await axios.delete(`/cohort-syncs/${id}`)
    },
  },
})

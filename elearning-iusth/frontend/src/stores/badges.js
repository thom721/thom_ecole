import { defineStore } from 'pinia'
import axios from 'axios'

export const useBadgesStore = defineStore('badges', {
  actions: {
    async fetchCourseBadges(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/badges`)
      return data
    },

    async createCourseBadge(courseId, payload) {
      const { data } = await axios.post(`/courses/${courseId}/badges`, payload)
      return data
    },

    async createSiteBadge(payload) {
      const { data } = await axios.post('/badges/site', payload)
      return data
    },

    async fetchBadge(id) {
      const { data } = await axios.get(`/badges/${id}`)
      return data
    },

    async updateBadge(id, payload) {
      const { data } = await axios.patch(`/badges/${id}`, payload)
      return data
    },

    async deleteBadge(id) {
      await axios.delete(`/badges/${id}`)
    },

    async replaceCriteria(id, criteria) {
      const { data } = await axios.put(`/badges/${id}/criteria`, { criteria })
      return data
    },

    async awardBadge(id, userId) {
      const { data } = await axios.post(`/badges/${id}/award`, { user_id: userId })
      return data
    },

    async reevaluate(courseId, studentId) {
      const { data } = await axios.post(`/courses/${courseId}/badges/reevaluate`, null, {
        params: studentId ? { student_id: studentId } : {},
      })
      return data
    },

    async fetchCourseBadgesMine(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/badges/mine`)
      return data
    },

    async fetchMyBadges() {
      const { data } = await axios.get('/badges/mine')
      return data
    },
  },
})

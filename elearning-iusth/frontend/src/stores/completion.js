import { defineStore } from 'pinia'
import axios from 'axios'

export const useCompletionStore = defineStore('completion', {
  actions: {
    async fetchMine(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/completion/mine`)
      return data
    },

    async fetchReport(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/completion/report`)
      return data
    },

    async markComplete(resourceId) {
      await axios.post(`/resources/${resourceId}/complete`)
    },

    async unmarkComplete(resourceId) {
      await axios.delete(`/resources/${resourceId}/complete`)
    },

    async markCompleteGeneric(itemType, itemId) {
      await axios.post(`/completion/${itemType}/${itemId}`)
    },

    async unmarkCompleteGeneric(itemType, itemId) {
      await axios.delete(`/completion/${itemType}/${itemId}`)
    },

    async fetchConfig(itemType, itemId) {
      const { data } = await axios.get(`/completion-config/${itemType}/${itemId}`)
      return data
    },

    async updateConfig(itemType, itemId, mode) {
      const { data } = await axios.patch(`/completion-config/${itemType}/${itemId}`, { mode })
      return data
    },
  },
})

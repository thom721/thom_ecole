import { defineStore } from 'pinia'
import axios from 'axios'

export const useAccessConditionsStore = defineStore('accessConditions', {
  actions: {
    async fetchConditions(itemType, itemId) {
      const { data } = await axios.get(`/access-conditions/${itemType}/${itemId}`)
      return data
    },

    async createCondition(itemType, itemId, payload) {
      const { data } = await axios.post(`/access-conditions/${itemType}/${itemId}`, payload)
      return data
    },

    async deleteCondition(id) {
      await axios.delete(`/access-conditions/${id}`)
    },
  },
})

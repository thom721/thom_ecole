import { defineStore } from 'pinia'
import axios from 'axios'

export const useChoicesStore = defineStore('choices', {
  actions: {
    async createChoice(sectionId, payload) {
      const { data } = await axios.post(`/sections/${sectionId}/choices`, payload)
      return data
    },

    async fetchChoice(id) {
      const { data } = await axios.get(`/choices/${id}`)
      return data
    },

    async respond(id, optionIds) {
      const { data } = await axios.post(`/choices/${id}/respond`, { option_ids: optionIds })
      return data
    },

    async retract(id) {
      const { data } = await axios.delete(`/choices/${id}/respond`)
      return data
    },
  },
})

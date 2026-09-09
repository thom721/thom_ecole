import { defineStore } from 'pinia'
import axios from 'axios'

export const useBlocksStore = defineStore('blocks', {
  actions: {
    async fetchMyBlocks() {
      const { data } = await axios.get('/blocks/mine')
      return data
    },

    async addBlock(payload) {
      const { data } = await axios.post('/blocks/mine', payload)
      return data
    },

    async updateBlock(id, payload) {
      const { data } = await axios.patch(`/blocks/mine/${id}`, payload)
      return data
    },

    async reorder(region, orderedIds) {
      await axios.post('/blocks/mine/reorder', { region, ordered_ids: orderedIds })
    },

    async deleteBlock(id) {
      await axios.delete(`/blocks/mine/${id}`)
    },
  },
})

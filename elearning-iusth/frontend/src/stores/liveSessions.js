import { defineStore } from 'pinia'
import axios from 'axios'

export const useLiveSessionsStore = defineStore('liveSessions', {
  actions: {
    async createLiveSession(sectionId, payload) {
      const { data } = await axios.post(`/sections/${sectionId}/live-sessions`, payload)
      return data
    },

    async fetchLiveSession(id) {
      const { data } = await axios.get(`/live-sessions/${id}`)
      return data
    },

    async updateLiveSession(id, payload) {
      const { data } = await axios.patch(`/live-sessions/${id}`, payload)
      return data
    },

    async deleteLiveSession(id) {
      await axios.delete(`/live-sessions/${id}`)
    },

    async join(id) {
      const { data } = await axios.post(`/live-sessions/${id}/join`)
      return data
    },

    async leave(id) {
      await axios.post(`/live-sessions/${id}/leave`)
    },

    async fetchAttendance(id) {
      const { data } = await axios.get(`/live-sessions/${id}/attendance`)
      return data
    },
  },
})

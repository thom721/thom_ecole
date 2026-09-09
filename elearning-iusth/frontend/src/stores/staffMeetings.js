import { defineStore } from 'pinia'
import axios from 'axios'

export const useStaffMeetingsStore = defineStore('staffMeetings', {
  actions: {
    async fetchEligibleUsers() {
      const { data } = await axios.get('/staff-meetings/eligible-users')
      return data
    },

    async createMeeting(payload) {
      const { data } = await axios.post('/staff-meetings', payload)
      return data
    },

    async fetchMine() {
      const { data } = await axios.get('/staff-meetings/mine')
      return data
    },

    async fetchMeeting(id) {
      const { data } = await axios.get(`/staff-meetings/${id}`)
      return data
    },

    async join(id) {
      const { data } = await axios.post(`/staff-meetings/${id}/join`)
      return data
    },

    async updateMeeting(id, payload) {
      const { data } = await axios.patch(`/staff-meetings/${id}`, payload)
      return data
    },

    async deleteMeeting(id) {
      await axios.delete(`/staff-meetings/${id}`)
    },
  },
})

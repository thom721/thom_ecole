import { defineStore } from 'pinia'
import axios from 'axios'

export const useCalendarStore = defineStore('calendar', {
  actions: {
    async fetchEvents(courseId, from, to) {
      const params = { from, to }
      if (courseId) params.course_id = courseId
      const { data } = await axios.get('/calendar', { params })
      return data
    },

    async createEvent(payload) {
      const { data } = await axios.post('/calendar/events', payload)
      return data
    },

    async updateEvent(id, payload) {
      const { data } = await axios.patch(`/calendar/events/${id}`, payload)
      return data
    },

    async deleteEvent(id) {
      await axios.delete(`/calendar/events/${id}`)
    },
  },
})

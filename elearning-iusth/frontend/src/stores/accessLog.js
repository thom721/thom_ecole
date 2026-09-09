import { defineStore } from 'pinia'
import axios from 'axios'

export const useAccessLogStore = defineStore('accessLog', {
  actions: {
    async fetchSummary(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/access-log/summary`)
      return data
    },

    async fetchStudentSummary(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/access-log/students`)
      return data
    },
  },
})

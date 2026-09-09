import { defineStore } from 'pinia'
import axios from 'axios'

export const useScalesStore = defineStore('scales', {
  actions: {
    async fetchScales(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/scales`)
      return data
    },

    async createScale(courseId, payload) {
      const { data } = await axios.post(`/courses/${courseId}/scales`, payload)
      return data
    },

    async createSiteScale(payload) {
      const { data } = await axios.post('/scales/site', payload)
      return data
    },

    async deleteScale(id) {
      await axios.delete(`/scales/${id}`)
    },

    async fetchGradeLetters(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/grade-letters`)
      return data
    },

    async replaceGradeLetters(courseId, letters) {
      const { data } = await axios.put(`/courses/${courseId}/grade-letters`, { letters })
      return data
    },
  },
})

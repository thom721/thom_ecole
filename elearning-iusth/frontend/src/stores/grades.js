import { defineStore } from 'pinia'
import axios from 'axios'

export const useGradesStore = defineStore('grades', {
  actions: {
    async fetchGradeCategories(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/grade-categories`)
      return data
    },

    async createGradeCategory(courseId, payload) {
      const { data } = await axios.post(`/courses/${courseId}/grade-categories`, payload)
      return data
    },

    async deleteGradeCategory(id) {
      await axios.delete(`/grade-categories/${id}`)
    },

    async fetchGradeItems(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/grade-items`)
      return data
    },

    async createGradeItem(courseId, payload) {
      const { data } = await axios.post(`/courses/${courseId}/grade-items`, payload)
      return data
    },

    async updateGradeItem(id, payload) {
      const { data } = await axios.patch(`/grade-items/${id}`, payload)
      return data
    },

    async deleteGradeItem(id) {
      await axios.delete(`/grade-items/${id}`)
    },

    async setManualGrade(itemId, studentId, payload) {
      const { data } = await axios.patch(`/grade-items/${itemId}/grades/${studentId}`, payload)
      return data
    },

    async fetchGradeReport(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/grades/report`)
      return data
    },

    async fetchMyGrades(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/grades/mine`)
      return data
    },
  },
})

import { defineStore } from 'pinia'
import axios from 'axios'

export const useLessonsStore = defineStore('lessons', {
  actions: {
    async createLesson(sectionId, payload) {
      const { data } = await axios.post(`/sections/${sectionId}/lessons`, payload)
      return data
    },

    async fetchLessonConfig(id) {
      const { data } = await axios.get(`/lessons/${id}/config`)
      return data
    },

    async updateLesson(id, payload) {
      const { data } = await axios.patch(`/lessons/${id}`, payload)
      return data
    },

    async deleteLesson(id) {
      await axios.delete(`/lessons/${id}`)
    },

    async addPage(lessonId, payload) {
      const { data } = await axios.post(`/lessons/${lessonId}/pages`, payload)
      return data
    },

    async updatePage(pageId, payload) {
      const { data } = await axios.patch(`/lesson-pages/${pageId}`, payload)
      return data
    },

    async deletePage(pageId) {
      await axios.delete(`/lesson-pages/${pageId}`)
    },

    async fetchEssayGradingQueue(lessonId) {
      const { data } = await axios.get(`/lessons/${lessonId}/essay-grading`)
      return data
    },

    async gradeEssayPageAttempt(pageAttemptId, payload) {
      const { data } = await axios.patch(`/lesson-page-attempts/${pageAttemptId}/grade`, payload)
      return data
    },

    async startAttempt(lessonId, password) {
      const { data } = await axios.post(`/lessons/${lessonId}/attempts`, { password: password || null })
      return data
    },

    async fetchAttempt(attemptId) {
      const { data } = await axios.get(`/lesson-attempts/${attemptId}`)
      return data
    },

    async answerPage(attemptId, pageId, payload) {
      const { data } = await axios.post(`/lesson-attempts/${attemptId}/pages/${pageId}/answer`, payload)
      return data
    },

    async completeAttempt(attemptId) {
      const { data } = await axios.post(`/lesson-attempts/${attemptId}/complete`)
      return data
    },

    async fetchMyAttempts(lessonId) {
      const { data } = await axios.get(`/lessons/${lessonId}/attempts/mine`)
      return data
    },
  },
})

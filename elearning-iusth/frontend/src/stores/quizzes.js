import { defineStore } from 'pinia'
import axios from 'axios'

export const useQuizzesStore = defineStore('quizzes', {
  actions: {
    async createQuiz(sectionId, payload) {
      const { data } = await axios.post(`/sections/${sectionId}/quizzes`, payload)
      return data
    },

    async fetchQuiz(id) {
      const { data } = await axios.get(`/quizzes/${id}`)
      return data
    },

    async fetchQuizConfig(id) {
      const { data } = await axios.get(`/quizzes/${id}/config`)
      return data
    },

    async addQuizQuestion(quizId, payload) {
      const { data } = await axios.post(`/quizzes/${quizId}/questions`, payload)
      return data
    },

    async removeQuizQuestion(quizQuestionId) {
      await axios.delete(`/quiz-questions/${quizQuestionId}`)
    },

    async addDrawRule(quizId, payload) {
      const { data } = await axios.post(`/quizzes/${quizId}/draw-rules`, payload)
      return data
    },

    async removeDrawRule(ruleId) {
      await axios.delete(`/draw-rules/${ruleId}`)
    },

    async fetchCourseQuestions(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/questions`)
      return data
    },

    async fetchCourseQuestionCategories(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/question-categories`)
      return data
    },

    async createQuestionCategory(courseId, payload) {
      const { data } = await axios.post(`/courses/${courseId}/question-categories`, payload)
      return data
    },

    async createQuestion(courseId, payload) {
      const { data } = await axios.post(`/courses/${courseId}/questions`, payload)
      return data
    },

    async startAttempt(quizId) {
      const { data } = await axios.post(`/quizzes/${quizId}/attempts`)
      return data
    },

    async fetchAttempt(attemptId) {
      const { data } = await axios.get(`/quiz-attempts/${attemptId}`)
      return data
    },

    async saveResponse(attemptId, questionId, answerData) {
      await axios.patch(`/quiz-attempts/${attemptId}/responses/${questionId}`, { answer_data: answerData })
    },

    async submitAttempt(attemptId) {
      const { data } = await axios.post(`/quiz-attempts/${attemptId}/submit`)
      return data
    },

    async fetchQuizAttempts(quizId) {
      const { data } = await axios.get(`/quizzes/${quizId}/attempts`)
      return data
    },

    async fetchMyQuizAttempts(quizId) {
      const { data } = await axios.get(`/quizzes/${quizId}/attempts/mine`)
      return data
    },

    async gradeResponse(attemptId, questionId, payload) {
      const { data } = await axios.patch(`/quiz-attempts/${attemptId}/responses/${questionId}/grade`, payload)
      return data
    },
  },
})

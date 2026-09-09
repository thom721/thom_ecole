import { defineStore } from 'pinia'
import axios from 'axios'

export const useWorkshopsStore = defineStore('workshops', {
  actions: {
    async createWorkshop(sectionId, payload) {
      const { data } = await axios.post(`/sections/${sectionId}/workshops`, payload)
      return data
    },

    async fetchWorkshop(id) {
      const { data } = await axios.get(`/workshops/${id}`)
      return data
    },

    async fetchDimensions(id) {
      const { data } = await axios.get(`/workshops/${id}/dimensions`)
      return data
    },

    async updateWorkshop(id, payload) {
      const { data } = await axios.patch(`/workshops/${id}`, payload)
      return data
    },

    async switchPhase(id, phase) {
      const { data } = await axios.post(`/workshops/${id}/switch-phase`, { phase })
      return data
    },

    async replaceDimensions(id, dimensions) {
      const { data } = await axios.put(`/workshops/${id}/dimensions`, { dimensions })
      return data
    },

    async fetchNumerrorsMap(id) {
      const { data } = await axios.get(`/workshops/${id}/numerrors-map`)
      return data
    },

    async replaceNumerrorsMap(id, rows) {
      const { data } = await axios.put(`/workshops/${id}/numerrors-map`, { rows })
      return data
    },

    async submit(workshopId, formData) {
      const { data } = await axios.post(`/workshops/${workshopId}/submissions`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },

    async fetchMySubmission(workshopId) {
      const { data } = await axios.get(`/workshops/${workshopId}/submissions/mine`)
      return data
    },

    async fetchSubmissions(workshopId) {
      const { data } = await axios.get(`/workshops/${workshopId}/submissions`)
      return data
    },

    async fetchSubmission(id) {
      const { data } = await axios.get(`/workshop-submissions/${id}`)
      return data
    },

    async overrideSubmission(id, payload) {
      const { data } = await axios.patch(`/workshop-submissions/${id}/override`, payload)
      return data
    },

    async allocateManual(workshopId, payload) {
      const { data } = await axios.post(`/workshops/${workshopId}/allocate/manual`, payload)
      return data
    },

    async allocateRandom(workshopId, reviewsPerSubmission) {
      const { data } = await axios.post(`/workshops/${workshopId}/allocate/random`, { reviews_per_submission: reviewsPerSubmission })
      return data
    },

    async deleteAssessment(id) {
      await axios.delete(`/workshop-assessments/${id}`)
    },

    async fetchMyAssessments(workshopId) {
      const { data } = await axios.get('/workshop-assessments/mine', { params: { workshop_id: workshopId } })
      return data
    },

    async fetchAssessment(id) {
      const { data } = await axios.get(`/workshop-assessments/${id}`)
      return data
    },

    async saveGrades(assessmentId, payload) {
      const { data } = await axios.put(`/workshop-assessments/${assessmentId}/grades`, payload)
      return data
    },

    async setFeedbackReviewer(assessmentId, payload) {
      const { data } = await axios.patch(`/workshop-assessments/${assessmentId}/feedback-reviewer`, payload)
      return data
    },
  },
})

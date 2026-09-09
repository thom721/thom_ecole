import { defineStore } from 'pinia'
import axios from 'axios'

export const useCompetenciesStore = defineStore('competencies', {
  actions: {
    async fetchFrameworks() {
      const { data } = await axios.get('/competency-frameworks')
      return data
    },

    async createFramework(payload) {
      const { data } = await axios.post('/competency-frameworks', payload)
      return data
    },

    async deleteFramework(id) {
      await axios.delete(`/competency-frameworks/${id}`)
    },

    async fetchFrameworkCompetencies(frameworkId) {
      const { data } = await axios.get(`/competency-frameworks/${frameworkId}/competencies`)
      return data
    },

    async createCompetency(frameworkId, payload) {
      const { data } = await axios.post(`/competency-frameworks/${frameworkId}/competencies`, payload)
      return data
    },

    async deleteCompetency(id) {
      await axios.delete(`/competencies/${id}`)
    },

    async fetchCourseCompetencies(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/competencies`)
      return data
    },

    async linkCourseCompetency(courseId, competencyId) {
      const { data } = await axios.post(`/courses/${courseId}/competencies`, { competency_id: competencyId })
      return data
    },

    async unlinkCourseCompetency(linkId) {
      await axios.delete(`/course-competencies/${linkId}`)
    },

    async linkModuleCompetency(itemType, itemId, courseId, competencyId) {
      const { data } = await axios.post(`/activities/${itemType}/${itemId}/competencies`, { competency_id: competencyId }, {
        params: { course_id: courseId },
      })
      return data
    },

    async gradeStudentCompetency(courseId, competencyId, studentId, gradeRank, note) {
      const { data } = await axios.patch(`/courses/${courseId}/competencies/${competencyId}/students/${studentId}`, {
        grade_rank: gradeRank, note,
      })
      return data
    },

    async fetchMyCourseCompetencies(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/competencies/mine`)
      return data
    },

    async fetchMyCompetencies() {
      const { data } = await axios.get('/competencies/mine')
      return data
    },

    async fetchScales(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/scales`)
      return data
    },

    // --- Plans ---
    async fetchMyPlans() {
      const { data } = await axios.get('/plans/mine')
      return data
    },

    async createPlan(payload) {
      const { data } = await axios.post('/plans', payload)
      return data
    },

    async fetchPlan(id) {
      const { data } = await axios.get(`/plans/${id}`)
      return data
    },

    async updatePlan(id, payload) {
      const { data } = await axios.patch(`/plans/${id}`, payload)
      return data
    },

    async deletePlan(id) {
      await axios.delete(`/plans/${id}`)
    },

    async addPlanCompetency(planId, competencyId) {
      const { data } = await axios.post(`/plans/${planId}/competencies`, null, { params: { competency_id: competencyId } })
      return data
    },

    async removePlanCompetency(linkId) {
      await axios.delete(`/plan-competencies/${linkId}`)
    },
  },
})

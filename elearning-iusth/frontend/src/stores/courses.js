import { defineStore } from 'pinia'
import axios from 'axios'

export const useCoursesStore = defineStore('courses', {
  state: () => ({
    myCourses: [],
    allCourses: [],
    allCoursesTotal: 0,
    currentCourse: null,
  }),

  actions: {
    async fetchMyCourses() {
      const { data } = await axios.get('/courses/mine')
      this.myCourses = data
    },

    async fetchAllCourses({ q = '', page = 1, pageSize = 20 } = {}) {
      const { data } = await axios.get('/courses', { params: { q: q || undefined, page, page_size: pageSize } })
      this.allCourses = data.items
      this.allCoursesTotal = data.total
      return data
    },

    async fetchCourse(id) {
      const { data } = await axios.get(`/courses/${id}`)
      this.currentCourse = data
      return data
    },

    async createCourse(payload) {
      const { data } = await axios.post('/courses', payload)
      return data
    },

    async updateCourse(id, payload) {
      const { data } = await axios.patch(`/courses/${id}`, payload)
      return data
    },

    async createSection(courseId, payload) {
      const { data } = await axios.post(`/courses/${courseId}/sections`, payload)
      return data
    },

    async updateSection(sectionId, payload) {
      const { data } = await axios.patch(`/sections/${sectionId}`, payload)
      return data
    },

    async createResource(sectionId, formData) {
      const { data } = await axios.post(`/sections/${sectionId}/resources`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },

    async createAssignment(sectionId, payload) {
      const { data } = await axios.post(`/sections/${sectionId}/assignments`, payload)
      return data
    },

    async fetchCategories() {
      const { data } = await axios.get('/categories')
      return data
    },

    async createCategory(payload) {
      const { data } = await axios.post('/categories', payload)
      return data
    },
  },
})

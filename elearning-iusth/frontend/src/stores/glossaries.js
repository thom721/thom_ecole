import { defineStore } from 'pinia'
import axios from 'axios'

export const useGlossariesStore = defineStore('glossaries', {
  state: () => ({
    // Concepts approuvés du cours courant, chargés une fois et réutilisés
    // par AutoLinkedText.vue partout où du texte libre est affiché.
    conceptsByCourse: {},
  }),

  actions: {
    async createGlossary(sectionId, payload) {
      const { data } = await axios.post(`/sections/${sectionId}/glossaries`, payload)
      return data
    },

    async fetchGlossary(id) {
      const { data } = await axios.get(`/glossaries/${id}`)
      return data
    },

    async createEntry(glossaryId, payload) {
      const { data } = await axios.post(`/glossaries/${glossaryId}/entries`, payload)
      return data
    },

    async approveEntry(entryId) {
      const { data } = await axios.patch(`/glossary-entries/${entryId}/approve`)
      return data
    },

    async deleteEntry(entryId) {
      await axios.delete(`/glossary-entries/${entryId}`)
    },

    async fetchEntry(id) {
      const { data } = await axios.get(`/glossary-entries/${id}`)
      return data
    },

    async fetchCourseConcepts(courseId) {
      if (this.conceptsByCourse[courseId]) return this.conceptsByCourse[courseId]
      const { data } = await axios.get(`/courses/${courseId}/glossary/concepts`)
      this.conceptsByCourse[courseId] = data
      return data
    },
  },
})

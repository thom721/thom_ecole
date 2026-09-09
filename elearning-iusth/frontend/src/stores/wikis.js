import { defineStore } from 'pinia'
import axios from 'axios'

export const useWikisStore = defineStore('wikis', {
  actions: {
    async createWiki(sectionId, payload) {
      const { data } = await axios.post(`/sections/${sectionId}/wikis`, payload)
      return data
    },

    async fetchMySubwiki(wikiId) {
      const { data } = await axios.get(`/wikis/${wikiId}`)
      return data
    },

    async fetchIndividualSubwikis(wikiId) {
      const { data } = await axios.get(`/wikis/${wikiId}/subwikis`)
      return data
    },

    async fetchSubwiki(id) {
      const { data } = await axios.get(`/subwikis/${id}`)
      return data
    },

    async createPage(subwikiId, payload) {
      const { data } = await axios.post(`/subwikis/${subwikiId}/pages`, payload)
      return data
    },

    async fetchPage(id) {
      const { data } = await axios.get(`/wiki-pages/${id}`)
      return data
    },

    async fetchPageByTitle(subwikiId, title) {
      const { data } = await axios.get('/wiki-pages/by-title', { params: { subwiki_id: subwikiId, title } })
      return data
    },

    async saveVersion(pageId, content) {
      const { data } = await axios.post(`/wiki-pages/${pageId}/versions`, { content })
      return data
    },

    async fetchVersions(pageId) {
      const { data } = await axios.get(`/wiki-pages/${pageId}/versions`)
      return data
    },

    async fetchDiff(pageId, from, to) {
      const { data } = await axios.get(`/wiki-pages/${pageId}/diff`, { params: { from, to } })
      return data
    },
  },
})

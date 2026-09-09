import { defineStore } from 'pinia'
import axios from 'axios'

export const useForumsStore = defineStore('forums', {
  actions: {
    async createForum(sectionId, payload) {
      const { data } = await axios.post(`/sections/${sectionId}/forums`, payload)
      return data
    },

    async fetchForum(id) {
      const { data } = await axios.get(`/forums/${id}`)
      return data
    },

    async createDiscussion(forumId, payload) {
      const { data } = await axios.post(`/forums/${forumId}/discussions`, payload)
      return data
    },

    async fetchDiscussion(id) {
      const { data } = await axios.get(`/forum-discussions/${id}`)
      return data
    },

    async createPost(discussionId, payload) {
      const { data } = await axios.post(`/forum-discussions/${discussionId}/posts`, payload)
      return data
    },

    async updatePost(id, payload) {
      const { data } = await axios.patch(`/forum-posts/${id}`, payload)
      return data
    },

    async deletePost(id) {
      await axios.delete(`/forum-posts/${id}`)
    },

    async subscribe(discussionId) {
      await axios.post(`/forum-discussions/${discussionId}/subscribe`)
    },

    async unsubscribe(discussionId) {
      await axios.delete(`/forum-discussions/${discussionId}/subscribe`)
    },
  },
})

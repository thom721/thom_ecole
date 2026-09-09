import { defineStore } from 'pinia'
import axios from 'axios'

export const useInteractiveVideosStore = defineStore('interactiveVideos', {
  actions: {
    async createVideo(sectionId, formData) {
      const { data } = await axios.post(`/sections/${sectionId}/interactive-videos`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },

    async fetchVideo(id) {
      const { data } = await axios.get(`/interactive-videos/${id}`)
      return data
    },

    async updateVideo(id, payload) {
      const { data } = await axios.patch(`/interactive-videos/${id}`, payload)
      return data
    },

    async deleteVideo(id) {
      await axios.delete(`/interactive-videos/${id}`)
    },

    async createCheckpoint(videoId, payload) {
      const { data } = await axios.post(`/interactive-videos/${videoId}/checkpoints`, payload)
      return data
    },

    async deleteCheckpoint(id) {
      await axios.delete(`/interactive-video-checkpoints/${id}`)
    },

    async startAttempt(videoId) {
      const { data } = await axios.post(`/interactive-videos/${videoId}/attempts`)
      return data
    },

    async updatePosition(attemptId, positionSeconds) {
      await axios.patch(`/interactive-video-attempts/${attemptId}/position`, { position_seconds: positionSeconds })
    },

    async answerCheckpoint(attemptId, checkpointId, answerData) {
      const { data } = await axios.post(`/interactive-video-attempts/${attemptId}/checkpoints/${checkpointId}/answer`, { answer_data: answerData })
      return data
    },

    async finishAttempt(attemptId) {
      const { data } = await axios.post(`/interactive-video-attempts/${attemptId}/finish`)
      return data
    },

    async fetchEssayGrading(videoId) {
      const { data } = await axios.get(`/interactive-videos/${videoId}/essay-grading`)
      return data
    },

    async gradeEssayResponse(responseId, payload) {
      const { data } = await axios.patch(`/interactive-video-responses/${responseId}/grade`, payload)
      return data
    },
  },
})

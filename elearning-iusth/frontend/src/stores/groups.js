import { defineStore } from 'pinia'
import axios from 'axios'

export const useGroupsStore = defineStore('groups', {
  actions: {
    async fetchGroups(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/groups`)
      return data
    },

    async createGroup(courseId, payload) {
      const { data } = await axios.post(`/courses/${courseId}/groups`, payload)
      return data
    },

    async deleteGroup(id) {
      await axios.delete(`/groups/${id}`)
    },

    async addMember(groupId, userId) {
      const { data } = await axios.post(`/groups/${groupId}/members`, { user_id: userId })
      return data
    },

    async removeMember(groupId, userId) {
      const { data } = await axios.delete(`/groups/${groupId}/members/${userId}`)
      return data
    },

    async fetchGroupings(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/groupings`)
      return data
    },

    async createGrouping(courseId, payload) {
      const { data } = await axios.post(`/courses/${courseId}/groupings`, payload)
      return data
    },

    async deleteGrouping(id) {
      await axios.delete(`/groupings/${id}`)
    },

    async addGroupToGrouping(groupingId, groupId) {
      const { data } = await axios.post(`/groupings/${groupingId}/groups`, { group_id: groupId })
      return data
    },

    async removeGroupFromGrouping(groupingId, groupId) {
      const { data } = await axios.delete(`/groupings/${groupingId}/groups/${groupId}`)
      return data
    },
  },
})

import { defineStore } from 'pinia'
import axios from 'axios'

export const usePermissionsStore = defineStore('permissions', {
  actions: {
    async fetchPermissions() {
      const { data } = await axios.get('/permissions')
      return data
    },

    async fetchRoles() {
      const { data } = await axios.get('/roles')
      return data
    },

    async createRole(payload) {
      const { data } = await axios.post('/roles', payload)
      return data
    },

    async updateRole(id, payload) {
      const { data } = await axios.patch(`/roles/${id}`, payload)
      return data
    },

    async deleteRole(id) {
      await axios.delete(`/roles/${id}`)
    },

    async fetchUserRoles(userId) {
      const { data } = await axios.get(`/users/${userId}/roles`)
      return data
    },

    async assignRole(userId, roleId) {
      const { data } = await axios.post(`/users/${userId}/roles`, { role_id: roleId })
      return data
    },

    async revokeRole(userRoleId) {
      await axios.delete(`/user-roles/${userRoleId}`)
    },
  },
})

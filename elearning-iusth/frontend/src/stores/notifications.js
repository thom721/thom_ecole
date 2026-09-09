import { defineStore } from 'pinia'
import axios from 'axios'

export const useNotificationsStore = defineStore('notifications', {
  actions: {
    async fetchMine(unreadOnly = false) {
      const { data } = await axios.get('/notifications/mine', { params: { unread_only: unreadOnly } })
      return data
    },

    async fetchUnreadCount() {
      const { data } = await axios.get('/notifications/mine/unread-count')
      return data.count
    },

    async markRead(id) {
      const { data } = await axios.patch(`/notifications/${id}/read`)
      return data
    },

    async markAllRead() {
      await axios.post('/notifications/mine/read-all')
    },
  },
})

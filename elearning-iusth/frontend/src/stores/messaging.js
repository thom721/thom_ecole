import { defineStore } from 'pinia'
import axios from 'axios'

export const useMessagingStore = defineStore('messaging', {
  actions: {
    async fetchUnreadCount() {
      const { data } = await axios.get('/messaging/unread-count')
      return data.count
    },

    async fetchConversations() {
      const { data } = await axios.get('/messaging/conversations')
      return data
    },

    async startIndividual(otherUserId) {
      const { data } = await axios.post('/messaging/conversations/individual', { other_user_id: otherUserId })
      return data
    },

    async startGroup(name, memberIds) {
      const { data } = await axios.post('/messaging/conversations/group', { name, member_ids: memberIds })
      return data
    },

    async fetchConversation(id) {
      const { data } = await axios.get(`/messaging/conversations/${id}`)
      return data
    },

    async sendMessage(conversationId, content) {
      const { data } = await axios.post(`/messaging/conversations/${conversationId}/messages`, { content })
      return data
    },

    async deleteMessage(id) {
      await axios.delete(`/messaging/messages/${id}`)
    },

    async muteConversation(id) {
      await axios.post(`/messaging/conversations/${id}/mute`)
    },

    async unmuteConversation(id) {
      await axios.delete(`/messaging/conversations/${id}/mute`)
    },

    async lookup(email) {
      const { data } = await axios.get('/messaging/lookup', { params: { email } })
      return data
    },

    async fetchContacts() {
      const { data } = await axios.get('/messaging/contacts')
      return data
    },

    async sendContactRequest(userId) {
      const { data } = await axios.post('/messaging/contacts/requests', { user_id: userId })
      return data
    },

    async fetchContactRequests() {
      const { data } = await axios.get('/messaging/contacts/requests')
      return data
    },

    async acceptContactRequest(id) {
      const { data } = await axios.post(`/messaging/contacts/requests/${id}/accept`)
      return data
    },

    async declineContactRequest(id) {
      await axios.delete(`/messaging/contacts/requests/${id}`)
    },

    async removeContact(id) {
      await axios.delete(`/messaging/contacts/${id}`)
    },

    async fetchBlocked() {
      const { data } = await axios.get('/messaging/blocked')
      return data
    },

    async blockUser(userId) {
      await axios.post(`/messaging/blocked/${userId}`)
    },

    async unblockUser(userId) {
      await axios.delete(`/messaging/blocked/${userId}`)
    },

    async updatePrivacy(messagePrivacy) {
      const { data } = await axios.patch('/messaging/privacy', { message_privacy: messagePrivacy })
      return data
    },
  },
})

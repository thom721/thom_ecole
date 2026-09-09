import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('auth-token') || null,
    user: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.system_role === 'admin',
    isTeacher: (state) => state.user?.system_role === 'teacher',
    isStudent: (state) => state.user?.system_role === 'student',
  },

  actions: {
    async login(email, password) {
      const { data } = await axios.post('/auth/login', { email, password })
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('auth-token', this.token)
    },

    async fetchMe() {
      if (!this.token) return
      const { data } = await axios.get('/auth/me')
      this.user = data
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('auth-token')
    },

    async forgotPassword(email) {
      const { data } = await axios.post('/auth/forgot-password', { email })
      return data.message
    },

    async resetPassword(token, newPassword) {
      const { data } = await axios.post('/auth/reset-password', { token, new_password: newPassword })
      return data.message
    },
  },
})

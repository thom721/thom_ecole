import { defineStore } from 'pinia';
import axios from 'axios'
import api from '../services/api'; // On suppose que tu as créé src/services/api.js
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    school: null,
    token: localStorage.getItem('auth-token') || null,
    loading: false,
    error: null
  }),

  getters: {
    // roleNames: (state) => state.user?.roles?.map(role => role.name) || [],
    roleNames: (state) => {
      if (!state.user || !state.user.roles) return [];
      return state.user.roles.map(role => typeof role === 'object' ? role.name : role);
    },

    // Vérifications de rôle de base
    isBaseUser: (state) => {
      const names = state.user?.roles || [];
      return names.some(role =>
        (typeof role === 'object' ? role.name : role) === 'user'
      ) && names.length === 1; // Uniquement le rôle "user", pas d'autres rôles
    },

    isAdmin: (state) => {
      const names = state.user?.roles || [];
      return names.some(role =>
        (typeof role === 'object' ? role.name : role) === 'admin'
      );
    },

    isTeacher: (state) => {
      const names = state.user?.roles || [];
      return names.some(role =>
        (typeof role === 'object' ? role.name : role) === 'teacher'
      );
    },

    isStudent: (state) => {
      const names = state.user?.roles || [];
      return names.some(role =>
        (typeof role === 'object' ? role.name : role) === 'student'
      );
    },

    isCaissier: (state) => {
      const names = state.user?.roles || [];
      return names.some(role =>
        (typeof role === 'object' ? role.name : role) === 'Caissier'
      );
    },

    isResponsableFinancier: (state) => {
      const names = state.user?.roles || [];
      return names.some(role =>
        (typeof role === 'object' ? role.name : role) === 'Responsable financier'
      );
    },

    isResponsableAdmissions: (state) => {
      const names = state.user?.roles || [];
      return names.some(role =>
        (typeof role === 'object' ? role.name : role) === 'Responsable des admissions'
      );
    },

    isResponsablePedagogique: (state) => {
      const names = state.user?.roles || [];
      return names.some(role =>
        (typeof role === 'object' ? role.name : role) === 'Responsable pédagogique'
      );
    },

    isComptable: (state) => {
      const names = state.user?.roles || [];
      return names.some(role =>
        (typeof role === 'object' ? role.name : role) === 'Comptable'
      );
    },

    // Vérification si l'utilisateur a un rôle métier (pas juste "user")
    hasBusinessRole(state) {
      const roles = state.user?.roles || [];
      if (roles.length === 0) return false;
      if (roles.length === 1 && roles[0] === 'user') return false;
      return true;
    },

    // Vérifications d'accès aux modules
    canAccessDashboard(state) {
      const roles = this.roleNames;
      if (roles.includes('user') && roles.length === 1) return false;
      return roles.some(r => ['Responsable pédagogique', 'Comptable', 'admin'].includes(r));
    },

    canAccessEtudiants(state) {
      const roles = this.roleNames;
      if (roles.includes('user') && roles.length === 1) return false;
      return true; // Tous les autres rôles peuvent au moins consulter
    },

    canAccessPaiement(state) {
      const roles = this.roleNames;
      if (roles.includes('user') && roles.length === 1) return false;
      return roles.some(r => ['Caissier', 'Responsable financier', 'Comptable', 'admin'].includes(r));
    },

    canAccessTresorerie(state) {
      const roles = this.roleNames;
      if (roles.includes('user') && roles.length === 1) return false;
      return roles.some(r => ['Caissier', 'Responsable financier', 'Comptable', 'admin'].includes(r));
    },

    canAccessNotes(state) {
      const roles = this.roleNames;
      if (roles.includes('user') && roles.length === 1) return false;
      return roles.some(r => ['Responsable pédagogique', 'admin', 'teacher'].includes(r));
    },

    canAccessPresences(state) {
      const roles = this.roleNames;
      if (roles.includes('user') && roles.length === 1) return false;
      return roles.some(r => ['Responsable pédagogique', 'admin', 'teacher'].includes(r));
    },

    canAccessCours(state) {
      const roles = this.roleNames;
      if (roles.includes('user') && roles.length === 1) return false;
      return roles.some(r => ['Responsable pédagogique', 'admin', 'teacher'].includes(r));
    },

    canAccessProfesseurs(state) {
      const roles = this.roleNames;
      if (roles.includes('user') && roles.length === 1) return false;
      return roles.some(r => ['Comptable', 'admin'].includes(r));
    },

    canAccessRapports(state) {
      const roles = this.roleNames;
      if (roles.includes('user') && roles.length === 1) return false;
      return roles.length > 0;
    },

    canAccessParametres(state) {
      const roles = this.roleNames;
      if (roles.includes('user') && roles.length === 1) return false;
      return roles.some(r => ['Responsable pédagogique', 'Comptable', 'admin'].includes(r));
    },

    canEditParameters(state) {
      const roles = this.roleNames;
      return roles.some(r => ['Comptable', 'admin'].includes(r));
    },

    canAccessAdministration(state) {
      const roles = this.roleNames;
      return roles.includes('admin');
    },

    shouldMaskFinancials(state) {
      const roles = this.roleNames;
      return roles.includes('Responsable pédagogique');
    },

    isAuthenticated: (state) => !!state.user && !!state.token,

    userName: (state) => state.user?.name || '',

    userEmail: (state) => state.user?.email || '',

    userPhoto: (state) => state.user?.profile_photo_url || null
  },

  actions: {
    hasRole(rolesToCheck) { 
      const checks = Array.isArray(rolesToCheck) ? rolesToCheck : [rolesToCheck];
      const userRoles = this.roleNames;  
      
      return checks.some(role => userRoles.includes(role));
    },

    setUser(user) {
      this.user = user
    },

    setSchool(school) {
      this.school = school
    },

    setToken(token) {
      this.token = token
      if (token) {
        localStorage.setItem('auth-token', token)
        sessionStorage.setItem('auth-token', token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      } else {
        localStorage.removeItem('auth-token')
        sessionStorage.removeItem('auth-token')
        delete axios.defaults.headers.common['Authorization']
      }
    },

    setLoading(status) {
      this.loading = status
    },

    setError(error) {
      this.error = error
    },

    updateUser(userData) {
      if (this.user) {
        this.user = { ...this.user, ...userData }
      }
    },

    updateUserField(field, value) {
      if (this.user) {
        this.user[field] = value
      }
    },

    addRole(role) {
      if (this.user && !this.user.roles.some(r => r.name === role)) {
        this.user.roles.push({ name: role })
      }
    },

    removeRole(role) {
      if (this.user?.roles) {
        this.user.roles = this.user.roles.filter(r => r.name !== role)
      }
    },
 

    async login(credentials) {
      this.setLoading(true)
      this.setError(null)
      
      try {
        const response = await axios.post('/auth/login', credentials, {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        })
        this.setToken(response.data.token)
        this.user=response.data
        this.setUser(response.data)
        
        
        if (response.data.school) {
          this.setSchool(response.data.school)
        }
    
          return { success: true, user: response.data.user }

      } catch (error) { 
        this.setError(error.response?.data?.detail || 'Erreur de connexion')
        return error.response
      } finally {
        this.setLoading(false)
      }
    },

    async register(userData) {
      this.setLoading(true)
      this.setError(null)
      
      try {
        const response = await axios.post('/auth/register', userData, {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        })

        this.setToken(response.data.token)
        this.setUser(response.data.user)
        
        return { success: true, user: response.data.user }
        
      } catch (error) { 
        this.setError(error.response?.data?.message || "Erreur d'inscription")
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    async logout() {
      this.setLoading(true)
      
      try {
        await axios.post('/auth/logout', {}, {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })
        this.clearAuth()
      } catch (error) { 
      } finally {
        this.clearAuth()
        this.setLoading(false)
      }
    },

    clearAuth() {
      this.setUser(null)
      this.setSchool(null)
      this.setToken(null)
      this.setError(null)
      localStorage.removeItem('auth-token')
      sessionStorage.removeItem('auth-token')
      localStorage.removeItem('api_token')
    },


    async fetchUser() { 
      if (!this.token) { 
        return false
      }

      this.setLoading(true)
      
      try {
        const response = await axios.get('/verify-token', {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })
        
        this.setUser(response.data)
        return true
        
      } catch (error) {         
        if (error.response?.status === 422) {
          this.clearAuth()
        }
        
        this.setError(error.response?.data?.message || 'Erreur de chargement')
        return false
        
      } finally {
        this.setLoading(false)
      }
    },

    async fetchSchool() {
      if (!this.token) { 
        return false
      }

      try {
        const response = await axios.get('/get-profile', {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })
        
        this.setSchool(response.data)
        return true
        
      } catch (error) { 
        return false
      }
    },

    // =====================================
    // UPDATE PROFILE
    // =====================================

    async updateProfile(profileData) {
      this.setLoading(true)
      this.setError(null)
      
      try {
        const response = await axios.put('/api/user/profile', profileData, {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        })
        
        this.updateUser(response.data)
        return { success: true, user: response.data }
        
      } catch (error) { 
        this.setError(error.response?.data?.message || 'Erreur de mise à jour')
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    async updatePassword(passwords) {
      this.setLoading(true)
      this.setError(null)
      
      try {
        await axios.put('/api/user/password', passwords, {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        })
        
        return { success: true, message: 'Mot de passe mis à jour' }
        
      } catch (error) { 
        this.setError(error.response?.data?.message || 'Erreur de mise à jour')
        // throw error
      } finally {
        this.setLoading(false)
      }
    },

    async uploadProfilePhoto(file) {
      this.setLoading(true)
      this.setError(null)
      
      try {
        const formData = new FormData()
        formData.append('photo', file)
        
        const response = await axios.post('/api/user/profile-photo', formData, {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'multipart/form-data'
          }
        })
        
        this.updateUserField('profile_photo_url', response.data.profile_photo_url)
        return { success: true, url: response.data.profile_photo_url }
        
      } catch (error) { 
        this.setError(error.response?.data?.message || 'Erreur de téléchargement')
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    // =====================================
    // VERIFICATION
    // =====================================

    async checkAuth() {
      if (this.token && !this.user) {
        return await this.fetchUser()
      }
      return !!this.user
    },

    // =====================================
    // INITIALIZATION
    // =====================================

    initializeAuth1() {
      const token = localStorage.getItem('auth-token') || sessionStorage.getItem('auth-token')
      
      if (token) {
        this.setToken(token)
        this.fetchUser()
        this.fetchSchool()
      }
    },
 
  async initializeAuth() {
    const token = localStorage.getItem('auth-token');
    if (!token) return;

    try {
      // Remplace par ton endpoint réel (ex: /api/user ou /api/me)
      // const response = await axios.get('/api/user', {
      //   headers: { Authorization: `Bearer ${token}` }
      // });
      // this.user = response.data; // On remplit le store
      // return response;
      if (token) {
        this.setToken(token)
        await  this.fetchUser()
        this.fetchSchool()
      }
    } catch (error) {
      this.user = null;
      throw error;
    }
  }
// }
  }
})
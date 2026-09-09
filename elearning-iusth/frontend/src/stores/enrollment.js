import { defineStore } from 'pinia'
import axios from 'axios'

export const useEnrollmentStore = defineStore('enrollment', {
  actions: {
    async fetchEnrollments(courseId) {
      const { data } = await axios.get(`/courses/${courseId}/enrollments`)
      return data
    },

    async enrollUser(courseId, userId, roleInCourse = 'student') {
      const { data } = await axios.post(`/courses/${courseId}/enrollments`, {
        user_id: userId,
        role_in_course: roleInCourse,
      })
      return data
    },

    async unenroll(enrollmentId) {
      await axios.delete(`/enrollments/${enrollmentId}`)
    },
  },
})

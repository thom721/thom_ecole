import { defineStore } from 'pinia'
import axios from 'axios'

export const useCourseExportStore = defineStore('courseExport', {
  actions: {
    async exportCourse(courseId, suggestedFilename = 'cours.json', includeStudentData = false) {
      const response = await axios.get(`/courses/${courseId}/export`, {
        responseType: 'blob', params: { include_student_data: includeStudentData },
      })
      const disposition = response.headers['content-disposition']
      const match = disposition && disposition.match(/filename="?([^"]+)"?/)
      const filename = match ? match[1] : suggestedFilename

      const url = URL.createObjectURL(new Blob([response.data], { type: 'application/json' }))
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      URL.revokeObjectURL(url)
    },

    async importCourse(payload) {
      const { data } = await axios.post('/courses/import', payload)
      return data
    },
  },
})

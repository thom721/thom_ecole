<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-lg font-bold text-gray-900 mb-1">{{ t('admin.studentActivation.title') }}</h1>
    <p class="text-sm text-gray-500 mb-6">{{ t('admin.studentActivation.subtitle') }}</p>

    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-4">
      <label class="block text-xs text-gray-600 mb-1">{{ t('admin.integrationImport.yearLabel') }}</label>
      <select v-model="selectedAnnee" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3" @change="onAnneeChange">
        <option value="">{{ t('admin.integrationImport.yearPlaceholder') }}</option>
        <option v-for="a in annees" :key="a.id" :value="a.id">{{ a.label }}</option>
      </select>

      <template v-if="selectedAnnee">
        <label class="block text-xs text-gray-600 mb-1">{{ t('admin.studentActivation.classeLabel') }}</label>
        <select v-model="selectedClasse" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" @change="onClasseChange">
          <option value="">{{ t('admin.studentActivation.classePlaceholder') }}</option>
          <option v-for="c in classes" :key="c.id" :value="c.id">{{ c.nom_classe }} — {{ c.niveau_name }}</option>
        </select>
      </template>

      <p v-if="error" class="text-xs text-red-600 mt-2">{{ error }}</p>
    </div>

    <div v-if="students.length" class="space-y-3">
      <div v-for="s in students" :key="s.etudiant_id" class="bg-white border border-gray-200 rounded-xl p-4">
        <p class="text-sm font-medium text-gray-900 mb-2">{{ s.prenom }} {{ s.nom }} <span class="text-xs text-gray-400">({{ s.identifiant }})</span></p>
        <div class="flex gap-2">
          <input v-model="emails[s.etudiant_id]" type="email" :placeholder="t('admin.studentActivation.emailPlaceholder')"
            class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-50"
            :disabled="!emails[s.etudiant_id] || activating[s.etudiant_id]" @click="onActivate(s)">
            {{ activating[s.etudiant_id] ? t('admin.studentActivation.activating') : t('admin.studentActivation.activateButton') }}
          </button>
        </div>

        <div v-if="results[s.etudiant_id]" class="mt-3 space-y-2">
          <p class="text-xs" :class="results[s.etudiant_id].account_created ? 'text-green-700' : 'text-blue-700'">
            {{ results[s.etudiant_id].account_created ? t('admin.studentActivation.accountCreated') : t('admin.studentActivation.accountExisting') }}
            — {{ t('admin.studentActivation.enrolledCount', { count: results[s.etudiant_id].enrolled_courses.length }) }}
          </p>
          <ul v-if="results[s.etudiant_id].warnings.length" class="text-xs text-amber-700 list-disc list-inside">
            <li v-for="(w, i) in results[s.etudiant_id].warnings" :key="i">{{ w }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { useIntegrationStore } from '@/stores/integration'

const { t } = useI18n()
const integration = useIntegrationStore()

const annees = ref([])
const classes = ref([])
const students = ref([])
const selectedAnnee = ref('')
const selectedClasse = ref('')
const error = ref('')
const emails = reactive({})
const activating = reactive({})
const results = reactive({})

integration.fetchEcoleNginxAnnees().then((a) => { annees.value = a }).catch((e) => {
  error.value = e.response?.data?.detail || t('admin.integrationImport.unreachableError')
})

async function onAnneeChange() {
  selectedClasse.value = ''
  students.value = []
  classes.value = []
  error.value = ''
  if (!selectedAnnee.value) return
  try {
    classes.value = await integration.fetchEcoleNginxClasses(selectedAnnee.value)
  } catch (e) {
    error.value = e.response?.data?.detail || t('admin.integrationImport.unreachableError')
  }
}

async function onClasseChange() {
  students.value = []
  if (!selectedClasse.value) return
  try {
    students.value = await integration.fetchEcoleNginxClasseStudents(selectedClasse.value, selectedAnnee.value)
    // Pré-remplit avec l'email de connexion déjà connu côté ecole_nginx
    // (étudiant déjà activé là-bas, voir plan Épic 19) — l'admin peut
    // toujours le corriger avant de valider.
    for (const s of students.value) {
      emails[s.etudiant_id] = s.etudiant_login_email || s.email || ''
    }
  } catch (e) {
    error.value = e.response?.data?.detail || t('admin.integrationImport.unreachableError')
  }
}

async function onActivate(student) {
  activating[student.etudiant_id] = true
  try {
    results[student.etudiant_id] = await integration.activateStudent({
      etudiant_id: student.etudiant_id,
      classe_id: selectedClasse.value,
      annee_academique_id: selectedAnnee.value,
      email: emails[student.etudiant_id],
      first_name: student.prenom,
      last_name: student.nom,
    })
  } catch (e) {
    error.value = e.response?.data?.detail || t('admin.studentActivation.activateError')
  } finally {
    activating[student.etudiant_id] = false
  }
}
</script>

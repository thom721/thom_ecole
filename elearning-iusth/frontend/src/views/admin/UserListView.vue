<template>
  <div>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('admin.users.title') }}</h1>

    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('admin.users.createTitle') }}</h2>
      <div class="grid grid-cols-2 gap-3 mb-3">
        <input v-model="form.first_name" :placeholder="t('admin.users.firstNamePlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <input v-model="form.last_name" :placeholder="t('admin.users.lastNamePlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <input v-model="form.email" :placeholder="t('admin.users.emailPlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <input v-model="form.password" type="password" :placeholder="t('admin.users.passwordPlaceholder')" class="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <select v-model="form.system_role" class="border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="student">{{ t('admin.users.roleStudent') }}</option>
          <option value="teacher">{{ t('admin.users.roleTeacher') }}</option>
          <option value="admin">{{ t('admin.users.roleAdmin') }}</option>
        </select>
      </div>
      <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onCreate">{{ t('common.create') }}</button>
      <p v-if="message" class="text-xs text-red-600 mt-2">{{ message }}</p>
    </div>

    <table class="w-full text-sm bg-white border border-gray-200 rounded-xl overflow-hidden">
      <thead class="bg-gray-50 text-left text-xs text-gray-500">
        <tr>
          <th class="px-3 py-2">{{ t('admin.users.colName') }}</th>
          <th class="px-3 py-2">{{ t('admin.users.colEmail') }}</th>
          <th class="px-3 py-2">{{ t('admin.users.colRole') }}</th>
          <th class="px-3 py-2">{{ t('admin.users.colStatus') }}</th>
          <th class="px-3 py-2"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id" class="border-t border-gray-100">
          <td class="px-3 py-2">{{ u.first_name }} {{ u.last_name }}</td>
          <td class="px-3 py-2">{{ u.email }}</td>
          <td class="px-3 py-2">{{ u.system_role }}</td>
          <td class="px-3 py-2">{{ u.is_active ? t('admin.users.statusActive') : t('admin.users.statusDisabled') }}</td>
          <td class="px-3 py-2">
            <button v-if="u.is_active" class="text-red-600 text-xs" @click="onDeactivate(u.id)">{{ t('admin.users.deactivate') }}</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()
const users = ref([])
const message = ref('')
const form = reactive({ first_name: '', last_name: '', email: '', password: '', system_role: 'student' })

async function load() {
  const { data } = await axios.get('/users')
  users.value = data
}

async function onCreate() {
  message.value = ''
  try {
    await axios.post('/users', { ...form })
    Object.assign(form, { first_name: '', last_name: '', email: '', password: '', system_role: 'student' })
    await load()
  } catch (e) {
    message.value = e.response?.data?.detail || t('common.error')
  }
}

async function onDeactivate(id) {
  await axios.patch(`/users/${id}/deactivate`)
  await load()
}

onMounted(load)
</script>

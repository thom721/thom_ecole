<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-lg font-bold text-gray-900 mb-1">{{ t('admin.roles.title') }}</h1>
    <p class="text-sm text-gray-500 mb-6">{{ t('admin.roles.subtitle') }}</p>

    <div class="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('admin.roles.rolesListTitle') }}</h2>
      <div v-for="r in roles" :key="r.id" class="border-t border-gray-100 first:border-t-0 py-2">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium">{{ r.name }}</p>
            <p class="text-xs text-gray-500">{{ r.permission_names.join(', ') || t('admin.roles.noPermissions') }}</p>
          </div>
          <button class="text-red-600 text-xs" @click="onDeleteRole(r.id)">{{ t('common.remove') }}</button>
        </div>
      </div>
    </div>

    <details class="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('admin.roles.addRole') }}</summary>
      <div class="mt-3 space-y-2">
        <input v-model="newRoleName" :placeholder="t('common.title')" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <div v-for="p in permissions" :key="p.name" class="flex items-center gap-2 text-sm">
          <input type="checkbox" :value="p.name" v-model="newRolePermissions" />
          <span>{{ p.name }}</span>
        </div>
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onCreateRole">{{ t('common.create') }}</button>
      </div>
    </details>

    <div class="bg-white border border-gray-200 rounded-xl p-4">
      <h2 class="font-semibold text-gray-900 mb-3">{{ t('admin.roles.assignTitle') }}</h2>
      <div class="flex gap-2 mb-3">
        <input v-model="assignEmail" :placeholder="t('admin.roles.emailPlaceholder')" class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        <select v-model="assignRoleId" class="border border-gray-300 rounded-lg px-3 py-2 text-sm">
          <option value="">{{ t('admin.roles.chooseRole') }}</option>
          <option v-for="r in roles" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
        <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onAssign">{{ t('admin.roles.assignButton') }}</button>
      </div>
      <p v-if="assignError" class="text-xs text-red-600">{{ assignError }}</p>
      <p v-if="assignSuccess" class="text-xs text-green-700">{{ assignSuccess }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { usePermissionsStore } from '@/stores/permissions'

const { t } = useI18n()
const permissionsStore = usePermissionsStore()

const roles = ref([])
const permissions = ref([])
const newRoleName = ref('')
const newRolePermissions = ref([])
const assignEmail = ref('')
const assignRoleId = ref('')
const assignError = ref('')
const assignSuccess = ref('')

async function load() {
  roles.value = await permissionsStore.fetchRoles()
  permissions.value = await permissionsStore.fetchPermissions()
}

async function onCreateRole() {
  if (!newRoleName.value) return
  await permissionsStore.createRole({ name: newRoleName.value, permission_names: newRolePermissions.value })
  newRoleName.value = ''
  newRolePermissions.value = []
  await load()
}

async function onDeleteRole(id) {
  await permissionsStore.deleteRole(id)
  await load()
}

async function onAssign() {
  assignError.value = ''
  assignSuccess.value = ''
  if (!assignEmail.value || !assignRoleId.value) return
  try {
    const { data: users } = await axios.get('/users')
    const user = users.find((u) => u.email === assignEmail.value)
    if (!user) {
      assignError.value = t('admin.roles.userNotFound')
      return
    }
    await permissionsStore.assignRole(user.id, assignRoleId.value)
    assignSuccess.value = t('admin.roles.assignedSuccess')
    assignEmail.value = ''
    assignRoleId.value = ''
  } catch (e) {
    assignError.value = e.response?.data?.detail || t('admin.roles.assignError')
  }
}

onMounted(load)
</script>

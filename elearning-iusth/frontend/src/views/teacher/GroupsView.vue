<template>
  <div>
    <button class="text-sm text-gray-500 hover:underline mb-4" @click="$router.back()">{{ t('common.back') }}</button>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('groups.title') }}</h1>

    <div class="grid grid-cols-2 gap-6">
      <!-- Groupes -->
      <div>
        <h2 class="font-semibold text-gray-900 mb-3">{{ t('groups.groups') }}</h2>
        <div class="flex gap-2 mb-4">
          <input v-model="newGroupName" :placeholder="t('groups.namePlaceholder')" class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm flex-1" />
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onCreateGroup">{{ t('common.create') }}</button>
        </div>

        <div v-for="g in groups" :key="g.id" class="bg-white border border-gray-200 rounded-xl p-3 mb-3">
          <div class="flex items-center justify-between mb-2">
            <p class="font-medium text-gray-900">{{ g.name }}</p>
            <button class="text-red-600 text-xs" @click="onDeleteGroup(g.id)">{{ t('common.remove') }}</button>
          </div>
          <ul class="text-sm mb-2">
            <li v-for="m in g.members" :key="m.user_id" class="flex items-center justify-between py-0.5">
              <span>{{ m.name }}</span>
              <button class="text-red-600 text-xs" @click="onRemoveMember(g, m.user_id)">{{ t('common.remove') }}</button>
            </li>
          </ul>
          <div class="flex gap-2">
            <input v-model="newMemberEmail[g.id]" :placeholder="t('groups.memberEmailPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-xs flex-1" />
            <button class="bg-gray-100 rounded-lg px-2 py-1 text-xs" @click="onAddMember(g)">{{ t('common.add') }}</button>
          </div>
          <p v-if="memberError[g.id]" class="text-xs text-red-600 mt-1">{{ memberError[g.id] }}</p>
        </div>
      </div>

      <!-- Groupements -->
      <div>
        <h2 class="font-semibold text-gray-900 mb-3">{{ t('groups.groupings') }}</h2>
        <div class="flex gap-2 mb-4">
          <input v-model="newGroupingName" :placeholder="t('groups.namePlaceholder')" class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm flex-1" />
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onCreateGrouping">{{ t('common.create') }}</button>
        </div>

        <div v-for="gr in groupings" :key="gr.id" class="bg-white border border-gray-200 rounded-xl p-3 mb-3">
          <div class="flex items-center justify-between mb-2">
            <p class="font-medium text-gray-900">{{ gr.name }}</p>
            <button class="text-red-600 text-xs" @click="onDeleteGrouping(gr.id)">{{ t('common.remove') }}</button>
          </div>
          <label v-for="g in groups" :key="g.id" class="flex items-center gap-2 text-xs text-gray-600 py-0.5">
            <input type="checkbox" :checked="isInGrouping(gr, g.id)" @change="onToggleGroupInGrouping(gr, g.id, $event.target.checked)" />
            {{ g.name }}
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useGroupsStore } from '@/stores/groups'
import axios from 'axios'

const { t } = useI18n()
const route = useRoute()
const groupsStore = useGroupsStore()

const groups = ref([])
const groupings = ref([])
const newGroupName = ref('')
const newGroupingName = ref('')
const newMemberEmail = reactive({})
const memberError = reactive({})

async function loadAll() {
  groups.value = await groupsStore.fetchGroups(route.params.id)
  groupings.value = await groupsStore.fetchGroupings(route.params.id)
}

async function onCreateGroup() {
  if (!newGroupName.value) return
  await groupsStore.createGroup(route.params.id, { name: newGroupName.value })
  newGroupName.value = ''
  await loadAll()
}

async function onDeleteGroup(id) {
  await groupsStore.deleteGroup(id)
  await loadAll()
}

async function onAddMember(group) {
  memberError[group.id] = ''
  try {
    const { data: user } = await axios.get('/users/lookup', { params: { email: newMemberEmail[group.id] } })
    await groupsStore.addMember(group.id, user.id)
    newMemberEmail[group.id] = ''
    await loadAll()
  } catch (e) {
    memberError[group.id] = e.response?.data?.detail || t('common.error')
  }
}

async function onRemoveMember(group, userId) {
  await groupsStore.removeMember(group.id, userId)
  await loadAll()
}

async function onCreateGrouping() {
  if (!newGroupingName.value) return
  await groupsStore.createGrouping(route.params.id, { name: newGroupingName.value })
  newGroupingName.value = ''
  await loadAll()
}

async function onDeleteGrouping(id) {
  await groupsStore.deleteGrouping(id)
  await loadAll()
}

function isInGrouping(grouping, groupId) {
  return grouping.groups.some((g) => g.id === groupId)
}

async function onToggleGroupInGrouping(grouping, groupId, checked) {
  if (checked) await groupsStore.addGroupToGrouping(grouping.id, groupId)
  else await groupsStore.removeGroupFromGrouping(grouping.id, groupId)
  await loadAll()
}

onMounted(loadAll)
</script>

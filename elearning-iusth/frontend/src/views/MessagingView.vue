<template>
  <div>
    <div class="flex gap-4 mb-6 text-sm border-b border-gray-200">
      <button v-for="tab in tabs" :key="tab" class="pb-2 px-1"
        :class="activeTab === tab ? 'border-b-2 border-gray-900 font-semibold text-gray-900' : 'text-gray-500'"
        @click="activeTab = tab">
        {{ t(`messaging.tab.${tab}`) }}
      </button>
    </div>

    <!-- Conversations -->
    <div v-if="activeTab === 'conversations'" class="grid grid-cols-3 gap-4">
      <div class="col-span-1">
        <div class="bg-white border border-gray-200 rounded-xl p-3 mb-3">
          <input v-model="newConvEmail" :placeholder="t('messaging.emailPlaceholder')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm mb-2" />
          <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onStartConversation">{{ t('messaging.startConversation') }}</button>
          <p v-if="startError" class="text-xs text-red-600 mt-2">{{ startError }}</p>
        </div>
        <button v-for="c in conversations" :key="c.id" class="w-full text-left bg-white border border-gray-200 rounded-xl p-3 mb-2 hover:bg-gray-50"
          :class="{ 'ring-1 ring-gray-900': currentConversation && currentConversation.id === c.id }"
          @click="openConversation(c.id)">
          <p class="font-medium text-gray-900 text-sm">
            {{ c.name || t('messaging.withUser', { id: c.other_user_id }) }}
            <span v-if="c.muted" class="text-gray-400 text-xs">🔇</span>
          </p>
          <p class="text-xs text-gray-500 truncate">{{ c.last_message || t('messaging.noMessagesYet') }}</p>
          <span v-if="c.unread_count > 0" class="text-xs bg-red-600 text-white rounded-full px-1.5">{{ c.unread_count }}</span>
        </button>
      </div>

      <div class="col-span-2">
        <div v-if="currentConversation" class="bg-white border border-gray-200 rounded-xl p-4">
          <div class="flex items-center justify-between mb-3">
            <p class="font-semibold text-gray-900">{{ currentConversation.name || t('messaging.conversationTitle') }}</p>
            <button class="text-xs text-gray-500 hover:underline" @click="onToggleMute">
              {{ currentConversation.muted ? t('messaging.unmute') : t('messaging.mute') }}
            </button>
          </div>
          <div class="space-y-2 max-h-96 overflow-y-auto mb-3">
            <div v-for="m in currentConversation.messages" :key="m.id" class="flex items-start justify-between bg-gray-50 rounded-lg p-2 text-sm">
              <span>{{ m.content }}</span>
              <button class="text-red-600 text-xs ml-2" @click="onDeleteMessage(m.id)">{{ t('common.remove') }}</button>
            </div>
          </div>
          <div class="flex gap-2">
            <input v-model="newMessage" :placeholder="t('messaging.messagePlaceholder')" class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm" @keyup.enter="onSendMessage" />
            <button class="bg-gray-900 text-white rounded-lg px-4 py-2 text-sm font-semibold" @click="onSendMessage">{{ t('messaging.send') }}</button>
          </div>
        </div>
        <p v-else class="text-sm text-gray-500">{{ t('messaging.selectConversation') }}</p>
      </div>
    </div>

    <!-- Contacts -->
    <div v-else-if="activeTab === 'contacts'" class="grid grid-cols-2 gap-6">
      <div>
        <h2 class="font-semibold text-gray-900 mb-2">{{ t('messaging.contactsTitle') }}</h2>
        <div class="flex gap-2 mb-3">
          <input v-model="newContactEmail" :placeholder="t('messaging.emailPlaceholder')" class="border border-gray-300 rounded-lg px-2 py-1 text-sm flex-1" />
          <button class="bg-gray-100 rounded-lg px-3 py-1 text-sm" @click="onSendContactRequest">{{ t('common.add') }}</button>
        </div>
        <p v-if="contactError" class="text-xs text-red-600 mb-2">{{ contactError }}</p>
        <ul class="text-sm">
          <li v-for="c in contacts" :key="c.id" class="flex items-center justify-between py-1 border-t border-gray-100 first:border-t-0">
            <span>{{ c.other_user_id }}</span>
            <button class="text-red-600 text-xs" @click="onRemoveContact(c.id)">{{ t('common.remove') }}</button>
          </li>
        </ul>
      </div>
      <div>
        <h2 class="font-semibold text-gray-900 mb-2">{{ t('messaging.requestsTitle') }}</h2>
        <ul class="text-sm">
          <li v-for="r in contactRequests" :key="r.id" class="flex items-center justify-between py-1 border-t border-gray-100 first:border-t-0">
            <span>{{ r.direction === 'incoming' ? r.user_id : r.requested_user_id }} <span class="text-gray-400 text-xs">({{ t(`messaging.direction.${r.direction}`) }})</span></span>
            <span class="flex gap-2">
              <button v-if="r.direction === 'incoming'" class="text-green-700 text-xs" @click="onAcceptRequest(r.id)">{{ t('messaging.accept') }}</button>
              <button class="text-red-600 text-xs" @click="onDeclineRequest(r.id)">{{ t('common.remove') }}</button>
            </span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Bloqués -->
    <div v-else-if="activeTab === 'blocked'">
      <h2 class="font-semibold text-gray-900 mb-2">{{ t('messaging.blockedTitle') }}</h2>
      <ul class="text-sm">
        <li v-for="u in blocked" :key="u.id" class="flex items-center justify-between py-1 border-t border-gray-100 first:border-t-0">
          <span>{{ u.first_name }} {{ u.last_name }} ({{ u.email }})</span>
          <button class="text-blue-600 text-xs" @click="onUnblock(u.id)">{{ t('messaging.unblock') }}</button>
        </li>
      </ul>
    </div>

    <!-- Confidentialité -->
    <div v-else-if="activeTab === 'privacy'" class="max-w-sm">
      <h2 class="font-semibold text-gray-900 mb-2">{{ t('messaging.privacyTitle') }}</h2>
      <select v-model="privacy" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm mb-2">
        <option value="course_member">{{ t('messaging.privacy.course_member') }}</option>
        <option value="only_contacts">{{ t('messaging.privacy.only_contacts') }}</option>
        <option value="site">{{ t('messaging.privacy.site') }}</option>
      </select>
      <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onSavePrivacy">{{ t('common.save') }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMessagingStore } from '@/stores/messaging'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const messaging = useMessagingStore()
const auth = useAuthStore()

const tabs = ['conversations', 'contacts', 'blocked', 'privacy']
const activeTab = ref('conversations')

const conversations = ref([])
const currentConversation = ref(null)
const newConvEmail = ref('')
const newMessage = ref('')
const startError = ref('')

const contacts = ref([])
const contactRequests = ref([])
const newContactEmail = ref('')
const contactError = ref('')

const blocked = ref([])
const privacy = ref(auth.user?.message_privacy || 'course_member')

async function loadConversations() {
  conversations.value = await messaging.fetchConversations()
}

async function openConversation(id) {
  currentConversation.value = await messaging.fetchConversation(id)
  await loadConversations()
}

async function onStartConversation() {
  startError.value = ''
  if (!newConvEmail.value) return
  try {
    const user = await messaging.lookup(newConvEmail.value)
    const conv = await messaging.startIndividual(user.id)
    newConvEmail.value = ''
    await loadConversations()
    await openConversation(conv.id)
  } catch (e) {
    startError.value = e.response?.data?.detail || t('common.error')
  }
}

async function onSendMessage() {
  if (!newMessage.value || !currentConversation.value) return
  await messaging.sendMessage(currentConversation.value.id, newMessage.value)
  newMessage.value = ''
  await openConversation(currentConversation.value.id)
}

async function onDeleteMessage(id) {
  await messaging.deleteMessage(id)
  await openConversation(currentConversation.value.id)
}

async function onToggleMute() {
  if (currentConversation.value.muted) await messaging.unmuteConversation(currentConversation.value.id)
  else await messaging.muteConversation(currentConversation.value.id)
  await openConversation(currentConversation.value.id)
}

async function loadContacts() {
  contacts.value = await messaging.fetchContacts()
  contactRequests.value = await messaging.fetchContactRequests()
}

async function onSendContactRequest() {
  contactError.value = ''
  if (!newContactEmail.value) return
  try {
    const user = await messaging.lookup(newContactEmail.value)
    await messaging.sendContactRequest(user.id)
    newContactEmail.value = ''
    await loadContacts()
  } catch (e) {
    contactError.value = e.response?.data?.detail || t('common.error')
  }
}

async function onAcceptRequest(id) {
  await messaging.acceptContactRequest(id)
  await loadContacts()
}

async function onDeclineRequest(id) {
  await messaging.declineContactRequest(id)
  await loadContacts()
}

async function onRemoveContact(id) {
  await messaging.removeContact(id)
  await loadContacts()
}

async function loadBlocked() {
  blocked.value = await messaging.fetchBlocked()
}

async function onUnblock(userId) {
  await messaging.unblockUser(userId)
  await loadBlocked()
}

async function onSavePrivacy() {
  await messaging.updatePrivacy(privacy.value)
}

onMounted(async () => {
  await loadConversations()
  await loadContacts()
  await loadBlocked()
})
</script>

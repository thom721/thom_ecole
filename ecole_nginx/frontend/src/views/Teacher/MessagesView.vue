<!-- src/views/MessagesView.vue -->
<template>
  <div class="flex flex-col gap-6 animate-[fadeUp_0.4s_ease_both]">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-3xl font-bold text-[#e8eaf0] mb-1" style="font-family:'Playfair Display',serif">Messages</h1>
        <p class="text-[#7c83a0] text-sm flex items-center gap-2">
          <span>{{ unreadTotal }} message{{ unreadTotal > 1 ? 's' : '' }} non lu{{ unreadTotal > 1 ? 's' : '' }}</span>
          <span class="inline-flex items-center gap-1 text-[11px]" :title="connected ? 'Temps réel actif' : 'Reconnexion…'">
            <span class="w-1.5 h-1.5 rounded-full" :class="connected ? 'bg-[#6ee7b7]' : 'bg-[#f59e0b]'" />
            {{ connected ? 'en direct' : 'reconnexion…' }}
          </span>
        </p>
      </div>
      <button @click="openPicker" class="px-4 py-2 text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0" :style="{ background: 'var(--accent,#4f8ef7)' }">+ Nouveau message</button>
    </div>

    <p v-if="error" class="text-sm text-[#f87171] bg-[#f87171]/10 rounded-xl px-4 py-3">{{ error }}</p>

    <div class="grid md:grid-cols-[300px_1fr] bg-[#171b26] border border-white/[0.07] rounded-2xl overflow-hidden h-[calc(100vh-260px)] min-h-[480px]">

      <!-- Colonne gauche : conversations ou choix d'un destinataire -->
      <div class="border-b md:border-b-0 md:border-r border-white/[0.07] flex flex-col min-h-0">
        <template v-if="picking">
          <div class="p-3 border-b border-white/[0.07] flex gap-2">
            <input
              ref="pickerInput" v-model="contactSearch" type="search" placeholder="Rechercher un destinataire…"
              class="flex-1 bg-[#1e2335] border border-white/10 rounded-xl px-3 py-2 text-[#e8eaf0] text-sm outline-none focus:border-white/20"
            />
            <button @click="picking = false" class="px-3 text-[#7c83a0] hover:text-[#e8eaf0] bg-transparent border-0 cursor-pointer text-sm">Annuler</button>
          </div>
          <div class="overflow-y-auto flex-1">
            <p v-if="!contacts.length" class="p-4 text-[12.5px] text-[#7c83a0]">{{ contactsLoading ? 'Chargement…' : 'Aucun destinataire trouvé.' }}</p>
            <div v-for="c in contacts" :key="c.id" @click="startWith(c)"
              class="flex items-center gap-3 px-4 py-3 border-b border-white/[0.05] cursor-pointer hover:bg-white/[0.03]">
              <div class="w-9 h-9 rounded-full flex items-center justify-center text-[12px] font-bold text-[#0f1117] flex-shrink-0" :style="{ background: gradientFor(c.id) }">{{ initials(c.name) }}</div>
              <div class="min-w-0">
                <p class="text-[13px] text-[#e8eaf0] truncate">{{ c.name }}</p>
                <p class="text-[11px] text-[#7c83a0] truncate">{{ c.role }} · {{ c.email }}</p>
              </div>
            </div>
          </div>
        </template>

        <div v-else class="overflow-y-auto flex-1">
          <p v-if="!conversations.length" class="p-4 text-[12.5px] text-[#7c83a0]">
            {{ loading ? 'Chargement…' : 'Aucune conversation. Cliquez sur « + Nouveau message » pour en commencer une.' }}
          </p>
          <div
            v-for="c in conversations" :key="c.user.id"
            @click="openThread(c.user)"
            class="flex items-start gap-3 p-4 border-b border-white/[0.05] cursor-pointer transition-colors last:border-0"
            :class="activeUser?.id===c.user.id ? '' : 'hover:bg-white/[0.03]'"
            :style="activeUser?.id===c.user.id ? { background: 'color-mix(in srgb, var(--accent,#4f8ef7) 8%, transparent)' } : {}"
          >
            <div class="w-9 h-9 rounded-full flex items-center justify-center text-[12px] font-bold text-[#0f1117] flex-shrink-0" :style="{ background: gradientFor(c.user.id) }">{{ initials(c.user.name) }}</div>
            <div class="flex-1 min-w-0">
              <p class="text-[13px] truncate" :class="c.unread ? 'font-bold text-[#e8eaf0]' : 'text-[#b0b5cc]'">{{ c.user.name }}</p>
              <p class="text-[11.5px] text-[#7c83a0] truncate mt-0.5">
                <span v-if="c.last_message.sender_id === myId">Vous : </span>{{ c.last_message.body }}
              </p>
            </div>
            <div class="flex flex-col items-end gap-1.5 flex-shrink-0">
              <span class="text-[11px] text-[#7c83a0]">{{ shortTime(c.last_message.created_at) }}</span>
              <span v-if="c.unread" class="min-w-[18px] h-[18px] px-1 rounded-full text-[10px] font-bold text-white flex items-center justify-center" :style="{ background: 'var(--accent,#4f8ef7)' }">{{ c.unread }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Colonne droite : fil de la conversation -->
      <div class="flex flex-col min-h-0">
        <div v-if="!activeUser" class="flex-1 flex items-center justify-center text-[#7c83a0] text-sm p-6 text-center">
          Sélectionnez une conversation ou commencez-en une nouvelle.
        </div>

        <template v-else>
          <div class="flex items-center gap-3 px-6 py-4 border-b border-white/[0.07]">
            <div class="w-10 h-10 rounded-full flex items-center justify-center text-[13px] font-bold text-[#0f1117]" :style="{ background: gradientFor(activeUser.id) }">{{ initials(activeUser.name) }}</div>
            <div class="min-w-0">
              <p class="text-[15px] font-semibold text-[#e8eaf0] truncate">{{ activeUser.name }}</p>
              <p class="text-[12px] text-[#7c83a0] truncate">{{ activeUser.role }}<template v-if="activeUser.email"> · {{ activeUser.email }}</template></p>
            </div>
          </div>

          <div ref="threadEl" class="flex-1 overflow-y-auto px-6 py-4 flex flex-col gap-2">
            <button v-if="hasMore" @click="loadOlder" class="self-center text-[12px] text-[#7c83a0] hover:text-[#e8eaf0] bg-transparent border-0 cursor-pointer mb-2">Charger les messages précédents</button>
            <p v-if="!threadLoading && !thread.length" class="text-center text-[12.5px] text-[#7c83a0] my-auto">Aucun message. Écrivez le premier ci-dessous.</p>
            <template v-for="(m, i) in thread" :key="m.id">
              <p v-if="showDay(i)" class="self-center text-[11px] text-[#7c83a0] my-2">{{ dayLabel(m.created_at) }}</p>
              <div class="max-w-[75%] flex flex-col" :class="m.sender_id === myId ? 'self-end items-end' : 'self-start items-start'">
                <div
                  class="px-4 py-2.5 rounded-2xl text-[13.5px] leading-relaxed whitespace-pre-wrap break-words"
                  :class="m.sender_id === myId ? 'text-white rounded-br-md' : 'bg-[#1e2335] text-[#e8eaf0] rounded-bl-md'"
                  :style="m.sender_id === myId ? { background: 'var(--accent,#4f8ef7)' } : {}"
                >{{ m.body }}</div>
                <span class="text-[10.5px] text-[#7c83a0] mt-1 px-1">
                  {{ timeOnly(m.created_at) }}<template v-if="m.sender_id === myId && m.read_at"> · lu</template>
                </span>
              </div>
            </template>
          </div>

          <div class="flex flex-col gap-2 p-4 border-t border-white/[0.07]">
            <textarea
              v-model="draft"
              @keydown.enter.exact.prevent="send"
              class="w-full bg-[#1e2335] border border-white/10 rounded-xl px-4 py-3 text-[#e8eaf0] text-sm resize-none outline-none focus:border-white/20 transition-colors"
              placeholder="Écrire un message… (Entrée pour envoyer, Maj+Entrée pour aller à la ligne)" rows="2" maxlength="5000"
            />
            <div class="flex items-center justify-between gap-3">
              <span class="text-[11px] text-[#f87171]">{{ sendError }}</span>
              <button @click="send" :disabled="sending || !draft.trim()"
                class="px-5 py-2 text-white rounded-xl text-sm font-medium hover:brightness-110 transition-all cursor-pointer border-0 disabled:opacity-50 disabled:cursor-not-allowed"
                :style="{ background: 'var(--accent,#4f8ef7)' }">{{ sending ? 'Envoi…' : 'Envoyer' }}</button>
            </div>
          </div>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMessages, startMessaging, onRealtime, messagesApi } from '@/composables/useMessages'
import { initials } from '@/composables/useTeacherData'

const authStore = useAuthStore()
const myId = computed(() => authStore.user?.user?.id)
const { unreadTotal, connected } = useMessages()

const conversations = ref([])
const loading = ref(true)
const error = ref('')

const activeUser = ref(null)
const thread = ref([])
const threadLoading = ref(false)
const hasMore = ref(false)
const threadEl = ref(null)

const draft = ref('')
const sending = ref(false)
const sendError = ref('')

const picking = ref(false)
const contacts = ref([])
const contactSearch = ref('')
const contactsLoading = ref(false)
const pickerInput = ref(null)

const GRADIENTS = [
  'linear-gradient(135deg,#6ee7b7,#4f8ef7)', 'linear-gradient(135deg,#f59e0b,#f87171)',
  'linear-gradient(135deg,#a78bfa,#4f8ef7)', 'linear-gradient(135deg,#22d3ee,#6ee7b7)',
  'linear-gradient(135deg,#f87171,#f59e0b)',
]
function gradientFor(id = '') {
  let h = 0
  for (const ch of id) h = (h * 31 + ch.charCodeAt(0)) >>> 0
  return GRADIENTS[h % GRADIENTS.length]
}

// Les dates du serveur sont en UTC sans suffixe
const toDate = (iso) => new Date(iso && !/[zZ]|[+-]\d\d:?\d\d$/.test(iso) ? iso + 'Z' : iso)
const timeOnly = (iso) => toDate(iso).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
function shortTime(iso) {
  const d = toDate(iso)
  const now = new Date()
  if (d.toDateString() === now.toDateString()) return timeOnly(iso)
  const hier = new Date(now); hier.setDate(now.getDate() - 1)
  if (d.toDateString() === hier.toDateString()) return 'Hier'
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
}
const dayLabel = (iso) => toDate(iso).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })
const showDay = (i) => i === 0 || toDate(thread.value[i].created_at).toDateString() !== toDate(thread.value[i - 1].created_at).toDateString()

async function loadConversations() {
  try {
    const data = await messagesApi.conversations()
    conversations.value = data.conversations
    error.value = ''
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Impossible de charger vos conversations.'
  } finally {
    loading.value = false
  }
}

async function scrollBottom() {
  await nextTick()
  if (threadEl.value) threadEl.value.scrollTop = threadEl.value.scrollHeight
}

async function openThread(user) {
  picking.value = false
  activeUser.value = user
  thread.value = []
  sendError.value = ''
  threadLoading.value = true
  try {
    const data = await messagesApi.thread(user.id)
    if (activeUser.value?.id !== user.id) return
    activeUser.value = data.user
    thread.value = data.messages
    hasMore.value = data.has_more
    await scrollBottom()
    markConversationRead(user.id)
  } finally {
    threadLoading.value = false
  }
}

async function loadOlder() {
  if (!thread.value.length) return
  const el = threadEl.value
  const before = el?.scrollHeight ?? 0
  const data = await messagesApi.thread(activeUser.value.id, thread.value[0].id)
  thread.value = [...data.messages, ...thread.value]
  hasMore.value = data.has_more
  await nextTick()
  if (el) el.scrollTop = el.scrollHeight - before
}

function markConversationRead(userId) {
  const conv = conversations.value.find(c => c.user.id === userId)
  if (conv?.unread) {
    conv.unread = 0
    messagesApi.markRead(userId)
  }
}

// Insère/maj un message dans la liste des conversations (en tête)
function upsertConversation(msg, user) {
  const otherId = msg.sender_id === myId.value ? msg.recipient_id : msg.sender_id
  const idx = conversations.value.findIndex(c => c.user.id === otherId)
  const incoming = msg.sender_id !== myId.value
  const isOpen = activeUser.value?.id === otherId
  if (idx === -1) {
    if (!user) return loadConversations()   // interlocuteur inconnu : recharger
    conversations.value.unshift({ user, last_message: msg, unread: incoming && !isOpen ? 1 : 0 })
    return
  }
  const conv = conversations.value.splice(idx, 1)[0]
  if (conv.last_message.id <= msg.id) conv.last_message = msg
  if (incoming && !isOpen) conv.unread += 1
  conversations.value.unshift(conv)
}

function addToThread(msg) {
  if (thread.value.some(m => m.id === msg.id)) return false
  thread.value.push(msg)
  return true
}

async function send() {
  const body = draft.value.trim()
  if (!body || sending.value || !activeUser.value) return
  sending.value = true
  sendError.value = ''
  try {
    const msg = await messagesApi.send(activeUser.value.id, body)
    draft.value = ''
    addToThread(msg)
    upsertConversation(msg, activeUser.value)
    scrollBottom()
  } catch (e) {
    sendError.value = e?.response?.data?.detail?.[0]?.msg || e?.response?.data?.detail || "Le message n'a pas pu être envoyé."
  } finally {
    sending.value = false
  }
}

// Temps réel
const offRealtime = onRealtime(async (evt) => {
  if (evt.type !== 'message') return
  const msg = evt.message
  const otherId = msg.sender_id === myId.value ? msg.recipient_id : msg.sender_id
  if (activeUser.value?.id === otherId && addToThread(msg)) {
    const el = threadEl.value
    const nearBottom = !el || el.scrollHeight - el.scrollTop - el.clientHeight < 120
    if (nearBottom) scrollBottom()
    if (msg.sender_id !== myId.value) messagesApi.markRead(otherId)
  }
  upsertConversation(msg, activeUser.value?.id === otherId ? activeUser.value : null)
})

// Choix d'un destinataire
let searchTimer = null
async function loadContacts() {
  contactsLoading.value = true
  try {
    contacts.value = await messagesApi.contacts(contactSearch.value)
  } catch {
    contacts.value = []
  } finally {
    contactsLoading.value = false
  }
}
watch(contactSearch, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadContacts, 250)
})
async function openPicker() {
  picking.value = true
  contactSearch.value = ''
  loadContacts()
  await nextTick()
  pickerInput.value?.focus()
}
function startWith(contact) {
  const existing = conversations.value.find(c => c.user.id === contact.id)
  openThread(existing?.user ?? contact)
}

onMounted(() => {
  startMessaging()
  loadConversations()
})
onUnmounted(() => {
  offRealtime()
  clearTimeout(searchTimer)
})
</script>

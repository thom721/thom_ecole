// Messagerie interne : REST (/messages/...) + WebSocket temps réel
// (/ws/messages, voir app/Routes/RMessages.py). Une seule connexion
// WebSocket par onglet, partagée par la page Messages et le badge du menu.
import { ref } from 'vue'
import axios from 'axios'

const unreadTotal = ref(0)
const connected = ref(false)
const listeners = new Set()

let socket = null
let pingTimer = null
let retryTimer = null
let retryDelay = 1000
let wanted = false

function wsUrl() {
  // Le préfixe de l'API (ex. https://aplekol360.local/api/v1) mène aussi à
  // la WebSocket : /api/v1/ws/messages côté serveur
  const base = (axios.defaults.baseURL || '').trim().replace(/\/+$/, '')
  const token = localStorage.getItem('auth-token') || sessionStorage.getItem('auth-token') || ''
  return `${base.replace(/^http/, 'ws')}/ws/messages?token=${encodeURIComponent(token)}`
}

function open() {
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) return
  if (!localStorage.getItem('auth-token') && !sessionStorage.getItem('auth-token')) return

  socket = new WebSocket(wsUrl())

  socket.onopen = () => {
    connected.value = true
    retryDelay = 1000
    clearInterval(pingTimer)
    pingTimer = setInterval(() => socket?.readyState === WebSocket.OPEN && socket.send('ping'), 25000)
  }

  socket.onmessage = (ev) => {
    if (ev.data === 'pong') return
    let data
    try { data = JSON.parse(ev.data) } catch { return }
    listeners.forEach(fn => fn(data))
  }

  socket.onclose = (ev) => {
    connected.value = false
    clearInterval(pingTimer)
    socket = null
    // 4401 = jeton refusé : inutile d'insister
    if (!wanted || ev.code === 4401) return
    clearTimeout(retryTimer)
    retryTimer = setTimeout(open, retryDelay)
    retryDelay = Math.min(retryDelay * 2, 30000)
  }
}

export function startMessaging() {
  wanted = true
  open()
  refreshUnread()
}

export function stopMessaging() {
  wanted = false
  clearTimeout(retryTimer)
  clearInterval(pingTimer)
  socket?.close()
  socket = null
}

export function onRealtime(fn) {
  listeners.add(fn)
  return () => listeners.delete(fn)
}

export async function refreshUnread() {
  try {
    const { data } = await axios.get('/messages/unread-count')
    unreadTotal.value = data?.unread ?? 0
  } catch { /* badge simplement non mis à jour */ }
}

// Badge du menu : nouveau message reçu → recompte
onRealtime((evt) => {
  if (evt.type === 'message') refreshUnread()
})

export const messagesApi = {
  conversations: () => axios.get('/messages/conversations').then(r => r.data),
  contacts: (q = '') => axios.get('/messages/contacts', { params: { q } }).then(r => r.data.contacts),
  thread: (userId, beforeId) => axios.get(`/messages/with/${userId}`, { params: beforeId ? { before_id: beforeId } : {} }).then(r => r.data),
  markRead: (userId) => axios.post(`/messages/with/${userId}/read`).then(() => refreshUnread()),
  send: (recipientId, body) => axios.post('/messages', { recipient_id: recipientId, body }).then(r => r.data.message),
}

export function useMessages() {
  return { unreadTotal, connected }
}

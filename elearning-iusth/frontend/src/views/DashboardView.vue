<template>
  <div>
    <h1 class="text-lg font-bold text-gray-900 mb-6">{{ t('dashboard.title') }}</h1>

    <div class="grid grid-cols-3 gap-6">
      <div class="col-span-2 space-y-4">
        <BlockCard v-for="b in mainBlocks" :key="b.id" :block="b"
          @move-up="onMove(b, 'main', -1)" @move-down="onMove(b, 'main', 1)"
          @move-region="onMoveRegion(b, $event)" @toggle-visible="onToggleVisible(b)" @remove="onRemove(b)" />
      </div>
      <div class="col-span-1 space-y-4">
        <BlockCard v-for="b in sideBlocks" :key="b.id" :block="b"
          @move-up="onMove(b, 'side', -1)" @move-down="onMove(b, 'side', 1)"
          @move-region="onMoveRegion(b, $event)" @toggle-visible="onToggleVisible(b)" @remove="onRemove(b)" />
      </div>
    </div>

    <details class="bg-white border border-gray-200 rounded-xl p-4 mt-6">
      <summary class="cursor-pointer font-semibold text-gray-900">{{ t('dashboard.addBlock') }}</summary>
      <div class="mt-3 space-y-2 max-w-sm">
        <select v-model="newBlock.block_type" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm">
          <option value="my_courses">{{ t('dashboard.blockType.my_courses') }}</option>
          <option value="calendar">{{ t('dashboard.blockType.calendar') }}</option>
          <option value="recent_activity">{{ t('dashboard.blockType.recent_activity') }}</option>
          <option value="grades_overview">{{ t('dashboard.blockType.grades_overview') }}</option>
          <option value="badges">{{ t('dashboard.blockType.badges') }}</option>
          <option value="messages">{{ t('dashboard.blockType.messages') }}</option>
          <option value="online_users">{{ t('dashboard.blockType.online_users') }}</option>
          <option value="html">{{ t('dashboard.blockType.html') }}</option>
        </select>
        <select v-model="newBlock.region" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm">
          <option value="main">{{ t('dashboard.region.main') }}</option>
          <option value="side">{{ t('dashboard.region.side') }}</option>
        </select>
        <template v-if="newBlock.block_type === 'html'">
          <input v-model="newBlock.title" :placeholder="t('common.title')" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm" />
          <textarea v-model="newBlock.content" rows="3" class="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm"></textarea>
        </template>
        <button class="bg-gray-900 text-white rounded-lg px-3 py-1.5 text-sm font-semibold" @click="onAdd">{{ t('common.add') }}</button>
      </div>
    </details>
  </div>
</template>

<script setup>
import { reactive, computed, onMounted, h } from 'vue'
import { useI18n } from 'vue-i18n'
import { useBlocksStore } from '@/stores/blocks'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const store = useBlocksStore()
const router = useRouter()
const auth = useAuthStore()
const roleBase = auth.isAdmin ? '/admin' : auth.isTeacher ? '/teacher' : '/student'

const blocks = reactive([])
const newBlock = reactive({ block_type: 'my_courses', region: 'side', title: '', content: '' })

const mainBlocks = computed(() => blocks.filter((b) => b.region === 'main').sort((a, b) => a.weight - b.weight))
const sideBlocks = computed(() => blocks.filter((b) => b.region === 'side').sort((a, b) => a.weight - b.weight))

async function load() {
  const data = await store.fetchMyBlocks()
  blocks.splice(0, blocks.length, ...data)
}

async function onAdd() {
  const payload = { block_type: newBlock.block_type, region: newBlock.region }
  if (newBlock.block_type === 'html') {
    payload.config_json = JSON.stringify({ title: newBlock.title, content: newBlock.content })
  }
  await store.addBlock(payload)
  newBlock.title = ''
  newBlock.content = ''
  await load()
}

async function onMove(block, region, delta) {
  const list = (region === 'main' ? mainBlocks : sideBlocks).value.map((b) => b.id)
  const index = list.indexOf(block.id)
  const target = index + delta
  if (target < 0 || target >= list.length) return
  ;[list[index], list[target]] = [list[target], list[index]]
  await store.reorder(region, list)
  await load()
}

async function onMoveRegion(block, region) {
  await store.updateBlock(block.id, { region })
  await load()
}

async function onToggleVisible(block) {
  await store.updateBlock(block.id, { is_visible: !block.is_visible })
  await load()
}

async function onRemove(block) {
  await store.deleteBlock(block.id)
  await load()
}

onMounted(load)

// --- Sous-composant local, rendu de chaque bloc selon son type ---
const BlockCard = {
  props: ['block'],
  emits: ['move-up', 'move-down', 'move-region', 'toggle-visible', 'remove'],
  setup(props, { emit }) {
    return () => h('div', { class: 'bg-white border border-gray-200 rounded-xl p-4' }, [
      h('div', { class: 'flex items-center justify-between mb-2' }, [
        h('p', { class: 'font-semibold text-gray-900 text-sm' }, blockTitle(props.block)),
        h('div', { class: 'flex gap-1 text-xs' }, [
          h('button', { class: 'text-gray-500', onClick: () => emit('move-up') }, '▲'),
          h('button', { class: 'text-gray-500', onClick: () => emit('move-down') }, '▼'),
          h('select', {
            class: 'text-xs border border-gray-200 rounded',
            value: props.block.region,
            onChange: (e) => emit('move-region', e.target.value),
          }, [
            h('option', { value: 'main' }, t('dashboard.region.main')),
            h('option', { value: 'side' }, t('dashboard.region.side')),
          ]),
          h('button', { class: 'text-gray-500', onClick: () => emit('toggle-visible') }, props.block.is_visible ? '👁️' : '🚫'),
          h('button', { class: 'text-red-600', onClick: () => emit('remove') }, t('common.remove')),
        ]),
      ]),
      props.block.is_visible ? renderBody(props.block) : h('p', { class: 'text-xs text-gray-400' }, t('dashboard.hidden')),
    ])
  },
}

function blockTitle(block) {
  if (block.block_type === 'html') return block.data.title || t('dashboard.blockType.html')
  return t(`dashboard.blockType.${block.block_type}`)
}

function renderBody(block) {
  const d = block.data
  if (block.block_type === 'my_courses') {
    return h('ul', { class: 'text-sm space-y-1' }, (d.courses || []).map((c) =>
      h('li', [h('a', { class: 'text-blue-600 cursor-pointer', onClick: () => router.push(`${roleBase}/courses/${c.id}`) }, c.full_name)])
    ))
  }
  if (block.block_type === 'html') {
    return h('p', { class: 'text-sm text-gray-600 whitespace-pre-wrap' }, d.content || '')
  }
  if (block.block_type === 'calendar') {
    return h('ul', { class: 'text-xs space-y-1 text-gray-600' }, (d.events || []).map((e) =>
      h('li', `${new Date(e.start_at).toLocaleDateString()} — ${e.title}`)
    ))
  }
  if (block.block_type === 'recent_activity') {
    return h('ul', { class: 'text-xs space-y-1 text-gray-600' }, (d.items || []).map((i) =>
      h('li', `${i.item_type} — ${new Date(i.accessed_at).toLocaleString()}`)
    ))
  }
  if (block.block_type === 'grades_overview') {
    return h('ul', { class: 'text-xs space-y-1 text-gray-600' }, (d.courses || []).map((c) =>
      h('li', `${c.course_name} — ${c.final_percent !== null ? c.final_percent.toFixed(1) + '%' : '—'} ${c.final_letter ? '(' + c.final_letter + ')' : ''}`)
    ))
  }
  if (block.block_type === 'badges') {
    return h('ul', { class: 'text-xs space-y-1 text-gray-600' }, (d.badges || []).map((b) =>
      h('li', `${b.image_emoji || '🏅'} ${b.name}`)
    ))
  }
  if (block.block_type === 'messages') {
    return h('div', { class: 'text-xs text-gray-600' }, [
      h('p', { class: 'font-medium mb-1' }, t('dashboard.unreadCount', { count: d.unread_count || 0 })),
      ...(d.conversations || []).map((c) => h('p', c.last_message)),
    ])
  }
  if (block.block_type === 'online_users') {
    return h('ul', { class: 'text-xs space-y-1 text-gray-600' }, (d.users || []).map((u) =>
      h('li', `🟢 ${u.first_name} ${u.last_name}`)
    ))
  }
  return null
}
</script>

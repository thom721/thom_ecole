<!--
  Rendu générique pour les sections ajoutées via "+ Ajouter une section"
  (voir composables/usePageSections.js pour la liste des templates). Chaque
  layout combine image/pas d'image et une position de texte différente,
  contrairement aux 6 sections historiques de l'accueil qui ont leur propre
  markup sur mesure (voir HomeView.vue).
-->
<template>
  <div v-if="section.is_visible !== false || isAdmin" class="relative py-16" :class="wrapperBg">
    <div v-if="isAdmin && !section.is_visible" class="absolute inset-0 bg-red-500/5 border-2 border-dashed border-red-300/40 z-10 pointer-events-none"></div>
    <div v-if="isAdmin" class="absolute top-2 right-4 flex items-center gap-1 z-20">
      <span :class="['text-[10px] px-2 py-0.5 rounded-full font-medium', section.is_visible ? 'bg-emerald-500/20 text-emerald-600' : 'bg-red-500/20 text-red-500']">
        {{ section.is_visible ? 'Visible' : 'Masqué' }}
      </span>
      <button v-if="hasItems" @click="openItemEdit()" class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 text-xs">+ Élément</button>
      <button @click="openSectionEdit()" class="px-2 py-0.5 rounded bg-blue-500/10 text-blue-600 hover:bg-blue-500/20 text-xs">Modifier</button>
      <button @click="$emit('toggle', section)" class="p-1 rounded bg-gray-100 text-gray-500 hover:bg-gray-200 text-xs">👁</button>
      <button @click="$emit('delete', section)" class="p-1 rounded bg-red-50 text-red-400 hover:bg-red-100 text-xs">✕</button>
    </div>

    <!-- ── TEXTE CENTRÉ (sans image) ── -->
    <div v-if="section.layout === 'text_center'" class="max-w-2xl mx-auto px-6 text-center">
      <p v-if="section.sous_titre" class="text-xs tracking-widest uppercase font-bold text-gold">{{ section.sous_titre }}</p>
      <h2 class="font-serif text-3xl mt-1 mb-4">{{ section.titre }}</h2>
      <p class="text-gray-500 leading-relaxed whitespace-pre-line">{{ section.description }}</p>
    </div>

    <!-- ── IMAGE GAUCHE / DROITE ── -->
    <div v-else-if="section.layout === 'image_left' || section.layout === 'image_right'"
         class="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
      <div :class="section.layout === 'image_right' ? 'md:order-2' : ''">
        <img v-if="section.image_url" :src="section.image_url" :alt="section.titre"
             class="w-full rounded-2xl object-cover" style="max-height:360px;box-shadow:0 16px 48px rgba(11,31,58,.18)"/>
        <div v-else class="w-full rounded-2xl bg-gray-100 flex items-center justify-center text-gray-300 text-sm" style="height:280px">Aucune image</div>
      </div>
      <div>
        <p v-if="section.sous_titre" class="text-xs tracking-widest uppercase font-bold text-gold">{{ section.sous_titre }}</p>
        <h2 class="font-serif text-3xl mt-1 mb-4">{{ section.titre }}</h2>
        <p class="text-gray-500 leading-relaxed whitespace-pre-line">{{ section.description }}</p>
      </div>
    </div>

    <!-- ── BANNIÈRE IMAGE ── -->
    <div v-else-if="section.layout === 'image_banner'" class="relative overflow-hidden" style="height:50vh;min-height:340px">
      <img v-if="section.image_url" :src="section.image_url" :alt="section.titre" class="w-full h-full object-cover block"/>
      <div v-else class="w-full h-full bg-gray-100"></div>
      <div class="absolute inset-0" style="background:linear-gradient(135deg,rgba(11,31,58,.85),rgba(212,168,83,.3))"></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-6">
        <p v-if="section.sous_titre" class="text-xs font-bold mb-3" style="color:#fde68a;letter-spacing:.3em;text-transform:uppercase">{{ section.sous_titre }}</p>
        <h2 class="font-serif text-white mb-3" style="font-size:clamp(1.8rem,4vw,3rem)">{{ section.titre }}</h2>
        <p class="max-w-lg leading-relaxed" style="color:rgba(255,255,255,.85)">{{ section.description }}</p>
      </div>
    </div>

    <!-- ── GRILLE DE CARTES ── -->
    <div v-else-if="section.layout === 'cards_grid'" class="max-w-6xl mx-auto px-6">
      <div v-if="section.titre" class="text-center mb-10">
        <p v-if="section.sous_titre" class="text-xs tracking-widest uppercase font-bold text-gold">{{ section.sous_titre }}</p>
        <h2 class="font-serif text-3xl mt-1">{{ section.titre }}</h2>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        <div v-for="(it, i) in section.items" :key="i" class="bg-white rounded-2xl shadow-md p-6 relative">
          <img v-if="it.img" :src="it.img" :alt="it.t" class="w-full h-32 object-cover rounded-xl mb-4"/>
          <div v-else-if="it.i" class="text-3xl mb-3">{{ it.i }}</div>
          <div class="font-bold text-sm mb-1">{{ it.t }}</div>
          <div class="text-gray-500 text-xs leading-relaxed">{{ it.d }}</div>
          <div v-if="isAdmin" class="absolute top-2 right-2 flex gap-1">
            <button @click="openItemEdit(i)" class="w-5 h-5 rounded bg-blue-500/15 text-blue-600 text-xs flex items-center justify-center">✎</button>
            <button @click="$emit('delete-item', section, i)" class="w-5 h-5 rounded bg-red-500/15 text-red-500 text-xs flex items-center justify-center">✕</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── LIGNE DE CHIFFRES ── -->
    <div v-else-if="section.layout === 'stats_row'" class="max-w-4xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6">
      <div v-for="(it, i) in section.items" :key="i" class="text-center relative">
        <div class="font-black leading-none mb-1" style="font-size:2.4rem;background:linear-gradient(135deg,#0B2545,#1A7A4A);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{{ it.n }}</div>
        <div class="text-xs text-gray-500 uppercase tracking-widest">{{ it.l }}</div>
        <div v-if="isAdmin" class="absolute top-0 right-0 flex gap-1">
          <button @click="openItemEdit(i)" class="w-5 h-5 rounded bg-blue-500/15 text-blue-600 text-xs flex items-center justify-center">✎</button>
          <button @click="$emit('delete-item', section, i)" class="w-5 h-5 rounded bg-red-500/15 text-red-500 text-xs flex items-center justify-center">✕</button>
        </div>
      </div>
    </div>

    <!-- ══ MODAL : texte + image de section ══ -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showSectionModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="showSectionModal = false">
        <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h2 class="text-sm font-semibold text-gray-800">Modifier la section</h2>
            <button @click="showSectionModal = false" class="text-gray-500 hover:text-gray-600">✕</button>
          </div>
          <div class="px-6 py-5 space-y-4 max-h-[60vh] overflow-y-auto">
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Sous-titre</label>
              <input v-model="sectionForm.sous_titre" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"/>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Titre</label>
              <input v-model="sectionForm.titre" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"/>
            </div>
            <div v-if="section.layout !== 'cards_grid' && section.layout !== 'stats_row'">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Texte</label>
              <textarea v-model="sectionForm.description" rows="4" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400 resize-none"/>
            </div>
            <div v-if="['image_left','image_right','image_banner'].includes(section.layout)">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Image</label>
              <img v-if="sectionForm.image_url" :src="sectionForm.image_url" alt="Aperçu" class="w-full h-28 object-cover rounded-lg mb-2 border border-gray-200"/>
              <input type="file" accept="image/*" @change="onSectionImageChange"
                class="w-full text-xs text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-amber-50 file:text-amber-600 hover:file:bg-amber-100"/>
              <p v-if="uploadingImage" class="text-xs text-gray-500 mt-1">Envoi en cours…</p>
            </div>
          </div>
          <div class="flex justify-end gap-3 px-6 py-4 border-t">
            <button @click="showSectionModal = false" class="px-4 py-2 text-sm text-gray-500 hover:text-gray-800">Annuler</button>
            <button @click="saveSectionText" :disabled="savingSection"
              class="px-5 py-2 text-sm font-semibold text-white rounded-full disabled:opacity-50" style="background:#D4A853">
              {{ savingSection ? '…' : 'Enregistrer' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ══ MODAL : élément (cards_grid / stats_row) ══ -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" enter-to-class="opacity-100"
                leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="showItemModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
           @click.self="showItemModal = false">
        <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h2 class="text-sm font-semibold text-gray-800">{{ editingItemIdx !== null ? 'Modifier' : 'Ajouter' }} un élément</h2>
            <button @click="showItemModal = false" class="text-gray-500 hover:text-gray-600">✕</button>
          </div>
          <div class="px-6 py-5 space-y-4">
            <template v-if="section.layout === 'stats_row'">
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Valeur</label>
                <input v-model="itemForm.n" type="text" placeholder="16" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"/>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Libellé</label>
                <input v-model="itemForm.l" type="text" placeholder="Programmes" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"/>
              </div>
            </template>
            <template v-else>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Titre</label>
                <input v-model="itemForm.t" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"/>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Description</label>
                <textarea v-model="itemForm.d" rows="3" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400 resize-none"/>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Icône (emoji) — ou une image ci-dessous</label>
                <input v-model="itemForm.i" type="text" placeholder="🎯" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-amber-400"/>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Image (facultative)</label>
                <img v-if="itemForm.img" :src="itemForm.img" alt="Aperçu" class="w-full h-24 object-cover rounded-lg mb-2 border border-gray-200"/>
                <input type="file" accept="image/*" @change="onItemImageChange"
                  class="w-full text-xs text-gray-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-amber-50 file:text-amber-600 hover:file:bg-amber-100"/>
              </div>
            </template>
          </div>
          <div class="flex justify-end gap-3 px-6 py-4 border-t">
            <button @click="showItemModal = false" class="px-4 py-2 text-sm text-gray-500 hover:text-gray-800">Annuler</button>
            <button @click="saveItem" :disabled="savingItem"
              class="px-5 py-2 text-sm font-semibold text-white rounded-full disabled:opacity-50" style="background:#D4A853">
              {{ savingItem ? '…' : (editingItemIdx !== null ? 'Modifier' : 'Ajouter') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePageSections } from '@/composables/usePageSections.js'

const props = defineProps({
  section: { type: Object, required: true },
  isAdmin: { type: Boolean, default: false },
  page: { type: String, required: true },
})
const emit = defineEmits(['toggle', 'delete', 'delete-item', 'changed'])

const { updateSection, uploadImage } = usePageSections(props.page)

const wrapperBg = computed(() => props.section.layout === 'image_banner' ? '' : (props.section.ordre % 2 ? '' : 'bg-white'))
const hasItems = computed(() => ['cards_grid', 'stats_row'].includes(props.section.layout))

// ── Édition texte/image de section ──
const showSectionModal = ref(false)
const sectionForm = ref({})
const savingSection = ref(false)
const uploadingImage = ref(false)

const openSectionEdit = () => {
  sectionForm.value = {
    titre: props.section.titre, sous_titre: props.section.sous_titre,
    description: props.section.description, image_url: props.section.image_url,
  }
  showSectionModal.value = true
}

const onSectionImageChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  uploadingImage.value = true
  try { sectionForm.value.image_url = await uploadImage(file) }
  finally { uploadingImage.value = false }
}

const saveSectionText = async () => {
  savingSection.value = true
  const ok = await updateSection(props.section, sectionForm.value)
  savingSection.value = false
  if (ok) { showSectionModal.value = false; emit('changed') }
}

// ── Édition d'un élément (cards_grid / stats_row) ──
const showItemModal = ref(false)
const editingItemIdx = ref(null)
const itemForm = ref({})

const openItemEdit = (idx = null) => {
  editingItemIdx.value = idx
  itemForm.value = idx !== null ? JSON.parse(JSON.stringify(props.section.items[idx])) : {}
  showItemModal.value = true
}

const onItemImageChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  itemForm.value.img = await uploadImage(file)
}

const savingItem = ref(false)
const saveItem = async () => {
  savingItem.value = true
  const items = JSON.parse(JSON.stringify(props.section.items || []))
  if (editingItemIdx.value !== null) items[editingItemIdx.value] = itemForm.value
  else items.push(itemForm.value)
  const ok = await updateSection(props.section, { items })
  savingItem.value = false
  if (ok) { showItemModal.value = false; emit('changed') }
}
</script>

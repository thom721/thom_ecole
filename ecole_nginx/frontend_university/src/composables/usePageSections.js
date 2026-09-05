// CRUD des sections de page (voir app/Routes/RPageSections.py) — partagé
// entre toutes les pages publiques pour que "Ajouter une section" marche
// partout (Accueil, Formations, À propos, Contact, Événements...) sans
// dupliquer cette logique dans chaque vue.
import { ref } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { useAuthStore } from '@/stores/auth'

// Templates de mise en page génériques (voir GenericSection.vue pour le
// rendu) — indépendants des 6 sections historiques de la page d'accueil
// (stats/cycles/features/activities/testimonials/values, qui gardent leur
// propre rendu sur mesure). Chaque template combine image/pas d'image et
// une position de texte différente.
export const LAYOUT_TEMPLATES = [
  { layout: 'text_center', label: 'Texte centré',        desc: 'Titre + texte, centré, sans image.' },
  { layout: 'image_left',  label: 'Image à gauche',      desc: 'Image à gauche, titre + texte à droite.' },
  { layout: 'image_right', label: 'Image à droite',      desc: 'Titre + texte à gauche, image à droite.' },
  { layout: 'image_banner',label: 'Bannière image',      desc: 'Image pleine largeur en fond, texte en superposition.' },
  { layout: 'cards_grid',  label: 'Grille de cartes',    desc: 'Plusieurs cartes (icône ou photo, titre, description).' },
  { layout: 'stats_row',   label: 'Ligne de chiffres',   desc: 'Chiffres clés (nombre + libellé), sans image.' },
]

function errMsg(e, fallback = 'Erreur') {
  return e.response?.data?.detail || fallback
}

// Emplacements possibles pour un bloc générique, par page — chacun
// correspond à un espace réel entre deux sections déjà fixes dans le
// template (voir les commentaires "══ ... ══" dans chaque vue). On réutilise
// le champ `ordre` déjà présent sur PageSection pour coder l'emplacement
// (comparaison exacte, pas de tri complexe) : pas besoin de réorganiser tout
// l'affichage de la page ni d'ajouter une colonne — seulement de rendre
// plusieurs petites zones à des endroits différents du template au lieu
// d'une seule à la fin.
export const PAGE_ZONES = {
  home: [
    { ordre: 5,  label: 'Tout en haut (après le hero)' },
    { ordre: 15, label: 'Après "Chiffres clés"' },
    { ordre: 25, label: 'Après "Présentation"' },
    { ordre: 35, label: 'Après "Cycles"' },
    { ordre: 45, label: 'Après "Atouts"' },
    { ordre: 55, label: 'Après "Vie scolaire"' },
    { ordre: 65, label: 'Après "Témoignages"' },
    { ordre: 75, label: 'Après "Actualités"' },
    { ordre: 95, label: 'Tout en bas' },
  ],
  formations: [
    { ordre: 5,  label: 'Tout en haut (après le hero)' },
    { ordre: 45, label: 'Après "Atouts"' },
    { ordre: 95, label: 'Tout en bas' },
  ],
  apropos: [
    { ordre: 5,  label: 'Tout en haut (après le hero)' },
    { ordre: 25, label: 'Après "Mission"' },
    { ordre: 65, label: 'Après "Notre parcours"' },
    { ordre: 95, label: 'Tout en bas' },
  ],
  contact: [
    { ordre: 5,  label: 'Tout en haut (après le hero)' },
    { ordre: 95, label: 'Tout en bas' },
  ],
  evenements: [
    { ordre: 5,  label: 'Tout en haut (après le hero)' },
    { ordre: 95, label: 'Tout en bas' },
  ],
}

export function usePageSections(page) {
  const url = import.meta.env.VITE_APP_BASE_URL
  const authStore = useAuthStore()

  const sections = ref([])
  const loading  = ref(false)

  const sec = (key) => sections.value.find(s => s.section_key === key)

  const fetchSections = async () => {
    loading.value = true
    try {
      const endpoint = authStore.isAdmin
        ? `${url}/page-sections/${page}/all`
        : `${url}/page-sections/${page}`
      const { data } = await axios.get(endpoint)
      sections.value = data
    } catch (e) { console.error(`[${page}] sections`, e) }
    finally { loading.value = false }
  }

  // Sections génériques ajoutées par l'admin (par opposition aux sections
  // historiques identifiées par leur section_key fixe) — reconnues par la
  // présence d'un `layout`.
  const genericSections = () => sections.value.filter(s => s.layout)
  // Sous-ensemble affiché à un emplacement donné (voir PAGE_ZONES ci-dessus).
  const genericSectionsInZone = (zoneOrdre) => genericSections().filter(s => s.ordre === zoneOrdre)

  const zones = PAGE_ZONES[page] ?? [{ ordre: 95, label: 'Tout en bas' }]

  const createGenericSection = async (tpl, zoneOrdre) => {
    try {
      await axios.post(`${url}/page-sections/`, {
        page,
        section_key: `${tpl.layout}_${Date.now()}`,
        layout: tpl.layout,
        titre: tpl.label,
        sous_titre: null,
        description: '',
        items: [],
        ordre: zoneOrdre,
      })
      await fetchSections()
      return true
    } catch (e) {
      Swal.fire({ icon: 'error', title: 'Erreur', text: errMsg(e), background: '#0f1117', color: '#e8eaf0' })
      return false
    }
  }

  const updateSection = async (s, patch) => {
    try {
      await axios.put(`${url}/page-sections/${s.id}`, patch)
      await fetchSections()
      return true
    } catch (e) {
      Swal.fire({ icon: 'error', title: 'Erreur', text: errMsg(e), background: '#0f1117', color: '#e8eaf0' })
      return false
    }
  }

  const toggleSection = async (s) => {
    try {
      await axios.patch(`${url}/page-sections/${s.id}/toggle`)
      await fetchSections()
    } catch (e) {
      Swal.fire({ icon: 'error', title: 'Erreur', text: errMsg(e), background: '#0f1117', color: '#e8eaf0' })
    }
  }

  const deleteSection = async (s) => {
    const res = await Swal.fire({
      title: `Supprimer la section "${s.titre || s.section_key}" ?`,
      text: 'Cette action est irréversible.',
      icon: 'warning', showCancelButton: true,
      confirmButtonColor: '#ef4444', cancelButtonColor: '#374151',
      confirmButtonText: 'Supprimer', cancelButtonText: 'Annuler',
      background: '#0f1117', color: '#e8eaf0'
    })
    if (!res.isConfirmed) return
    try {
      await axios.delete(`${url}/page-sections/${s.id}`)
      await fetchSections()
    } catch (e) {
      Swal.fire({ icon: 'error', title: 'Erreur', text: errMsg(e), background: '#0f1117', color: '#e8eaf0' })
    }
  }

  const saveItems = async (s, items) => {
    return updateSection(s, { items })
  }

  // L'API renvoie un chemin relatif ("/static/uploads/..."), qui se
  // résoudrait contre l'origine du FRONTEND (dev server ou domaine statique)
  // et non celle de l'API — deux origines différentes en déploiement web,
  // d'où l'image cassée. On le rend absolu ici, une seule fois, pour que
  // tout appelant (item ou section) obtienne une URL qui fonctionne partout.
  const apiOrigin = url.replace(/\/api\/v1\/?$/, '')
  const uploadImage = async (file) => {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await axios.post(`${url}/page-sections/upload-image`, fd)
    return data.image_url.startsWith('http') ? data.image_url : `${apiOrigin}${data.image_url}`
  }

  return {
    url, authStore, sections, loading, sec, fetchSections, zones,
    genericSections, genericSectionsInZone, createGenericSection, updateSection,
    toggleSection, deleteSection, saveItems, uploadImage,
  }
}

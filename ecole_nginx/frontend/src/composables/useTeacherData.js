// Données de l'espace enseignant, partagées entre Tableau de bord, Mes
// Classes, Statistiques et Calendrier — chargées une fois par session de
// navigation (refresh(true) pour forcer).
//
// Moyennes sur 10, même formule que les bulletins (voir
// /mes-statistiques-prof dans app/Routes/RProgramme.py).
import { ref } from 'vue'
import axios from 'axios'

const stats = ref(null)
const events = ref([])
const loading = ref(false)
const error = ref('')
let pending = null

export const PALETTE = ['#4f8ef7', '#6ee7b7', '#f59e0b', '#a78bfa', '#f87171', '#22d3ee']
export const SEUIL_REUSSITE = 5

export function colorAt(i) {
  return PALETTE[i % PALETTE.length]
}

// Statut d'une classe d'après sa moyenne /10 (null = aucune note saisie)
export function classStatus(moyenne) {
  if (moyenne === null || moyenne === undefined) return { status: 'none',  label: 'Pas de notes' }
  if (moyenne < SEUIL_REUSSITE)                  return { status: 'red',   label: 'À risque'     }
  if (moyenne < 6.5)                             return { status: 'amber', label: 'Attention'    }
  if (moyenne >= 8)                              return { status: 'green', label: 'Excellent'    }
  return                                                { status: 'green', label: 'En cours'     }
}

export function formatMoyenne(m) {
  return m === null || m === undefined ? '—' : Number(m).toFixed(1)
}

export function formatPct(p) {
  return p === null || p === undefined ? '—' : `${p}%`
}

export function initials(nom) {
  return (nom || '?').split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join('')
}

// Abréviation affichée dans la pastille de la carte classe (ex : "CE1 C" → "CE1")
export function levelTag(nomClasse) {
  return (nomClasse || '').split(/\s+/)[0].slice(0, 4)
}

const MOIS_COURTS = ['Jan', 'Fév', 'Mars', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc']
export const MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

export function eventView(ev) {
  const d = new Date(ev.start_date)
  const heure = d.getHours() || d.getMinutes()
    ? ` · ${String(d.getHours()).padStart(2, '0')}h${String(d.getMinutes()).padStart(2, '0')}`
    : ''
  return {
    ...ev,
    date: d,
    day: String(d.getDate()).padStart(2, '0'),
    month: MOIS_COURTS[d.getMonth()],
    sub: `${ev.location || (ev.audience === 'professeurs' ? 'Enseignants' : 'Toute l\'école')}${heure}`,
    tagLabel: ev.category?.name || (ev.audience === 'professeurs' ? 'Enseignants' : 'École'),
    tag: ev.audience === 'professeurs' ? 'amber' : 'blue',
    color: ev.audience === 'professeurs' ? '#f59e0b' : '#4f8ef7',
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [s, e] = await Promise.allSettled([
      axios.get('/mes-statistiques-prof'),
      axios.get('/events/', { params: { published_only: true } }),
    ])
    if (s.status === 'fulfilled') {
      stats.value = s.value.data
    } else {
      error.value = s.reason?.response?.data?.detail || 'Impossible de charger vos statistiques.'
    }
    // Événements visibles par un enseignant : publics + réservés aux profs
    events.value = e.status === 'fulfilled'
      ? (e.value.data || [])
          .filter(ev => ev.audience === 'public' || ev.audience === 'professeurs')
          .map(eventView)
      : []
  } finally {
    loading.value = false
    pending = null
  }
}

export function useTeacherData() {
  function refresh(force = false) {
    if (pending) return pending
    if (stats.value && !force) return Promise.resolve()
    pending = load()
    return pending
  }
  refresh()

  const upcoming = (limit = 4) => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    return events.value.filter(ev => ev.date >= today).sort((a, b) => a.date - b.date).slice(0, limit)
  }

  return { stats, events, loading, error, refresh, upcoming }
}

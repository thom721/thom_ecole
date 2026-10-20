// ─────────────────────────────────────────────
//  src/composables/useApiErrors.js
//  Lecture uniforme des erreurs renvoyées par l'API FastAPI.
//
//  Le backend renvoie plusieurs formats selon l'origine de l'erreur :
//   - validation Pydantic (app/main.py) :
//       { errors: { champ: "msg" }, details: { "liste.0.champ": ["msg"] } }
//   - HTTPException dans une route :
//       { detail: "msg" } | { detail: { errors: "msg" | {...} } } | { detail: [...] }
//  Sans traitement commun, un formulaire qui n'attend qu'un seul format
//  n'affiche rien du tout pour les autres.
// ─────────────────────────────────────────────

import Swal from 'sweetalert2'

const asList = (v) => (Array.isArray(v) ? v : [v]).filter(Boolean).map(String)

/**
 * @returns {{ fields: Record<string, string[]>, messages: string[] }}
 *   fields   : erreurs par chemin de champ (pour l'affichage sous le champ)
 *   messages : tous les messages lisibles (pour une alerte globale)
 */
export function parseApiErrors(error, fallback = 'Une erreur est survenue.') {
  const data = error?.response?.data
  const fields = {}
  const messages = []

  const addObject = (obj) => {
    for (const [k, v] of Object.entries(obj)) {
      fields[k] = asList(v)
      messages.push(...fields[k])
    }
  }

  if (data?.details && typeof data.details === 'object') addObject(data.details)
  else if (data?.errors && typeof data.errors === 'object') addObject(data.errors)
  else if (typeof data?.errors === 'string') messages.push(data.errors)

  const detail = data?.detail
  if (typeof detail === 'string') messages.push(detail)
  else if (Array.isArray(detail)) messages.push(...detail.map(d => d?.msg || d).filter(Boolean).map(String))
  else if (detail && typeof detail === 'object') {
    if (typeof detail.errors === 'string') messages.push(detail.errors)
    else if (detail.errors && typeof detail.errors === 'object') addObject(detail.errors)
    else if (detail.message) messages.push(String(detail.message))
  }

  if (!messages.length && typeof data?.message === 'string') messages.push(data.message)
  if (!messages.length) messages.push(error?.response ? fallback : 'Impossible de joindre le serveur.')

  return { fields, messages: [...new Set(messages)] }
}

const escapeHtml = (s) => s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))

/**
 * Affiche l'erreur dans une alerte (qui reste ouverte jusqu'au clic) et
 * renvoie les erreurs par champ, à placer dans le `errors` du formulaire.
 */
export function showApiError(error, title = 'Enregistrement impossible') {
  const { fields, messages } = parseApiErrors(error)
  Swal.fire({
    icon: 'error',
    title,
    html: messages.length > 1
      ? `<ul style="text-align:left;margin:0;padding-left:1.2em">${messages.map(m => `<li>${escapeHtml(m)}</li>`).join('')}</ul>`
      : escapeHtml(messages[0]),
  })
  return fields
}

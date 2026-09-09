// Titre/description/canonical par page, dérivés directement de la route
// courante via useHead() plutôt que poussés dans un objet partagé.
//
// Piège évité ici : un `reactive({...})` défini au niveau du module serait
// un singleton unique dans le process Node — pendant le pré-rendu
// (vite-ssg), plusieurs pages sont rendues dans le MÊME process, donc un tel
// objet partagé se ferait écraser par la dernière page rendue et polluerait
// toutes les autres (constaté : chaque page pré-rendue avait le titre de la
// toute dernière route traitée). route.meta/route.path sont en revanche
// propres à chaque instance de router (vite-ssg recrée une app + un router
// par page pré-rendue), donc aucune fuite entre pages.
import { useRoute } from 'vue-router'
import { useHead } from '@unhead/vue'

const appName = import.meta.env.VITE_APP_NAME

// Les pages publiques sont pré-rendues en fichiers statiques (dist/<route>/
// index.html) : l'hébergeur (règle DirectorySlash d'Apache) redirige donc en
// 301 l'URL sans slash final vers sa forme avec slash. canonical/og:url
// doivent pointer directement sur cette forme finale — sinon la page déclare
// comme "canonique" une adresse qui redirige elle-même ailleurs.
function withTrailingSlash(path) {
  return path === '/' || path.endsWith('/') ? path : `${path}/`
}

export function registerHead() {
  const route = useRoute()

  useHead({
    title: () => route.meta?.title ?? appName,
    meta: () => [
      { name: 'description', content: route.meta?.description ?? '' },
      { property: 'og:title', content: route.meta?.title ?? appName },
      { property: 'og:url', content: `${import.meta.env.VITE_APP_URL}${withTrailingSlash(route.path)}` },
    ],
    link: () => [
      { rel: 'canonical', href: `${import.meta.env.VITE_APP_URL}${withTrailingSlash(route.path)}` },
    ],
  })
}

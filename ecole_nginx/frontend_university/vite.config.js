import { defineConfig, loadEnv } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'// ou react

// export default defineConfig({
//   plugins: [
//     vue(),
//     tailwindcss(),
//   ],
// })


 // 1. Importe le module path de Node

// Les 8 pages publiques marketing (voir router/index.js) — /connexion est
// public mais n'a aucune valeur SEO (formulaire de connexion), donc
// volontairement exclue du pré-rendu.
const PUBLIC_ROUTES = [
  '/',
  '/facultes',
  '/formations',
  '/admission',
  '/evenements',
  '/mentions-legales',
  '/a-propos',
  '/contact',
  // Page 404 statique (voir router/index.js, route catch-all "not-found") —
  // /404 lui-même ne correspond à aucune autre route, donc c'est bien le
  // composant NotFound.vue qui est pré-rendu ici. Servie par Apache via
  // ErrorDocument 404 (voir public/.htaccess) pour renvoyer un vrai statut
  // HTTP 404 plutôt qu'un 200 sur contenu vide (audit CCA v2, P0-5).
  '/404',
]

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBase = env.VITE_APP_BASE_URL

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        // 2. Définit @ comme raccourci vers le dossier 'src'
        '@': path.resolve(__dirname, './src'),
      },
    },
    ssgOptions: {
      script: 'async',
      formatting: 'minify',
      // 'nested' -> dist/facultes/index.html au lieu de dist/facultes.html :
      // compatible tel quel avec le .htaccess existant, qui laisse passer
      // une requête vers un vrai DOSSIER (-d) pour qu'Apache serve son
      // index.html par défaut — aucune règle de réécriture supplémentaire
      // à ajouter.
      dirStyle: 'nested',
      // On fournit la liste exacte des routes à pré-rendre plutôt que de
      // laisser vite-ssg suivre les liens <a> (crawlLinks) — l'app mélange
      // dans le même routeur les pages publiques et tout l'espace
      // /admin, /professeur-*, /student/* (authentifié, dynamique, sans
      // valeur SEO) : un crawl automatique risquerait d'essayer de
      // pré-rendre ces routes-là aussi.
      crawlLinks: false,
      includedRoutes: async () => {
        const routes = [...PUBLIC_ROUTES]
        // Actualités publiées réelles — sans ça, /actualites/:id resterait
        // un simple SPA classique (pas grave en soi, mais autant profiter
        // du pré-rendu pour ces pages aussi, mêmes enjeux SEO/partage).
        try {
          const res = await fetch(`${apiBase}/news/?published_only=true`)
          if (res.ok) {
            const articles = await res.json()
            for (const a of articles) {
              if (a?.id != null) routes.push(`/actualites/${a.id}`)
            }
          } else {
            console.warn(`[vite-ssg] /news/ a répondu ${res.status} — pré-rendu des actualités ignoré.`)
          }
        } catch (e) {
          console.warn('[vite-ssg] Impossible de récupérer les actualités pour le pré-rendu :', e.message)
        }
        return routes
      },
    },
  }
})

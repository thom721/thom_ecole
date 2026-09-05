import { useAuthStore } from '../stores/auth'
import { ref } from 'vue'
import { useSchoolStoreInfo } from '../stores/schoolStore'

export const isGlobalLoading = ref(false) 
import ResetPassword  from '../views/auth/Resetpassword.vue'
import FirstConnexion  from '../views/auth/FirstConnexion.vue'

import DashboardView    from '@/views/Teacher/DashboardView.vue'
import ClassesView      from '@/views/Teacher/ClassesView.vue'
import NotesView        from '@/views/Teacher/NotesView.vue'
import CoursView        from '@/views/Teacher/CoursView.vue'
import MessagesView     from '@/views/Teacher/MessagesView.vue'
import CalendrierView   from '@/views/Teacher/CalendrierView.vue'
import StatistiquesView from '@/views/Teacher/StatistiquesView.vue'
import ParametresView   from '@/views/Teacher/ParametresView.vue'

const HomeView       = () => import('../views/public/HomeView.vue')
const FacultesView   = () => import('../views/public/FacultesView.vue')
const FormationsView = () => import('../views/public/FormationsView.vue')
const AdmissionView  = () => import('../views/public/AdmissionView.vue')
const EvenementsView = () => import('../views/public/EvenementsView.vue')
const ActualiteView  = () => import('../views/public/ActualiteView.vue')
const LegalView      = () => import('../views/public/LegalView.vue')
const AProposView    = () => import('../views/public/AProposView.vue')
const ContactView    = () => import('../views/public/ContactView.vue')
const ConnexionView  = () => import('../views/public/ConnexionView.vue')
const NotFoundView   = () => import('../views/public/NotFound.vue')
const appName = import.meta.env.VITE_APP_NAME
// Format demandé par l'audit CCA v2 (P0-2) : « Page — IUSTH | Institut
// Universitaire des Sciences et des Technologies d'Haïti ».
const FULL_NAME = "Institut Universitaire des Sciences et des Technologies d'Haïti"
const routes = [

  {
    path: '/',
    component: () => import('../layouts/PublicLayout.vue'),
    children: [
    {
    path: '/',
    name: 'accueil',
    component: HomeView,
    meta: {
      title: `${appName} | ${FULL_NAME}`,
      description: "L'IUSTH forme des scientifiques, professionnels et techniciens en Haïti : sciences infirmières, administratives, informatiques, agronomiques, génie civil. Institution reconnue d'utilité publique.",
    },
    },
  {
    path: '/facultes',
    name: 'facultes',
    component: FacultesView,
    meta: {
      title: `Les facultés — ${appName} | ${FULL_NAME}`,
      description: "Découvrez les facultés ouvertes à l'IUSTH : sciences infirmières, administratives, informatiques, agronomiques et génie civil & architecture.",
    },
  },
  {
    path: '/formations',
    name: 'formations',
    component: FormationsView,
    meta: {
      title: `Formations et diplômes — ${appName} | ${FULL_NAME}`,
      description: "Licences et diplômes d'ingénieur (sciences infirmières, administratives, agronome, civil, informatique) ainsi que nos cycles courts techniques.",
    },
  },
  {
    path: '/admission',
    name: 'admission',
    component: AdmissionView,
    meta: {
      title: `Admission — ${appName} | ${FULL_NAME}`,
      description: "Conditions d'admission à l'IUSTH : par équivalence ou par concours (octobre chaque année). Documents requis et démarche d'inscription en ligne.",
    },
  },
  {
    path: '/evenements',
    name: 'evenements',
    component: EvenementsView,
    meta: {
      title: `Événements — ${appName} | ${FULL_NAME}`,
      description: "Agenda des événements, cérémonies et actualités de l'IUSTH.",
    },
  },
  {
    path: '/actualites/:id',
    name: 'actualite-detail',
    component: ActualiteView,
    meta: {
      title: `Actualité — ${appName} | ${FULL_NAME}`,
      description: "Article de presse et actualités concernant l'IUSTH.",
    },
  },
  {
    path: '/mentions-legales',
    name: 'legal',
    component: LegalView,
    meta: {
      title: `Mentions légales — ${appName} | ${FULL_NAME}`,
      description: "Mentions légales, politique de confidentialité et politique de cookies de l'IUSTH.",
    },
  },
  {
    path: '/a-propos',
    name: 'apropos',
    component: AProposView,
    meta: {
      title: `À propos — ${appName} | ${FULL_NAME}`,
      description: "Mission, vision, valeurs et gouvernance de l'IUSTH, institution privée d'enseignement supérieur créée en 2021, reconnue d'utilité publique par l'État haïtien.",
    },
  },
  {
    path: '/contact',
    name: 'contact',
    component: ContactView,
    meta: {
      title: `Contact — ${appName} | ${FULL_NAME}`,
      description: "Contactez l'IUSTH : téléphone, email, adresse et horaires d'accueil (vendredi et samedi, 8h–17h).",
    },
  },
  {
    path: '/connexion',
    name: 'login',
    component: ConnexionView,
    meta: {
      title: `Connexion-${appName}`, 
      hideShell: true,
    },    
  },

    {
    path: '/forgot-password',
    name: 'resetpassword',
    component: ResetPassword,
    meta: {
      title: `Connexion-${appName}`, 
      hideShell: true,
    },
    },

        {
    path: '/first-connexion',
    name: 'first.connexion',
    component: FirstConnexion,
    meta: {
      title: `Connexion-${appName}`,
      firstLogin: true,
      hideShell: true,
    },
    },

  // 404 réel (voir audit CCA v2, P0-5) — remplace l'ancien catch-all qui
  // affichait silencieusement la page de connexion avec un statut 200 pour
  // n'importe quelle URL inconnue. Placé en dernier enfant de PublicLayout
  // pour garder le header/footer du site ; /admin, /professeur-*, /student
  // restent des arbres de routes top-level distincts et plus spécifiques,
  // donc jamais interceptés par ce joker (Vue Router classe par
  // spécificité de chemin, pas par ordre de déclaration).
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
    meta: {
      title: `Page introuvable — ${appName}`,
    },
  },
]
  },

 
  {
    path: '/admin',
    alias: '/',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: ['admin', 'user', 'Caissier', 'Responsable financier', 'Responsable des admissions', 'Responsable pédagogique', 'Comptable'] },
    children: [
      { path: '', redirect: { name: 'Dashboard' } },

      { path: 'dashboard',      name: 'Dashboard',       component: () => import('../views/admin/Dashboard.vue')       },
      { path: 'administration', name: 'Administration',  component: () => import('../views/admin/Administration.vue')  },

      // Étudiants
      { path: 'etudiants',                     name: 'Étudiants',    component: () => import('../views/admin/Etudiants.vue'),       },
      { path: 'etudiants/ajouter',             name: 'student-add',  component: () => import('../views/admin/Ajout_etudiant.vue'),  props: true },
      { path: 'etudiants/voir/:etudiantId',    name: 'student-view', component: () => import('../views/admin/Ajout_etudiant.vue'),  props: true },
      { path: 'etudiants/modifier/:etudiantId',name: 'student-edit', component: () => import('../views/admin/Ajout_etudiant.vue'),  props: true },
      // { path: 'destion-de-classe',  name: 'classe-detail', component: () => import('../views/admin/DetaisClasse.vue'),  props: true },

// {
//   path: '/classe/:id',
//   component: DetailClasse,
//   props: route => ({
//     id: Number(route.params.id)
//   })
// }

//       {
//   path: '/gestion-de-classe',
//   name: 'paiement-detail',
//   component: () => import('../views/admin/DetaisClasse.vue'),
//   props: route => ({ 
//     id: route.query.id,
//     nom: route.query.nom
//   })
// }
{
    path: '/statistiques',
    name: 'Statistiques',
    component: () => import('../views/admin/Dashboard.vue'),
    meta: { requiresAuth: true } // protégée par auth
  },

      // Paiements
      { path: 'paiements',             name: 'Paiements',    component: () => import('../views/admin/Paiements.vue'),    },
      { path: 'paiement/:etudiantId',  name: 'add-paiement', component: () => import('../views/admin/AddPaiement.vue'),  props: true },
      
      { path: 'paiement-detail/:paiement_id',  name: 'paiement-detail', component: () => import('../views/admin/DetaisPaiement.vue'),  props: true },


      { path: 'tresorerie',            name: 'Trésorerie',       component: () => import('../views/admin/Tresorerie.vue')    },
      { path: 'communaute',            name: 'Communauté',       component: () => import('../views/admin/Communaute.vue')    },
      { path: 'presences',            name: 'Présences',       component: () => import('../views/admin/Presences.vue')    },

      { path: 'profile',            name: 'Profile',       component: () => import('../views/admin/adProfile.vue')    },
      // meta.role aligné sur canAccessProfesseurs (stores/auth.js) : sans ça,
      // seul tab_ids filtrait la navigation directe par URL — un rôle non
      // admin/Comptable avec tab_ids=null (défaut) pouvait ouvrir la page
      // (salaires inclus) malgré le lien de menu masqué pour lui.
      { path: 'professeurs',        name: 'Professeurs',   component: () => import('../views/admin/Professeur.vue'),  meta: { role: ['admin', 'Comptable'] } },
      { path: 'notes',              name: 'Notes',         component: () => import('../views/admin/Notes.vue')        },
      { path: 'cours',              name: 'Cours',         component: () => import('../views/admin/Cours.vue')        },
      { path: 'parametres',         name: 'Paramètres',    component: () => import('../views/admin/Parametres.vue')   },
      { path: 'abonnement',         name: 'Abonnement',    component: () => import('../views/admin/Abonnement.vue')   },
      { path: 'rapport',            name: 'Rapport',       component: () => import('../views/admin/Rapport.vue')      },
      { path: 'ajouter-cours',      name: 'add-cours',     component: () => import('../views/admin/AddCours.vue')     },
      { path: 'ajouter-programme',  name: 'add-programme', component: () => import('../views/admin/AddProgramme.vue') },
      { path: 'ajouter-notes',      name: 'add-notes',     component: () => import('../views/admin/NoteForm.vue')     },
    ],
  },

 
  {
    path: '/',
    component: () => import('../layouts/TeacherLayout.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
    children: [
      { path: '/professeur-dashboard',        name: 'teacher.dashboard',     component: DashboardView,    meta: { label: 'Tableau de Bord'    } },
      
    { path: '/professeur-classes',     name: 'teacher.classes',      component: ClassesView,      meta: { label: 'Mes Classes'         } },
    { path: '/professeur-notes',    name: 'teacher.notes',    component: NotesView,        meta: { label: 'Devoirs & Notes'     } },
    { path: 'professeur-ajouter-notes', name: 'teacher.add-notes',  component: () => import('../views/Teacher/NoteForm.vue')  },
    { path: '/professeur-cours',      name: 'teacher.cours',     component: CoursView,        meta: { label: 'Cours & Ressources'  } },
    { path: '/professeur-messages',     name: 'teacher.messages', component: MessagesView,     meta: { label: 'Messages'            } },
    { path: '/professeur-calendrier',   name: 'teacher.calendrier', component: CalendrierView,   meta: { label: 'Calendrier'          } },
    { path: '/professeur-statistiques', name: 'teacher.statistiques', component: StatistiquesView, meta: { label: 'Statistiques'        } },
    { path: '/professeur-parametres',   name: 'teacher.profile', component: ParametresView,   meta: { label: 'Paramètres'          } },
      // { path: '', redirect: { name: 'teacher.dashboard' } },

      // { path: 'professeur-dashboard',     name: 'teacher.dashboard',  component: () => import('../views/Teacher/Dashboard.vue') },
      // { path: 'professeur-cours',         name: 'teacher.cours',      component: () => import('../views/Teacher/Cours.vue')     },
      // { path: 'professeur-notes',         name: 'teacher.notes',      component: () => import('../views/Teacher/Notes.vue')     },
      // { path: 'professeur-ajouter-notes', name: 'teacher.add-notes',  component: () => import('../views/Teacher/NoteForm.vue')  },
      // { path: 'professeur-profile',       name: 'teacher.profile',    component: () => import('../views/Teacher/Profile.vue')   },
    ],
  },


  {
    path: '/student',
    alias: '/',                                            // ← préfixe rendu optionnel
    component: () => import('../layouts/StudentLayout.vue'),
    meta: { requiresAuth: true, role: 'student' },
    children: [
      { path: '', redirect: { name: 'etudiant.dashboard' } },

      { path: 'dashboard', name: 'etudiant.dashboard', component: () => import('../views/Student/Dashboard.vue') },
      { path: 'paiement', name: 'etudiant.paiement', component: () => import('../views/Student/Paiement.vue') },
      { path: 'cours',    name: 'etudiant.cours',     component: () => import('../views/Student/Cours.vue')     },
      { path: 'notes',     name: 'etudiant.notes',     component: () => import('../views/Student/Notes.vue')     },
      { path: 'profile',   name: 'etudiant.profile',   component: () => import('../views/Student/Profile.vue')   },
    ],
  },

]

/* ══════════════════════════════════════════════════════════════════
   ROUTES + GARDES — la création du router elle-même est déléguée à
   vite-ssg (voir main.js) : createWebHistory() n'existe pas côté Node
   pendant le pré-rendu, vite-ssg choisit le bon mode d'historique selon
   l'environnement (client vs SSG) à partir de ce même tableau `routes`.
══════════════════════════════════════════════════════════════════ */
export { routes }

export function setupRouterGuards(router) {
  router.beforeEach(async (to, from, next) => {
    // Pré-rendu (vite-ssg) : aucune des 9 pages publiques ciblées n'a besoin
    // d'auth/session — et localStorage n'existe pas côté Node. On saute
    // entièrement cette garde pendant le SSR plutôt que de la truffer de
    // vérifications typeof window partout.
    if (import.meta.env.SSR) return next()

    isGlobalLoading.value = true

    const schoolStore = useSchoolStoreInfo()
    const authStore   = useAuthStore()
    const token       = localStorage.getItem('auth-token')

    // charger dépendances école
    schoolStore.fetchAllDependencies()

    // initialiser l'utilisateur depuis le token
    if (token && !authStore.user) {
      try {
        await authStore.initializeAuth()
      } catch {
        localStorage.removeItem('auth-token')
        return next({ name: 'login' })
      }
    }

    const isAuthenticated = !!authStore.user

    // route protégée sans auth
    if (to.meta.requiresAuth && !isAuthenticated) {
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }

    if (
    isAuthenticated &&
    authStore.user?.user?.password_changed_at =='' &&
    to.name !== 'first.connexion'
  ) {
    return next({ name: 'first.connexion' })
  }

    // déjà connecté → pas besoin du login
    if (to.name === 'login' && isAuthenticated) {
      return next(homeRoute(authStore))
    }

    // Chaque record matched (parent ET enfant) qui déclare meta.role doit être
    // satisfait — .find() ne gardait que le PREMIER trouvé dans la chaîne
    // (le parent /admin arrive avant l'enfant dans to.matched), donc un
    // meta.role posé sur une route enfant (ex: 'professeurs') se faisait
    // silencieusement écraser par celui, plus large, du parent /admin.
    const roleGuards = to.matched.filter(r => r.meta?.role)
    const passesRoleGuards = roleGuards.every(r => {
      const roles = Array.isArray(r.meta.role) ? r.meta.role : [r.meta.role]
      return roles.some(role => authStore.roleNames.includes(role))
    })

    if (roleGuards.length && isAuthenticated && !passesRoleGuards) {
      return next(homeRoute(authStore))
    }

    // Bloquer les utilisateurs avec seulement le rôle 'user' d'accéder aux routes autres que Profile
    const userRoles = authStore.roleNames ?? []
    const isBaseUser = userRoles.length === 1 && userRoles.includes('user')

    if (isBaseUser && to.path.startsWith('/admin') && to.name !== 'Profile') {
      return next({ name: 'Profile' })
    }

    // Respecter accessible_tabs : bloquer la navigation directe par URL
    const ROUTE_TAB_ID = {
      'Dashboard':       'home',
      'Administration':  'admin',
      'Étudiants':       'etudiant',
      'student-add':     'etudiant',
      'student-view':    'etudiant',
      'student-edit':    'etudiant',
      'Professeurs':     'prof',
      'Notes':           'notes',
      'add-notes':       'notes',
      'Cours':           'cours',
      'add-cours':       'cours',
      'add-programme':   'cours',
      'Paiements':       'paiement',
      'add-paiement':    'paiement',
      'paiement-detail': 'paiement',
      'Trésorerie':      'vente',
      'Présences':       'presences',
      'Rapport':         'rapport',
      'Paramètres':      'settings',
      'Communauté':      'communaute',
      'Abonnement':      'abonnement',
    }
    if (isAuthenticated && to.name !== 'Profile') {
      const tabs = authStore.user?.tab_ids ?? null
      if (tabs !== null) {
        const tabId = ROUTE_TAB_ID[to.name]
        if (tabId && !tabs.includes(tabId)) {
          return next({ name: 'Profile' })
        }
      }
    }

    next()
  })

  router.afterEach(() => {
    // Titre/description/canonical par page : gérés par usePageMeta.js
    // (useHead() dérivé directement de la route courante), plus par
    // manipulation de `document` ici — voir ce fichier pour le pourquoi.
    if (!import.meta.env.SSR) isGlobalLoading.value = false
  })
}

function homeRoute(authStore) {
  const roles = authStore.roleNames ?? []

  // Utilisateur avec seulement le rôle 'user' → Profile uniquement
  if (roles.length === 1 && roles.includes('user')) {
    return { name: 'Profile' }
  }

  // Utilisateurs avec rôles métier
  if (roles.includes('admin')) {
    return { name: 'Dashboard' }
  } else if (roles.includes('teacher')) {
    return { name: 'teacher.dashboard' }
  } else if (roles.includes('student')) {
    return { name: 'etudiant.dashboard' }
  } else if (roles.some(r => ['Caissier', 'Responsable financier', 'Responsable des admissions', 'Responsable pédagogique', 'Comptable'].includes(r))) {
    return { name: 'Dashboard' }
  }

  // Rôle inconnu → logout
  localStorage.removeItem('auth-token')
  return { name: 'login' }
}

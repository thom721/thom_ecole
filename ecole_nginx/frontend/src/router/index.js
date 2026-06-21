import { createRouter, createWebHistory } from 'vue-router'
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
const FormationsView = () => import('../views/public/FormationsView.vue')
const AdmissionView  = () => import('../views/public/AdmissionView.vue')
const EvenementsView = () => import('../views/public/EvenementsView.vue')
const AProposView    = () => import('../views/public/AProposView.vue')
const ContactView    = () => import('../views/public/ContactView.vue')
const ConnexionView  = () => import('../views/public/ConnexionView.vue')
const appName = import.meta.env.VITE_APP_NAME
const routes = [

  {
    path: '/',
    component: () => import('../layouts/PublicLayout.vue'),
    children: [
    {
    path: '/',
    name: 'accueil',
    component: HomeView,
    meta: { title: `Accueil-${appName}` },
    },
  {
    path: '/formations',
    name: 'formations',
    component: FormationsView,
    meta: { title: `Formations-${appName}` },
  },
  {
    path: '/admission',
    name: 'admission',
    component: AdmissionView,
    meta: { title: `Admission-${appName}` },
  },
  {
    path: '/evenements',
    name: 'evenements',
    component: EvenementsView,
    meta: { title: `Événements-${appName}` },
  },
  {
    path: '/a-propos',
    name: 'apropos',
    component: AProposView,
    meta: { title: `À Propos-${appName}` },
  },
  {
    path: '/contact',
    name: 'contact',
    component: ContactView,
    meta: { title: `Contact-${appName}` },
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
      { path: 'professeurs',        name: 'Professeurs',   component: () => import('../views/admin/Professeur.vue')   },
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

  /* ────────────────────────────────────────────────
     404
  ──────────────────────────────────────────────── */
  // {
  //   path: '/:catchAll(.*)',
  //   name: 'not-found',
  //   // component: () => import('../views/public/NotFound.vue'),
  //   redirect: { name: 'login' },
  // },

  { path: '/:pathMatch(.*)*', name: 'login', component: ConnexionView }
  // ]
//   {
//   path: '/:pathMatch(.*)*',
//   name: 'not-found',
//   redirect: { name: 'login' }
//   // component: () => import('../views/public/NotFound.vue')
// }
//  {
//       path: '/connexion',
//       redirect: (route) => ({ name: 'login', params: { pathMatch: route.path.substring(1).split('/') } }) // route is the param here
//     }
]

/* ══════════════════════════════════════════════════════════════════
   CRÉATION DU ROUTER
══════════════════════════════════════════════════════════════════ */
const router = createRouter({
  history: createWebHistory(),
  routes,
  // scrollBehavior: (to, from, saved) => saved ?? { top: 0 },

    scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) return savedPosition          // Bouton Précédent du navigateur
    return { top: 0, behavior: 'smooth' }
  },
})

// router.push({ name: 'login', params: { pathMatch: route.path.substring(1).split('/') } })
router.beforeEach(async (to, from, next) => {
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

  const routeRole = to.matched.find(r => r.meta?.role)?.meta.role
const roles = Array.isArray(routeRole) ? routeRole : [routeRole]

if (routeRole && isAuthenticated && !roles.some(r => authStore.roleNames.includes(r))) {
  return next(homeRoute(authStore))
}

  // Bloquer les utilisateurs avec seulement le rôle 'user' d'accéder aux routes autres que Profile
  const userRoles = authStore.roleNames ?? []
  const isBaseUser = userRoles.length === 1 && userRoles.includes('user')

  if (isBaseUser && to.path.startsWith('/admin') && to.name !== 'Profile') {
    return next({ name: 'Profile' })
  }

  next()
})


router.afterEach((to) => {
  isGlobalLoading.value = false
  document.title = to.meta?.title ?? `${appName}`
})
 
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

export default router

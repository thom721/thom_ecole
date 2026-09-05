import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ref } from 'vue'
import { useSchoolStoreInfo } from '../stores/schoolStore'
// import AuthLayout     from '../layouts/AuthLayout.vue' 

export const isGlobalLoading = ref(false)

// import Login          from '@/views/auth/Login.vue'
import ResetPassword  from '../views/auth/Resetpassword.vue'

const HomeView       = () => import('../views/public/HomeView.vue')
const FormationsView = () => import('../views/public/FormationsView.vue')
const AdmissionView  = () => import('../views/public/AdmissionView.vue')
const EvenementsView = () => import('../views/public/EvenementsView.vue')
const AProposView    = () => import('../views/public/AProposView.vue')
const ContactView    = () => import('../views/public/ContactView.vue')
const ConnexionView  = () => import('../views/public/ConnexionView.vue')

/* ══════════════════════════════════════════════════════════════════
   ROUTES
   ─────
   /          → PublicLayout   (accueil, login, etc.)
   /admin     → AdminLayout    (préfixe visible)
   /teacher   → TeacherLayout  (préfixe visible)
   /student   → StudentLayout  (préfixe CACHÉ via alias: '/')
                └─ /student/dashboard ET /dashboard → même page
══════════════════════════════════════════════════════════════════ */

const routes = [

  // {
  //   path: '/',
  //   component: AuthLayout,
  //   children: [
  //     { path: 'login',          name: 'Login',         component: Login         }
  //     // { path: 'reset-password', name: 'ResetPassword', component: ResetPassword },
  //     // {
  //     //   path: 'reset-password/first',
  //     //   name: 'FirstLogin',
  //     //   component: ResetPassword,
  //     //   meta: { firstLogin: true }
  //     // },
  //   ]
  // },

  /* ────────────────────────────────────────────────
     PUBLIC
  ──────────────────────────────────────────────── */
  // {
  //   path: '/',
  //   component: () => import('../layouts/PublicLayout.vue'),
  //   children: [
  //     { path: '',          name: 'accueil',   component: () => import('../views/public/Accueil.vue')   },
  //     { path: 'admission', name: 'admission', component: () => import('../views/public/Admission.vue') },
  //     { path: 'about',     name: 'about',     component: () => import('../views/public/About.vue')     },
  //     { path: 'contact',   name: 'contact',   component: () => import('../views/public/Contact.vue')   },
  //     { path: 'formation', name: 'formation', component: () => import('../views/public/Formation.vue') },
  //     { path: 'evenement', name: 'evenement', component: () => import('../views/public/Evenement.vue') },
  //     { path: 'login',     name: 'login',     component: () => import('../views/auth/Login.vue')  ,meta: { hideNav: true }     }, 
  //     { path: '/reset-password', name: 'ResetPassword', component: ResetPassword, meta: { hideNav: true } }, 
  //   ],
  // },

  {
    path: '/',
    component: () => import('../layouts/PublicLayout.vue'),
    children: [
    {
    path: '/',
    name: 'accueil',
    component: HomeView,
    meta: { title: 'Accueil — EduSphere' },
    },
  {
    path: '/formations',
    name: 'formations',
    component: FormationsView,
    meta: { title: 'Formations — EduSphere' },
  },
  {
    path: '/admission',
    name: 'admission',
    component: AdmissionView,
    meta: { title: 'Admission — EduSphere' },
  },
  {
    path: '/evenements',
    name: 'evenements',
    component: EvenementsView,
    meta: { title: 'Événements — EduSphere' },
  },
  {
    path: '/a-propos',
    name: 'apropos',
    component: AProposView,
    meta: { title: 'À Propos — EduSphere' },
  },
  {
    path: '/contact',
    name: 'contact',
    component: ContactView,
    meta: { title: 'Contact — EduSphere' },
  },
  {
    path: '/login',
    name: 'login',
    component: ConnexionView,
    meta: {
      title: 'Connexion — EduSphere', 
      hideShell: true,
    },    
  },

    {
    path: '/forgot-password',
    name: 'resetpassword',
    component: ResetPassword,
    meta: {
      title: 'Connexion — EduSphere', 
      hideShell: true,
    },
    },
  // Catch-all : toute URL inconnue redirige vers l'accueil
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  }
]
  },

  /* ────────────────────────────────────────────────
     ADMIN  (/admin/...)
  ──────────────────────────────────────────────── */
  {
    path: '/admin',
    alias: '/', 
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: '', redirect: { name: 'Dashboard' } },

      { path: 'dashboard',      name: 'Dashboard',       component: () => import('../views/admin/Dashboard.vue')       },
      { path: 'administration', name: 'Administration',  component: () => import('../views/admin/Administration.vue')  },

      // Étudiants
      { path: 'etudiants',                     name: 'Étudiants',    component: () => import('../views/admin/Etudiants.vue'),       },
      { path: 'etudiants/ajouter',             name: 'student-add',  component: () => import('../views/admin/Ajout_etudiant.vue'),  props: true },
      { path: 'etudiants/voir/:etudiantId',    name: 'student-view', component: () => import('../views/admin/Ajout_etudiant.vue'),  props: true },
      { path: 'etudiants/modifier/:etudiantId',name: 'student-edit', component: () => import('../views/admin/Ajout_etudiant.vue'),  props: true },

      // Paiements
      { path: 'paiements',             name: 'Paiements',    component: () => import('../views/admin/Paiements.vue'),    },
      { path: 'paiement/:etudiantId',  name: 'add-paiement', component: () => import('../views/admin/AddPaiement.vue'),  props: true },

      // Autres
      { path: 'profile',            name: 'Profile',       component: () => import('../views/admin/adProfile.vue')    },
      { path: 'professeurs',        name: 'Professeurs',   component: () => import('../views/admin/Professeur.vue')   },
      { path: 'notes',              name: 'Notes',         component: () => import('../views/admin/Notes.vue')        },
      { path: 'cours',              name: 'Cours',         component: () => import('../views/admin/Cours.vue')        },
      { path: 'parametres',         name: 'Paramètres',    component: () => import('../views/admin/Parametres.vue')   },
      { path: 'rapport',            name: 'Rapport',       component: () => import('../views/admin/Rapport.vue')      },
      { path: 'ajouter-cours',      name: 'add-cours',     component: () => import('../views/admin/AddCours.vue')     },
      { path: 'ajouter-programme',  name: 'add-programme', component: () => import('../views/admin/AddProgramme.vue') },
      { path: 'ajouter-notes',      name: 'add-notes',     component: () => import('../views/admin/NoteForm.vue')     },
    ],
  },

  /* ────────────────────────────────────────────────
     TEACHER  (/teacher/...)
     Bug corrigé : '/ajouter-notes' (absolu) → 'ajouter-notes' (relatif)
  ──────────────────────────────────────────────── */
  {
    path: '/teacher',
    alias:'/',
    component: () => import('../layouts/TeacherLayout.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
    children: [
      { path: '', redirect: { name: 'teacher.dashboard' } },

      { path: 'dashboard',     name: 'teacher.dashboard',  component: () => import('../views/Teacher/Dashboard.vue') },
      { path: 'cours',         name: 'teacher.cours',      component: () => import('../views/Teacher/Cours.vue')     },
      { path: 'notes',         name: 'teacher.notes',      component: () => import('../views/Teacher/Notes.vue')     },
      { path: 'ajouter-notes', name: 'teacher.add-notes',  component: () => import('../views/Teacher/NoteForm.vue')  },
      { path: 'profile',       name: 'teacher.profile',    component: () => import('../views/Teacher/Profile.vue')   },
    ],
  },

  /* ────────────────────────────────────────────────
     STUDENT — PREFIX /student CACHÉ
     ──────────────────────────────────────────────
     Technique : alias: '/'  sur le parent
                 alias: '/xxx' sur chaque enfant

     Résultat dans le navigateur :
       router.push({ name: 'etudiant.dashboard' })
         → URL affichée : /dashboard   (ou /student/dashboard si l'user a tapé ça)
       Les deux URLs fonctionnent, le navigateur garde ce qu'il connaît.

     ⚠️  Si vous voulez FORCER l'URL courte :
         router.replace('/dashboard')   après la navigation
  ──────────────────────────────────────────────── */
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
  {
    path: '/:catchAll(.*)',
    name: 'not-found',
    // component: () => import('../views/public/NotFound.vue'),
    redirect: { name: 'login' },
  },
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

/* ══════════════════════════════════════════════════════════════════
   GUARD GLOBAL
   ────────────
   1. Charge les dépendances école (inchangé)
   2. Initialise l'auth depuis le token (inchangé)
   3. Route protégée sans auth → login
   4. Login avec auth → bon espace selon le rôle
   5. Mauvais espace selon le rôle → redirection correcte
══════════════════════════════════════════════════════════════════ */
router.beforeEach(async (to, from, next) => {
  isGlobalLoading.value = true
  console.log(`to ${to} from ${from} next ${next}`);
  
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

  // déjà connecté → pas besoin du login
  if (to.name === 'login' && isAuthenticated) {
    return next(homeRoute(authStore))
  }

  // mauvais espace selon le rôle
  const routeRole = to.matched.find(r => r.meta?.role)?.meta.role
  if (routeRole && isAuthenticated && !authStore.roleNames.includes(routeRole)) {
    return next(homeRoute(authStore))
  }

  next()
})


router.afterEach((to) => {
  isGlobalLoading.value = false
  document.title = to.meta?.title ?? 'Lekol360'
})
// router.afterEach(() => {
//   isGlobalLoading.value = false
// })

/* ══════════════════════════════════════════════════════════════════
   HELPER — route d'accueil selon le rôle
══════════════════════════════════════════════════════════════════ */
function homeRoute(authStore) {
  const roles = authStore.roleNames ?? []
  
  console.log(roles,roles.includes('teacher'));
  
  if (roles.includes('admin')) {
      return { name: 'Dashboard'  }    
    }else if (roles.includes('teacher')) {
    console.log(roles);
    return { name: 'teacher.dashboard'  }
  }else if (roles.includes('student')){ 
    return { name: 'etudiant.dashboard' }
  }
  // rôle inconnu → logout
  localStorage.removeItem('auth-token')
  return { name: 'login' }
}

export default router

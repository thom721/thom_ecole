import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ref } from 'vue';
import { useSchoolStoreInfo } from '@/stores/schoolStore'

export const isGlobalLoading = ref(false);

const routes = [
  {
    path: '/',
    component: () => import('../layouts/PublicLayout.vue'),
    children: [
      { path: '', name: 'accueil', component: () => import('@/views/public/Accueil.vue') },
      { path: 'admission', name: 'admission', component: () => import('@/views/public/Admission.vue') },
      { path: 'about', name: 'about', component: () => import('@/views/public/About.vue') },
      { path: 'contact', name: 'contact', component: () => import('@/views/public/Contact.vue') },
      { path: 'formation', name: 'formation', component: () => import('@/views/public/Formation.vue') },
      { path: 'evenement', name: 'evenement', component: () => import('@/views/public/Evenement.vue') },
      { path: 'login', name: 'login', component: () => import('@/views/auth/Login.vue') },
      
    ]
  },
 

  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [

  { path: '/admin/dashboard',name: 'Dashboard',  icon: 'fas fa-tachometer-alt', component: () => import('@/views/admin/Dashboard.vue') },

  { path: '/admin/administration',name: 'Administration', icon: 'fas fa-user-shield', component: () => import('@/views/admin/Administration.vue') },

  {  path: '/admin/etudiants/ajouter', component: () => import('@/views/admin/Ajout_etudiant.vue'), name: 'add-student', props: true  },
  
  {  path: '/admin/etudiants/voir/:etudiantId', component: () => import('@/views/admin/Ajout_etudiant.vue'), name: 'add-student', props: true  },
  {  path: '/admin/etudiants/modifier/:etudiantId', component: () => import('@/views/admin/Ajout_etudiant.vue'), name: 'add-student', props: true  },
  { path: '/admin/etudiants',  name: 'Étudiants', icon: 'fas fa-user-graduate', component: () => import('@/views/admin/Etudiants.vue') },


  { path: '/admin/professeurs',  name: 'Professeurs',icon: 'fas fa-chalkboard-teacher', component: () => import('@/views/admin/Professeur.vue') },
  { path: '/admin/notes', name: 'Notes', icon: 'fas fa-file-signature', component: () => import('@/views/admin/Notes.vue') },
  { path: '/admin/cours', name: 'Cours', icon: 'fas fa-book', component: () => import('@/views/admin/Cours.vue') },
  {  path: '/admin/paiements',name: 'Paiements', icon: 'fas fa-money-bill-wave', component: () => import('@/views/admin/Paiements.vue') },
  {  path: '/admin/paiement/:etudiantId', component: () => import('@/views/admin/AddPaiement.vue'), name: 'add-paiement', props: true  },
  
  {  path: '/admin/parametres',name: 'Paramètres', icon: 'fas fa-gears', component: () => import('@/views/admin/Parametres.vue') },

   {  path: '/admin/rapport',name: 'Rapport', icon: 'fas fa-gears', component: () => import('@/views/admin/Rapport.vue') },
 
  { path: '/admin/ajouter-cours', name: 'add-cours', icon: 'fas fa-book', component: () => import('@/views/admin/AddCours.vue') },
  { path: '/admin/ajouter-programme', name: 'add-programme', icon: 'fas fa-book', component: () => import('@/views/admin/AddProgramme.vue') },
  { path: '/admin/ajouter-notes', name: 'add-notes', icon: 'fas fa-book', component: () => import('@/views/admin/NoteForm.vue') },
   
    ]
  },
    {
    path: '/teacher',
    // component: TeacherLayout,
    component: () => import('@/layouts/TeacherLayout.vue'),
    meta: { requiresAuth: true },      
      children: [
        { path: 'dashboard',name:"teacher.dashboard", component: () => import('@/views/Teacher/Dashboard.vue') },
        { path: 'cours',name:"teacher.cours", component: () => import('@/views/Teacher/Cours.vue') },
        { path: 'notes',name:"teacher.notes", component: () => import('@/views/Teacher/Notes.vue') },
        { path: '/ajouter-notes', name: 'teacher.add-notes', icon: 'fas fa-book', component: () => import('@/views/Teacher/NoteForm.vue') },
        { path: 'profile',name:"teacher.profile", component: () => import('@/views/Teacher/Profile.vue') },
      ]
    }  
 
]



const router = createRouter({
  history: createWebHistory(),
  routes
})


router.beforeEach(async (to, from, next) => {
  isGlobalLoading.value = true;
  const schoolStore = useSchoolStoreInfo()
  const authStore = useAuthStore();
  const token = localStorage.getItem('auth-token');
 schoolStore.fetchAllDependencies()
  if (token && !authStore.user) {
    try { 
      await authStore.initializeAuth();
    } catch (error) { 
      localStorage.removeItem('auth-token');
      return next({ name: 'login' });
    }
  }
 
  const isAuthenticated = !!authStore.user;

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'login' });
  }
 
  if (to.name === 'login' && isAuthenticated) {
    return next(authStore.roleNames.includes('teacher') ? '/teacher/dashboard' : '/admin/dashboard');
  }

  next();
});

// router.beforeEach(async (to, from, next) => {
//   const authStore = useAuthStore();
//   isGlobalLoading.value = true;
  
//   if (!authStore.user && localStorage.getItem('auth-token')) {
//     await authStore.initializeAuth();
//   }

//   const isAuthenticated = !!authStore.user;
 
//   if (to.path.startsWith('/teacher')) {
//     if (!isAuthenticated) {
//       return next({ name: 'login' });
//     }
     
//     const isTeacher = authStore.roleNames.includes('teacher');
//     if (!isTeacher) { 
//       return next({ name: 'teacher.dashboard' }); // Ou une page 403
//     }
//   }else if (to.path.startsWith('/admin')) {
//     if (!isAuthenticated) {
//       return next({ name: 'login' });
//     }
     
//     const isTeacher = authStore.roleNames.includes('admin');
//     if (!isTeacher) { 
//       return next({ name: 'Dashboard' }); // Ou une page 403
//     }
//   }

//   next();
// });

// router.beforeEach(async (to, from, next) => {
//   const authStore = useAuthStore();
//   const isAuthenticated = !!localStorage.getItem('auth-token');

//   // 1. Éviter la boucle sur la page Login
//   if (to.name === 'login') {
//     if (isAuthenticated) {
//       // Si déjà connecté, on l'envoie vers son espace au lieu du login
//       return next(authStore.isTeacher ? '/teacher/dashboard' : '/admin/dashboard');
//     }
//     return next(); // Libre accès au login
//   }

//   // 2. Vérification globale
//   if (to.meta.requiresAuth && !isAuthenticated) {
//     return next({ name: 'login' });
//   }

//   // 3. Vérification des rôles (C'est ici que ça boucle souvent !)
//   if (to.path.startsWith('/admin') && !authStore.isAdmin) {
//     // Si l'utilisateur n'est pas admin, NE LE RENVOIE PAS vers login s'il est déjà connecté
//     // Envoie-le plutôt vers sa propre page d'accueil (Teacher)
//     return next({ name: 'teacher.dashboard' });
//   }

//   next(); // Dans tous les autres cas, on laisse passer
// });

router.afterEach(() => { 
  isGlobalLoading.value = false;
});

export default router
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ref } from 'vue';
import { useSchoolStoreInfo } from '../stores/schoolStore'

export const isGlobalLoading = ref(false);

const routes = [
  {
    path: '/',
    component: () => import('../layouts/PublicLayout.vue'),
    children: [
      { path: '', name: 'accueil', component: () => import('../views/public/Accueil.vue') },
      { path: 'admission', name: 'admission', component: () => import('../views/public/Admission.vue') },
      { path: 'about', name: 'about', component: () => import('../views/public/About.vue') },
      { path: 'contact', name: 'contact', component: () => import('../views/public/Contact.vue') },
      { path: 'formation', name: 'formation', component: () => import('../views/public/Formation.vue') },
      { path: 'evenement', name: 'evenement', component: () => import('../views/public/Evenement.vue') },
      { path: 'login', name: 'login', component: () => import('../views/auth/Login.vue') },
      
    ]
  },
 

  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
  { path: 'dashboard', name: 'Dashboard', component: () => import('../views/admin/Dashboard.vue') },
  { path: 'administration', name: 'Administration', component: () => import('../views/admin/Administration.vue') },
  
  // ROUTES ÉTUDIANTS (Noms uniques !)
  { path: 'etudiants', name: 'Étudiants', component: () => import('../views/admin/Etudiants.vue') },
  { path: 'etudiants/ajouter', name: 'student-add', component: () => import('../views/admin/Ajout_etudiant.vue'), props: true },
  { path: 'etudiants/voir/:etudiantId', name: 'student-view', component: () => import('../views/admin/Ajout_etudiant.vue'), props: true },
  { path: 'etudiants/modifier/:etudiantId', name: 'student-edit', component: () => import('../views/admin/Ajout_etudiant.vue'), props: true },
  
  // PAIEMENTS
  { path: 'paiements', name: 'Paiements', component: () => import('../views/admin/Paiements.vue') },
  { path: 'profile', name: 'Profile', component: () => import('../views/admin/adProfile.vue') },
  { path: 'paiement/:etudiantId', name: 'add-paiement', component: () => import('../views/admin/AddPaiement.vue'), props: true },


  { path: 'professeurs',  name: 'Professeurs',icon: 'fas fa-chalkboard-teacher', component: () => import('../views/admin/Professeur.vue') },
  { path: 'notes', name: 'Notes', icon: 'fas fa-file-signature', component: () => import('../views/admin/Notes.vue') },
  { path: 'cours', name: 'Cours', icon: 'fas fa-book', component: () => import('../views/admin/Cours.vue') },
 
  
  {  path: 'parametres',name: 'Paramètres', icon: 'fas fa-gears', component: () => import('../views/admin/Parametres.vue') },

   {  path: 'rapport',name: 'Rapport', icon: 'fas fa-gears', component: () => import('../views/admin/Rapport.vue') },
 
  { path: 'ajouter-cours', name: 'add-cours', icon: 'fas fa-book', component: () => import('../views/admin/AddCours.vue') },
  { path: 'ajouter-programme', name: 'add-programme', icon: 'fas fa-book', component: () => import('../views/admin/AddProgramme.vue') },
  { path: 'ajouter-notes', name: 'add-notes', icon: 'fas fa-book', component: () => import('../views/admin/NoteForm.vue') },
   
    ]
  },
    {
    path: '/teacher',
    // component: TeacherLayout,
    component: () => import('../layouts/TeacherLayout.vue'),
    meta: { requiresAuth: true },      
      children: [
        { path: 'dashboard',name:"teacher.dashboard", component: () => import('../views/Teacher/Dashboard.vue') },
        { path: 'cours',name:"teacher.cours", component: () => import('../views/Teacher/Cours.vue') },
        { path: 'notes',name:"teacher.notes", component: () => import('../views/Teacher/Notes.vue') },
        { path: '/ajouter-notes', name: 'teacher.add-notes', icon: 'fas fa-book', component: () => import('../views/Teacher/NoteForm.vue') },
        { path: 'profile',name:"teacher.profile", component: () => import('../views/Teacher/Profile.vue') },
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
// if (schoolStore.dependencies.length === 0) {
//     schoolStore.fetchAllDependencies();
// }
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


router.afterEach(() => { 
  isGlobalLoading.value = false;
});

export default router
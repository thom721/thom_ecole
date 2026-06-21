import { createRouter, createWebHistory } from 'vue-router'

import HomeView      from '@/views/HomeView.vue'
import StoreView     from '@/views/StoreView.vue'
import AboutView     from '@/views/AboutView.vue'
import ContactView   from '@/views/ContactView.vue'
import PrivacyView   from '@/views/PrivacyView.vue'
import TermsView     from '@/views/TermsView.vue'
import NotFoundView  from '@/views/NotFoundView.vue'

const routes = [
  { path: '/',        name: 'home',      component: HomeView     },
  { path: '/store',   name: 'store',     component: StoreView    },
  { path: '/about',   name: 'about',     component: AboutView    },
  { path: '/contact', name: 'contact',   component: ContactView  },
  { path: '/privacy', name: 'privacy',   component: PrivacyView  },
  { path: '/terms',   name: 'terms',     component: TermsView    },
  { path: '/admin',   name: 'admin',     component: () => import('@/views/AdminView.vue') },
  { path: '/renouveler', name: 'renouveler', component: () => import('@/views/RenouvellerView.vue') },
  { path: '/:pathMatch(.*)*', name: '404', component: NotFoundView },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() { return { top: 0, behavior: 'smooth' } }
})

export default router

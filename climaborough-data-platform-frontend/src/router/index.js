import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { authService } from '../services/authService'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/bot',
      name: 'bot',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/LLMAgent.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/projects',
      name: 'projects',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/Projects.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/Dashboard/:city',
      name: 'Dashboard',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/datacatalogue',
      name: 'datacatalogue',
      component: () => import('../views/DataCatalogue.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/tos',
      name: 'tos',
      // route level code-splitting
      component: () => import('../views/TOS.vue')
    },
    {
      path: '/demo',
      name: 'demo',
      component: () => import('../views/DemoDashboard.vue')
    },
    {
      path: '/callback',
      name: 'Callback',
      component: () => import('../components/Callback.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue')
    },
  ]
})

// Navigation guard - COMMENTED OUT to allow popup authentication on page
// router.beforeEach((to, from, next) => {
//   const isAuthenticated = authService.isAuthenticated();
  
//   if (to.meta.requiresAuth && !isAuthenticated) {
//     // Store the intended destination
//     sessionStorage.setItem('postLoginRedirect', to.fullPath);
//     // Redirect to home page, which will show the login prompt
//     next('/');
//   } else {
//     next();
//   }
// });

export default router

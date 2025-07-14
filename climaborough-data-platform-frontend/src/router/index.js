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
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue')
    },
  ]
})

// Navigation guard for protected routes
router.beforeEach(async (to, from, next) => {
  const isAuthenticated = authService.isAuthenticated();
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Store the intended destination
    sessionStorage.setItem('postLoginRedirect', to.fullPath);
    // Redirect to login page
    next('/login');
  } else {
    next();
  }
});

// Handle successful authentication after page loads
router.afterEach((to, from) => {
  // Check if this is a successful login redirect
  if (authService.isAuthenticated() && to.path !== '/login') {
    // Emit login success event for components to react to
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('keycloak-login-success'));
    }, 100);
  }
});

export default router

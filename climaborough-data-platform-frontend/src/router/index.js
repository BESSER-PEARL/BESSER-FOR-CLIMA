import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

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
      component: () => import('../views/LLMAgent.vue')
    },
    {
      path: '/projects',
      name: 'projects',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/Projects.vue')
    },
    {
      path: '/Dashboard/:city',
      name: 'Dashboard',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/Dashboard.vue')
    },
    {
      path: '/tos',
      name: 'tos',
      // route level code-splitting
      component: () => import('../views/TOS.vue')
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminDashboard,
      beforeEnter: (to, from, next) => {
        const userType = localStorage.getItem('userType');
        if (userType === 'admin') {
          next();
        } else {
          next('/');
        }
      }
    }
  ]
})

export default router

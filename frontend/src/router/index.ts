import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { authService } from '../services/auth.service';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'landing',
    component: () => import('../views/Landing.vue'),
  },
  {
    path: '/auth/login',
    name: 'login',
    component: () => import('../views/auth/Login.vue'),
  },
  {
    path: '/auth/register',
    name: 'register',
    component: () => import('../views/auth/Register.vue'),
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/dashboard/Dashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/projects/:id',
    name: 'project',
    component: () => import('../views/dashboard/Project.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/timer/:sessionId',
    name: 'timer',
    component: () => import('../views/timer/Timer.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/profile/Profile.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/stats',
    name: 'stats',
    component: () => import('../views/stats/Stats.vue'),
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Track if we've checked auth on app start
let authChecked = false;

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();
  
  // Check auth on first navigation if token exists and not already checked
  if (!authChecked) {
    authChecked = true;
    const token = authService.getToken();
    if (token) {
      // Only fetch if we have a token
      await authStore.fetchCurrentUser();
    }
  }
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' });
  } else if ((to.name === 'login' || to.name === 'register') && authStore.isAuthenticated) {
    next({ name: 'dashboard' });
  } else {
    next();
  }
});

export default router;

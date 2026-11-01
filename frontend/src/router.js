import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    path: '/checklists/:name?',
    name: 'Checklists',
    component: () => import('@/pages/Checklists.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/planner'),
  routes,
})

export default router

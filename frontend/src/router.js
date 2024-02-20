import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    path: '/planner',
    name: "Planner",
    component:  () => import('@/pages/Planner.vue'),
  },
  {
    path: '/project',
    name: "Project",
    component:  () => import('@/pages/Project.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/planner'),
  routes,
})

export default router

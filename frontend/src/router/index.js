import { createRouter, createWebHistory } from "vue-router";
import { session } from '../data/session'
import { users } from '../data/users'
import { getScrollContainer, scrollTo } from '../utils/scrollContainer'

const Planner = () => import("@/pages/Planner.vue");
const Dashboard = () => import("@/pages/Dashboard.vue");

const routes = [
  {
    path: "/",
    name: "Dashboard",
    component: () => import("@/pages/Dashboard.vue"),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: "/planner/:dashboardName/:department",
    name: "Planner",
    component: () => import("@/pages/Planner.vue"),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/pages/Login.vue"),
  },
];

const router = createRouter({
  history: createWebHistory('/frontend'),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return {
      top: 0,
      behavior: 'instant'
    }
  },
});

let scrollPositions = {}
function saveAndRestoreScrollPosition(to, from) {
  let scrollContainer = getScrollContainer()
  if (scrollContainer) {
    scrollPositions[from.path] = scrollContainer.scrollTop
  }
  if (scrollPositions[to.path] !== undefined && to.path !== from.path) {
    setTimeout(() => {
      scrollTo({ top: scrollPositions[to.path] })
    }, 0)
  }
}

router.beforeEach(async (to, from, next) => {

  saveAndRestoreScrollPosition(to, from)

  let isLoggedIn = session.isLoggedIn
  console.log("isloggedin", isLoggedIn)
  try {
    await users.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Dashboard' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else {
    next()
  }
})


export default router;

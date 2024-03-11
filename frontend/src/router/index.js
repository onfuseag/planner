import { createRouter, createWebHistory } from "vue-router";

const Montageansicht = () => import("@/pages/Montageansicht.vue");
const SignIn = () => import("@/pages/SignIn.vue");
const Dashboard = () => import("@/pages/Dashboard.vue");

// import { AuthStore } from "@/stores/AuthStore"

const routes = [
  // {
  //   path: "/:pathMatch(.*)*",
  //   redirect: '/login'
  // },
  {
    path: "/",
    name: "Dashboard",
    component: Dashboard,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: "/montageansicht",
    name: "Montageansicht",
    component: Montageansicht,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: "/signin",
    name: "SignIn",
    component: SignIn,
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

router.beforeEach(async (to, from, next) => {
  next();
});


export default router;

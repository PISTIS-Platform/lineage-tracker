import { createRouter, createWebHistory } from 'vue-router'
import LineageView from '../views/LineageView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/:id',
      name: 'home',
      component: LineageView
    }
  ]
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../components/HomePage.vue'
import AStarAlgorithm from '../components/AStarAlgorithm.vue'

const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: HomePage
  },
  {
    path: '/astar',
    name: 'astar',
    component: AStarAlgorithm
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
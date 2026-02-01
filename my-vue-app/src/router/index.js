import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../components/HomePage.vue'
import AStarAlgorithm from '../components/AStarAlgorithm.vue'
import GeneticAlgorithm from '../components/GeneticAlgorithm.vue'
import MixedIntegerAlgorithm from '../components/MixedIntegerAlgorithm.vue'

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
  },
  {
    path: '/genetic',
    name: 'genetic',
    component: GeneticAlgorithm
  },
  {
    path: '/mixed-integer',
    name: 'mixed-integer',
    component: MixedIntegerAlgorithm
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
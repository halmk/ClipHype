import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import NotFoundView from '../views/NotFoundView.vue'
import ChStreamerView from '../views/ChStreamerView.vue'
import ChArchiveView from '../views/ChArchiveView.vue'
import ChClipView from '../views/ChClipView.vue'
import ChHighlightView from '../views/ChHighlightView.vue'
import ChVideoView from '../views/ChVideoView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/streamer/:id',
    component: ChStreamerView,
    children: [
      {
        path: 'archives',
        component: ChArchiveView
      },
      {
        path: 'clips',
        component: ChClipView
      },
      {
        path: 'highlights',
        component: ChHighlightView
      },
      {
        path: 'videos',
        component: ChVideoView
      }
    ]
  },
  {
    path: '/*',
    component: NotFoundView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router

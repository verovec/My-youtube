import Vue from 'vue'
import Router from 'vue-router'
import { interopDefault } from './utils'
import scrollBehavior from './router.scrollBehavior.js'

const _72270b1d = () => interopDefault(import('../pages/dashboard/index.vue' /* webpackChunkName: "pages/dashboard/index" */))
const _a4dff4fe = () => interopDefault(import('../pages/video.vue' /* webpackChunkName: "pages/video" */))
const _8e1272a8 = () => interopDefault(import('../pages/auth/login.vue' /* webpackChunkName: "pages/auth/login" */))
const _33eac2b0 = () => interopDefault(import('../pages/auth/register.vue' /* webpackChunkName: "pages/auth/register" */))
const _cb55f474 = () => interopDefault(import('../pages/dashboard/upload.vue' /* webpackChunkName: "pages/dashboard/upload" */))
const _2dfb1658 = () => interopDefault(import('../pages/index.vue' /* webpackChunkName: "pages/index" */))

// TODO: remove in Nuxt 3
const emptyFn = () => {}
const originalPush = Router.prototype.push
Router.prototype.push = function push (location, onComplete = emptyFn, onAbort) {
  return originalPush.call(this, location, onComplete, onAbort)
}

Vue.use(Router)

export const routerOptions = {
  mode: 'history',
  base: decodeURI('/'),
  linkActiveClass: 'nuxt-link-active',
  linkExactActiveClass: 'nuxt-link-exact-active',
  scrollBehavior,

  routes: [{
    path: "/dashboard",
    component: _72270b1d,
    name: "dashboard"
  }, {
    path: "/video",
    component: _a4dff4fe,
    name: "video"
  }, {
    path: "/auth/login",
    component: _8e1272a8,
    name: "auth-login"
  }, {
    path: "/auth/register",
    component: _33eac2b0,
    name: "auth-register"
  }, {
    path: "/dashboard/upload",
    component: _cb55f474,
    name: "dashboard-upload"
  }, {
    path: "/",
    component: _2dfb1658,
    name: "index"
  }],

  fallback: false
}

export function createRouter () {
  return new Router(routerOptions)
}

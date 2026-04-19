import { createRouter, createWebHistory } from "vue-router"

import Login             from "../pages/auth/Login.vue"
import Register          from "../pages/auth/Register.vue"
import Home              from "../pages/customer/Home.vue"
import Products          from "../pages/customer/Products.vue"
import Cart              from "../pages/customer/Cart.vue"
import Orders            from "../pages/customer/Orders.vue"
import OrderTracking     from "../pages/customer/OrderTracking.vue"
import AdminDashboard    from "../pages/admin/Dashboard.vue"
import AdminProducts     from "../pages/admin/Products.vue"
import AdminInventory    from "../pages/admin/Inventory.vue"
import AdminOrders       from "../pages/admin/Orders.vue"
import AdminAnalytics    from "../pages/admin/Analytics.vue"
import AssignedOrders    from "../pages/packers/AssignedOrders.vue"
import PackingPanel      from "../pages/packers/PackingPanel.vue"
import DeliveryDashboard from "../pages/delivery/DeliveryDashboard.vue"
import ProductDetails    from "../pages/customer/ProductDetails.vue"

const routes = [
  { path:"/login",           component:Login,             meta:{ public:true } },
  { path:"/register",        component:Register,          meta:{ public:true } },
  { path:"/",                component:Home,              meta:{ role:"customer" } },
  { path:"/products",        component:Products,          meta:{ role:"customer" } },
  { path:"/cart",            component:Cart,              meta:{ role:"customer" } },
  { path:"/orders",          component:Orders,            meta:{ role:"customer" } },
  { path:"/order/:id",       component:OrderTracking,     meta:{ role:"customer" } },
  { path:"/admin",           component:AdminDashboard,    meta:{ role:"admin" } },
  { path:"/admin/products",  component:AdminProducts,     meta:{ role:"admin" } },
  { path:"/admin/inventory", component:AdminInventory,    meta:{ role:"admin" } },
  { path:"/admin/orders",    component:AdminOrders,       meta:{ role:"admin" } },
  { path:"/admin/analytics", component:AdminAnalytics,    meta:{ role:"admin" } },
  { path:"/packer/orders",   component:AssignedOrders,    meta:{ role:"packer" } },
  { path:"/packing/:id",     component:PackingPanel,      meta:{ role:"packer" } },
  { path:"/delivery",        component:DeliveryDashboard, meta:{ role:"delivery" } },
  {path: "/product/:id",     component:ProductDetails,    meta:{ role:"customer" } }
]

export function getDashboard(role) {
  return { admin:"/admin", packer:"/packer/orders", delivery:"/delivery" }[role] || "/"
}

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, _, next) => {
  const token = localStorage.getItem("token")
  const role  = localStorage.getItem("role")
  if (to.meta.public)  return token ? next(getDashboard(role)) : next()
  if (!token)          return next("/login")
  if (to.meta.role && to.meta.role !== role) return next(getDashboard(role))
  next()
})

export default router

<template>
  <div class="fade-in-up">
    <h5 class="fw-bold mb-4">📦 My Orders</h5>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>
    <div v-else-if="orders.length===0" class="fm-empty-state text-center py-5">
      <div style="font-size:4rem">📦</div>
      <h5 class="mt-3">No orders yet</h5>
      <router-link to="/products" class="btn btn-fm-green px-4 mt-2">Start Shopping</router-link>
    </div>
    <div v-else class="d-flex flex-column gap-3">
      <div class="fm-card p-3 p-md-4" v-for="o in orders" :key="o.id">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <div>
            <span class="fw-bold font-nunito fs-6">#{{ o.id }}</span>
            <span :class="`status-badge status-${o.status} ms-2`">{{ o.status.replace(/_/g,' ') }}</span>
          </div>
          <span class="text-success fw-bold font-nunito fs-5">₹{{ o.total_amount }}</span>
        </div>
        <div class="text-muted small mb-3">Placed {{ formatDate(o.created_at) }}</div>
        <router-link :to="`/order/${o.id}`" class="btn btn-fm-outline btn-sm px-4">
          Track Order →
        </router-link>
      </div>
    </div>
  </div>
</template>
<script>
import { getOrders } from "../../services/orderService.js"
export default {
  data(){ return { orders:[], loading:true } },
  async mounted(){ try{ const r=await getOrders(); this.orders=r.data }finally{ this.loading=false } },
  methods:{ formatDate(d){ return new Date(d).toLocaleDateString("en-IN",{day:"numeric",month:"short",year:"numeric"}) } }
}
</script>
<style scoped>
.font-nunito { font-family:"Nunito",sans-serif; }
</style>

<template>
  <div class="fade-in-up">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="fw-bold mb-0">📦 My Assigned Orders</h5>
      <span class="badge bg-primary fs-6 px-3 py-2">{{ orders.length }} Tasks</span>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else-if="orders.length===0" class="text-center py-5 text-muted">
      <div style="font-size:4rem">📦</div>
      <h5 class="mt-3">No orders assigned yet</h5>
      <p>Check back later for new packing tasks</p>
    </div>

    <div v-else class="row g-3">
      <div class="col-md-6" v-for="o in orders" :key="o.order_id">
        <div class="fm-card p-4 h-100">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <span class="fw-bold font-nunito fs-6">#{{ o.order_id }}</span>
            <span :class="o.status==='packed' ? 'fm-badge-ok' : 'fm-badge-pending'">{{ o.status }}</span>
          </div>
          <div class="text-muted small mb-1"><i class="bi bi-person me-1"></i>{{ o.customer }}</div>
          <div class="text-muted small mb-3"><i class="bi bi-geo-alt me-1"></i>{{ o.delivery_address }}</div>
          <div class="fm-items-list mb-3">
            <span v-for="item in o.items" :key="item.id" class="fm-item-chip">
              {{ item.name }} ×{{ item.quantity }}
            </span>
          </div>
          <button v-if="o.status!=='packed'" class="btn btn-fm-green w-100"
                  @click="$router.push(`/packing/${o.order_id}`)">
            📦 Start Packing →
          </button>
          <div v-else class="text-center text-success fw-bold py-2">
            <i class="bi bi-check-circle-fill me-2"></i>Packed!
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getAssignedOrders } from "../../services/packerService.js"
export default {
  data() { return { orders:[], loading:true } },
  async mounted() { try{const r=await getAssignedOrders();this.orders=r.data}finally{this.loading=false} }
}
</script>

<style scoped>
.font-nunito { font-family:"Nunito",sans-serif; }
.fm-badge-ok      { background:#dcfce7;color:#166534;border:1px solid #bbf7d0;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;font-family:"Nunito",sans-serif; }
.fm-badge-pending { background:#fff7ed;color:#c2410c;border:1px solid #fed7aa;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;font-family:"Nunito",sans-serif; }
.fm-items-list { display:flex;flex-wrap:wrap;gap:6px; }
.fm-item-chip  { background:#f3f4f6;color:#374151;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;font-family:"Nunito",sans-serif; }
</style>

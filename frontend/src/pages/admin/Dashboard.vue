<template>
  <div class="fade-in-up">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h5 class="fw-bold mb-0">Dashboard</h5>
        <div class="text-muted small">{{ today }}</div>
      </div>
      <button class="btn btn-fm-green btn-sm px-3" @click="load">↻ Refresh</button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success"></div>
    </div>

    <div v-else>
      <!-- KPI cards -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-4 col-lg-2" v-for="c in cards" :key="c.title">
          <div class="fm-kpi-card" :style="`--kpi-color:${c.color}`">
            <div class="fm-kpi-icon">{{ c.icon }}</div>
            <div class="fm-kpi-value">{{ c.value }}</div>
            <div class="fm-kpi-label">{{ c.title }}</div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <!-- Quick Actions -->
        <div class="col-md-6">
          <div class="fm-card p-4">
            <h6 class="fw-bold mb-3">⚡ Quick Actions</h6>
            <div class="d-grid gap-2">
              <button class="btn btn-fm-green"   @click="$router.push('/admin/orders')">📋 View Pending Orders</button>
              <button class="btn btn-fm-outline" @click="$router.push('/admin/products')">🛒 Manage Products</button>
              <button class="btn btn-fm-outline" @click="$router.push('/admin/inventory')">📦 Check Inventory</button>
              <button class="btn btn-fm-outline" @click="$router.push('/admin/analytics')">📈 View Analytics</button>
            </div>
          </div>
        </div>

        <!-- Low Stock Alerts -->
        <div class="col-md-6">
          <div class="fm-card p-4">
            <h6 class="fw-bold mb-3">⚠️ Low Stock Alerts</h6>
            <div v-if="!lowStock.length" class="text-center text-muted py-3">
              <div style="font-size:2rem">🎉</div>
              <div class="small mt-1">All items well stocked</div>
            </div>
            <div v-for="item in lowStock" :key="item.id"
                 class="d-flex justify-content-between align-items-center mb-2 p-2 rounded"
                 style="background:#fef2f2">
              <span class="fw-semibold small">{{ item.product_name }}</span>
              <span class="badge bg-danger">{{ item.stock_quantity }} left</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getDashboard } from "../../services/adminService.js"

export default {
  data() { return { stats: null, loading: true } },
  computed: {
    today() { return new Date().toDateString() },
    cards() {
      if (!this.stats) return []
      const s = this.stats
      return [
        { title:"Pending",       value: s.pending_orders,       icon:"⏳", color:"#f97316" },
        { title:"Packing",       value: s.packing_orders,       icon:"📦", color:"#8b5cf6" },
        { title:"Out for Del.",  value: s.out_for_delivery,     icon:"🚚", color:"#0ea5e9" },
        { title:"Low Stock",     value: s.low_stock_count,      icon:"⚠️", color:"#ef4444" },
        { title:"Today Orders",  value: s.today_orders,         icon:"🛒", color:"#10b981" },
        { title:"Revenue Today", value: `₹${s.today_revenue}`,  icon:"💰", color:"#0d7740" },
      ]
    },
    lowStock() { return this.stats?.low_stock_items || [] }
  },
  async mounted() { await this.load() },
  methods: {
    async load() {
      this.loading = true
      try { const r = await getDashboard(); this.stats = r.data }
      finally { this.loading = false }
    }
  }
}
</script>

<style scoped>
.fm-kpi-card {
  background: #fff; border-radius: 14px; padding: 16px 12px;
  text-align: center; box-shadow: var(--fm-shadow);
  border-top: 3px solid var(--kpi-color); transition: transform .2s;
}
.fm-kpi-card:hover { transform: translateY(-2px); }
.fm-kpi-icon  { font-size: 1.8rem; margin-bottom: 4px; }
.fm-kpi-value { font-family:"Nunito",sans-serif; font-weight: 900; font-size: 1.4rem; }
.fm-kpi-label { font-size: 11px; color: var(--fm-gray-500); font-weight: 600; margin-top: 2px; }
</style>

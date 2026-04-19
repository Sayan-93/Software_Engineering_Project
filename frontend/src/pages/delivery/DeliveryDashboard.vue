<template>
  <div class="fade-in-up">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="fw-bold mb-0">🚚 My Deliveries</h5>
      <div class="d-flex gap-2">
        <span class="badge bg-warning text-dark px-3 py-2">{{ active.length }} Active</span>
        <span class="badge bg-success px-3 py-2">{{ done.length }} Done</span>
      </div>
    </div>

    <!-- Tab toggle -->
    <div class="fm-tab-row mb-3">
      <button class="fm-tab-btn" :class="{active:tab==='active'}" @click="tab='active'">
        🚚 Active ({{ active.length }})
      </button>
      <button class="fm-tab-btn" :class="{active:tab==='done'}" @click="tab='done'">
        ✅ Delivered ({{ done.length }})
      </button>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else-if="current.length===0" class="text-center py-5 text-muted">
      <div style="font-size:4rem">{{ tab==='active' ? '🚴' : '✅' }}</div>
      <h5 class="mt-3">{{ tab==='active' ? 'No active deliveries' : 'No delivered orders yet' }}</h5>
    </div>

    <div v-else class="row g-3">
      <div class="col-md-6" v-for="d in current" :key="d.assignment_id">
        <div class="fm-card p-4 h-100">

          <!-- Header -->
          <div class="d-flex justify-content-between align-items-center mb-3">
            <span class="fw-bold font-nunito fs-6">#{{ d.order_id }}</span>
            <span :class="`status-badge status-${d.status}`">{{ d.status.replace(/_/g,' ') }}</span>
          </div>

          <!-- Customer -->
          <div class="fm-delivery-info-row">
            <div class="fm-di-icon">👤</div>
            <div><div class="fw-semibold">{{ d.customer }}</div><div class="text-muted small">{{ d.phone }}</div></div>
          </div>
          <div class="fm-delivery-info-row">
            <div class="fm-di-icon">📍</div>
            <div class="text-muted small">{{ d.address }}</div>
          </div>
          <div class="fm-delivery-info-row mb-3">
            <div class="fm-di-icon">💰</div>
            <div class="fw-bold text-success">₹{{ d.total_amount }}</div>
          </div>

          <!-- Items -->
          <div class="fm-items-list mb-3">
            <span v-for="item in d.items" :key="item.id" class="fm-item-chip">{{ item.name }}</span>
          </div>

          <!-- Action buttons for active -->
          <template v-if="tab==='active'">
            <div class="d-flex gap-2 mb-2">
              <a :href="`tel:${d.phone}`" class="btn btn-outline-primary btn-sm flex-fill">
                📞 Call
              </a>
              <a :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(d.address)}`"
                 target="_blank" class="btn btn-outline-secondary btn-sm flex-fill">
                🗺 Map
              </a>
            </div>
            <div class="d-flex gap-2 flex-wrap">
              <button v-if="d.status==='assigned'"
                      class="btn btn-warning btn-sm flex-fill"
                      @click="updateStatus(d,'picked_up')">
                📦 Picked Up
              </button>
              <button v-if="d.status==='picked_up'"
                      class="btn btn-info btn-sm flex-fill text-white"
                      @click="updateStatus(d,'out_for_delivery')">
                🚚 Out for Delivery
              </button>
              <button v-if="['picked_up','out_for_delivery'].includes(d.status)"
                      class="btn btn-fm-green btn-sm flex-fill"
                      @click="updateStatus(d,'delivered')">
                ✅ Mark Delivered
              </button>
            </div>
          </template>

          <div v-else class="text-center text-success fw-semibold small py-1">
            ✓ Delivered {{ d.delivered_at ? new Date(d.delivered_at).toLocaleDateString("en-IN") : "" }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getDeliveries, updateDeliveryStatus } from "../../services/deliveryService.js"

export default {
  data() { return { deliveries:[], loading:true, tab:"active" } },
  computed: {
    active()  { return this.deliveries.filter(d => d.status !== "delivered") },
    done()    { return this.deliveries.filter(d => d.status === "delivered") },
    current() { return this.tab === "active" ? this.active : this.done }
  },
  async mounted() {
    try { const r = await getDeliveries(); this.deliveries = r.data }
    finally { this.loading = false }
  },
  methods: {
    async updateStatus(delivery, status) {
      try {
        await updateDeliveryStatus({ order_id:delivery.order_id, status })
        delivery.status = status
        if (status === "delivered") delivery.delivered_at = new Date().toISOString()
      } catch(e) { alert(e.response?.data?.error || "Error") }
    }
  }
}
</script>

<style scoped>
.font-nunito { font-family:"Nunito",sans-serif; }
.fm-tab-row { display:flex; gap:8px; }
.fm-tab-btn { padding:8px 20px;border-radius:20px;border:2px solid #e5e7eb;background:#fff;font-size:13px;font-weight:700;font-family:"Nunito",sans-serif;cursor:pointer;transition:.2s; }
.fm-tab-btn.active { background:var(--fm-green);color:#fff;border-color:var(--fm-green); }
.fm-delivery-info-row { display:flex;align-items:flex-start;gap:10px;margin-bottom:8px; }
.fm-di-icon { font-size:16px;flex-shrink:0;margin-top:1px; }
.fm-items-list { display:flex;flex-wrap:wrap;gap:6px; }
.fm-item-chip  { background:#f3f4f6;color:#374151;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px; }
</style>

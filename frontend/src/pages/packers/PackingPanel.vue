<template>
  <div class="fade-in-up">
    <div class="d-flex align-items-center gap-2 mb-4">
      <button class="btn btn-outline-secondary btn-sm" @click="$router.back()">←</button>
      <h5 class="fw-bold mb-0">Pack Order #{{ orderId }}</h5>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>
    <div v-else-if="!order" class="alert alert-warning">Order not found.</div>

    <div v-else class="row g-3">
      <!-- Items checklist -->
      <div class="col-md-7">
        <div class="fm-card p-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="fw-bold mb-0">Items to Pack</h6>
            <span class="text-muted small">{{ packedCount }}/{{ order.items.length }} checked</span>
          </div>
          <div class="progress mb-4" style="height:8px;border-radius:4px">
            <div class="progress-bar bg-success" :style="`width:${packProgress}%`" style="transition:.3s"></div>
          </div>
          <div v-for="item in order.items" :key="item.id"
               class="fm-pack-item" :class="{checked: item.packed}"
               @click="item.packed = !item.packed">
            <div class="fm-pack-checkbox" :class="{checked: item.packed}">
              <i class="bi bi-check-lg" v-if="item.packed"></i>
            </div>
            <div class="flex-grow-1">
              <div class="fw-semibold">{{ item.name }}</div>
              <div class="text-muted small">Qty: {{ item.quantity }}</div>
            </div>
            <span class="text-success fw-bold">₹{{ (item.price * item.quantity).toFixed(0) }}</span>
          </div>
        </div>
      </div>

      <!-- Assign delivery -->
      <div class="col-md-5">
        <div class="fm-card p-4">
          <h6 class="fw-bold mb-3">🚚 Assign Delivery</h6>
          <div v-if="!allPacked" class="fm-info-box mb-3">
            <i class="bi bi-info-circle me-2"></i>Check all items first
          </div>
          <div class="fm-delivery-list mb-3">
            <div v-for="d in deliveryStaff" :key="d.id"
                 class="fm-delivery-item" :class="{selected: selectedDelivery===d.id}"
                 @click="selectedDelivery=d.id">
              <div class="fm-delivery-avatar">{{ d.name[0] }}</div>
              <div>
                <div class="fw-semibold small">{{ d.name }}</div>
                <div class="text-muted" style="font-size:11px">{{ d.phone || "No phone" }}</div>
              </div>
              <i v-if="selectedDelivery===d.id" class="bi bi-check-circle-fill text-success ms-auto"></i>
            </div>
          </div>

          <div v-if="error" class="text-danger small mb-2">{{ error }}</div>

          <button class="btn btn-fm-green w-100 py-2"
                  :disabled="!allPacked || !selectedDelivery || submitting"
                  @click="complete">
            <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
            {{ submitting ? "Processing..." : "✅ Complete & Assign Delivery" }}
          </button>
        </div>

        <div v-if="done" class="fm-success-banner mt-3 fade-in-up">
          <div style="font-size:2.5rem">🎉</div>
          <div class="fw-bold mt-2">Order Packed!</div>
          <div class="text-muted small">Delivery person assigned</div>
          <button class="btn btn-fm-green btn-sm mt-3" @click="$router.push('/packer/orders')">Back to Orders</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getAssignedOrders, markPacked, assignDelivery, getDeliveryStaff } from "../../services/packerService.js"

export default {
  data() { return { order:null, deliveryStaff:[], selectedDelivery:"", loading:true, submitting:false, error:"", done:false } },
  computed: {
    orderId()      { return this.$route.params.id },
    allPacked()    { return this.order?.items.every(i => i.packed) },
    packedCount()  { return this.order?.items.filter(i => i.packed).length || 0 },
    packProgress() { return this.order ? (this.packedCount / this.order.items.length * 100) : 0 }
  },
  async mounted() {
    const [ordRes, staffRes] = await Promise.all([getAssignedOrders(), getDeliveryStaff()])
    const found = ordRes.data.find(o => String(o.order_id) === String(this.orderId))
    if (found) this.order = { ...found, items: found.items.map(i => ({...i, packed:false})) }
    this.deliveryStaff = staffRes.data
    this.loading = false
  },
  methods: {
    async complete() {
      this.submitting=true; this.error=""
      try {
        await markPacked(this.orderId)
        await assignDelivery({ order_id:parseInt(this.orderId), delivery_person_id:this.selectedDelivery })
        this.done = true
      } catch(e) { this.error = e.response?.data?.error || "Something went wrong." }
      finally { this.submitting=false }
    }
  }
}
</script>

<style scoped>
.fm-pack-item { display:flex;align-items:center;gap:12px;padding:12px;border:2px solid #e5e7eb;border-radius:12px;margin-bottom:8px;cursor:pointer;transition:.2s; }
.fm-pack-item.checked { border-color:var(--fm-green);background:var(--fm-green-light); }
.fm-pack-checkbox { width:24px;height:24px;border-radius:6px;border:2px solid #d1d5db;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:.2s;font-size:14px; }
.fm-pack-checkbox.checked { background:var(--fm-green);border-color:var(--fm-green);color:#fff; }

.fm-info-box { background:#eff6ff;color:#1d4ed8;border-radius:10px;padding:10px 14px;font-size:13px; }

.fm-delivery-list { display:flex;flex-direction:column;gap:8px; }
.fm-delivery-item { display:flex;align-items:center;gap:10px;padding:10px;border:2px solid #e5e7eb;border-radius:12px;cursor:pointer;transition:.2s; }
.fm-delivery-item:hover { border-color:var(--fm-green); }
.fm-delivery-item.selected { border-color:var(--fm-green);background:var(--fm-green-light); }
.fm-delivery-avatar { width:34px;height:34px;border-radius:50%;background:#0ea5e9;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;flex-shrink:0; }

.fm-success-banner { background:var(--fm-green);color:#fff;border-radius:16px;padding:24px;text-align:center; }
</style>

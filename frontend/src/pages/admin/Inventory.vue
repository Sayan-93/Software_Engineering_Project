<template>
  <div class="fade-in-up">
    <h5 class="fw-bold mb-4">Inventory Management</h5>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else class="fm-card overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead style="background:#f9fafb">
            <tr>
              <th class="ps-4">Product</th>
              <th>Current Stock</th>
              <th>Reorder Level</th>
              <th>Status</th>
              <th>Update Stock</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in inventory" :key="item.id" :class="item.low_stock ? 'table-danger bg-opacity-25' : ''">
              <td class="ps-4 fw-semibold">{{ item.product_name }}</td>
              <td>
                <span class="fw-bold fs-6" :class="item.low_stock ? 'text-danger' : 'text-success'">
                  {{ item.stock_quantity }}
                </span>
                <span class="text-muted small ms-1">units</span>
              </td>
              <td class="text-muted">{{ item.reorder_level }}</td>
              <td>
                <span v-if="item.low_stock" class="fm-badge-low">⚠️ Low Stock</span>
                <span v-else class="fm-badge-ok">✓ In Stock</span>
              </td>
              <td>
                <div class="d-flex gap-2 align-items-center">
                  <input v-model.number="item._newQty" type="number" min="0"
                         class="form-control form-control-sm" style="width:80px"
                         :placeholder="String(item.stock_quantity)" />
                  <button class="btn btn-fm-green btn-sm" @click="update(item)">Update</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <transition name="toast-slide">
      <div v-if="toast" class="fm-toast">{{ toast }}</div>
    </transition>
  </div>
</template>

<script>
import { getInventory, updateInventory } from "../../services/inventoryService.js"

export default {
  data() { return { inventory:[], loading:true, toast:"" } },
  async mounted() {
    try { const r = await getInventory(); this.inventory = r.data.map(i => ({...i, _newQty:""})) }
    finally { this.loading = false }
  },
  methods: {
    async update(item) {
      const qty = parseInt(item._newQty)
      if (isNaN(qty) || qty < 0) { alert("Enter a valid quantity"); return }
      await updateInventory(item.id, { stock_quantity: qty })
      item.stock_quantity = qty
      item.low_stock = qty < item.reorder_level
      item._newQty = ""
      this.toast = `✓ ${item.product_name} updated to ${qty} units`
      setTimeout(() => this.toast = "", 2500)
    }
  }
}
</script>

<style scoped>
.fm-badge-low { background:#fef2f2;color:#991b1b;border:1px solid #fecaca;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;font-family:"Nunito",sans-serif; }
.fm-badge-ok  { background:#f0fdf4;color:#166534;border:1px solid #bbf7d0;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;font-family:"Nunito",sans-serif; }
.fm-toast { position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#1f2937;color:#fff;padding:10px 20px;border-radius:20px;font-size:13px;font-weight:600;z-index:8000;white-space:nowrap; }
.toast-slide-enter-active,.toast-slide-leave-active{transition:.3s}
.toast-slide-enter-from,.toast-slide-leave-to{opacity:0;transform:translate(-50%,10px)}
</style>

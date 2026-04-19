<template>
  <div class="fade-in-up">
    <h5 class="fw-bold mb-3">Orders Management</h5>

    <!-- ✅ ONLY ADDITION: PDF BUTTON (NO STYLE CHANGES) -->
    <button
      class="btn btn-fm-green btn-sm mb-3"
      :disabled="loading || filtered.length === 0 || pdfLoading"
      @click="downloadPdf"
    >
      <span v-if="pdfLoading" class="spinner-border spinner-border-sm me-2"></span>
      Download Pending Orders PDF
    </button>

    <!-- Status filter pills -->
    <div class="fm-filter-row mb-3">
      <button v-for="s in statuses" :key="s"
              class="fm-filter-btn" :class="{ active: filter===s }"
              @click="filter=s">
        {{ s==='all' ? 'All' : s.replace(/_/g,' ') }}
        <span class="fm-filter-count">{{ count(s) }}</span>
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success"></div>
    </div>

    <div v-else class="fm-card overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead style="background:#f9fafb">
            <tr>
              <th class="ps-4">#</th>
              <th>Customer</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Date</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="o in filtered" :key="o.id">
              <td class="ps-4 fw-bold">#{{ o.id }}</td>
              <td>{{ o.customer }}</td>
              <td class="fw-bold text-success">₹{{ o.total_amount }}</td>
              <td>
                <span :class="`status-badge status-${o.status}`">
                  {{ o.status.replace(/_/g,' ') }}
                </span>
              </td>
              <td class="text-muted small">
                {{ fmtDate(o.created_at) }}
              </td>
              <td>
                <button v-if="o.status==='pending'" class="btn btn-success btn-sm me-1"
                        @click="approve(o)">✓ Approve</button>

                <button v-if="o.status==='approved'" class="btn btn-primary btn-sm"
                        @click="openAssign(o)">Assign Packer</button>

                <span v-if="!['pending','approved'].includes(o.status)" class="text-muted small">—</span>
              </td>
            </tr>

            <tr v-if="filtered.length===0">
              <td colspan="6" class="text-center text-muted py-4">
                No orders for this filter
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Assign Packer Modal -->
    <div v-if="assignModal" class="fm-modal-bg" @click.self="assignModal=false">
      <div class="fm-modal fade-in-up" style="max-width:380px">
        <h6 class="fw-bold mb-3">
          Assign Packer — Order #{{ assignOrder?.id }}
        </h6>

        <div class="fm-packer-list">
          <div v-for="p in packers" :key="p.id"
               class="fm-packer-item"
               :class="{ selected: selectedPacker===p.id }"
               @click="selectedPacker=p.id">
            <div class="fm-packer-avatar">{{ p.name[0] }}</div>
            <span class="fw-semibold">{{ p.name }}</span>
            <i v-if="selectedPacker===p.id"
               class="bi bi-check-circle-fill text-success ms-auto"></i>
          </div>
        </div>

        <div v-if="assignError" class="text-danger small mt-2">
          {{ assignError }}
        </div>

        <div class="d-flex gap-2 mt-3">
          <button class="btn btn-outline-secondary flex-fill"
                  @click="assignModal=false">Cancel</button>

          <button class="btn btn-fm-green flex-fill"
                  @click="confirmAssign"
                  :disabled="!selectedPacker">
            Assign
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { getOrders, approveOrder } from "../../services/orderService.js"
import { getPackers, assignPacker } from "../../services/adminService.js"
import apiClient from "../../services/apiClient.js"

export default {
  data() {
    return {
      orders: [],
      packers: [],
      loading: true,
      pdfLoading: false,

      filter: "all",
      statuses: ["all","pending","approved","packing","packed","out_for_delivery","delivered","cancelled"],

      assignModal: false,
      assignOrder: null,
      selectedPacker: "",
      assignError: ""
    }
  },

  computed: {
    filtered() {
      return this.filter==="all"
        ? this.orders
        : this.orders.filter(o => o.status===this.filter)
    },
    count() {
      return s => s==="all"
        ? this.orders.length
        : this.orders.filter(o=>o.status===s).length
    }
  },

  async mounted() {
    const [or, pr] = await Promise.all([
      getOrders(),
      getPackers()
    ])
    this.orders = or.data
    this.packers = pr.data
    this.loading = false
  },

  methods: {
    async approve(o) {
      await approveOrder(o.id)
      o.status = "approved"
    },

    openAssign(o) {
      this.assignOrder = o
      this.selectedPacker = ""
      this.assignError = ""
      this.assignModal = true
    },

    async confirmAssign() {
      try {
        await assignPacker({
          order_id: this.assignOrder.id,
          packer_id: this.selectedPacker
        })
        this.assignOrder.status = "packing"
        this.assignModal = false
      } catch (e) {
        this.assignError = e.response?.data?.error || "Error assigning"
      }
    },

    fmtDate(d) {
      return new Date(d).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short"
      })
    },

    // ✅ ONLY NEW FUNCTION
    async downloadPdf() {
      this.pdfLoading = true

      try {
        const response = await apiClient.get(
          `/admin/orders/export-pdf?status=pending`,
          { responseType: "blob" }
        )

        const url = window.URL.createObjectURL(
          new Blob([response.data], { type: "application/pdf" })
        )

        const link = document.createElement("a")
        const today = new Date().toISOString().slice(0, 10)

        link.href = url
        link.setAttribute("download", `pending_orders_${today}.pdf`)
        document.body.appendChild(link)
        link.click()

        link.remove()
        window.URL.revokeObjectURL(url)

      } catch (err) {
        alert("Failed to download PDF. Please try again.")
        console.error(err)
      } finally {
        this.pdfLoading = false
      }
    }
  }
}
</script>


<style scoped>
.fm-filter-row { display:flex; gap:6px; flex-wrap:wrap; }
.fm-filter-btn {
  padding:6px 14px; border-radius:20px; border:2px solid #e5e7eb;
  background:#fff; font-size:12px; font-weight:700; font-family:"Nunito",sans-serif;
  cursor:pointer; transition:.15s; white-space:nowrap; display:flex; align-items:center; gap:5px;
}
.fm-filter-btn:hover  { border-color:var(--fm-green); color:var(--fm-green); }
.fm-filter-btn.active { background:var(--fm-green); color:#fff; border-color:var(--fm-green); }
.fm-filter-count { background:rgba(255,255,255,.3); padding:1px 6px; border-radius:10px; font-size:10px; }
.fm-filter-btn.active .fm-filter-count { background:rgba(255,255,255,.25); }

.fm-packer-list { display:flex; flex-direction:column; gap:8px; }
.fm-packer-item { display:flex; align-items:center; gap:10px; padding:10px 14px; border:2px solid #e5e7eb; border-radius:12px; cursor:pointer; transition:.15s; }
.fm-packer-item:hover    { border-color:var(--fm-green); background:var(--fm-green-light); }
.fm-packer-item.selected { border-color:var(--fm-green); background:var(--fm-green-light); }
.fm-packer-avatar { width:34px;height:34px;border-radius:50%;background:var(--fm-green);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-family:"Nunito",sans-serif;flex-shrink:0; }

.fm-modal-bg { position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:2000;display:flex;align-items:center;justify-content:center;padding:16px; }
.fm-modal    { background:#fff;border-radius:20px;padding:28px;width:100%; }
</style>

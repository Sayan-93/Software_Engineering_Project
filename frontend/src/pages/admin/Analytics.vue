<template>
  <div class="fade-in-up">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="fw-bold mb-0">Analytics</h5>
      <div class="d-flex gap-2">
        <button class="btn btn-sm btn-fm-outline" @click="doForecast" :disabled="busy">🔮 Run Forecast</button>
        <button class="btn btn-sm btn-fm-green"   @click="doRebuild"  :disabled="busy">🔁 Rebuild Recs</button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else>
      <!-- KPI row -->
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <div class="fm-card p-4 text-center">
            <div class="text-muted small mb-1">Total Revenue</div>
            <div class="fw-bold text-success" style="font-size:2rem;font-family:'Nunito',sans-serif">₹{{ summary.total_revenue }}</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="fm-card p-4 text-center">
            <div class="text-muted small mb-1">Units Sold</div>
            <div class="fw-bold" style="font-size:2rem;font-family:'Nunito',sans-serif">{{ summary.total_quantity_sold }}</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="fm-card p-4 text-center">
            <div class="text-muted small mb-1">Today's Revenue</div>
            <div class="fw-bold text-primary" style="font-size:2rem;font-family:'Nunito',sans-serif">₹{{ todayRevenue }}</div>
          </div>
        </div>
      </div>

      <!-- Chart + Top Products -->
      <div class="row g-3 mb-4">
        <div class="col-md-8">
          <div class="fm-card p-4">
            <h6 class="fw-bold mb-3">📊 Revenue — Last 7 Days</h6>
            <canvas ref="chart" height="110"></canvas>
          </div>
        </div>
        <div class="col-md-4">
          <div class="fm-card p-4 h-100">
            <h6 class="fw-bold mb-3">🏆 Top Products</h6>
            <div v-for="(p, i) in topProducts" :key="p.product_id" class="mb-3">
              <div class="d-flex justify-content-between small mb-1">
                <span class="fw-semibold">{{ i+1 }}. {{ p.product_name }}</span>
                <span class="text-success fw-bold">₹{{ p.total_revenue }}</span>
              </div>
              <div class="progress" style="height:6px;border-radius:3px">
                <div class="progress-bar bg-success" :style="`width:${pct(p.total_revenue)}%`"></div>
              </div>
              <div class="text-muted" style="font-size:10px;margin-top:2px">{{ p.total_qty }} units sold</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Forecast -->
      <div class="fm-card p-4" v-if="forecasts.length">
        <h6 class="fw-bold mb-3">📈 Stock Demand Forecast (Next 7 Days)</h6>
        <div class="table-responsive">
          <table class="table table-sm align-middle mb-0">
            <thead style="background:#f9fafb">
              <tr><th>Product</th><th>Forecast Date</th><th>Predicted Demand</th><th>Indicator</th></tr>
            </thead>
            <tbody>
              <tr v-for="f in forecasts.slice(0,14)" :key="f.id">
                <td class="fw-semibold">{{ f.product_name }}</td>
                <td class="text-muted">{{ f.forecast_date }}</td>
                <td><span class="badge" style="background:#dbeafe;color:#1d4ed8">{{ f.predicted_demand }} units</span></td>
                <td>
                  <div class="progress" style="height:6px;width:80px;border-radius:3px">
                    <div class="progress-bar" style="background:#3b82f6" :style="`width:${Math.min(f.predicted_demand*3,100)}%`"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <transition name="toast-slide">
      <div v-if="toast" class="fm-toast">{{ toast }}</div>
    </transition>
  </div>
</template>

<script>
import Chart from "chart.js/auto"
import { getSalesSummary, getTopProducts, getForecast } from "../../services/analyticsService.js"
import { runForecast, rebuildRecs } from "../../services/adminService.js"

export default {
  data() { return { summary:{}, topProducts:[], forecasts:[], loading:true, chartInst:null, busy:false, toast:"" } },
  computed: {
    todayRevenue() {
      const d = this.summary.last_7_days
      return d?.length ? d[d.length-1].revenue : 0
    }
  },
  async mounted() {
    const [sr, tr, fr] = await Promise.all([getSalesSummary(), getTopProducts(), getForecast()])
    this.summary = sr.data; this.topProducts = tr.data; this.forecasts = fr.data
    this.loading = false
    this.$nextTick(() => this.drawChart())
  },
  methods: {
    drawChart() {
      const days = this.summary.last_7_days || []
      if (this.chartInst) this.chartInst.destroy()
      this.chartInst = new Chart(this.$refs.chart, {
        type: "bar",
        data: {
          labels: days.map(d => d.label),
          datasets: [{
            label:"Revenue (₹)",
            data: days.map(d => d.revenue),
            backgroundColor: days.map((_, i) => i === days.length-1 ? "#0d7740" : "#bbf7d0"),
            borderRadius: 8, borderSkipped: false
          }]
        },
        options: {
          responsive:true,
          plugins:{ legend:{ display:false } },
          scales:{ y:{ grid:{ color:"#f3f4f6" }, ticks:{ color:"#9ca3af" } }, x:{ grid:{ display:false }, ticks:{ color:"#6b7280" } } }
        }
      })
    },
    pct(val) {
      const max = Math.max(...this.topProducts.map(p=>p.total_revenue))
      return max ? Math.round(val/max*100) : 0
    },
    async doForecast() { this.busy=true; await runForecast(); const r=await getForecast(); this.forecasts=r.data; this.busy=false; this.showToast("🔮 Forecast updated!") },
    async doRebuild()  { this.busy=true; await rebuildRecs(); this.busy=false; this.showToast("🔁 Recommendations rebuilt!") },
    showToast(m) { this.toast=m; setTimeout(()=>this.toast="",2500) }
  },
  beforeUnmount() { if(this.chartInst) this.chartInst.destroy() }
}
</script>

<style scoped>
.fm-toast { position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#1f2937;color:#fff;padding:10px 20px;border-radius:20px;font-size:13px;font-weight:600;z-index:8000;white-space:nowrap; }
.toast-slide-enter-active,.toast-slide-leave-active{transition:.3s}
.toast-slide-enter-from,.toast-slide-leave-to{opacity:0;transform:translate(-50%,10px)}
</style>

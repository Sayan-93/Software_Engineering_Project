<template>
  <div class="fade-in-up">
    <div class="d-flex align-items-center gap-2 mb-4">
      <button class="btn btn-outline-secondary btn-sm" @click="$router.back()">←</button>
      <h5 class="fw-bold mb-0">Track Order #{{ $route.params.id }}</h5>
    </div>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>
    <div v-else>
      <div class="fm-card p-4 mb-3">
        <div class="fm-timeline">
          <div v-for="(step,i) in steps" :key="i" class="fm-tl-item" :class="{done:step.done,current:isCurrent(i)}">
            <div class="fm-tl-dot"><i :class="step.done ? 'bi bi-check-lg' : 'bi bi-circle'"></i></div>
            <div class="fm-tl-line" v-if="i < steps.length-1"></div>
            <div class="fm-tl-label">{{ step.label }}</div>
          </div>
        </div>
      </div>
      <div class="fm-card p-4" v-if="order">
        <h6 class="fw-bold mb-3">Order Items</h6>
        <div v-for="item in order.items" :key="item.id" class="d-flex justify-content-between mb-2 small">
          <span>{{ item.name }} × {{ item.quantity }}</span>
          <span class="text-success fw-bold">₹{{ (item.price*item.quantity).toFixed(0) }}</span>
        </div>
        <hr/><div class="d-flex justify-content-between fw-bold"><span>Total</span><span class="text-success">₹{{ order.total_amount }}</span></div>
      </div>
    </div>
  </div>
</template>
<script>
import { getOrder, getOrderStatus } from "../../services/orderService.js"
const LABELS = { pending:"Order Placed",approved:"Approved",packing:"Being Packed",packed:"Ready to Ship",out_for_delivery:"Out for Delivery",delivered:"Delivered" }
export default {
  data(){ return { order:null, steps:[], loading:true } },
  async mounted(){
    const id=this.$route.params.id
    try{
      const [or,sr]=await Promise.all([getOrder(id),getOrderStatus(id)])
      this.order=or.data
      this.steps=sr.data.steps.map(s=>({label:LABELS[s.label]||s.label,done:s.done,key:s.label}))
    }finally{ this.loading=false }
  },
  methods:{ isCurrent(i){ return !this.steps[i].done && (i===0||this.steps[i-1].done) } }
}
</script>
<style scoped>
.fm-timeline { display:flex; gap:0; }
.fm-tl-item  { flex:1; display:flex; flex-direction:column; align-items:center; position:relative; }
.fm-tl-dot   { width:32px;height:32px;border-radius:50%;border:2px solid #e5e7eb;background:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;z-index:1;transition:.3s; }
.fm-tl-item.done .fm-tl-dot   { background:var(--fm-green);border-color:var(--fm-green);color:#fff; }
.fm-tl-item.current .fm-tl-dot{ border-color:var(--fm-orange);color:var(--fm-orange);animation:pulse-green 1.5s infinite; }
.fm-tl-line  { position:absolute;top:15px;left:50%;right:-50%;height:2px;background:#e5e7eb;z-index:0; }
.fm-tl-item.done .fm-tl-line { background:var(--fm-green); }
.fm-tl-label { font-size:10px;text-align:center;margin-top:6px;font-weight:600;font-family:"Nunito",sans-serif;color:var(--fm-gray-500); }
.fm-tl-item.done .fm-tl-label { color:var(--fm-green); }
</style>

<template>
  <div class="fade-in-up">
    <h5 class="fw-bold mb-4">🛒 Your Cart</h5>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else-if="items.length === 0" class="fm-empty-cart">
      <div style="font-size:5rem">🛒</div>
      <h5 class="mt-3">Your cart is empty</h5>
      <p class="text-muted">Add some fresh items to get started</p>
      <router-link to="/products" class="btn btn-fm-green px-5 py-2">Browse Products</router-link>
    </div>

    <div v-else class="row g-3">
      <!-- Cart items -->
      <div class="col-md-8">
        <div class="fm-card p-0 overflow-hidden">
          <div class="fm-cart-header px-4 py-3">
            <span class="fw-bold">{{ items.length }} item{{ items.length>1?'s':'' }}</span>
            <button class="btn btn-link text-danger small p-0" @click="clearAll">Clear all</button>
          </div>

          <div class="fm-cart-item" v-for="item in items" :key="item.id">
            <div class="fm-cart-item-img" :style="{background: itemBg(item)}">
              <span>{{ itemEmoji(item.name) }}</span>
            </div>
            <div class="fm-cart-item-info">
              <div class="fm-cart-item-name">{{ item.name }}</div>
              <div class="fm-cart-item-unit text-muted">{{ item.selected_weight || item.unit }}</div>
              <div class="fm-cart-item-price text-success fw-bold">₹{{ item.price }}</div>
            </div>
            <div class="fm-cart-item-right">
              <div class="fm-qty-ctrl-cart">
                <button @click="changeQty(item,-1)">−</button>
                <span>{{ item.quantity }}</span>
                <button @click="changeQty(item,1)">+</button>
              </div>
              <div class="fm-cart-item-total fw-bold">₹{{ (item.price * item.quantity).toFixed(0) }}</div>
            </div>
          </div>
        </div>

        <!-- Savings banner -->
        <div class="fm-savings-banner mt-3" v-if="totalSaved > 0">
          <span>🎉</span>
          <span>You save <strong>₹{{ totalSaved }}</strong> on this order!</span>
        </div>
      </div>

      <!-- Order summary -->
      <div class="col-md-4">
        <div class="fm-card p-4 fm-summary">
          <h6 class="fw-bold mb-3">Order Summary</h6>
          <div class="fm-summary-row"><span>Subtotal ({{ items.length }} items)</span><span>₹{{ subtotal }}</span></div>
          <div class="fm-summary-row text-success" v-if="totalSaved > 0"><span>Savings</span><span>-₹{{ totalSaved }}</span></div>
          <div class="fm-summary-row"><span>Delivery charge</span><span :class="deliveryFree ? 'text-success' : ''">{{ deliveryFree ? "FREE" : "₹30" }}</span></div>
          <hr />
          <div class="fm-summary-row fw-bold fs-5"><span>Total</span><span class="text-success">₹{{ grandTotal }}</span></div>
          <div v-if="!deliveryFree" class="fm-delivery-tip mt-2">
            Add ₹{{ 300 - parseInt(subtotal) }} more for free delivery
          </div>
          <button class="btn btn-fm-green w-100 py-3 mt-3 fw-bold" @click="showCheckout = true">
            Proceed to Checkout →
          </button>
        </div>
      </div>
    </div>

    <!-- Checkout modal -->
    <div v-if="showCheckout" class="fm-modal-bg" @click.self="showCheckout=false">
      <div class="fm-modal fade-in-up">
        <div v-if="orderDone" class="text-center py-4">
          <div style="font-size:4rem">🎉</div>
          <h5 class="mt-3 fw-bold">Order Placed!</h5>
          <p class="text-muted">Order #{{ placedId }} confirmed</p>
          <p class="small text-success">🚴 Estimated delivery in 30 minutes</p>
          <router-link to="/orders" class="btn btn-fm-green px-5" @click="showCheckout=false">Track Order</router-link>
        </div>
        <div v-else>
          <h6 class="fw-bold mb-4">Checkout</h6>
          <div class="mb-3">
            <label class="form-label small fw-semibold">Delivery Address</label>
            <textarea v-model="address" class="form-control" rows="2" placeholder="Full delivery address"></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label small fw-semibold">Payment</label>
            <div class="fm-payment-options">
              <label v-for="opt in ['COD','UPI','Card']" :key="opt" class="fm-pay-opt" :class="{ selected: payMethod===opt }">
                <input type="radio" v-model="payMethod" :value="opt" />
                <span>{{ payIcon(opt) }} {{ opt }}</span>
              </label>
            </div>
          </div>
          <div class="fm-checkout-total">Total: <strong class="text-success">₹{{ grandTotal }}</strong></div>
          <div v-if="checkoutErr" class="text-danger small mt-2">{{ checkoutErr }}</div>
          <div class="d-flex gap-2 mt-3">
            <button class="btn btn-outline-secondary flex-fill" @click="showCheckout=false">Cancel</button>
            <button class="btn btn-fm-green flex-fill py-2" @click="placeOrder" :disabled="placing">
              <span v-if="placing" class="spinner-border spinner-border-sm me-2"></span>
              {{ placing ? "Placing..." : "Confirm Order" }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getCart, updateCartItem, removeFromCart, clearCart } from "../../services/cartService.js"
import { placeOrder } from "../../services/orderService.js"
import { cartStore } from "../../stores/cart.js"

const EMOJIS = {apple:"🍎",banana:"🍌",mango:"🥭",orange:"🍊",tomato:"🍅",potato:"🥔",onion:"🧅",carrot:"🥕",spinach:"🥬",coriander:"🌿",default:"🛒"}
const COLORS  = ["#fef3c7","#dcfce7","#fee2e2","#e0f2fe","#fce7f3","#ede9fe","#fef9c3"]

export default {
  data() { return { items:[], loading:true, showCheckout:false, address:"", payMethod:"COD", placing:false, orderDone:false, placedId:null, checkoutErr:"" } },
  computed: {
    subtotal()    { return this.items.reduce((s,i) => s + i.price * i.quantity, 0).toFixed(0) },
    totalSaved()  { return 0 },
    deliveryFree(){ return parseInt(this.subtotal) >= 300 },
    grandTotal()  { return parseInt(this.subtotal) + (this.deliveryFree ? 0 : 30) }
  },
  async mounted() {
    try { const r = await getCart(); this.items = r.data.items || [] } catch {}
    finally { this.loading = false }
    try { this.address = JSON.parse(localStorage.getItem("user"))?.address || "" } catch {}
  },
  methods: {
    itemEmoji(name) { return EMOJIS[name?.toLowerCase()] || EMOJIS.default },
    itemBg(item)    { return COLORS[(item.product_id||0) % COLORS.length] },
    payIcon(p)      { return { COD:"💵", UPI:"📱", Card:"💳" }[p] },
    async changeQty(item, d) {
      const nq = item.quantity + d
      if (nq <= 0) { await removeFromCart(item.id); this.items = this.items.filter(i=>i.id!==item.id); cartStore.setCount(this.items.length) }
      else { await updateCartItem(item.id, { quantity:nq }); item.quantity = nq }
    },
    async clearAll() {
      if (!confirm("Clear entire cart?")) return
      await clearCart(); this.items = []; cartStore.setCount(0)
    },
    async placeOrder() {
      if (!this.address.trim()) { this.checkoutErr = "Please enter delivery address."; return }
      this.placing = true; this.checkoutErr = ""
      try {
        const r = await placeOrder({ delivery_address:this.address, payment_method:this.payMethod })
        this.placedId = r.data.order.id; this.orderDone = true
        this.items = []; cartStore.setCount(0)
      } catch(e) { this.checkoutErr = e.response?.data?.error || "Order failed." }
      finally { this.placing = false }
    }
  }
}
</script>

<style scoped>
.fm-empty-cart { text-align:center; padding:80px 16px; }
.fm-cart-header { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f0f0f0; }
.fm-cart-item { display:flex; gap:12px; align-items:center; padding:14px 16px; border-bottom:1px solid #f9f9f9; transition:.15s; }
.fm-cart-item:hover { background:#fafafa; }
.fm-cart-item:last-child { border-bottom:none; }
.fm-cart-item-img { width:56px; height:56px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:26px; flex-shrink:0; }
.fm-cart-item-info { flex:1; }
.fm-cart-item-name { font-weight:700; font-family:"Nunito",sans-serif; font-size:15px; }
.fm-cart-item-unit { font-size:12px; }
.fm-cart-item-price { font-size:14px; }
.fm-cart-item-right { display:flex; flex-direction:column; align-items:flex-end; gap:8px; }
.fm-cart-item-total { font-size:15px; font-family:"Nunito",sans-serif; }

.fm-qty-ctrl-cart { display:flex; align-items:center; gap:6px; border:2px solid var(--fm-green); border-radius:8px; padding:2px 4px; }
.fm-qty-ctrl-cart button { width:24px; height:24px; border:none; background:none; font-size:18px; font-weight:700; cursor:pointer; color:var(--fm-green); display:flex; align-items:center; justify-content:center; }
.fm-qty-ctrl-cart span { font-weight:800; font-family:"Nunito",sans-serif; min-width:20px; text-align:center; }

.fm-savings-banner { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; padding:10px 16px; display:flex; align-items:center; gap:10px; font-size:14px; }
.fm-summary-row { display:flex; justify-content:space-between; margin-bottom:10px; font-size:14px; }
.fm-delivery-tip { background:#fff7ed; color:#c2410c; border-radius:8px; padding:8px 12px; font-size:12px; text-align:center; }
.fm-checkout-total { background:#f0fdf4; border-radius:10px; padding:10px 14px; font-size:15px; text-align:center; }

.fm-payment-options { display:flex; gap:10px; flex-wrap:wrap; }
.fm-pay-opt { display:flex; align-items:center; gap:6px; padding:8px 16px; border:2px solid #e5e7eb; border-radius:10px; cursor:pointer; font-size:14px; font-weight:600; font-family:"Nunito",sans-serif; transition:.2s; }
.fm-pay-opt input { display:none; }
.fm-pay-opt.selected { border-color:var(--fm-green); background:var(--fm-green-light); color:var(--fm-green); }

.fm-modal-bg { position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:2000;display:flex;align-items:center;justify-content:center;padding:16px; }
.fm-modal { background:#fff;border-radius:20px;padding:28px;width:100%;max-width:420px; }
</style>

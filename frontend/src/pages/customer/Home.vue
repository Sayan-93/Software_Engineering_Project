<template>
  <div class="fade-in-up">

    <!-- Delivery banner -->
    <div class="fm-delivery-banner">
      <div class="fm-delivery-left">
        <div class="fm-delivery-tag">⚡ Express Delivery</div>
        <div class="fm-delivery-time">Delivery in <strong>30 minutes</strong></div>
        <div class="fm-delivery-addr">
          <i class="bi bi-geo-alt-fill text-success me-1"></i>
          {{ userAddress || "Set your location" }}
        </div>
      </div>
      <div class="fm-delivery-art">🚴</div>
    </div>

    <!-- Category pills -->
    <div class="fm-section-title mb-2">Shop by Category</div>
    <div class="fm-cats-row">
      <div v-for="c in categories" :key="c.id"
           class="fm-cat-pill"
           :class="{ active: selectedCat === c.id }"
           @click="filterByCat(c)">
        <span class="fm-cat-icon">{{ catIcon(c.name) }}</span>
        <span>{{ c.name }}</span>
      </div>
    </div>

    <!-- Featured products -->
    <div class="d-flex justify-content-between align-items-center mt-4 mb-2">
      <div class="fm-section-title mb-0">
        {{ selectedCat ? selectedCatName : "Featured Products" }}
      </div>
      <router-link to="/products" class="fm-view-all">View all →</router-link>
    </div>

    <div v-if="loading" class="fm-loading-grid">
      <div v-for="n in 8" :key="n" class="fm-skeleton-card">
        <div class="fm-skeleton-img"></div>
        <div class="fm-skeleton-line w-60"></div>
        <div class="fm-skeleton-line w-40"></div>
      </div>
    </div>

    <div v-else class="fm-products-grid">
      <ProductCard
        v-for="p in products"
        :key="p.id"
        :product="p"
        :cartItems="cartItems"
        @add-to-cart="addToCart"
        @update-qty="updateQty"
      />
    </div>

    <!-- Deals banner -->
    <div class="fm-deals-banner mt-4" v-if="deals.length">
      <div class="fm-deals-header">
        <span>🔥 Today's Deals</span>
        <router-link to="/products" class="fm-view-all" style="color:#fff">View all</router-link>
      </div>
      <div class="fm-deals-row">
        <div v-for="p in deals" :key="p.id" class="fm-deal-chip" @click="$router.push('/products')">
          <span>{{ catIcon(p.name) }}</span>
          <span class="fw-bold">{{ p.name }}</span>
          <span class="fm-deal-pct">{{ p.discount }}% off</span>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition name="toast-slide">
      <div v-if="toast" class="fm-toast">{{ toast }}</div>
    </transition>
  </div>
</template>

<script>
import ProductCard from "../../components/ProductCard.vue"
import { getProducts, getCategories } from "../../services/productService.js"
import { getCart, addToCart, updateCartItem, removeFromCart } from "../../services/cartService.js"
import { cartStore } from "../../stores/cart.js"

const CAT_ICONS = { Fruits:"🍎", Vegetables:"🥦", "Leafy Greens":"🥬", "Herbs & Spices":"🌿" }

export default {
  components: { ProductCard },
  data() {
    return { products:[], categories:[], cartItems:[], selectedCat:null, loading:true, toast:"" }
  },
  computed: {
    userAddress() { try { return JSON.parse(localStorage.getItem("user"))?.address } catch { return "" } },
    selectedCatName() { return this.categories.find(c => c.id === this.selectedCat)?.name || "" },
    deals() { return this.products.filter(p => p.discount > 0) }
  },
  async mounted() {
    const [catRes, cartRes] = await Promise.all([getCategories(), getCart().catch(() => ({ data:{ items:[] } }))])
    this.categories = catRes.data
    this.cartItems  = cartRes.data.items || []
    cartStore.setCount(this.cartItems.length)
    await this.loadProducts()
  },
  methods: {
    catIcon(name) { return CAT_ICONS[name] || "🛒" },
    async filterByCat(cat) {
      this.selectedCat = this.selectedCat === cat.id ? null : cat.id
      await this.loadProducts()
    },
    async loadProducts() {
      this.loading = true
      try {
        const res = await getProducts({ category_id: this.selectedCat || undefined })
        this.products = res.data.slice(0, 8)
      } finally { this.loading = false }
    },
    async addToCart({ product, selectedWeight, finalPrice }) {
      try {
        await addToCart({ product_id: product.id, quantity: 1, selected_weight: selectedWeight || null, price: finalPrice })
        const existing = this.cartItems.find(i => i.product_id === product.id && i.selected_weight === (selectedWeight || null))
        if (existing) existing.quantity++
        else this.cartItems.push({ product_id: product.id, quantity: 1, selected_weight: selectedWeight || null })
        cartStore.setCount(this.cartItems.length)
        this.showToast(`${product.name}${selectedWeight ? ' ('+selectedWeight+')' : ''} added to cart! 🛒`)
      } catch(e) { this.showToast(e.response?.data?.error || "Error") }
    },
    async updateQty({ product, delta, currentQty, selectedWeight }) {
      const newQty = currentQty + delta
      const item = this.cartItems.find(i => i.product_id === product.id && i.selected_weight === (selectedWeight || null))
      if (newQty <= 0 && item) {
        await removeFromCart(item.id)
        this.cartItems = this.cartItems.filter(i => !(i.product_id === product.id && i.selected_weight === (selectedWeight || null)))
        cartStore.setCount(this.cartItems.length)
      } else if (newQty > 0 && item) {
        await updateCartItem(item.id, { quantity: newQty })
        item.quantity = newQty
      } else if (newQty > 0) {
        await addToCart({ product_id: product.id, quantity: newQty, selected_weight: selectedWeight || null, price: finalPrice })
        this.cartItems.push({ product_id: product.id, quantity: newQty, selected_weight: selectedWeight || null })
        cartStore.setCount(this.cartItems.length)
      }
    },
    showToast(msg) { this.toast = msg; setTimeout(() => this.toast = "", 2500) }
  }
}
</script>

<style scoped>
/* Delivery banner */
.fm-delivery-banner {
  background:linear-gradient(135deg,var(--fm-green),#0a5c2e);
  border-radius:16px; padding:20px 24px;
  display:flex; justify-content:space-between; align-items:center;
  color:#fff; margin-bottom:20px;
}
.fm-delivery-tag { background:rgba(255,255,255,.2); display:inline-block; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:700; margin-bottom:6px; }
.fm-delivery-time { font-family:"Nunito",sans-serif; font-weight:800; font-size:1.3rem; }
.fm-delivery-addr { font-size:13px; opacity:.85; margin-top:4px; }
.fm-delivery-art  { font-size:3.5rem; }

/* Categories */
.fm-cats-row { display:flex; gap:10px; overflow-x:auto; padding-bottom:8px; }
.fm-cats-row::-webkit-scrollbar { display:none; }
.fm-cat-pill {
  display:flex; align-items:center; gap:6px; white-space:nowrap;
  padding:8px 16px; border-radius:20px; cursor:pointer;
  border:2px solid var(--fm-gray-200); background:#fff;
  font-size:13px; font-weight:600; font-family:"Nunito",sans-serif;
  transition:.2s;
}
.fm-cat-pill:hover { border-color:var(--fm-green); color:var(--fm-green); }
.fm-cat-pill.active { background:var(--fm-green); color:#fff; border-color:var(--fm-green); }
.fm-cat-icon { font-size:18px; }

/* Section title */
.fm-section-title { font-family:"Nunito",sans-serif; font-weight:800; font-size:1.1rem; color:var(--fm-text); }
.fm-view-all { font-size:13px; font-weight:700; color:var(--fm-green); text-decoration:none; font-family:"Nunito",sans-serif; }

/* Products grid */
.fm-products-grid { display:grid; grid-template-columns:repeat(2, 1fr); gap:12px; }
@media(min-width:576px) { .fm-products-grid { grid-template-columns:repeat(3,1fr); } }
@media(min-width:768px) { .fm-products-grid { grid-template-columns:repeat(4,1fr); } }

/* Skeleton */
.fm-loading-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; }
@media(min-width:768px) { .fm-loading-grid { grid-template-columns:repeat(4,1fr); } }
.fm-skeleton-card { background:#fff; border-radius:12px; overflow:hidden; padding-bottom:12px; }
.fm-skeleton-img  { height:130px; background:linear-gradient(90deg,#f0f0f0 25%,#e0e0e0 50%,#f0f0f0 75%); background-size:200% 100%; animation:shimmer 1.4s infinite; }
.fm-skeleton-line { height:12px; background:#f0f0f0; border-radius:6px; margin:10px 12px 6px; animation:shimmer 1.4s infinite; }
.fm-skeleton-line.w-60 { width:60%; }
.fm-skeleton-line.w-40 { width:40%; }
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

/* Deals */
.fm-deals-banner { background:#1a1a2e; border-radius:16px; padding:16px 20px; }
.fm-deals-header { display:flex; justify-content:space-between; align-items:center; color:#fff; font-family:"Nunito",sans-serif; font-weight:800; font-size:15px; margin-bottom:12px; }
.fm-deals-row { display:flex; gap:10px; overflow-x:auto; }
.fm-deals-row::-webkit-scrollbar { display:none; }
.fm-deal-chip { display:flex; align-items:center; gap:8px; padding:8px 14px; border-radius:12px; background:rgba(255,255,255,.08); color:#fff; font-size:13px; white-space:nowrap; cursor:pointer; transition:.15s; }
.fm-deal-chip:hover { background:rgba(255,255,255,.15); }
.fm-deal-pct { background:var(--fm-orange); color:#fff; font-size:10px; font-weight:700; padding:2px 7px; border-radius:20px; font-family:"Nunito",sans-serif; }

/* Toast */
.fm-toast { position:fixed; bottom:90px; left:50%; transform:translateX(-50%); background:#1f2937; color:#fff; padding:10px 20px; border-radius:20px; font-size:13px; font-weight:600; font-family:"Nunito",sans-serif; z-index:8000; white-space:nowrap; }
.toast-slide-enter-active,.toast-slide-leave-active { transition:.3s; }
.toast-slide-enter-from,.toast-slide-leave-to { opacity:0; transform:translate(-50%,10px); }
</style>

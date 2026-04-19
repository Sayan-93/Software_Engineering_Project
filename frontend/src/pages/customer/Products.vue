<template>
  <div class="fade-in-up">
    <!-- Search bar -->
    <div class="fm-search-page mb-3">
      <i class="bi bi-search"></i>
      <input v-model="search" placeholder="Search fruits, vegetables..." @input="onSearch" />
      <button v-if="search" @click="search=''; fetchProducts()"><i class="bi bi-x-lg"></i></button>
    </div>

    <!-- Category tabs -->
    <div class="fm-cats-scroll mb-3">
      <button class="fm-cat-tab" :class="{ active:!catId }" @click="catId=null; fetchProducts()">All</button>
      <button v-for="c in categories" :key="c.id"
              class="fm-cat-tab" :class="{ active:catId===c.id }"
              @click="catId=c.id; fetchProducts()">
        {{ catIcon(c.name) }} {{ c.name }}
      </button>
    </div>

    <!-- Count -->
    <div class="text-muted small mb-3" v-if="!loading">
      {{ products.length }} item{{ products.length !== 1 ? "s" : "" }} found
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="fm-products-grid">
      <div v-for="n in 8" :key="n" class="fm-skeleton-card">
        <div style="height:130px;background:linear-gradient(90deg,#f0f0f0 25%,#e8e8e8 50%,#f0f0f0 75%);background-size:200% 100%;animation:shimmer 1.4s infinite;border-radius:12px 12px 0 0"></div>
        <div style="padding:10px"><div style="height:12px;background:#f0f0f0;border-radius:6px;margin-bottom:8px;width:70%"></div><div style="height:10px;background:#f0f0f0;border-radius:6px;width:50%"></div></div>
      </div>
    </div>

    <div v-else-if="products.length === 0" class="fm-empty-state">
      <div style="font-size:4rem">🔍</div>
      <h5>No products found</h5>
      <p class="text-muted">Try a different search or category</p>
      <button class="btn btn-fm-green px-4" @click="search='';catId=null;fetchProducts()">Clear filters</button>
    </div>

    <div v-else class="fm-products-grid">
      <ProductCard v-for="p in products" :key="p.id" :product="p" :cartItems="cartItems"
                   @add-to-cart="addToCart" @update-qty="updateQty" />
    </div>

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
  data() { return { products:[], categories:[], cartItems:[], search:"", catId:null, loading:false, toast:"", debounce:null } },
  async mounted() {
    this.search = this.$route.query.search || ""
    const [cr, cartRes] = await Promise.all([getCategories(), getCart().catch(() => ({data:{items:[]}}))])
    this.categories = cr.data
    this.cartItems  = cartRes.data.items || []
    await this.fetchProducts()
  },
  methods: {
    catIcon(n) { return CAT_ICONS[n] || "🛒" },
    onSearch() { clearTimeout(this.debounce); this.debounce = setTimeout(this.fetchProducts, 350) },
    async fetchProducts() {
      this.loading = true
      try {
        const res = await getProducts({ search:this.search||undefined, category_id:this.catId||undefined })
        this.products = res.data
      } finally { this.loading = false }
    },
    async addToCart(product) {
      try {
        await addToCart({ product_id: product.id, quantity:1 })
        const ex = this.cartItems.find(i => i.product_id === product.id)
        if (ex) ex.quantity++; else this.cartItems.push({ product_id:product.id, quantity:1 })
        cartStore.setCount(this.cartItems.length)
        this.showToast(`${product.name} added! 🛒`)
      } catch(e) { this.showToast(e.response?.data?.error || "Error") }
    },
    async updateQty({ product, delta, currentQty }) {
      const newQty = currentQty + delta
      const item = this.cartItems.find(i => i.product_id === product.id)
      if (newQty <= 0 && item) {
        await removeFromCart(item.id)
        this.cartItems = this.cartItems.filter(i => i.product_id !== product.id)
        cartStore.setCount(this.cartItems.length)
      } else if (item) {
        await updateCartItem(item.id, { quantity:newQty }); item.quantity = newQty
      }
    },
    showToast(m) { this.toast = m; setTimeout(() => this.toast = "", 2000) }
  }
}
</script>

<style scoped>
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
.fm-search-page {
  display:flex; align-items:center; gap:10px;
  background:#fff; border:2px solid #e5e7eb; border-radius:14px;
  padding:10px 14px;
}
.fm-search-page:focus-within { border-color:var(--fm-green); }
.fm-search-page i { color:var(--fm-gray-500); }
.fm-search-page input { flex:1; border:none; outline:none; font-size:15px; background:transparent; }
.fm-search-page button { background:none; border:none; color:var(--fm-gray-500); cursor:pointer; padding:0; }

.fm-cats-scroll { display:flex; gap:8px; overflow-x:auto; padding-bottom:4px; }
.fm-cats-scroll::-webkit-scrollbar { display:none; }
.fm-cat-tab { padding:7px 16px; border-radius:20px; border:2px solid var(--fm-gray-200); background:#fff; font-size:13px; font-weight:700; font-family:"Nunito",sans-serif; cursor:pointer; white-space:nowrap; transition:.2s; }
.fm-cat-tab:hover { border-color:var(--fm-green); color:var(--fm-green); }
.fm-cat-tab.active { background:var(--fm-green); color:#fff; border-color:var(--fm-green); }

.fm-products-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; }
@media(min-width:576px){.fm-products-grid{grid-template-columns:repeat(3,1fr)}}
@media(min-width:768px){.fm-products-grid{grid-template-columns:repeat(4,1fr)}}

.fm-empty-state { text-align:center; padding:64px 16px; }
.fm-toast { position:fixed;bottom:90px;left:50%;transform:translateX(-50%);background:#1f2937;color:#fff;padding:10px 20px;border-radius:20px;font-size:13px;font-weight:600;z-index:8000;white-space:nowrap; }
.toast-slide-enter-active,.toast-slide-leave-active{transition:.3s}
.toast-slide-enter-from,.toast-slide-leave-to{opacity:0;transform:translate(-50%,10px)}
</style>

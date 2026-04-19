<template>
  <nav class="fm-navbar">
    <div class="fm-navbar-inner">

      <!-- Left: Logo -->
      <router-link to="/" class="fm-logo">
        <span class="fm-logo-icon">🥦</span>
        <span class="fm-logo-text">FreshMart</span>
      </router-link>

      <!-- Center: Search (customer only) -->
      <div v-if="role === 'customer'" class="fm-search-wrap">
        <i class="bi bi-search fm-search-icon"></i>
        <input
          v-model="searchQuery"
          class="fm-search-input"
          placeholder="Search for fruits, vegetables..."
          @keyup.enter="goSearch"
          @focus="searchFocused = true"
          @blur="searchFocused = false"
        />
        <button v-if="searchQuery" class="fm-search-clear" @click="searchQuery = ''">
          <i class="bi bi-x"></i>
        </button>
      </div>

      <!-- Center: Role label (non-customer) -->
      <div v-else class="fm-role-label">
        <span v-if="role === 'admin'">⚙️ Admin Panel</span>
        <span v-else-if="role === 'packer'">📦 Packing Station</span>
        <span v-else-if="role === 'delivery'">🚚 Delivery Hub</span>
      </div>

      <!-- Right: Actions -->
      <div class="fm-nav-actions">

        <!-- Cart (customer) -->
        <router-link v-if="role === 'customer'" to="/cart" class="fm-cart-btn">
          <i class="bi bi-cart3"></i>
          <span v-if="cartCount > 0" class="fm-cart-badge">{{ cartCount }}</span>
        </router-link>

        <!-- User pill -->
        <div class="fm-user-pill" @click="menuOpen = !menuOpen" ref="userPill">
          <div class="fm-avatar">{{ initials }}</div>
          <span class="fm-user-name d-none d-md-block">{{ userName }}</span>
          <i class="bi bi-chevron-down fm-chevron" :class="{ rotated: menuOpen }"></i>
        </div>

        <!-- Dropdown menu -->
        <div v-if="menuOpen" class="fm-dropdown" @click.stop>
          <div class="fm-dropdown-header">
            <div class="fm-avatar lg">{{ initials }}</div>
            <div>
              <div class="fw-bold">{{ userName }}</div>
              <span class="fm-role-badge">{{ role }}</span>
            </div>
          </div>
          <hr class="my-2" />
          <router-link v-if="role==='customer'" to="/orders" class="fm-dropdown-item" @click="menuOpen=false">
            <i class="bi bi-box-seam"></i> My Orders
          </router-link>
          <router-link v-if="role==='admin'" to="/admin" class="fm-dropdown-item" @click="menuOpen=false">
            <i class="bi bi-speedometer2"></i> Dashboard
          </router-link>
          <button class="fm-dropdown-item danger" @click="logout">
            <i class="bi bi-box-arrow-right"></i> Logout
          </button>
        </div>
      </div>
    </div>

    <!-- Sub-nav for admin -->
    <div v-if="role === 'admin'" class="fm-subnav">
      <router-link to="/admin"           class="fm-subnav-link"><i class="bi bi-grid"></i> Dashboard</router-link>
      <router-link to="/admin/orders"    class="fm-subnav-link"><i class="bi bi-receipt"></i> Orders</router-link>
      <router-link to="/admin/products"  class="fm-subnav-link"><i class="bi bi-basket"></i> Products</router-link>
      <router-link to="/admin/inventory" class="fm-subnav-link"><i class="bi bi-boxes"></i> Inventory</router-link>
      <router-link to="/admin/analytics" class="fm-subnav-link"><i class="bi bi-bar-chart"></i> Analytics</router-link>
    </div>
  </nav>
</template>

<script>
import { cartStore } from "../stores/cart.js"
import { getCart } from "../services/cartService.js"

export default {
  name: "Navbar",
  data() { return { searchQuery: "", menuOpen: false, searchFocused: false } },
  computed: {
    role()      { return localStorage.getItem("role") || "" },
    userName()  { try { return JSON.parse(localStorage.getItem("user"))?.name || "User" } catch { return "User" } },
    initials()  { return this.userName.split(" ").map(w => w[0]).join("").slice(0,2).toUpperCase() },
    cartCount() { return cartStore.count }
  },
  async mounted() {
    if (this.role === "customer") {
      try { const r = await getCart(); cartStore.setCount(r.data.items?.length || 0) } catch {}
    }
    document.addEventListener("click", this.closeMenu)
  },
  beforeUnmount() { document.removeEventListener("click", this.closeMenu) },
  methods: {
    goSearch() {
      if (this.searchQuery.trim())
        this.$router.push({ path: "/products", query: { search: this.searchQuery } })
    },
    logout()  { localStorage.clear(); cartStore.setCount(0); this.$router.push("/login") },
    closeMenu(e) { if (!this.$refs.userPill?.contains(e.target)) this.menuOpen = false }
  }
}
</script>

<style scoped>
.fm-navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,.1);
}
.fm-navbar-inner {
  max-width: 1200px; margin: 0 auto;
  display: flex; align-items: center; gap: 16px;
  padding: 10px 16px;
}

/* Logo */
.fm-logo { display:flex; align-items:center; gap:8px; text-decoration:none; flex-shrink:0; }
.fm-logo-icon { font-size:26px; }
.fm-logo-text { font-family:"Nunito",sans-serif; font-weight:900; font-size:20px; color:var(--fm-green); }

/* Search */
.fm-search-wrap {
  flex:1; position:relative; max-width:500px;
}
.fm-search-icon {
  position:absolute; left:12px; top:50%; transform:translateY(-50%);
  color:var(--fm-gray-500); font-size:14px;
}
.fm-search-input {
  width:100%; padding:9px 36px 9px 36px;
  border:2px solid var(--fm-gray-200); border-radius:10px;
  font-family:"DM Sans",sans-serif; font-size:14px;
  outline:none; transition:.2s;
  background: var(--fm-gray-50);
}
.fm-search-input:focus { border-color:var(--fm-green); background:#fff; }
.fm-search-clear {
  position:absolute; right:10px; top:50%; transform:translateY(-50%);
  background:none; border:none; color:var(--fm-gray-500); cursor:pointer; padding:0;
}
.fm-role-label { flex:1; font-family:"Nunito",sans-serif; font-weight:700; font-size:16px; color:var(--fm-gray-500); }

/* Actions */
.fm-nav-actions { display:flex; align-items:center; gap:10px; flex-shrink:0; position:relative; }
.fm-cart-btn {
  position:relative; width:40px; height:40px; display:flex; align-items:center; justify-content:center;
  border-radius:10px; background:var(--fm-green-light); color:var(--fm-green);
  text-decoration:none; font-size:18px; transition:.2s;
}
.fm-cart-btn:hover { background:var(--fm-green); color:#fff; }
.fm-cart-badge {
  position:absolute; top:-4px; right:-4px;
  background:var(--fm-orange); color:#fff;
  font-size:10px; font-weight:800; font-family:"Nunito",sans-serif;
  width:18px; height:18px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  border:2px solid #fff;
}
.fm-user-pill {
  display:flex; align-items:center; gap:8px;
  padding:5px 10px 5px 5px; border-radius:20px;
  border:2px solid var(--fm-gray-200); cursor:pointer;
  transition:.2s; user-select:none;
}
.fm-user-pill:hover { border-color:var(--fm-green); }
.fm-avatar {
  width:30px; height:30px; border-radius:50%;
  background:var(--fm-green); color:#fff;
  display:flex; align-items:center; justify-content:center;
  font-family:"Nunito",sans-serif; font-weight:800; font-size:12px;
}
.fm-avatar.lg { width:40px; height:40px; font-size:16px; }
.fm-user-name { font-size:13px; font-weight:600; max-width:100px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.fm-chevron { font-size:12px; transition:transform .2s; color:var(--fm-gray-500); }
.fm-chevron.rotated { transform:rotate(180deg); }

/* Dropdown */
.fm-dropdown {
  position:absolute; top:calc(100% + 8px); right:0; min-width:220px;
  background:#fff; border-radius:12px; box-shadow:var(--fm-shadow-lg);
  border:1px solid var(--fm-gray-200); padding:12px; z-index:2000;
}
.fm-dropdown-header { display:flex; align-items:center; gap:10px; }
.fm-role-badge {
  font-size:10px; font-weight:700; text-transform:uppercase;
  background:var(--fm-green-light); color:var(--fm-green);
  padding:2px 8px; border-radius:20px; font-family:"Nunito",sans-serif;
}
.fm-dropdown-item {
  display:flex; align-items:center; gap:10px;
  padding:9px 10px; border-radius:8px;
  font-size:14px; font-weight:600; color:var(--fm-text);
  text-decoration:none; cursor:pointer;
  background:none; border:none; width:100%; text-align:left;
  transition:.15s;
}
.fm-dropdown-item:hover { background:var(--fm-gray-100); }
.fm-dropdown-item.danger { color:#dc2626; }
.fm-dropdown-item.danger:hover { background:#fef2f2; }

/* Subnav */
.fm-subnav {
  display:flex; gap:4px; overflow-x:auto;
  padding:0 16px 8px; border-top:1px solid var(--fm-gray-100);
  max-width:1200px; margin:0 auto;
}
.fm-subnav-link {
  display:flex; align-items:center; gap:6px;
  padding:6px 14px; border-radius:20px;
  font-size:13px; font-weight:700; font-family:"Nunito",sans-serif;
  color:var(--fm-gray-500); text-decoration:none; white-space:nowrap;
  transition:.15s;
}
.fm-subnav-link:hover { color:var(--fm-green); background:var(--fm-green-light); }
.fm-subnav-link.router-link-active { color:var(--fm-green); background:var(--fm-green-light); }
</style>

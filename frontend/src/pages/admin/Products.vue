<template>
  <div class="fade-in-up">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5 class="fw-bold mb-0">Products</h5>
      <button class="btn btn-fm-green btn-sm px-3" @click="openAdd">+ Add Product</button>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else class="fm-card overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead style="background:#f9fafb">
            <tr>
              <th class="ps-4">Product</th>
              <th>Category</th>
              <th>Base Price</th>
              <th>Discount</th>
              <th>Unit</th>
              <th>Weight & Prices</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in products" :key="p.id">
              <td class="ps-4">
                <div class="d-flex align-items-center gap-2">
                  <div class="fm-prod-thumb" :style="`background:${thumbBg(p.id)}`">
                    {{ emoji(p.name) }}
                  </div>
                  <span class="fw-semibold">{{ p.name }}</span>
                </div>
              </td>
              <td><span class="badge" style="background:#e0f2fe;color:#0369a1">{{ p.category }}</span></td>
              <td class="fw-bold">₹{{ p.price }}</td>
              <td>
                <span v-if="p.discount>0" class="badge bg-warning text-dark">{{ p.discount }}%</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td class="text-muted small">{{ p.unit }}</td>
              <td>
                <div v-if="p.weight_options && p.weight_options.length" class="d-flex flex-wrap gap-1">
                  <span v-for="w in p.weight_options" :key="w" class="fm-weight-price-badge">
                    {{ w }}
                    <span v-if="p.weight_prices && p.weight_prices[w]" class="fm-weight-price-amount">₹{{ p.weight_prices[w] }}</span>
                  </span>
                </div>
                <span v-else class="text-muted small">—</span>
              </td>
              <td>
                <span :class="p.is_active ? 'fm-badge-active' : 'fm-badge-inactive'">
                  {{ p.is_active ? "Active" : "Inactive" }}
                </span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-1" @click="openEdit(p)">Edit</button>
                <button class="btn btn-sm btn-outline-danger" @click="deactivate(p.id)">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Product Modal -->
    <div v-if="showModal" class="fm-modal-bg" @click.self="showModal=false">
      <div class="fm-modal fade-in-up" style="max-width:520px;max-height:90vh;overflow-y:auto">
        <h6 class="fw-bold mb-4">{{ editMode ? "✏️ Edit Product" : "➕ Add Product" }}</h6>
        <div v-if="formError" class="alert alert-danger py-2 small">{{ formError }}</div>

        <div class="row g-3">
          <div class="col-12">
            <label class="fm-label">Product Name</label>
            <input v-model="form.name" class="fm-input" placeholder="e.g. Fresh Apple" />
          </div>
          <div class="col-12">
            <label class="fm-label">Description</label>
            <input v-model="form.description" class="fm-input" placeholder="Short description" />
          </div>
          <div class="col-12">
            <label class="fm-label">Category</label>
            <select v-model="form.category_id" class="fm-input">
              <option value="" disabled>Select category</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="col-6">
            <label class="fm-label">Base Price (₹)</label>
            <input v-model="form.price" type="number" class="fm-input" placeholder="0" />
            <div class="text-muted" style="font-size:11px;margin-top:4px">Used when no weight is selected</div>
          </div>
          <div class="col-6">
            <label class="fm-label">Discount (%)</label>
            <input v-model="form.discount" type="number" class="fm-input" placeholder="0" min="0" max="90" />
          </div>
          <div class="col-6">
            <label class="fm-label">Unit</label>
            <select v-model="form.unit" class="fm-input">
              <option>kg</option><option>dozen</option>
              <option>piece</option><option>bundle</option>
            </select>
          </div>
          <div class="col-6">
            <label class="fm-label">Status</label>
            <select v-model="form.is_active" class="fm-input">
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
          </div>

          <!-- Weight Options + per-weight prices -->
          <div class="col-12">
            <label class="fm-label">Weight Options & Prices</label>
            <p class="text-muted" style="font-size:12px;margin-bottom:10px">Select weights and set a price for each variant</p>
            <div class="fm-weight-price-list">
              <div v-for="w in weightChoices" :key="w" class="fm-weight-price-row" :class="{ active: form.weight_options.includes(w) }">
                <label class="fm-weight-toggle" :class="{ selected: form.weight_options.includes(w) }" @click="toggleWeight(w)">
                  {{ w }}
                </label>
                <div class="fm-weight-price-input-wrap" v-if="form.weight_options.includes(w)">
                  <span class="fm-rupee">₹</span>
                  <input
                    type="number"
                    class="fm-price-input"
                    placeholder="Price"
                    :value="form.weight_prices[w] || ''"
                    @input="setWeightPrice(w, $event.target.value)"
                    min="0"
                  />
                </div>
                <div v-else class="fm-weight-price-placeholder">— not available —</div>
              </div>
            </div>
          </div>

          <div class="col-12">
            <label class="fm-label">Image URL (optional)</label>
            <input v-model="form.image_url" class="fm-input" placeholder="https://..." />
          </div>
        </div>

        <div class="d-flex gap-2 mt-4">
          <button class="btn btn-outline-secondary flex-fill" @click="showModal=false">Cancel</button>
          <button class="btn btn-fm-green flex-fill" @click="save" :disabled="saving">
            {{ saving ? "Saving..." : "Save Product" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getProducts, addProduct, updateProduct, deleteProduct, getCategories } from "../../services/productService.js"

const EMOJIS = {apple:"🍎",banana:"🍌",mango:"🥭",orange:"🍊",tomato:"🍅",potato:"🥔",onion:"🧅",carrot:"🥕",spinach:"🥬",coriander:"🌿",default:"🛒"}
const COLORS = ["#fef3c7","#dcfce7","#fee2e2","#e0f2fe","#fce7f3","#ede9fe"]
const WEIGHT_CHOICES = ["50g","100g","250g","500g","750g","1kg"]
const blank = () => ({ name:"",description:"",category_id:"",price:"",discount:0,unit:"kg",image_url:"",is_active:true,weight_options:[],weight_prices:{} })

export default {
  data() {
    return { products:[], categories:[], loading:true, showModal:false, editMode:false, editId:null, form:blank(), formError:"", saving:false, weightChoices:WEIGHT_CHOICES }
  },
  async mounted() {
    const [pr,cr] = await Promise.all([getProducts(), getCategories()])
    this.products = pr.data; this.categories = cr.data; this.loading = false
  },
  methods: {
    emoji(name)    { return EMOJIS[name?.toLowerCase()] || EMOJIS.default },
    thumbBg(id)    { return COLORS[id % COLORS.length] },
    openAdd()      { this.editMode=false; this.editId=null; this.form=blank(); this.formError=""; this.showModal=true },
    openEdit(p) {
      this.editMode=true; this.editId=p.id
      this.form = {
        ...p,
        weight_options: Array.isArray(p.weight_options) ? [...p.weight_options] : [],
        weight_prices: p.weight_prices ? {...p.weight_prices} : {}
      }
      this.formError=""; this.showModal=true
    },
    toggleWeight(w) {
      const idx = this.form.weight_options.indexOf(w)
      if (idx === -1) {
        this.form.weight_options.push(w)
      } else {
        this.form.weight_options.splice(idx, 1)
        const prices = { ...this.form.weight_prices }
        delete prices[w]
        this.form.weight_prices = prices
      }
    },
    setWeightPrice(w, val) {
      this.form.weight_prices = { ...this.form.weight_prices, [w]: val ? parseFloat(val) : '' }
    },
    async save() {
      if (!this.form.name || !this.form.price) { this.formError="Name and price are required."; return }
      // Validate: all selected weights must have a price
      const missing = this.form.weight_options.filter(w => !this.form.weight_prices[w])
      if (missing.length) { this.formError=`Please set a price for: ${missing.join(', ')}`; return }
      this.saving=true; this.formError=""
      try {
        if (this.editMode) await updateProduct(this.editId, this.form)
        else await addProduct(this.form)
        const r = await getProducts(); this.products = r.data; this.showModal=false
      } catch(e) { this.formError = e.response?.data?.error || "Error saving." }
      finally { this.saving=false }
    },
    async deactivate(id) {
      if (!confirm("Remove this product?")) return
      await deleteProduct(id); this.products = this.products.filter(p => p.id !== id)
    }
  }
}
</script>

<style scoped>
.fm-prod-thumb { width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0; }
.fm-badge-active   { background:#dcfce7;color:#166534;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;font-family:"Nunito",sans-serif; }
.fm-badge-inactive { background:#fee2e2;color:#991b1b;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;font-family:"Nunito",sans-serif; }
.fm-label { font-size:13px;font-weight:600;display:block;margin-bottom:6px;color:#374151; }
.fm-input { width:100%;padding:10px 13px;border:2px solid #e5e7eb;border-radius:10px;font-size:14px;outline:none;transition:.2s; }
.fm-input:focus { border-color:var(--fm-green); }
.fm-modal-bg { position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:2000;display:flex;align-items:center;justify-content:center;padding:16px; }
.fm-modal    { background:#fff;border-radius:20px;padding:28px;width:100%; }

/* Weight + price list */
.fm-weight-price-list { display:flex;flex-direction:column;gap:8px; }
.fm-weight-price-row  { display:flex;align-items:center;gap:10px; }
.fm-weight-toggle {
  width:60px;flex-shrink:0;text-align:center;
  padding:5px 0;border-radius:20px;border:2px solid #e5e7eb;
  font-size:12px;font-weight:700;font-family:"Nunito",sans-serif;
  cursor:pointer;transition:.15s;user-select:none;
  background:#fff;color:#9ca3af;
}
.fm-weight-toggle:hover  { border-color:var(--fm-green);color:var(--fm-green); }
.fm-weight-toggle.selected { background:var(--fm-green);color:#fff;border-color:var(--fm-green); }
.fm-weight-price-input-wrap { display:flex;align-items:center;border:2px solid var(--fm-green);border-radius:10px;overflow:hidden;flex:1; }
.fm-rupee { padding:0 8px;font-weight:700;color:var(--fm-green);font-size:14px;background:#f0fdf4; }
.fm-price-input { flex:1;border:none;outline:none;padding:7px 10px;font-size:14px;font-weight:600; }
.fm-weight-price-placeholder { flex:1;font-size:12px;color:#d1d5db;font-style:italic; }

/* Table weight+price badges */
.fm-weight-price-badge { display:inline-flex;align-items:center;gap:4px;background:#f0fdf4;border:1px solid #bbf7d0;color:#166534;font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;font-family:"Nunito",sans-serif; }
.fm-weight-price-amount { color:var(--fm-green);font-weight:800; }
</style>

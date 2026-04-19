<template>
  <div class="fm-product-card" @click="handleClick">
    
    <!-- Discount ribbon -->
    <div v-if="product.discount > 0" class="fm-discount-tag">
      {{ product.discount }}% OFF
    </div>

    <!-- Image -->
    <div class="fm-product-img-wrap" :style="{ background: bgColor }">
      <img
        v-if="imgOk"
        :src="product.image_url"
        :alt="product.name"
        class="fm-product-img"
        @error="imgOk = false"
      />
      <div v-else class="fm-product-emoji">{{ emoji }}</div>
    </div>

    <!-- Info -->
    <div class="fm-product-info">

      <div class="fm-product-name">{{ product.name }}</div>

      <!-- Weight selector -->
      <div
        v-if="product.weight_options && product.weight_options.length"
        class="fm-weight-row"
        @click.stop
      >
        <button
          v-for="w in product.weight_options"
          :key="w"
          class="fm-weight-chip"
          :class="{ active: selectedWeight === w }"
          @click.stop="selectedWeight = w"
        >
          {{ w }}
        </button>
      </div>

      <div v-else class="fm-product-weight text-muted">
        {{ product.unit }}
      </div>

      <!-- Footer -->
      <div class="fm-product-footer">

        <div class="fm-price-block">
          <span class="fm-price">₹{{ finalPrice }}</span>
          <span v-if="product.discount > 0" class="fm-price-original">
            ₹{{ originalPrice }}
          </span>
        </div>

        <!-- Qty control -->
        <div v-if="qty > 0" class="fm-qty-ctrl">
          <button class="fm-qty-btn" @click.stop="change(-1)">−</button>
          <span class="fm-qty-num">{{ qty }}</span>
          <button class="fm-qty-btn plus" @click.stop="change(1)">+</button>
        </div>

        <!-- Add button -->
        <button
          v-else
          class="fm-add-btn"
          @click.stop="addToCart"
        >
          <i class="bi bi-plus"></i> Add
        </button>

      </div>
    </div>
  </div>
</template>

<script>
const EMOJIS = {
  apple:"🍎", banana:"🍌", mango:"🥭", orange:"🍊", grape:"🍇",
  tomato:"🍅", potato:"🥔", onion:"🧅", carrot:"🥕", spinach:"🥬",
  coriander:"🌿", broccoli:"🥦", corn:"🌽", pepper:"🫑", lemon:"🍋",
  watermelon:"🍉", pineapple:"🍍", strawberry:"🍓", default:"🛒"
}

const COLORS = ["#fef3c7","#dcfce7","#fee2e2","#e0f2fe","#fce7f3","#ede9fe","#fef9c3","#ecfdf5"]

export default {
  name: "ProductCard",

  props: {
    product: Object,
    cartItems: { type: Array, default: () => [] }
  },

  emits: ["add-to-cart", "update-qty", "view"],

  data() {
    return {
      imgOk: !!this.product.image_url,
      selectedWeight:
        this.product.weight_options?.length
          ? this.product.weight_options[0]
          : null
    }
  },

  computed: {
    weightBasePrice() {
      if (
        this.selectedWeight &&
        this.product.weight_prices?.[this.selectedWeight]
      ) {
        return parseFloat(this.product.weight_prices[this.selectedWeight])
      }
      return this.product.price
    },

    finalPrice() {
      return (
        this.weightBasePrice *
        (1 - (this.product.discount || 0) / 100)
      ).toFixed(0)
    },

    originalPrice() {
      return this.weightBasePrice
    },

    emoji() {
      return EMOJIS[this.product.name?.toLowerCase()] || EMOJIS.default
    },

    bgColor() {
      return COLORS[(this.product.id || 0) % COLORS.length]
    },

    qty() {
      const item = this.cartItems.find(
        i =>
          i.product_id === this.product.id &&
          i.selected_weight === this.selectedWeight
      )
      return item ? item.quantity : 0
    }
  },

  methods: {
    handleClick() {
      this.$emit("view", this.product)
      this.$router.push(`/product/${this.product.id}`)
    },

    change(delta) {
      this.$emit("update-qty", {
        product: this.product,
        delta,
        currentQty: this.qty,
        selectedWeight: this.selectedWeight
      })
    },

    addToCart() {
      this.$emit("add-to-cart", {
        product: this.product,
        selectedWeight: this.selectedWeight,
        finalPrice: Number(this.finalPrice)
      })
    }
  }
}
</script>

<style scoped>
/* Card */
.fm-product-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform .2s, box-shadow .2s;
  box-shadow: 0 1px 6px rgba(0,0,0,.07);
  display: flex;
  flex-direction: column;
}
.fm-product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,.12);
}

/* Discount */
.fm-discount-tag {
  position:absolute;
  top:8px; left:8px;
  background:var(--fm-orange);
  color:#fff;
  font-size:10px;
  font-weight:800;
  padding:2px 7px;
  border-radius:20px;
}

/* Image */
.fm-product-img-wrap {
  height:130px;
  display:flex;
  align-items:center;
  justify-content:center;
}
.fm-product-img { width:100%; height:100%; object-fit:cover; }
.fm-product-emoji { font-size:3.5rem; }

/* Info */
.fm-product-info {
  padding:10px;
  display:flex;
  flex-direction:column;
  gap:4px;
}

.fm-product-name {
  font-weight:700;
  font-size:14px;
}

/* Weight */
.fm-weight-row {
  display:flex;
  gap:4px;
}
.fm-weight-chip {
  padding:2px 8px;
  border-radius:12px;
  border:1px solid #ddd;
  font-size:11px;
  cursor:pointer;
}
.fm-weight-chip.active {
  background:var(--fm-green);
  color:#fff;
}

/* Footer */
.fm-product-footer {
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-top:auto;
}

.fm-price { font-weight:800; }
.fm-price-original {
  font-size:11px;
  text-decoration:line-through;
}

/* Button */
.fm-add-btn {
  background:var(--fm-green);
  color:#fff;
  border:none;
  padding:5px 12px;
  border-radius:8px;
}

/* Qty */
.fm-qty-ctrl {
  display:flex;
  gap:6px;
  background:var(--fm-green);
  padding:3px;
  border-radius:8px;
}
.fm-qty-btn {
  width:24px;
  height:24px;
  border:none;
  color:#fff;
  background:rgba(255,255,255,.2);
}
</style>
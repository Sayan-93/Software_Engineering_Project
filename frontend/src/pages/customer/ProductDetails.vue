<template>
    <div v-if="product" class="fm-card p-4">
  <h4 class="fw-bold">{{ product.name }}</h4>
  <p class="text-muted">{{ product.description }}</p>
  <div class="fw-bold text-success">₹{{ product.price }}</div>
</div>

<div v-if="recommendations.length" class="mt-5">
  <h5 class="fw-bold mb-3">🧠 You may also like</h5>

  <div class="row g-3">
    <div v-for="r in recommendations" :key="r.id" class="col-md-3">
      <div class="fm-card p-3 h-100">
        <div class="fw-semibold">{{ r.name }}</div>
        <div class="text-muted small">{{ r.description }}</div>
        <div class="fw-bold text-success">₹{{ r.price }}</div>
      </div>
    </div>
  </div>
</div>
</template>


<script>
import { getProduct, getRecommendations } from "../../services/productService"

export default {
  data() {
    return {
      product: null,
      recommendations: []
    }
  },

  async mounted() {
    const id = this.$route.params.id

    const res = await getProduct(id)
    this.product = res.data

    if (!this.product) {
      return
    }

    const rec = await getRecommendations(this.product.id)
    this.recommendations = rec.data
  }
}
</script>

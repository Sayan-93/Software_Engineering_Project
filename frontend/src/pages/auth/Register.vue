<template>
  <div class="auth-bg d-flex align-items-center justify-content-center min-vh-100" style="background:#f0fdf4">
    <div class="auth-card fade-in-up">
      <div class="text-center mb-4">
        <div style="font-size:3rem">🥦</div>
        <h3 class="mt-2 mb-1">Create Account</h3>
        <p class="text-muted small">Join FreshMart for fresh groceries</p>
      </div>

      <div v-if="error"   class="auth-error">{{ error }}</div>
      <div v-if="success" class="auth-success"><i class="bi bi-check-circle-fill me-2"></i>{{ success }}</div>

      <div class="row g-3">
        <div class="col-12">
          <label class="form-label small fw-semibold">Full Name</label>
          <input v-model="form.name" class="auth-input" placeholder="Your full name" />
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-semibold">Email</label>
          <input v-model="form.email" type="email" class="auth-input" placeholder="you@example.com" />
        </div>
        <div class="col-md-6">
          <label class="form-label small fw-semibold">Phone</label>
          <input v-model="form.phone" class="auth-input" placeholder="10-digit number" />
        </div>
        <div class="col-12">
          <label class="form-label small fw-semibold">Delivery Address</label>
          <input v-model="form.address" class="auth-input" placeholder="Your address" />
        </div>
        <div class="col-12">
          <label class="form-label small fw-semibold">Flat / Unit Number</label>
          <input v-model="form.flat_unit_number" class="auth-input" placeholder="e.g. Flat 3B, Unit 12" />
        </div>
        <div class="col-12">
          <label class="form-label small fw-semibold">Password</label>
          <input v-model="form.password" type="password" class="auth-input" placeholder="Min. 6 characters" />
        </div>
      </div>

      <button class="auth-btn mt-4" @click="register" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
        {{ loading ? "Creating..." : "Create Account →" }}
      </button>

      <p class="text-center small text-muted mt-3 mb-0">
        Already have an account? <router-link to="/login" class="text-success fw-bold">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { register } from "../../services/authService.js"
export default {
  data() { return { form:{name:"",email:"",phone:"",address:"",flat_unit_number:"",password:""}, loading:false, error:"", success:"" } },
  methods: {
    async register() {
      this.error = ""; this.success = ""
      const {name, email, password, phone, address, flat_unit_number} = this.form
      if (!name||!email||!password) { this.error="Name, email and password are required."; return }
      if (!phone||!address||!flat_unit_number) { this.error="Phone, delivery address and flat/unit number are required."; return }
      this.loading = true
      try {
        await register({...this.form, role:"customer"})
        this.success = "Account created! Redirecting to login..."
        setTimeout(() => this.$router.push("/login"), 1500)
      } catch(e) { this.error = e.response?.data?.error || "Registration failed." }
      finally { this.loading = false }
    }
  }
}
</script>

<style scoped>
.auth-card { background:#fff; border-radius:20px; padding:40px 36px; width:100%; max-width:480px; box-shadow:0 8px 32px rgba(0,0,0,.1); }
.auth-input { width:100%; padding:11px 14px; border:2px solid #e5e7eb; border-radius:10px; font-size:14px; outline:none; transition:.2s; }
.auth-input:focus { border-color:var(--fm-green); box-shadow:0 0 0 3px rgba(13,119,64,.1); }
.auth-btn { width:100%; padding:13px; border-radius:12px; border:none; background:var(--fm-green); color:#fff; font-family:"Nunito",sans-serif; font-weight:800; font-size:15px; cursor:pointer; transition:.2s; }
.auth-btn:hover:not(:disabled) { background:var(--fm-green-dark); }
.auth-error   { background:#fef2f2; border:1px solid #fecaca; color:#dc2626; border-radius:10px; padding:10px 14px; font-size:13px; margin-bottom:16px; }
.auth-success { background:#f0fdf4; border:1px solid #bbf7d0; color:#166534; border-radius:10px; padding:10px 14px; font-size:13px; margin-bottom:16px; }
</style>

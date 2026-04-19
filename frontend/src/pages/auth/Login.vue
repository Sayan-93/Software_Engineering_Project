<template>
  <div class="auth-bg">
    <div class="auth-left d-none d-md-flex">
      <div class="auth-brand fade-in-up">
        <div style="font-size:5rem;margin-bottom:16px">🥦</div>
        <h1>FreshMart</h1>
        <p>Fresh fruits & vegetables delivered in minutes, straight from our warehouse to your door.</p>
        <div class="auth-features">
          <div class="auth-feature"><span>⚡</span> 30-min delivery</div>
          <div class="auth-feature"><span>🌱</span> Farm fresh daily</div>
          <div class="auth-feature"><span>💯</span> Quality guaranteed</div>
        </div>
      </div>
    </div>

    <div class="auth-right">
      <div class="auth-card fade-in-up">
        <div class="text-center mb-4">
          <span style="font-size:2.5rem">👋</span>
          <h3 class="mt-2 mb-1">Welcome back!</h3>
          <p class="text-muted small">Login to continue shopping</p>
        </div>

        <div v-if="error" class="auth-error">
          <i class="bi bi-exclamation-circle-fill me-2"></i>{{ error }}
        </div>

        <div class="fm-input-group">
          <label>Email address</label>
          <div class="fm-input-wrap">
            <i class="bi bi-envelope"></i>
            <input v-model="email" type="email" placeholder="you@example.com" @keyup.enter="login" />
          </div>
        </div>

        <div class="fm-input-group">
          <label>Password</label>
          <div class="fm-input-wrap">
            <i class="bi bi-lock"></i>
            <input v-model="password" :type="showPwd ? 'text' : 'password'" placeholder="••••••••" @keyup.enter="login" />
            <button class="pwd-toggle" @click="showPwd = !showPwd" type="button">
              <i :class="showPwd ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
            </button>
          </div>
        </div>

        <button class="auth-btn" @click="login" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? "Logging in..." : "Login →" }}
        </button>

        <p class="text-center small text-muted mt-3 mb-3">
          New here? <router-link to="/register" class="text-success fw-bold">Create account</router-link>
        </p>

        <div class="demo-box">
          <div class="demo-title">🧪 Demo Accounts</div>
          <div class="demo-row" v-for="d in demos" :key="d.role" @click="fillDemo(d)">
            <span class="demo-icon">{{ d.icon }}</span>
            <div>
              <div class="demo-role">{{ d.role }}</div>
              <div class="demo-cred">{{ d.email }}</div>
            </div>
            <span class="demo-pwd">{{ d.pwd }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { login } from "../../services/authService.js"
import { getDashboard } from "../../router/index.js"

export default {
  data() {
    return {
      email:"", password:"", loading:false, error:"", showPwd:false,
      demos:[
        { icon:"⚙️", role:"Admin",    email:"admin@freshmart.com",  pwd:"admin123" },
        { icon:"🛒", role:"Customer", email:"rahul@example.com",    pwd:"customer123" },
        { icon:"📦", role:"Packer",   email:"kumar@freshmart.com",  pwd:"packer123" },
        { icon:"🚚", role:"Delivery", email:"arun@freshmart.com",   pwd:"delivery123" },
      ]
    }
  },
  methods: {
    fillDemo(d) { this.email = d.email; this.password = d.pwd },
    async login() {
      this.error = ""
      if (!this.email || !this.password) { this.error = "Please enter email and password."; return }
      this.loading = true
      try {
        const res = await login({ email:this.email, password:this.password })
        localStorage.setItem("token", res.data.token)
        localStorage.setItem("role",  res.data.role)
        localStorage.setItem("user",  JSON.stringify(res.data.user))
        this.$router.push(getDashboard(res.data.role))
      } catch(e) { this.error = e.response?.data?.error || "Invalid credentials." }
      finally { this.loading = false }
    }
  }
}
</script>

<style scoped>
.auth-bg { min-height:100vh; display:flex; }
.auth-left {
  flex:1; background:linear-gradient(135deg,#085c2f,#0d7740);
  display:flex; align-items:center; justify-content:center; padding:48px;
  color:#fff;
}
.auth-brand h1 { font-family:"Nunito",sans-serif; font-weight:900; font-size:2.5rem; }
.auth-brand p  { opacity:.85; font-size:1.1rem; margin:16px 0 24px; line-height:1.7; }
.auth-features { display:flex; flex-direction:column; gap:12px; }
.auth-feature  { display:flex; align-items:center; gap:10px; font-weight:600; opacity:.9; font-size:15px; }

.auth-right {
  width:100%; max-width:480px;
  display:flex; align-items:center; justify-content:center;
  padding:32px 24px; background:#f9fafb;
}
.auth-card { width:100%; max-width:400px; }

.auth-error {
  background:#fef2f2; border:1px solid #fecaca; color:#dc2626;
  border-radius:10px; padding:10px 14px; font-size:13px; margin-bottom:16px;
}

.fm-input-group { margin-bottom:16px; }
.fm-input-group label { font-size:13px; font-weight:600; color:#374151; display:block; margin-bottom:6px; }
.fm-input-wrap {
  position:relative; display:flex; align-items:center;
  background:#fff; border:2px solid #e5e7eb; border-radius:12px; transition:.2s;
}
.fm-input-wrap:focus-within { border-color:var(--fm-green); box-shadow:0 0 0 3px rgba(13,119,64,.1); }
.fm-input-wrap > i { position:absolute; left:14px; color:#9ca3af; font-size:15px; }
.fm-input-wrap input {
  flex:1; border:none; outline:none; padding:12px 14px 12px 38px;
  background:transparent; font-size:15px; border-radius:12px;
}
.pwd-toggle {
  background:none; border:none; padding:0 14px; color:#9ca3af; cursor:pointer; font-size:15px;
}

.auth-btn {
  width:100%; padding:14px; border-radius:12px; border:none;
  background:var(--fm-green); color:#fff;
  font-family:"Nunito",sans-serif; font-weight:800; font-size:16px;
  cursor:pointer; transition:.2s; margin-top:4px;
}
.auth-btn:hover:not(:disabled) { background:var(--fm-green-dark); transform:translateY(-1px); box-shadow:0 4px 16px rgba(13,119,64,.3); }
.auth-btn:disabled { opacity:.7; cursor:not-allowed; }

.demo-box { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:12px; padding:14px; }
.demo-title { font-size:12px; font-weight:700; color:var(--fm-green); margin-bottom:10px; letter-spacing:.5px; text-transform:uppercase; }
.demo-row { display:flex; align-items:center; gap:10px; padding:7px 8px; border-radius:8px; cursor:pointer; transition:.15s; }
.demo-row:hover { background:#dcfce7; }
.demo-icon { font-size:20px; }
.demo-role { font-size:13px; font-weight:700; font-family:"Nunito",sans-serif; }
.demo-cred { font-size:11px; color:var(--fm-gray-500); }
.demo-pwd  { margin-left:auto; font-size:11px; background:#fff; border:1px solid #bbf7d0; padding:2px 8px; border-radius:20px; color:var(--fm-green); font-weight:600; }
</style>

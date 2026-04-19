<template>
  <div class="fm-app">
    <Navbar v-if="showNav" />
    <main :class="showNav ? 'fm-main' : ''">
      <router-view />
    </main>
    <Chatbot v-if="showChat" />
  </div>
</template>

<script>
import Navbar  from "./components/Navbar.vue"
import Chatbot from "./components/Chatbot.vue"

export default {
  components: { Navbar, Chatbot },
  computed: {
    showNav()  { return !["/login","/register"].includes(this.$route.path) },
    showChat() { return this.showNav && localStorage.getItem("role") === "customer" }
  }
}
</script>

<style>
/* ── Design Tokens ───────────────────────────────────── */
:root {
  --fm-green:       #0d7740;
  --fm-green-light: #e6f4ec;
  --fm-green-dark:  #085c2f;
  --fm-orange:      #f97316;
  --fm-red:         #ef4444;
  --fm-yellow:      #fbbf24;
  --fm-gray-50:     #f9fafb;
  --fm-gray-100:    #f3f4f6;
  --fm-gray-200:    #e5e7eb;
  --fm-gray-500:    #6b7280;
  --fm-gray-800:    #1f2937;
  --fm-text:        #111827;
  --fm-radius:      12px;
  --fm-shadow:      0 2px 12px rgba(0,0,0,.08);
  --fm-shadow-lg:   0 8px 32px rgba(0,0,0,.12);
}

/* ── Base ────────────────────────────────────────────── */
* { box-sizing: border-box; }
body {
  font-family: "DM Sans", sans-serif;
  background: var(--fm-gray-100);
  color: var(--fm-text);
  margin: 0;
}
h1,h2,h3,h4,h5,h6,.fw-bold,.fw-semibold { font-family: "Nunito", sans-serif; }

/* ── Layout ──────────────────────────────────────────── */
.fm-app { min-height: 100vh; }
.fm-main { max-width: 1200px; margin: 0 auto; padding: 16px; padding-top: 80px; }

/* ── Card ────────────────────────────────────────────── */
.fm-card {
  background: #fff;
  border-radius: var(--fm-radius);
  box-shadow: var(--fm-shadow);
  border: none;
}

/* ── Buttons ─────────────────────────────────────────── */
.btn-fm-green {
  background: var(--fm-green);
  color: #fff;
  border: none;
  font-family: "Nunito", sans-serif;
  font-weight: 700;
  border-radius: 8px;
}
.btn-fm-green:hover { background: var(--fm-green-dark); color: #fff; }
.btn-fm-outline {
  background: transparent;
  border: 2px solid var(--fm-green);
  color: var(--fm-green);
  font-family: "Nunito", sans-serif;
  font-weight: 700;
  border-radius: 8px;
}
.btn-fm-outline:hover { background: var(--fm-green-light); }

/* ── Badge override ──────────────────────────────────── */
.badge { font-family: "Nunito", sans-serif; font-weight: 700; }

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--fm-gray-100); }
::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }

/* ── Status badges ───────────────────────────────────── */
.status-pending       { background:#fff7ed; color:#c2410c; border:1px solid #fed7aa; }
.status-approved      { background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; }
.status-packing       { background:#faf5ff; color:#7c3aed; border:1px solid #e9d5ff; }
.status-packed        { background:#f0fdf4; color:#166534; border:1px solid #bbf7d0; }
.status-out_for_delivery { background:#ecfeff; color:#155e75; border:1px solid #a5f3fc; }
.status-delivered     { background:#f0fdf4; color:#166534; border:1px solid #86efac; }
.status-cancelled     { background:#fef2f2; color:#991b1b; border:1px solid #fecaca; }

.status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: capitalize;
  font-family: "Nunito", sans-serif;
}

/* ── Animations ──────────────────────────────────────── */
@keyframes fadeInUp {
  from { opacity:0; transform:translateY(16px); }
  to   { opacity:1; transform:translateY(0); }
}
.fade-in-up { animation: fadeInUp .35s ease both; }

@keyframes pulse-green {
  0%,100% { box-shadow: 0 0 0 0 rgba(13,119,64,.4); }
  50%      { box-shadow: 0 0 0 8px rgba(13,119,64,0); }
}
</style>

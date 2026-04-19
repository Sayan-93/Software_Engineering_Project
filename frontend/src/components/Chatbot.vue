<template>
  <div class="fm-chatbot">
    <button class="fm-chat-toggle" @click="toggle" :class="{ open }">
      <span class="fm-chat-icon">{{ open ? "✕" : "💬" }}</span>
    </button>

    <transition name="chat-slide">
      <div v-if="open" class="fm-chat-window">
        <div class="fm-chat-header">
          <div class="fm-chat-avatar">🤖</div>
          <div>
            <div class="fm-chat-title">FreshMart</div>
            <div class="fm-chat-subtitle">Online</div>
          </div>
          <button class="fm-chat-close" @click="open = false">✕</button>
        </div>

        <div class="fm-chat-messages" ref="msgBox">
          <div v-for="(m, i) in messages" :key="i"
               :class="['fm-msg', m.from === 'user' ? 'fm-msg-user' : 'fm-msg-bot']">
            <div class="fm-msg-avatar" v-if="m.from === 'bot'">🤖</div>
            <div class="fm-msg-content">
              <div class="fm-msg-bubble" v-html="formatMsg(m.text)"></div>
              
              <div v-if="m.products && m.products.length" class="fm-product-cards">
                <div v-for="p in m.products" :key="p.id" 
                     class="fm-product-card"
                     @click="viewProduct(p.id)">
                  <img v-if="p.image" :src="p.image" class="fm-product-img"/>
                  <div class="fm-product-info">
                    <div class="fm-product-name">{{ p.name }}</div>
                    <div class="fm-product-price">
                      ₹{{ p.price.toFixed(0) }}
                      <span v-if="!p.in_stock" class="fm-stock-badge">Out</span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="m.order" class="fm-order-card">
                <div class="fm-order-header">
                  <strong>Order #{{ m.order.id }}</strong>
                  <span :class="['fm-status', m.order.status]">{{ m.order.status }}</span>
                </div>
                <div class="fm-order-total">Total: ₹{{ m.order.total.toFixed(0) }}</div>
                <div v-if="m.order.items && m.order.items.length" class="fm-order-items">
                  <div v-for="(item, idx) in m.order.items" :key="idx" class="fm-order-item">
                    {{ typeof item === 'string' ? item : item.name + ' x' + item.quantity }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="typing" class="fm-msg fm-msg-bot">
            <div class="fm-msg-avatar">🤖</div>
            <div class="fm-typing-indicator"><span></span><span></span><span></span></div>
          </div>
        </div>

        <!-- QUICK REPLIES REMOVED -->

        <div class="fm-chat-input-area">
          <input v-model="input" placeholder="Type your message..." 
                 @keyup.enter="send" :disabled="typing"/>
          <button @click="send" :disabled="!input.trim() || typing">➤</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { sendMessage } from "../services/chatbotService.js"

const WELCOME = `Hi! I'm your FreshMart Assistant. Ask me about any product or your orders.`

export default {
  data() {
    return {
      open: false,
      input: "",
      typing: false,
      messages: [{ from: "bot", text: WELCOME, products: [] }],
      // quickReplies removed
    }
  },
  methods: {
    toggle() {
      this.open = !this.open
      if (this.open) this.$nextTick(() => this.scrollToBottom())
    },
    async send() {
      const msg = this.input.trim()
      if (!msg) return
      
      this.messages.push({ from: "user", text: msg, products: [] })
      this.input = ""
      this.typing = true
      
      const userId = localStorage.getItem("user_id") || localStorage.getItem("id") || null
      
      try {
        const res = await sendMessage(msg, userId)
        const data = res.data
        
        if (data.order) {
          this.messages.push({ 
            from: "bot", 
            text: data.answer,
            order: data.order,
            products: []
          })
        } else {
          this.messages.push({ 
            from: "bot", 
            text: data.answer, 
            products: data.products || [] 
          })
        }
      } catch (err) {
        console.error("Chat error:", err)
        this.messages.push({ from: "bot", text: "Please try again.", products: [] })
      } finally {
        this.typing = false
        this.$nextTick(() => this.scrollToBottom())
      }
    },
    scrollToBottom() {
      const el = this.$refs.msgBox
      if (el) el.scrollTop = el.scrollHeight
    },
    formatMsg(text) {
      return text.replace(/\$/g, "₹")
                 .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                 .replace(/\n/g, "<br>")
    },
    viewProduct(id) {
      this.$router.push(`/products/${id}`)
      this.open = false
    }
  }
}
</script>

<style scoped>
.fm-chatbot { position: fixed; bottom: 20px; right: 20px; z-index: 9000; }
.fm-chat-toggle { width: 50px; height: 50px; border-radius: 50%; border: none; background: #0d7740; color: #fff; font-size: 20px; cursor: pointer; }
.fm-chat-window { position: absolute; bottom: 60px; right: 0; width: 300px; background: #fff; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); overflow: hidden; }
.fm-chat-header { display: flex; align-items: center; gap: 10px; padding: 12px; background: #0d7740; color: #fff; }
.fm-chat-messages { height: 320px; overflow-y: auto; padding: 10px; background: #f5f5f5; }
.fm-msg { display: flex; gap: 8px; margin-bottom: 10px; }
.fm-msg-user { flex-direction: row-reverse; justify-content: flex-end; }
.fm-msg-bubble { max-width: 80%; padding: 10px; border-radius: 12px; background: #fff; font-size: 13px; }
.fm-msg-user .fm-msg-bubble { background: #0d7740; color: #fff; }

.fm-product-cards { margin-top: 8px; }
.fm-product-card { display: flex; gap: 10px; padding: 8px; background: #fff; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 6px; cursor: pointer; }
.fm-product-card:hover { border-color: #0d7740; }
.fm-product-img { width: 40px; height: 40px; border-radius: 6px; object-fit: cover; }
.fm-product-name { font-size: 13px; font-weight: 600; }
.fm-product-price { color: #0d7740; font-weight: 700; font-size: 13px; }
.fm-stock-badge { color: #ef4444; font-size: 11px; margin-left: 5px; }

.fm-order-card { background: #f0fdf4; border: 1px solid #0d7740; border-radius: 8px; padding: 10px; margin-top: 8px; }
.fm-order-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.fm-status { padding: 2px 6px; border-radius: 10px; font-size: 10px; text-transform: uppercase; font-weight: 600; }
.fm-status.pending { background: #fef3c7; color: #92400e; }
.fm-status.delivered { background: #dcfce7; color: #166534; }
.fm-order-total { font-weight: bold; color: #0d7740; font-size: 14px; margin-bottom: 6px; }
.fm-order-item { font-size: 12px; color: #374151; padding: 2px 0; border-bottom: 1px dashed #e5e7eb; }
.fm-order-item:last-child { border-bottom: none; }

.fm-chat-input-area { display: flex; padding: 10px; border-top: 1px solid #eee; }
.fm-chat-input-area input { flex: 1; border: 1px solid #ddd; border-radius: 20px; padding: 8px 12px; outline: none; }
.fm-chat-input-area button { width: 36px; border-radius: 50%; border: none; background: #0d7740; color: #fff; margin-left: 8px; cursor: pointer; }
.fm-chat-input-area button:disabled { background: #ccc; }
.fm-typing-indicator { display: flex; gap: 4px; padding: 10px; }
.fm-typing-indicator span { width: 6px; height: 6px; border-radius: 50%; background: #999; animation: bounce 1s infinite; }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
</style>

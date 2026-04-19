import api from "./apiClient"

// Send chat message
export const sendMessage = (msg, userId = null) => 
  api.post("/chat/message", { message: msg, user_id: userId })

// Check order status
export const checkOrderStatus = (orderId, userId) => 
  api.post("/chat/order-status", { order_id: orderId, user_id: userId })

// Admin: Reindex products (if needed)
export const reindexProducts = () => 
  api.post("/chat/reindex")

import api from "./apiClient"
export const getOrders      = ()      => api.get("/orders")
export const getOrder       = id      => api.get(`/orders/${id}`)
export const placeOrder     = d       => api.post("/orders", d)
export const getOrderStatus = id      => api.get(`/orders/${id}/status`)
export const cancelOrder    = id      => api.post(`/orders/${id}/cancel`)
export const approveOrder   = id      => api.post(`/orders/${id}/approve`)

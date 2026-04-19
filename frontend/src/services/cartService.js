import api from "./apiClient"
export const getCart        = ()      => api.get("/cart")
export const addToCart      = d       => api.post("/cart", d)
export const updateCartItem = (id, d) => api.put(`/cart/${id}`, d)
export const removeFromCart = id      => api.delete(`/cart/${id}`)
export const clearCart      = ()      => api.delete("/cart/clear")

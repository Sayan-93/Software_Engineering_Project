import api from "./apiClient"
export const getProducts    = p  => api.get("/products", { params: p })
export const getProduct     = id => api.get(`/products/${id}`)
export const addProduct     = d  => api.post("/products", d)
export const updateProduct  = (id,d) => api.put(`/products/${id}`, d)
export const deleteProduct  = id => api.delete(`/products/${id}`)
export const getCategories  = () => api.get("/categories")
export const addCategory    = d  => api.post("/categories", d)
export const getRecommendations = id => api.get(`/products/${id}/recommendations`)

import api from "./apiClient"
export const getInventory    = ()      => api.get("/inventory")
export const updateInventory = (id, d) => api.put(`/inventory/${id}`, d)
export const getLowStock     = ()      => api.get("/inventory/low-stock")

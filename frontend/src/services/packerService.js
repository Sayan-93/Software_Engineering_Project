import api from "./apiClient"
export const getAssignedOrders = ()  => api.get("/packer/orders")
export const markPacked        = id  => api.post(`/packer/orders/${id}/packed`)
export const assignDelivery    = d   => api.post("/assign-delivery", d)
export const getDeliveryStaff  = ()  => api.get("/users/delivery-staff")

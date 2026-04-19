import api from "./apiClient"
export const getDeliveries        = ()  => api.get("/delivery/orders")
export const updateDeliveryStatus = d   => api.post("/delivery/update", d)

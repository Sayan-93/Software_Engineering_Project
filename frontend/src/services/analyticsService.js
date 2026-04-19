import api from "./apiClient"
export const getSalesSummary = ()          => api.get("/analytics/sales")
export const getTopProducts  = (limit=5)   => api.get("/analytics/top-products", { params:{ limit } })
export const getForecast     = ()          => api.get("/analytics/forecast")

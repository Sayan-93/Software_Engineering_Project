import api from "./apiClient"
export const getDashboard = ()     => api.get("/admin/dashboard")
export const getUsers     = role   => api.get("/admin/users", { params: { role } })
export const getPackers   = ()     => api.get("/admin/packers")
export const assignPacker = d      => api.post("/admin/orders/assign-packer", d)
export const runForecast  = ()     => api.post("/ai/run-forecast")
export const rebuildRecs  = ()     => api.post("/ai/rebuild-recommendations")

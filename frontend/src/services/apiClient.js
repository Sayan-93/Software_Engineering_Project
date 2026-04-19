import axios from "axios"

const api = axios.create({ baseURL: "/api", headers: { "Content-Type": "application/json" } })

api.interceptors.request.use(cfg => {
  const t = localStorage.getItem("token")
  if (t) cfg.headers.Authorization = `Bearer ${t}`
  return cfg
})
api.interceptors.response.use(r => r, e => {
  if (e.response?.status === 401) { localStorage.clear(); window.location.href = "/login" }
  return Promise.reject(e)
})

export default api

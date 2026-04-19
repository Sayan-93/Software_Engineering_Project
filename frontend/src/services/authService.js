import api from "./apiClient"
export const login    = d => api.post("/login", d)
export const register = d => api.post("/register", d)

import { reactive } from "vue"

export const cartStore = reactive({
  count: 0,
  setCount(n) { this.count = n },
  inc() { this.count++ },
  dec() { if (this.count > 0) this.count-- }
})

# 🥦 FreshMart — Warehouse E-Commerce Platform

A full-stack fruit & vegetable warehouse management system with four user roles,
order lifecycle tracking, AI recommendations, stock forecasting, and a chatbot.

---

## Tech Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Frontend | Vue 3, Vue Router, Bootstrap 5, Axios, Chart.js |
| Backend  | Flask, Flask-JWT-Extended, Flask-CORS           |
| Database | SQLite via SQLAlchemy ORM                       |
| AI       | scikit-learn / NumPy (forecasting), co-occurrence (recommendations) |
| LLM(chat)| ollama(Llama 3.2) |

---

## Project Structure

```
FreshMart/
│
├── backend/                      # Flask Backend (API + AI + DB)
│   ├── app.py                   # Main entry point
│   ├── config.py                # App configuration
│   ├── requirements.txt         # Python dependencies
│   ├── seed.py                  # Sample data seeding
│   ├── run_index.py             # AI indexing
│
│   ├── models/                  # Database models
│   │   └── models.py
│
│   ├── routes/                  # API routes (role-based)
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── products.py
│   │   ├── cart.py
│   │   ├── orders.py
│   │   ├── inventory.py
│   │   ├── delivery.py
│   │   ├── packer.py
│   │   ├── analytics.py
│   │   └── ai_routes.py
│
│   ├── ai/                      # AI Features
│   │   ├── chatbot.py           # Chatbot logic
│   │   ├── recommendations.py   # Product recommendations
│   │   ├── forecasting.py       # Demand prediction
│   │   ├── retriever.py         # RAG retrieval logic
│   │   ├── indexer.py           # Vector DB indexing
│   │   └── routes.py            # AI endpoints
│
│   └── tests/                   # Backend testing
│       ├── test_auth.py
│       ├── test_products.py
│       ├── test_orders.py
│       └── ...
│
├── frontend/                    # Vue 3 Frontend
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│
│   └── src/
│       ├── main.js
│       ├── App.vue
│
│       ├── components/          # Reusable UI components
│       │   ├── Navbar.vue
│       │   ├── ProductCard.vue
│       │   └── Chatbot.vue
│
│       ├── pages/               # Role-based pages
│       │   ├── auth/
│       │   │   ├── Login.vue
│       │   │   └── Register.vue
│       │
│       │   ├── customer/
│       │   │   ├── Home.vue
│       │   │   ├── Products.vue
│       │   │   ├── Cart.vue
│       │   │   ├── Orders.vue
│       │   │   └── OrderTracking.vue
│       │
│       │   ├── admin/
│       │   │   ├── Dashboard.vue
│       │   │   ├── Products.vue
│       │   │   ├── Inventory.vue
│       │   │   └── Analytics.vue
│       │
│       │   ├── delivery/
│       │   │   └── DeliveryDashboard.vue
│       │
│       │   └── packers/
│       │       ├── AssignedOrders.vue
│       │       └── PackingPanel.vue
│
│       ├── router/              # Routing
│       │   └── index.js
│
│       ├── services/            # API communication layer
│       │   ├── apiClient.js
│       │   ├── authService.js
│       │   ├── productService.js
│       │   ├── orderService.js
│       │   └── ...
│
│       └── stores/              # State management
│           └── cart.js
│
├── README.md                   # Project documentation
└── .gitignore
```

---

## Setup & Run

### Prerequisites
- Python 3.9+
- Node.js 18+
- Ollama installed

---

### Step 1 — Backend

```bash
cd FreshMart/backend
pip install -r requirements.txt
python seed.py
python app.py
```

Backend runs on: **http://localhost:5000**

---

### Step 2 — Frontend (new terminal)

```bash
cd FreshMart/frontend
npm install
npm run dev
```

Frontend runs on: **http://localhost:5173**

---

### Step 3 — Run AI Model (Ollama)

```bash
ollama run llama3.2:1b
```
### Step 4 — Open App

Go to: **http://localhost:5173**

You will see the **Login page** first. After login you are automatically redirected
to the correct dashboard for your role.

---

## Demo Accounts

| Role     | Email                   | Password     | Redirects to        |
|----------|-------------------------|--------------|---------------------|
| Admin    | admin@freshmart.com     | admin123     | /admin              |
| Customer | rahul@example.com       | customer123  | / (Home)            |
| Packer   | kumar@freshmart.com     | packer123    | /packer/orders      |
| Delivery | arun@freshmart.com      | delivery123  | /delivery           |

---

## User Flows

### Customer
Login → Browse Products → Add to Cart → Checkout → Track Order

### Admin
Login → Dashboard (live KPIs) → Approve Orders → Assign Packers
      → Manage Products → Update Inventory → View Analytics

### Packer
Login → View Assigned Orders → Open Packing Panel
      → Check off each item → Select Delivery Person → Submit

### Delivery
Login → View Assigned Deliveries → Mark: Picked Up → Out for Delivery → Delivered

---

## Order Lifecycle

```
Customer places order
      ↓ (status: pending)
Admin approves
      ↓ (status: approved)
Admin assigns packer
      ↓ (status: packing)
Packer marks packed + assigns delivery person
      ↓ (status: packed → out_for_delivery)
Delivery person marks delivered
      ↓ (status: delivered)
```

---

## AI Features

| Feature               | How it works                                                 |
|-----------------------|--------------------------------------------------------------|
| Product Recommendations | Cosine similarity on product vectors to suggest similar items  |
| Stock Forecasting     | Linear regression on last 30-day sales per product           |
| Chatbot               | Ollama-powered (Llama 3.2)  |

Admin can trigger AI manually from the Analytics page:
- **Run Forecast** → predicts next 7 days demand
- **Rebuild Recommendations** → recalculates from all orders

---

## API Summary

All endpoints prefixed with `/api`. Protected routes need `Authorization: Bearer <token>`.

| Module      | Endpoints                                                    |
|-------------|--------------------------------------------------------------|
| Auth        | POST /login, POST /register                                  |
| Products    | GET/POST /products, PUT/DELETE /products/:id, GET /categories |
| Cart        | GET/POST /cart, PUT/DELETE /cart/:id, DELETE /cart/clear     |
| Orders      | GET/POST /orders, GET /orders/:id/status, POST /orders/:id/approve |
| Inventory   | GET /inventory, PUT /inventory/:id, GET /inventory/low-stock |
| Packer      | GET /packer/orders, POST /packer/orders/:id/packed, POST /assign-delivery |
| Delivery    | GET /delivery/orders, POST /delivery/update                  |
| Admin       | GET /admin/dashboard, GET /admin/users, POST /admin/orders/assign-packer |
| Analytics   | GET /analytics/sales, GET /analytics/top-products, GET /analytics/forecast |
| AI          | POST /chatbot, POST /ai/run-forecast, POST /ai/rebuild-recommendations |

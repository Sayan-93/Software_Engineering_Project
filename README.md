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

---

## Project Structure

```
FreshMart/
├── backend/
│   ├── app.py              ← Flask entry point
│   ├── config.py           ← Configuration
│   ├── seed.py             ← Database seeder (run once)
│   ├── requirements.txt    ← Python dependencies
│   ├── models/
│   │   └── models.py       ← All 15 SQLAlchemy models
│   ├── routes/
│   │   ├── auth.py         ← /login /register
│   │   ├── products.py     ← /products /categories
│   │   ├── cart.py         ← /cart
│   │   ├── orders.py       ← /orders
│   │   ├── inventory.py    ← /inventory
│   │   ├── packer.py       ← /packer/*
│   │   ├── delivery.py     ← /delivery/*
│   │   ├── admin.py        ← /admin/*
│   │   ├── analytics.py    ← /analytics/*
│   │   └── ai_routes.py    ← /chatbot /ai/*
│   └── ai/
│       ├── recommendations.py  ← Co-occurrence market basket
│       ├── forecasting.py      ← Linear regression demand forecast
│       └── chatbot.py          ← Rule-based customer chatbot
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js      ← Proxy: /api → localhost:5000
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/index.js         ← Auth guards + role redirects
        ├── services/               ← All Axios API calls
        ├── components/
        │   ├── Navbar.vue          ← Role-based navigation
        │   ├── Chatbot.vue         ← Floating chatbot widget
        │   └── ProductCard.vue
        └── pages/
            ├── auth/         Login.vue, Register.vue
            ├── customer/     Home, Products, Cart, Orders, OrderTracking
            ├── admin/        Dashboard, Products, Inventory, Orders, Analytics
            ├── packers/      AssignedOrders, PackingPanel
            └── delivery/     DeliveryDashboard
```

---

## Setup & Run

### Prerequisites
- Python 3.9+
- Node.js 18+

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

### Step 3 — Open Browser

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
| Product Recommendations | Co-occurrence on order history; top 3 products per item  |
| Stock Forecasting     | Linear regression on last 30-day sales per product           |
| Chatbot               | Rule-based; handles order status, stock queries, delivery info |

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

import json
from datetime import datetime
from models import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)   # admin | customer | packer | delivery
    phone = db.Column(db.Text)
    address = db.Column(db.Text)
    flat_unit_number = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
            "address": self.address,
            "flat_unit_number": self.flat_unit_number,
            "created_at": str(self.created_at)
        }


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    image_url = db.Column(db.Text)
    unit = db.Column(db.Text)
    weight_options = db.Column(db.Text)  # JSON array of weight strings, e.g. '["50g","100g","250g"]'
    weight_prices = db.Column(db.Text)   # JSON object of weight->price, e.g. '{"50g":20,"100g":35,"250g":80}'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("Category", backref="products")

    def to_dict(self):
        try:
            weight_options = json.loads(self.weight_options) if self.weight_options else []
        except Exception:
            weight_options = []
        try:
            weight_prices = json.loads(self.weight_prices) if self.weight_prices else {}
        except Exception:
            weight_prices = {}
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category_id": self.category_id,
            "category": self.category.name if self.category else None,
            "price": self.price,
            "discount": self.discount,
            "image_url": self.image_url,
            "unit": self.unit,
            "weight_options": weight_options,
            "weight_prices": weight_prices,
            "is_active": self.is_active,
            "created_at": str(self.created_at)
        }


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship("Product", backref=db.backref("inventory", uselist=False))

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "stock_quantity": self.stock_quantity,
            "reorder_level": self.reorder_level,
            "low_stock": self.stock_quantity < self.reorder_level,
            "last_updated": str(self.last_updated)
        }


class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship("User", backref="cart")
    items = db.relationship("CartItem", backref="cart", cascade="all, delete-orphan")


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    selected_weight = db.Column(db.Text)      # e.g. "500g", "1kg", or None
    price = db.Column(db.Float)               # actual price for selected weight after discount

    product = db.relationship("Product")

    def to_dict(self):
        # fallback price: weight price or base product price, with discount applied
        base = self.price
        if base is None and self.product:
            base = self.product.price
        return {
            "id": self.id,
            "product_id": self.product_id,
            "name": self.product.name if self.product else None,
            "price": base,
            "image_url": self.product.image_url if self.product else None,
            "unit": self.product.unit if self.product else None,
            "selected_weight": self.selected_weight,
            "quantity": self.quantity
        }


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    total_amount = db.Column(db.Float)
    status = db.Column(db.Text, default="pending")
    payment_status = db.Column(db.Text, default="pending")
    delivery_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship("User", backref="orders")
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")
    status_history = db.relationship("OrderStatusHistory", backref="order", cascade="all, delete-orphan")

    def to_dict(self, with_items=False):
        data = {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer": self.customer.name if self.customer else None,
            "total_amount": self.total_amount,
            "status": self.status,
            "payment_status": self.payment_status,
            "delivery_address": self.delivery_address,
            "created_at": str(self.created_at)
        }
        if with_items:
            data["items"] = [i.to_dict() for i in self.items]
        return data


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "name": self.product.name if self.product else None,
            "quantity": self.quantity,
            "price": self.price
        }


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    amount = db.Column(db.Float)
    payment_method = db.Column(db.Text)   # COD | UPI | Card
    payment_status = db.Column(db.Text, default="pending")
    transaction_id = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship("Order", backref=db.backref("payment", uselist=False))

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "transaction_id": self.transaction_id,
            "created_at": str(self.created_at)
        }


class PackingAssignment(db.Model):
    __tablename__ = "packing_assignments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    packer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.Text, default="assigned")   # assigned | packing | packed
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    packed_at = db.Column(db.DateTime)

    order = db.relationship("Order", backref=db.backref("packing_assignment", uselist=False))
    packer = db.relationship("User", foreign_keys=[packer_id])

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "packer_id": self.packer_id,
            "packer_name": self.packer.name if self.packer else None,
            "status": self.status,
            "assigned_at": str(self.assigned_at),
            "packed_at": str(self.packed_at) if self.packed_at else None
        }


class DeliveryAssignment(db.Model):
    __tablename__ = "delivery_assignments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    delivery_person_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.Text, default="assigned")   # assigned | picked_up | out_for_delivery | delivered
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime)

    order = db.relationship("Order", backref=db.backref("delivery_assignment", uselist=False))
    delivery_person = db.relationship("User", foreign_keys=[delivery_person_id])

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "delivery_person_id": self.delivery_person_id,
            "delivery_person_name": self.delivery_person.name if self.delivery_person else None,
            "status": self.status,
            "assigned_at": str(self.assigned_at),
            "delivered_at": str(self.delivered_at) if self.delivered_at else None
        }


class OrderStatusHistory(db.Model):
    __tablename__ = "order_status_history"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    status = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "status": self.status,
            "updated_at": str(self.updated_at)
        }


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    recommended_product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    score = db.Column(db.Float)

    product = db.relationship("Product", foreign_keys=[product_id])
    recommended_product = db.relationship("Product", foreign_keys=[recommended_product_id])

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "recommended_product_id": self.recommended_product_id,
            "recommended_product_name": self.recommended_product.name if self.recommended_product else None,
            "recommended_product_price": self.recommended_product.price if self.recommended_product else None,
            "recommended_product_image": self.recommended_product.image_url if self.recommended_product else None,
            "score": self.score
        }


class SalesAnalytics(db.Model):
    __tablename__ = "sales_analytics"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    quantity_sold = db.Column(db.Integer)
    date = db.Column(db.Date)
    revenue = db.Column(db.Float)

    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "quantity_sold": self.quantity_sold,
            "date": str(self.date),
            "revenue": self.revenue
        }


class StockForecast(db.Model):
    __tablename__ = "stock_forecast"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    predicted_demand = db.Column(db.Integer)
    forecast_date = db.Column(db.Date)

    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "predicted_demand": self.predicted_demand,
            "forecast_date": str(self.forecast_date)
        }

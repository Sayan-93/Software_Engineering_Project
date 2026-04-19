"""
seed.py — Run once to populate the database with demo data.
Usage:   python seed.py
"""
from datetime import date, timedelta
from werkzeug.security import generate_password_hash
from app import app
from models import db
from models.models import User, Category, Product, Inventory, SalesAnalytics

# Reliable placeholder images – no hotlink blocks
IMAGES = {
    "Apple":     "https://placehold.co/300x200/ef4444/ffffff?text=Apple",
    "Banana":    "https://placehold.co/300x200/eab308/ffffff?text=Banana",
    "Mango":     "https://placehold.co/300x200/f97316/ffffff?text=Mango",
    "Orange":    "https://placehold.co/300x200/fb923c/ffffff?text=Orange",
    "Tomato":    "https://placehold.co/300x200/dc2626/ffffff?text=Tomato",
    "Potato":    "https://placehold.co/300x200/a16207/ffffff?text=Potato",
    "Onion":     "https://placehold.co/300x200/7c3aed/ffffff?text=Onion",
    "Carrot":    "https://placehold.co/300x200/ea580c/ffffff?text=Carrot",
    "Spinach":   "https://placehold.co/300x200/16a34a/ffffff?text=Spinach",
    "Coriander": "https://placehold.co/300x200/15803d/ffffff?text=Coriander",
}

def seed():
    with app.app_context():
        db.create_all()

        if User.query.count() == 0:
            db.session.add_all([
                User(name="Admin Owner",    email="admin@freshmart.com",  password=generate_password_hash("admin123"),    role="admin",    phone="9000000001", address="Chennai"),
                User(name="Rahul Kumar",    email="rahul@example.com",    password=generate_password_hash("customer123"), role="customer", phone="9000000002", address="Velachery, Chennai"),
                User(name="Asha Devi",      email="asha@example.com",     password=generate_password_hash("customer123"), role="customer", phone="9000000003", address="Anna Nagar, Chennai"),
                User(name="Kumar Packer",   email="kumar@freshmart.com",  password=generate_password_hash("packer123"),   role="packer",   phone="9000000004"),
                User(name="Arun Delivery",  email="arun@freshmart.com",   password=generate_password_hash("delivery123"), role="delivery", phone="9000000005"),
                User(name="Priya Delivery", email="priya@freshmart.com",  password=generate_password_hash("delivery123"), role="delivery", phone="9000000006"),
            ])
            db.session.commit()
            print("Users seeded")

        if Category.query.count() == 0:
            db.session.add_all([
                Category(name="Fruits",         description="Fresh seasonal fruits"),
                Category(name="Vegetables",     description="Farm-fresh vegetables"),
                Category(name="Leafy Greens",   description="Nutritious leafy greens"),
                Category(name="Herbs & Spices", description="Aromatic herbs and spices"),
            ])
            db.session.commit()
            print("Categories seeded")

        if Product.query.count() == 0:
            f = Category.query.filter_by(name="Fruits").first().id
            v = Category.query.filter_by(name="Vegetables").first().id
            l = Category.query.filter_by(name="Leafy Greens").first().id
            db.session.add_all([
                Product(name="Apple",     description="Fresh red apples",      category_id=f, price=120.0, discount=5,  unit="kg",     image_url=IMAGES["Apple"]),
                Product(name="Banana",    description="Ripe yellow bananas",   category_id=f, price=60.0,  discount=0,  unit="dozen",  image_url=IMAGES["Banana"]),
                Product(name="Mango",     description="Alphonso mangoes",      category_id=f, price=200.0, discount=10, unit="kg",     image_url=IMAGES["Mango"]),
                Product(name="Orange",    description="Juicy Nagpur oranges",  category_id=f, price=80.0,  discount=0,  unit="kg",     image_url=IMAGES["Orange"]),
                Product(name="Tomato",    description="Fresh tomatoes",        category_id=v, price=40.0,  discount=0,  unit="kg",     image_url=IMAGES["Tomato"]),
                Product(name="Potato",    description="Farm potatoes",         category_id=v, price=30.0,  discount=0,  unit="kg",     image_url=IMAGES["Potato"]),
                Product(name="Onion",     description="Red onions",            category_id=v, price=35.0,  discount=0,  unit="kg",     image_url=IMAGES["Onion"]),
                Product(name="Carrot",    description="Organic carrots",       category_id=v, price=50.0,  discount=5,  unit="kg",     image_url=IMAGES["Carrot"]),
                Product(name="Spinach",   description="Fresh spinach leaves",  category_id=l, price=25.0,  discount=0,  unit="bundle", image_url=IMAGES["Spinach"]),
                Product(name="Coriander", description="Fresh coriander",       category_id=l, price=15.0,  discount=0,  unit="bundle", image_url=IMAGES["Coriander"]),
            ])
            db.session.commit()
            for p in Product.query.all():
                db.session.add(Inventory(product_id=p.id, stock_quantity=100, reorder_level=15))
            mango = Product.query.filter_by(name="Mango").first()
            if mango and mango.inventory:
                mango.inventory.stock_quantity = 8
            db.session.commit()
            print("Products + Inventory seeded")

        if SalesAnalytics.query.count() == 0:
            import random; random.seed(42)
            for i in range(7):
                d = date.today() - timedelta(days=i)
                for p in Product.query.all():
                    qty = random.randint(5, 30)
                    db.session.add(SalesAnalytics(product_id=p.id, date=d, quantity_sold=qty, revenue=round(qty*p.price*(1-p.discount/100),2)))
            db.session.commit()
            print("Sales analytics seeded")

        print("\nDatabase seeded!")
        print("  admin@freshmart.com  / admin123")
        print("  rahul@example.com    / customer123")
        print("  kumar@freshmart.com  / packer123")
        print("  arun@freshmart.com   / delivery123")

if __name__ == "__main__":
    seed()

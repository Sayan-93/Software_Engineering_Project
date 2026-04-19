from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import Config
from models import db

# ── Blueprints ──────────────────────────────────────────────────────────────
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.inventory import inventory_bp
from routes.packer import packer_bp
from routes.delivery import delivery_bp
from routes.admin import admin_bp
from routes.analytics import analytics_bp
from routes.ai_routes import ai_bp
from ai.routes import chatbot_bp



from ai.recommendations import build_recommendations

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register all blueprints under /api prefix
    prefix = "/api"
    for bp in [auth_bp, products_bp, cart_bp, orders_bp,
               inventory_bp, packer_bp, delivery_bp,
               admin_bp, analytics_bp, ai_bp,chatbot_bp]:
        app.register_blueprint(bp, url_prefix=prefix)
    print("\n=== REGISTERED ROUTES ===")
    for rule in app.url_map.iter_rules():
        methods = ','.join([m for m in rule.methods if m != 'OPTIONS' and m != 'HEAD'])
        if 'chat' in str(rule):
            print(f"  {methods} {rule.rule}")
    print("=========================\n")
    
 
    # Create tables on first run
    with app.app_context():
        db.create_all()
        build_recommendations()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)

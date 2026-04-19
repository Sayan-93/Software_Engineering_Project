from .retriever import GroceryRetriever
from models.models import Order, OrderStatusHistory, OrderItem, Product
import re

class GroceryChatbot:
    def __init__(self):
        print("Loading AI Assistant...")
        try:
            from langchain_community.llms import Ollama
            self.llm = Ollama(
                model="llama3.2:1b",
                temperature=0.1,
                base_url="http://localhost:11434"
            )
            print("✓ AI Model ready")
        except Exception as e:
            print(f"⚠ AI Error: {e}")
            self.llm = None
        
        self.retriever = None
    
    def _get_retriever(self):
        if self.retriever is None:
            self.retriever = GroceryRetriever()
        return self.retriever
    
    def chat(self, query, user_id=None):
        print(f"\n=== User: '{query}' ===")
        
        query_lower = query.lower().strip()
        
        try:
            retriever = self._get_retriever()
            
            # 1. ORDER TRACKING
            if any(word in query_lower for word in ["order", "track", "status", "my order", "where is"]):
                return self._handle_order(query, user_id)
            
            # 2. SEARCH PRODUCTS
            all_docs = retriever.retrieve(query, k=10)
            
            if not all_docs:
                return {"answer": "I couldn't find that. Try: milk, apple, rice, or vegetables.", "products": []}
            
            # Check for SPECIFIC product match
            specific_product = None
            for doc in all_docs:
                name = doc.metadata['product_name'].lower()
                # Exact or close match in query
                if name in query_lower and len(name) > 2:
                    specific_product = doc
                    break
            
            # Show ONLY specific product - FIXED FOR GROCERY CONTEXT
            if specific_product:
                p = {
                    "id": specific_product.metadata["product_id"],
                    "name": specific_product.metadata["product_name"],
                    "price": specific_product.metadata["final_price"],
                    "unit": specific_product.metadata["unit"],
                    "image": specific_product.metadata["image_url"],
                    "in_stock": specific_product.metadata["in_stock"]
                }
                
                # FIXED: Clear grocery context to avoid confusion
                if self.llm:
                    try:
                        # Explicitly tell AI this is a grocery/fruit/vegetable
                        prompt = f"""You are a grocery store assistant. 
A customer asked about: "{p['name']}" (this is a food/grocery item, NOT a technology company).
Price: ₹{p['price']:.0f} per {p['unit']}.
Give a simple 1-sentence answer stating ONLY the price of this food item."""
                        
                        response = self.llm.invoke(prompt, timeout=5)
                        response = response.strip().replace("$", "₹")
                        
                        # Check if AI is talking about wrong thing (Apple company, etc.)
                        bad_words = ["iphone", "mac", "company", "tim cook", "technology", 
                                   "product lineup", "₹5,000", "₹50,000", "apple inc", 
                                   "steve jobs", "ipad", "macbook", "phones", "devices"]
                        if any(bad in response.lower() for bad in bad_words):
                            print(f"AI confused, using fallback. Response was: {response[:100]}")
                            raise Exception("AI talking about company not food")
                            
                        return {"answer": response, "products": [p]}
                    except Exception as e:
                        print(f"AI failed: {e}")
                
                # Clean fallback - guaranteed correct
                stock = "In stock" if p['in_stock'] else "Out of stock"
                return {
                    "answer": f"**{p['name']}** costs ₹{p['price']:.0f} per {p['unit']}. {stock}.",
                    "products": [p]
                }
            
            # 3. GENERAL SEARCH (multiple products)
            products = [{
                "id": d.metadata["product_id"],
                "name": d.metadata["product_name"],
                "price": d.metadata["final_price"],
                "unit": d.metadata["unit"],
                "image": d.metadata["image_url"],
                "in_stock": d.metadata["in_stock"]
            } for d in all_docs[:3]]
            
            # Generate AI response for list
            if self.llm:
                try:
                    product_list = ", ".join([f"{p['name']} (₹{p['price']:.0f})" for p in products])
                    prompt = f"""You are a grocery store assistant.
Customer asked: "{query}"
Available groceries: {product_list}
Give a natural 1-2 sentence response about these food items."""
                    response = self.llm.invoke(prompt, timeout=8)
                    return {"answer": response.strip().replace("$", "₹"), "products": products}
                except:
                    pass
            
            # Fallback for list
            names = ", ".join([p["name"] for p in products])
            prices = [p["price"] for p in products]
            return {
                "answer": f"Found: {names}. Prices from ₹{min(prices):.0f}-₹{max(prices):.0f}.",
                "products": products
            }
            
        except Exception as e:
            print(f"Error: {e}")
            return {"answer": "Hello! I'm your FreshMart assistant. Ask me about any grocery product!", "products": []}
    
    def _handle_order(self, query, user_id):
        """Handle order tracking"""
        # Handle user_id
        if user_id in [None, "null", "undefined", "", "0"]:
            user_id = None
        else:
            try:
                user_id = int(user_id)
            except:
                user_id = None
        
        if not user_id:
            return {"answer": "Please log in to track your orders.", "products": []}
        
        try:
            order = Order.query.filter_by(customer_id=user_id).order_by(Order.created_at.desc()).first()
            
            if not order:
                return {"answer": "You don't have any orders yet. Start shopping! 🛒", "products": []}
            
            # Get order items
            items = []
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            for item in order_items:
                product = Product.query.filter_by(id=item.product_id).first()
                if product:
                    items.append(f"{product.name} x{item.quantity}")
            
            items_text = ", ".join(items[:3])
            if len(items) > 3:
                items_text += f" and {len(items)-3} more"
            
            # AI response or template
            if self.llm:
                try:
                    prompt = f"Order #{order.id} is {order.status}. Items: {items_text}. Total: ₹{order.total_amount:.0f}. Give friendly update."
                    response = self.llm.invoke(prompt, timeout=5)
                    return {
                        "answer": response.strip().replace("$", "₹"),
                        "order": {
                            "id": order.id,
                            "status": order.status,
                            "total": order.total_amount,
                            "items": items,
                            "delivery_address": order.delivery_address
                        },
                        "products": []
                    }
                except:
                    pass
            
            return {
                "answer": f"Order #{order.id} is **{order.status.upper()}**. Items: {items_text}. Total: ₹{order.total_amount:.0f}.",
                "order": {
                    "id": order.id,
                    "status": order.status,
                    "total": order.total_amount,
                    "items": items,
                    "delivery_address": order.delivery_address
                },
                "products": []
            }
            
        except Exception as e:
            return {"answer": "Could not fetch order details.", "products": []}
    
    def check_order_status(self, order_id, user_id):
        order = Order.query.filter_by(id=order_id, customer_id=user_id).first()
        if not order:
            return {"error": "Order not found"}, 404
        history = OrderStatusHistory.query.filter_by(order_id=order_id).order_by(OrderStatusHistory.updated_at.desc()).all()
        return {
            "order_id": order.id,
            "status": order.status,
            "timeline": [h.to_dict() for h in history]
        }

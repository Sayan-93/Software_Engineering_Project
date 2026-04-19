from flask import Blueprint, request, jsonify

# Remove url_prefix here - let app.py add the /api prefix
chatbot_bp = Blueprint('chatbot', __name__)

# Update routes to include /chat in the path
@chatbot_bp.route('/chat/message', methods=['POST'])
def chat_message():
    data = request.get_json()
    message = data.get('message')
    user_id = data.get('user_id')
    
    if not message:
        return jsonify({"error": "Message required"}), 400
    
    try:
        from . import get_chatbot
        bot = get_chatbot()
        result = bot.chat(message, user_id)
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"Chatbot error: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@chatbot_bp.route('/chat/order-status', methods=['POST'])
def order_status():
    data = request.get_json()
    order_id = data.get('order_id')
    user_id = data.get('user_id')
    
    if not order_id or not user_id:
        return jsonify({"error": "Order ID and User ID required"}), 400
    
    from . import get_chatbot
    bot = get_chatbot()
    result = bot.check_order_status(order_id, user_id)
    return jsonify(result)

@chatbot_bp.route('/chat/reindex', methods=['POST'])
def reindex():
    try:
        from flask import current_app
        from .indexer import build_vector_store
        
        build_vector_store(current_app._get_current_object())
        return jsonify({"status": "Vector store updated"})
    except Exception as e:
        import traceback
        print(f"Reindex error: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

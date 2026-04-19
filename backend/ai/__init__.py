from .chatbot import GroceryChatbot
from .indexer import build_vector_store

# Singleton instance
_chatbot = None

def get_chatbot():
    global _chatbot
    if _chatbot is None:
        _chatbot = GroceryChatbot()
    return _chatbot

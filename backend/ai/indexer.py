import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from models.models import Product, Inventory, db
from config import Config

def prepare_documents():
    documents = []
    products = Product.query.filter_by(is_active=True).all()
    
    for product in products:
        inventory = Inventory.query.filter_by(product_id=product.id).first()
        stock = inventory.stock_quantity if inventory else 0
        
        content = f"""
Product: {product.name}
Category: {product.category.name if product.category else 'General'}
Price: ${product.price:.2f}
Discount: {product.discount}%
Final Price: ${product.price * (1 - product.discount/100):.2f}
Unit: {product.unit or 'each'}
Stock: {stock} units
Description: {product.description or 'No description'}
        """.strip()
        
        metadata = {
            "product_id": product.id,
            "product_name": product.name,
            "category": product.category.name if product.category else None,
            "price": product.price,
            "final_price": product.price * (1 - product.discount/100),
            "stock_quantity": stock,
            "in_stock": stock > 0,
            "image_url": product.image_url,
            "unit": product.unit
        }
        
        documents.append(Document(page_content=content, metadata=metadata))
    
    return documents

def build_vector_store(app):
    with app.app_context():
        docs = prepare_documents()
        
        if not docs:
            print("No products found to index!")
            return
        
        print(f"Indexing {len(docs)} products...")
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=Config.VECTOR_STORE_PATH,
            collection_name="products"
        )
        
        vectorstore.persist()
        print(f"Done! Vector store saved to {Config.VECTOR_STORE_PATH}")

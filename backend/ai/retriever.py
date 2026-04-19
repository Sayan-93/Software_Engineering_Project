from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from models.models import Inventory
from config import Config
import re

class GroceryRetriever:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = Chroma(
            persist_directory=Config.VECTOR_STORE_PATH,
            embedding_function=self.embeddings,
            collection_name="products"
        )
    
    def get_live_stock(self, product_ids):
        inventories = Inventory.query.filter(
            Inventory.product_id.in_(product_ids)
        ).all()
        return {inv.product_id: inv.stock_quantity for inv in inventories}
    
    def retrieve(self, query, k=5, price_limit=None, category=None):
        filter_dict = {"in_stock": {"$eq": True}}
        
        if category:
            filter_dict["category"] = {"$eq": category}
        if price_limit:
            filter_dict["final_price"] = {"$lte": price_limit}
        
        try:
            docs = self.vectorstore.similarity_search(
                query, 
                k=k*2,
                filter=filter_dict
            )
        except Exception:
            docs = self.vectorstore.similarity_search(query, k=k*2)
        
        product_ids = [doc.metadata["product_id"] for doc in docs]
        stock_map = self.get_live_stock(product_ids)
        
        enriched = []
        for doc in docs:
            pid = doc.metadata["product_id"]
            live_stock = stock_map.get(pid, 0)
            
            doc.metadata["live_stock"] = live_stock
            doc.metadata["currently_available"] = live_stock > 0
            
            if "Stock:" in doc.page_content:
                lines = doc.page_content.split('\n')
                new_lines = []
                for line in lines:
                    if line.strip().startswith("Stock:"):
                        new_lines.append(f"Stock: {live_stock} units")
                    else:
                        new_lines.append(line)
                doc.page_content = '\n'.join(new_lines)
            
            enriched.append(doc)
        
        enriched.sort(key=lambda x: (not x.metadata["currently_available"], 0))
        return enriched[:k]
    
    def extract_price_limit(self, query):
        match = re.search(r'(?:under|below|less than|cheaper than)\s*\$?(\d+(?:\.\d{2})?)', query.lower())
        return float(match.group(1)) if match else None

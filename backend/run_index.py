from app import create_app
from ai.indexer import build_vector_store

app = create_app()

with app.app_context():
    build_vector_store(app)

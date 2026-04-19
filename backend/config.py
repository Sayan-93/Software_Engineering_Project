import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "warehouse-secret-key-2024")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-2024")
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    VECTOR_STORE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'vectorstore')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')  # Optional: for OpenAI
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')

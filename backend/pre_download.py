# Run this once to download models
print("Pre-loading embedding model...")
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("✓ Model cached")

print("Checking Ollama...")
import requests
try:
    r = requests.get("http://localhost:11434/api/tags", timeout=5)
    print("✓ Ollama is running")
    print("Available models:", [m['name'] for m in r.json().get('models', [])])
except:
    print("⚠ Ollama is NOT running. Start it with: ollama serve")

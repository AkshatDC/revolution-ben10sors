import os
from dotenv import load_dotenv

# --------------------------------------------------
# 🔰 Load Environment Variables
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# 📁 Directory Setup
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FAISS_DIR = os.path.join(DATA_DIR, "faiss_indices")
DB_PATH = os.path.join(DATA_DIR, "community_chats.db")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
CACHE_DIR = os.path.join(DATA_DIR, "cache")

# Create all required directories if not exist
for path in [DATA_DIR, FAISS_DIR, LOGS_DIR, CACHE_DIR]:
    os.makedirs(path, exist_ok=True)

# --------------------------------------------------
# 🔗 Firebase Configuration
# --------------------------------------------------
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
}

# --------------------------------------------------
# 💬 Application Settings
# --------------------------------------------------
APP_SETTINGS = {
    "default_community": "General",
    "summary_model": "gpt-4-turbo",         # Model for summarization
    "embed_model": "text-embedding-3-small", # Model for embeddings (FAISS)
    "max_docs_in_kb": 200,                   # Cap for knowledge base size
    "enable_cache": True,                    # Enable local cache for KB
    "search_top_k": 5,                       # Number of docs to fetch from KB
}

# --------------------------------------------------
# 🧠 Feature Flags
# --------------------------------------------------
FEATURE_FLAGS = {
    "enable_summary": True,
    "enable_rag": True,           # Retrieval-Augmented Generation
    "enable_chat_history": True,
    "enable_user_mapping": True,  # Map user IDs to names
    "enable_auto_save": True,
}

# --------------------------------------------------
# 🧩 Helper Paths (for modular extensions)
# --------------------------------------------------
FILES = {
    "firebase_kb": os.path.join(DATA_DIR, "firebase_kb_cache.json"),
    "faiss_index": os.path.join(FAISS_DIR, "kb_index.faiss"),
    "embedding_store": os.path.join(FAISS_DIR, "embeddings.pkl"),
    "user_map": os.path.join(DATA_DIR, "user_mapping.json"),
}

# --------------------------------------------------
# ✅ Print summary (optional)
# --------------------------------------------------
if __name__ == "__main__":
    print("✅ Config Loaded Successfully!")
    print(f"Data Directory: {DATA_DIR}")
    print(f"FAISS Directory: {FAISS_DIR}")
    print(f"Database Path: {DB_PATH}")
    print(f"Firebase Enabled: {bool(FIREBASE_CONFIG['apiKey'])}")

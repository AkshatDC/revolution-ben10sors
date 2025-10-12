from firebase_admin import db
import uuid
from difflib import SequenceMatcher
from datetime import datetime

# ============================================================
# Global Cache
# ============================================================
_kb_store = {}  # {community: {"store": [doc1, doc2, ...]}}


# ============================================================
# Initialize or Load Knowledge Base
# ============================================================
def init_kb(community: str):
    """
    Initialize or load the knowledge base for a community from Firebase.
    Ensures '_kb_store[community]["store"]' is always a valid list.
    """
    global _kb_store
    print(f"\n🟡 [init_kb] Loading KB for community: '{community}'")

    try:
        ref = db.reference(f'knowledgebase/{community}')
        data = ref.get() or {"store": []}

        # Handle inconsistent Firebase structures
        if isinstance(data, dict) and "store" in data and isinstance(data["store"], dict):
            print(f"🔍 [init_kb] Converting Firebase 'store' dict → list ({len(data['store'])} items)")
            data["store"] = list(data["store"].values())
        elif "store" not in data or not isinstance(data["store"], list):
            print("⚠️ [init_kb] Missing or invalid 'store' key, resetting as empty list")
            data["store"] = []

        _kb_store[community] = data
        print(f"✅ [init_kb] KB initialized with {len(data['store'])} entries for '{community}'")
        return data

    except Exception as e:
        print(f"❌ [init_kb] Error initializing KB for '{community}': {e}")
        _kb_store[community] = {"store": []}
        return _kb_store[community]


# ============================================================
# Add Document to KB
# ============================================================
def add_to_kb(community: str, content: str, metadata: dict = None):
    """
    Add a new document to the KB in Firebase and update the local cache.
    """
    global _kb_store
    print(f"\n🟢 [add_to_kb] Adding document to KB for community: '{community}'")

    if not content or not content.strip():
        print("⚠️ [add_to_kb] Empty content — skipping insert.")
        return None

    if metadata is None:
        metadata = {}

    new_doc = {
        "id": str(uuid.uuid4()),
        "content": content.strip(),
        "metadata": metadata,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        ref = db.reference(f'knowledgebase/{community}/store')
        ref.push(new_doc)
        print(f"✅ [add_to_kb] Pushed to Firebase: {new_doc['id']}")
    except Exception as e:
        print(f"❌ [add_to_kb] Firebase push failed: {e}")

    # Ensure local cache validity
    if community not in _kb_store or not isinstance(_kb_store[community], dict):
        _kb_store[community] = {"store": []}
    if "store" not in _kb_store[community] or not isinstance(_kb_store[community]["store"], list):
        _kb_store[community]["store"] = []

    _kb_store[community]["store"].append(new_doc)
    print(f"📦 [add_to_kb] Added locally → Total docs in '{community}': {len(_kb_store[community]['store'])}")
    return new_doc


# ============================================================
# Search KB
# ============================================================
def search_kb(community: str, query: str, top_k: int = 3):
    """
    Keyword-based search in the KB using SequenceMatcher similarity.
    Always reloads latest data from Firebase.
    """
    global _kb_store
    print(f"\n🔎 [search_kb] Searching KB for community '{community}' with query: '{query}'")

    try:
        ref = db.reference(f'knowledgebase/{community}/store')
        data = ref.get()

        # Handle data absence or irregular format
        if not data:
            print(f"⚠️ [search_kb] No data found in Firebase for '{community}'")
            _kb_store[community] = {"store": []}
            return []

        if isinstance(data, dict):
            docs = list(data.values())
        elif isinstance(data, list):
            docs = data
        else:
            print(f"⚠️ [search_kb] Unexpected data type for '{community}': {type(data)}")
            docs = []

        _kb_store[community] = {"store": docs}
        print(f"📚 [search_kb] Loaded {len(docs)} docs from Firebase for '{community}'")

    except Exception as e:
        print(f"❌ [search_kb] Error fetching KB for '{community}': {e}")
        return []

    docs = _kb_store.get(community, {}).get("store", [])
    if not docs:
        print(f"⚠️ [search_kb] No docs found after loading for '{community}'")
        return []

    # Compute similarity scores
    scored_docs = []
    for doc in docs:
        content = doc.get("content", "")
        score = SequenceMatcher(None, content.lower(), query.lower()).ratio()
        scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    results = [{"doc": doc, "score": round(score, 3)} for score, doc in scored_docs[:top_k]]

    print(f"✅ [search_kb] Found {len(results)} relevant docs for query '{query}' in '{community}'")
    for r in results:
        snippet = r['doc'].get('content', '')[:80]
        print(f"   ↳ Score: {r['score']} | Content: {snippet}...")

    return results


# ============================================================
# Utility: Get KB Size
# ============================================================
def get_kb_size(community: str):
    """
    Returns the number of KB entries currently cached in memory.
    """
    size = len(_kb_store.get(community, {}).get("store", []))
    print(f"📏 [get_kb_size] '{community}' has {size} KB entries in cache.")
    return size

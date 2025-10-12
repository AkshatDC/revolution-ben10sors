import sqlite3
from config import DB_PATH
from typing import List, Dict
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import uuid
import streamlit as st
import json

# ----------------------------
# SQLite Initialization (optional)
# ----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            community TEXT,
            role TEXT,
            content TEXT,
            user_id TEXT,
            metadata TEXT DEFAULT '',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# ----------------------------
# Firebase Initialization
# ----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-service-key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://revolution-7a48d-default-rtdb.firebaseio.com/'
    })

# ----------------------------
# User Profile / Unique ID
# ----------------------------
def get_user_profile(username: str) -> str:
    """
    Returns a unique user ID for the given username.
    Stores it in Firebase under 'users/{username}' if not already present.
    Also caches in Streamlit session for faster reuse.
    """
    if "user_ids" not in st.session_state:
        st.session_state.user_ids = {}

    if username in st.session_state.user_ids:
        return st.session_state.user_ids[username]

    # Check Firebase for existing user ID
    ref = db.reference(f"users/{username}")
    user_data = ref.get()
    if user_data and "id" in user_data:
        user_id = user_data["id"]
    else:
        user_id = str(uuid.uuid4())
        ref.set({"id": user_id, "created_at": datetime.now().isoformat()})

    # Cache locally
    st.session_state.user_ids[username] = user_id
    return user_id

# ----------------------------
# Firebase Chat Utilities
# ----------------------------
def add_message(community: str, username: str, content: str, role: str = "user") -> str:
    """
    Add a message to a community chat in Firebase.
    Uses the user's unique ID and stores username mapping.
    """
    content = content or ""
    role = role or "user"
    user_id = get_user_profile(username)

    ref = db.reference(f"chats/{community}")
    new_msg = {
        "role": role,
        "user_id": user_id,
        "username": username,
        "content": content,
        "timestamp": datetime.now().timestamp()
    }
    msg_ref = ref.push(new_msg)
    print(f"✅ Message added to {community}: {content} (user_id: {user_id})")
    return msg_ref.key

def fetch_messages(community: str, limit: int = 100) -> List[Dict]:
    """
    Fetch last N messages from Firebase for a community.
    Returns a list of dicts with keys: id, role, user_id, username, content.
    """
    try:
        ref = db.reference(f"chats/{community}")
        data = ref.order_by_key().limit_to_last(limit).get()
        if not data:
            return []

        rows = [
            {
                "id": k,
                "role": v.get("role", "user"),
                "user_id": v.get("user_id", ""),
                "username": v.get("username", "Unknown"),
                "content": v.get("content", "")
            }
            for k, v in sorted(data.items())
        ]
        return rows
    except Exception as e:
        print(f"❌ Error fetching messages: {e}")
        return []

# ----------------------------
# Optional SQLite Utilities
# ----------------------------
def get_last_id(community: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM chats WHERE community=? ORDER BY id DESC LIMIT 1", (community,))
    r = cur.fetchone()
    conn.close()
    return r[0] if r else 0

def export_community_json(community: str, path: str):
    rows = fetch_messages(community, limit=10000)
    data = [
        {
            "id": r["id"],
            "role": r["role"],
            "user_id": r["user_id"],
            "username": r["username"],
            "content": r["content"]
        } for r in rows
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def clear_community(community: str):
    """
    Clears all messages for a given community from Firebase.
    """
    try:
        ref = db.reference(f"chats/{community}")
        ref.delete()
        print(f"⚠️ Cleared all messages in {community}")
    except Exception as e:
        print(f"❌ Error clearing community: {e}")

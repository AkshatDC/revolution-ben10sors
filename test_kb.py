import firebase_admin
from firebase_admin import credentials, db
from kb_utils import init_kb, add_to_kb, search_kb, get_kb_size

# --- Initialize Firebase ---
cred = credentials.Certificate("firebase-service-key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://revolution-7a48d-default-rtdb.firebaseio.com/"
})

# --- TEST PARAMETERS ---
community = "General"

print("\n===== 🔰 INITIALIZING KB =====")
init_kb(community)

print("\n===== 📝 ADDING DOCS =====")
add_to_kb(community, "Akshat lives in Gujarat, India.")
add_to_kb(community, "Python is used for AI, ML, and automation.")
add_to_kb(community, "Streamlit is great for building interactive web apps.")

print("\n===== 📏 CHECK SIZE =====")
get_kb_size(community)

print("\n===== 🔍 SEARCH KB =====")
results = search_kb(community, "Where does Akshat live?")
print(f"\n🔹 Search Results: {results}")

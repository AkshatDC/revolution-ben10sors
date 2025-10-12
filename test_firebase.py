import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase (same as in your db_utils.py)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-service-key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://revolution-7a48d-default-rtdb.firebaseio.com/'
    })

# Reference your KB root
ref = db.reference('knowledgebase')
data = ref.get()

if not data:
    print("⚠️ No knowledgebase data found.")
else:
    print("✅ Knowledgebase data:")
    print(data)

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("firebase-service-key.json")  # download from Firebase console
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://revolution-7a48d-default-rtdb.firebaseio.com'
})

def create_user_profile(uid, name, email, interests=None, experience=None, achievements=None):
    ref = db.reference(f"users/{uid}")
    profile = {
        "name": name,
        "email": email,
        "interests": interests or [],
        "experience": experience or "",
        "achievements": achievements or []
    }
    ref.set(profile)
    return profile

def get_user_profile(uid):
    ref = db.reference(f"users/{uid}")
    return ref.get()

def update_user_profile(uid, data):
    ref = db.reference(f"users/{uid}")
    ref.update(data)

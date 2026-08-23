import firebase_admin
from firebase_admin import credentials, firestore
import os


# ============================================================
# FIREBASE CONFIGURATION
# Mandal Expense App
# ============================================================

KEY_FILE = "firebase_key.json"


# ------------------------------------------------------------
# Check Firebase key file
# ------------------------------------------------------------

if not os.path.exists(KEY_FILE):
    raise FileNotFoundError(
        "firebase_key.json सापडली नाही. "
        "कृपया firebase_key.json ही file "
        "app.py च्या same folder मध्ये ठेवा."
    )


# ------------------------------------------------------------
# Initialize Firebase
# ------------------------------------------------------------

if not firebase_admin._apps:

    cred = credentials.Certificate(KEY_FILE)

    firebase_admin.initialize_app(cred)


# ------------------------------------------------------------
# Firestore Database
# ------------------------------------------------------------

db = firestore.client()

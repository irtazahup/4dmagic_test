import json
import os
import time

DB_FILE = "documents_db.json"


# -------------------------
# Load DB
# -------------------------
def load_db():
    if not os.path.exists(DB_FILE):
        return {}

    with open(DB_FILE, "r") as f:
        return json.load(f)


# -------------------------
# Save DB
# -------------------------
def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


# -------------------------
# Add document
# -------------------------
def add_document(doc_id, filename, chunk_count):
    db = load_db()

    db[doc_id] = {
        "filename": filename,
        "chunk_count": chunk_count,
        "timestamp": time.time()
    }

    save_db(db)
    
    
def delete_document(doc_id):
    db = load_db()

    if doc_id in db:
        del db[doc_id]
        save_db(db)
        return True

    return False
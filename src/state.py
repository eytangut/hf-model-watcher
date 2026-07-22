import json
import os
from datetime import datetime

STATE_DIR = "state"
SEEN_MODELS_FILE = os.path.join(STATE_DIR, "seen_models.json")
PENDING_DIGEST_FILE = os.path.join(STATE_DIR, "pending_digest.json")

def load_json(filepath, default_value=None):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return default_value if default_value is not None else {}

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_seen_models():
    return load_json(SEEN_MODELS_FILE)

def save_seen_models(seen_models):
    save_json(SEEN_MODELS_FILE, seen_models)

def load_pending_digest():
    return load_json(PENDING_DIGEST_FILE, [])

def save_pending_digest(pending_models):
    save_json(PENDING_DIGEST_FILE, pending_models)

def add_to_pending_digest(model_data):
    pending = load_pending_digest()
    pending.append(model_data)
    save_pending_digest(pending)

def clear_pending_digest():
    save_pending_digest([])

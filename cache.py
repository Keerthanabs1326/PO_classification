import json
import hashlib
import os

CACHE_FILE = "po_cache.json"

def _load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def generate_key(po_description, supplier):
    key_string = f"{po_description.lower()}::{supplier.lower()}"
    return hashlib.sha256(key_string.encode()).hexdigest()

def get_cached(po_description, supplier):
    cache = _load_cache()
    key = generate_key(po_description, supplier)
    return cache.get(key)

def set_cache(po_description, supplier, result):
    cache = _load_cache()
    key = generate_key(po_description, supplier)
    cache[key] = result
    _save_cache(cache)

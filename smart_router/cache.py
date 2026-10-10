import os
import json
import time
import hashlib
import shutil
from typing import Optional, Dict, Any

CACHE_DIR = os.path.expanduser("~/.local/state/smart_router/cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()

def get_cached_response(prompt: str) -> Optional[Dict[str, Any]]:
    h = hash_prompt(prompt)
    cache_file = os.path.join(CACHE_DIR, f"{h}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
                return data
        except Exception:
            pass
    return None

def save_cached_response(prompt: str, response: str, model_used: str):
    h = hash_prompt(prompt)
    cache_file = os.path.join(CACHE_DIR, f"{h}.json")
    try:
        with open(cache_file, "w") as f:
            json.dump({
                "prompt": prompt,
                "response": response,
                "model": model_used,
                "timestamp": time.time()
            }, f, indent=2)
    except Exception:
        pass

def clear_cache() -> int:
    if not os.path.exists(CACHE_DIR):
        return 0
    files = [f for f in os.listdir(CACHE_DIR) if f.endswith(".json")]
    count = len(files)
    shutil.rmtree(CACHE_DIR)
    os.makedirs(CACHE_DIR, exist_ok=True)
    return count

def get_cache_stats() -> Dict[str, Any]:
    if not os.path.exists(CACHE_DIR):
        return {"total_entries": 0, "size_bytes": 0}
    files = [os.path.join(CACHE_DIR, f) for f in os.listdir(CACHE_DIR) if f.endswith(".json")]
    total_size = sum(os.path.getsize(f) for f in files)
    return {"total_entries": len(files), "size_bytes": total_size}

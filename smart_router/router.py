import os
import json
import time
import urllib.request
from typing import Tuple, Dict, Any, Optional
from smart_router.scorer import score_prompt_complexity
from smart_router.cache import get_cached_response, save_cached_response

def get_gemini_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    conf_path = os.path.expanduser("~/.config/environment.d/20-gemini.conf")
    if os.path.exists(conf_path):
        try:
            with open(conf_path, "r") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        return line.strip().split("=", 1)[1].strip('"').strip("'")
        except Exception:
            pass
    return ""

def get_claude_key() -> str:
    return os.environ.get("ANTHROPIC_API_KEY", "")

def execute_llm(model: str, prompt: str) -> str:
    """Execute LLM call across Claude, Gemini, or local Ollama."""
    # 1. Anthropic Claude
    claude_key = get_claude_key()
    if claude_key and "claude" in model.lower():
        try:
            url = "https://api.anthropic.com/v1/messages"
            payload = {
                "model": model,
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "x-api-key": claude_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["content"][0]["text"].strip()
        except Exception:
            pass

    # 2. Google Gemini
    gemini_key = get_gemini_key()
    if gemini_key and ("gemini" in model.lower() or "claude" not in model.lower()):
        gemini_model = model if "gemini" in model else "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog-api-key": gemini_key}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            pass

    # 3. Local Ollama Fallback ($0 Local Compute)
    ollama_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434/api/generate")
    ollama_model = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
    try:
        req = urllib.request.Request(
            ollama_url,
            data=json.dumps({"model": ollama_model, "prompt": prompt, "stream": False}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except Exception as e:
        return f"[Routing Execution Note: Offline/API unavailable ({e})]"

def route_and_execute(prompt: str, bypass_cache: bool = False) -> Dict[str, Any]:
    """
    Main routing pipeline:
    1. Check Response Cache (0ms, $0)
    2. Score Complexity (1-10)
    3. Route to optimal model tier
    4. Save to cache & return
    """
    t0 = time.time()

    # 1. Check Cache
    if not bypass_cache:
        cached = get_cached_response(prompt)
        if cached:
            return {
                "response": cached["response"],
                "model": cached.get("model", "cached"),
                "tier": "Cache Hit",
                "complexity": 0,
                "cached": True,
                "latency": time.time() - t0
            }

    # 2. Score Complexity
    score, tier_desc = score_prompt_complexity(prompt)
    has_api = bool(get_gemini_key() or get_claude_key())

    # 3. Select Model based on complexity
    if score <= 3:
        # Simple grunt work
        model = os.environ.get("TIER3_MODEL", "gemini-3.5-flash-lite" if has_api else "qwen2.5:1.5b")
    elif score <= 7:
        # Standard balanced work
        model = os.environ.get("TIER2_MODEL", "gemini-2.5-flash" if has_api else "qwen2.5:1.5b")
    else:
        # Deep reasoning / architecture
        model = os.environ.get("TIER1_MODEL", "gemini-2.5-pro" if has_api else "qwen2.5:1.5b")

    # 4. Execute
    response_text = execute_llm(model, prompt)
    latency = time.time() - t0

    # 5. Save to Cache
    save_cached_response(prompt, response_text, model)

    return {
        "response": response_text,
        "model": model,
        "tier": tier_desc,
        "complexity": score,
        "cached": False,
        "latency": latency
    }

import re
from typing import Tuple

COMPLEX_KEYWORDS = [
    "architect", "refactor", "security", "concurrency", "deadlock",
    "algorithm", "optimize memory", "race condition", "protocol",
    "design pattern", "verification", "self-heal", "distributed",
    "cryptography", "vulnerability", "microservice", "consensus",
    "memory leak", "thread-safe", "zero-copy"
]

SIMPLE_KEYWORDS = [
    "what is", "syntax", "convert", "translate", "list", "format",
    "git status", "kill", "find", "grep", "time", "date", "echo",
    "spell check", "capitalize", "json to yaml", "base64"
]

def score_prompt_complexity(prompt: str) -> Tuple[int, str]:
    """
    Score prompt difficulty from 1 (simple grunt work) to 10 (frontier reasoning).
    Returns (score, tier_description).
    """
    score = 3  # baseline
    lower = prompt.lower()

    # Keyword analysis
    for kw in COMPLEX_KEYWORDS:
        if kw in lower:
            score += 2
    for kw in SIMPLE_KEYWORDS:
        if kw in lower:
            score -= 1

    # Length heuristics
    words = len(prompt.split())
    if words > 150:
        score += 2
    elif words < 15:
        score -= 1

    # Code structures or backticks
    if "```" in prompt or "def " in prompt or "class " in prompt or "interface " in prompt:
        score += 2

    # Multiple question marks or compound instructions
    if prompt.count("?") > 2 or "furthermore" in lower or "additionally" in lower:
        score += 1

    score = max(1, min(10, score))

    if score <= 3:
        tier = "Tier 3: Local / Low-Compute ($0)"
    elif score <= 7:
        tier = "Tier 2: Balanced Standard"
    else:
        tier = "Tier 1: High-Reasoning Frontier"

    return score, tier

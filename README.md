# ⚡ SmartRouter

> **Intelligent LLM Complexity Scorer, Response Cache & Dynamic Model Router**  
> *Inspired by RouteLLM, LiteLLM, and GPTCache.*  
> Cut LLM API costs by up to 85% by classifying prompt difficulty, routing easy queries to $0 local models, and serving repeated questions instantly from disk cache.

---

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://www.python.org/)

## 💡 The Efficiency Loop

> *"The expensive architecture sends every single problem to the smartest model.*  
> *The better architecture knows when frontier models are actually needed."*

```
Request ──▶ 1. Cache Check ──────[Hit]──────▶ Return (0ms, $0)
                 │ [Miss]
                 ▼
            2. Classify (1-10)
                 │
      ┌──────────┼──────────┐
      ▼          ▼          ▼
   Tier 3     Tier 2     Tier 1
 (Ollama /   (Flash /    (Pro /
Flash-Lite)   Sonnet)     Opus)
      │          │          │
      └──────────┼──────────┘
                 ▼
            3. Save Cache & Return
```

1. **Local Response Cache (GPTCache Pattern)**: Checks local SHA-256 cache. If already answered, returns immediately in <5ms with $0 token usage.
2. **Dynamic Complexity Scoring (RouteLLM Pattern)**: Evaluates prompts on a 1–10 difficulty scale based on keyword intent, code block density, reasoning indicators, and instruction depth.
3. **Smart Tier Routing (LiteLLM Pattern)**:
   - **Score ≤ 3 (Tier 3)**: Dispatched to local Ollama (`qwen2.5:1.5b`) or ultra-fast low-cost models ($0).
   - **Score 4–7 (Tier 2)**: Dispatched to balanced daily driver models (`gemini-2.5-flash`, `claude-3-5-sonnet`).
   - **Score 8–10 (Tier 1)**: Dispatched to frontier reasoning models (`gemini-2.5-pro`, `claude-3-7-sonnet`, `opus`).

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/apravint/smart-router.git
cd smart-router

# Install locally via pip
pip install -e .
```

---

## ⚡ Quick Start

### 1. Intelligent Route & Execute
```bash
smart-router "Convert this JSON timestamp to ISO-8601"
# ⚡ [ROUTED] Model: qwen2.5:1.5b | Complexity: 2/10 (Tier 3: Local / Low-Compute ($0))

smart-router "Architect a zero-copy distributed ring buffer for IPC across shared memory"
# ⚡ [ROUTED] Model: gemini-2.5-pro | Complexity: 9/10 (Tier 1: High-Reasoning Frontier)
```

### 2. Instant Cache Retrieval
Run the exact same prompt again:
```bash
smart-router "Convert this JSON timestamp to ISO-8601"
# ⚡ [CACHE HIT] Served from local disk in 1.2ms ($0 compute)
```

### 3. Complexity Scoring Only
Inspect how SmartRouter scores your prompt without triggering inference:
```bash
smart-router --score-only "How do I format a date in Python?"
# Prompt Complexity: 2/10
# Allocated Tier:    Tier 3: Local / Low-Compute ($0)
```

### 4. Cache Management & Stats
```bash
# View cache usage statistics
smart-router --stats

# Purge cached entries
smart-router --clear-cache
```

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|---|---|---|
| `TIER1_MODEL` | Frontier model for complex reasoning | `gemini-2.5-pro` (or `qwen2.5:1.5b`) |
| `TIER2_MODEL` | Standard model for balanced tasks | `gemini-2.5-flash` (or `qwen2.5:1.5b`) |
| `TIER3_MODEL` | Low-compute model for simple grunt queries | `gemini-3.5-flash-lite` (or `qwen2.5:1.5b`) |
| `GEMINI_API_KEY` | Google Gemini API Key | Optional |
| `ANTHROPIC_API_KEY` | Anthropic Claude API Key | Optional |
| `OLLAMA_HOST` | Local Ollama endpoint | `http://localhost:11434/api/generate` |

---

## 🧪 Testing

```bash
python3 -m unittest discover tests
```

---

## 📜 License

MIT License © 2026 [Ayyappa Pravin](https://github.com/apravint)

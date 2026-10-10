import sys
import os
import argparse
from smart_router.scorer import score_prompt_complexity
from smart_router.router import route_and_execute
from smart_router.cache import clear_cache, get_cache_stats

# ANSI Colors
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
MAGENTA = "\033[0;35m"
BOLD = "\033[1m"
NC = "\033[0m"

def main():
    parser = argparse.ArgumentParser(
        description="SmartRouter: Intelligent LLM Complexity Scorer, Response Cache & Dynamic Model Router"
    )
    parser.add_argument("prompt", nargs="*", help="Query or prompt to evaluate and route")
    parser.add_argument("--score-only", action="store_true", help="Only calculate and display complexity score")
    parser.add_argument("--no-cache", action="store_true", help="Bypass local response cache")
    parser.add_argument("--clear-cache", action="store_true", help="Purge all cached responses")
    parser.add_argument("--stats", action="store_true", help="Show cache usage statistics")
    args = parser.parse_args()

    if args.clear_cache:
        count = clear_cache()
        print(f"{GREEN}✓ Purged {count} cached AI responses.{NC}")
        return

    if args.stats:
        stats = get_cache_stats()
        print(f"{BOLD}SmartRouter Cache Statistics:{NC}")
        print(f"  • Total Entries: {stats['total_entries']}")
        print(f"  • Storage Size:  {stats['size_bytes'] / 1024:.2f} KB")
        return

    if not args.prompt:
        parser.print_help()
        print("\nExamples:")
        print("  smart-router 'Convert this JSON timestamp to ISO-8601'")
        print("  smart-router 'Architect a zero-copy distributed ring buffer for IPC'")
        print("  smart-router --score-only 'Explain how asyncio event loops work'")
        sys.exit(1)

    prompt_str = " ".join(args.prompt)

    if args.score_only:
        score, tier_desc = score_prompt_complexity(prompt_str)
        print(f"{BOLD}Prompt Complexity:{NC} {score}/10")
        print(f"{BOLD}Allocated Tier:{NC}    {tier_desc}")
        return

    result = route_and_execute(prompt_str, bypass_cache=args.no_cache)

    print(f"\n{result['response']}\n")
    if result["cached"]:
        print(f"{GREEN}⚡ [CACHE HIT]{NC} Served from local disk in {result['latency']*1000:.1f}ms ($0 compute)")
    else:
        print(f"{BLUE}⚡ [ROUTED]{NC} Model: {result['model']} | Complexity: {result['complexity']}/10 ({result['tier']}) | Latency: {result['latency']:.2f}s")

if __name__ == "__main__":
    main()

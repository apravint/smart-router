import unittest
from smart_router.scorer import score_prompt_complexity
from smart_router.cache import hash_prompt, save_cached_response, get_cached_response, clear_cache

class TestSmartRouter(unittest.TestCase):
    def test_simple_prompt_scoring(self):
        score, tier = score_prompt_complexity("What is the time?")
        self.assertLessEqual(score, 3)
        self.assertIn("Tier 3", tier)

    def test_complex_prompt_scoring(self):
        prompt = (
            "Architect a distributed zero-copy concurrency protocol avoiding race conditions "
            "and deadlocks across shared memory ring buffers."
        )
        score, tier = score_prompt_complexity(prompt)
        self.assertGreaterEqual(score, 7)
        self.assertIn("Tier 1", tier)

    def test_cache_hit_and_clear(self):
        test_prompt = "Test unique prompt for unit test 12345"
        save_cached_response(test_prompt, "Mock response", "mock-model")
        cached = get_cached_response(test_prompt)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["response"], "Mock response")

        # Test clear
        clear_cache()
        self.assertIsNone(get_cached_response(test_prompt))

if __name__ == "__main__":
    unittest.main()

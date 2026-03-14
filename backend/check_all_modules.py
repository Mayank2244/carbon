
import asyncio
import sys
import unittest
from unittest.mock import MagicMock
import os

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Imports
from app.modules.query_analyzer.service import QueryAnalyzer
from app.modules.query_analyzer.models import QueryDomain, QueryIntent
from app.modules.prompt_optimizer.optimizer import PromptOptimizer, OptimizedPrompt
from app.core.stats import stats_manager
from app.modules.carbon_api.carbon_api_client import CarbonAPIClient

class TestCarbonSenseModules(unittest.IsolatedAsyncioTestCase):
    
    async def test_1_query_analyzer(self):
        print("\n[TEST] 1. Query Analyzer Module")
        analyzer = QueryAnalyzer()
        
        # Test Case A: Tech Query
        query = "write a python script to optimize database queries"
        result = await analyzer.analyze(query)
        
        print(f"  Query: '{query}'")
        print(f"  Detected Domain: {result.domain}")
        print(f"  Detected Intent: {result.intent}")
        
        self.assertEqual(result.domain, QueryDomain.TECH)
        self.assertEqual(result.intent, QueryIntent.CREATIVE) # 'write' -> CREATIVE
        
        # Test Case B: General Question
        query2 = "why is the sky blue"
        result2 = await analyzer.analyze(query2)
        print(f"  Query: '{query2}'")
        print(f"  Detected Intent: {result2.intent}")
        self.assertEqual(result2.intent, QueryIntent.ANALYTICAL) # 'why' -> ANALYTICAL
        
        print("✓ Query Analyzer Passed")

    async def test_2_prompt_optimizer(self):
        print("\n[TEST] 2. Prompt Optimizer Module")
        optimizer = PromptOptimizer()
        
        # Test Semantic Compression (Filler removal)
        raw_prompt = "Can you please help me write a python function to sort a list?"
        dummy_meta = {"complexity": "SIMPLE", "carbon_budget": 100}
        
        optimized = optimizer.optimize(raw_prompt, [], dummy_meta)
        
        print(f"  Original: '{raw_prompt}'")
        print(f"  Optimized: '{optimized.text}'")
        print(f"  Savings: {optimized.original_tokens - optimized.tokens} tokens")
        
        # Check that filler words are gone
        self.assertNotIn("Can you please", optimized.text)
        self.assertIn("write a python function", optimized.text) # Core content remains
        
        print("✓ Prompt Optimizer Passed")

    async def test_3_carbon_api_client(self):
        print("\n[TEST] 3. Carbon API Client Module")
        
        # Mock CacheManager
        mock_cache = MagicMock()
        mock_cache.get.return_value = None # No cache hit
        
        # Initialize Client
        client = CarbonAPIClient(cache_manager=mock_cache)
        
        # Test Payload Construction (White-box testing logic)
        region_code = client._get_climatiq_region_code(48.8566, 2.3522)
        print(f"  Region Lookup (FR): {region_code}")
        self.assertEqual(region_code, "FR")
        
        # Test Fallback Logic directly (unit test internal method)
        fallback_data = client._get_fallback_data(region_code="FR")
        print(f"  Fallback Data (FR): {fallback_data.carbon_intensity} gCO2/kWh")
        self.assertEqual(fallback_data.carbon_intensity, 50.0) # Smart static for FR
        
        print("✓ Carbon API Logic Passed")

    async def test_4_stats_manager(self):
        print("\n[TEST] 4. Stats Manager Module")
        
        # Reset for test
        stats_manager.initialize()
        
        # Record a fake request
        stats_manager.record_request(
            model="TestModel",
            tokens_used=100,
            tokens_saved=20,
            carbon_used=0.5,
            carbon_saved=0.1,
            latency=150.0,
            cached=False,
            energy_used_kwh=0.01,
            energy_saved_kwh=0.002
        )
        
        metrics = stats_manager.get_live_metrics()
        print(f"  Recorded Metrics: {metrics}")
        
        self.assertEqual(metrics['tokens_saved'], 20)
        self.assertEqual(metrics['response_times'][0]['latency'], 150.0)
        
        print("✓ Stats Manager Passed")

    async def test_5_dependency_flow(self):
        print("\n[TEST] 5. Integration / Dependency Flow")
        print("  Checking how modules feed into each other...")
        
        # Simulate the pipeline in 'process_query'
        
        # 1. Analyzer
        analyzer = QueryAnalyzer()
        analysis = await analyzer.analyze("explain quantum physics")
        self.assertIsNotNone(analysis)
        
        # 2. Optimizer (Depends on Analyzer output)
        optimizer = PromptOptimizer()
        meta = {"complexity": str(analysis.complexity), "carbon_budget": 50}
        opt_result = optimizer.optimize("explain quantum physics", [], meta)
        
        # Optimizer should add "Detailed." or "Moderate." based on complexity
        print(f"  Optimizer instruction based on complexity ({analysis.complexity}): {opt_result.text.splitlines()[-1]}")
        
        # 3. Stats (Depends on Optimizer output)
        saved = opt_result.original_tokens - opt_result.tokens
        stats_manager.record_request(
            model="IntegrationTest", 
            tokens_used=10, 
            tokens_saved=saved, 
            carbon_saved=0, 
            carbon_used=0, 
            latency=0, 
            cached=False
        )
        
        self.assertGreaterEqual(stats_manager.total_tokens_saved, saved)
        
        print("✓ Dependency Chain Verified")

if __name__ == '__main__':
    unittest.main()

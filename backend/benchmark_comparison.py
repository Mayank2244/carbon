
import sys
import os
import asyncio
import time
# Removed tabulate dependency

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# MOCK SETTINGS to avoid .env issues
from unittest.mock import MagicMock
sys.modules['app.core.config'] = MagicMock()
sys.modules['app.core.config'].settings = MagicMock()

# Import logical modules
from app.modules.query_analyzer.service import QueryAnalyzer, QueryComplexity
from app.modules.prompt_optimizer.optimizer import PromptOptimizer

# Constants for Simulation
BASELINE_MODEL = "GPT-4"
BASELINE_REGION_CO2 = 475 # gCO2/kWh (Global Avg)
BASELINE_COST_PER_1K_TOKENS = 0.03 # $

# Updated Model Specs
CARBONSENSE_MODELS = {
    "SIMPLE": {"name": "Llama-3-8B", "cost_per_1k": 0.0002, "energy_factor": 0.1},
    "MEDIUM": {"name": "Llama-3-70B", "cost_per_1k": 0.0008, "energy_factor": 0.4},
    "COMPLEX": {"name": "Claude-3-Haiku", "cost_per_1k": 0.005, "energy_factor": 0.8}
}

GREEN_REGION_CO2 = 150 # gCO2/kWh (e.g., Sweden/Quebec)

async def run_benchmark():
    print("\n" + "="*80)
    print(" 🚀 CARBONSENSE AI VS. BASELINE: COMPARATIVE BENCHMARK")
    print("="*80)

    analyzer = QueryAnalyzer()
    optimizer = PromptOptimizer()

    test_cases = [
        "What is the capital of France?",
        "Please write a python script to calculate fibonacci numbers recursively and explain complexity.",
        "I need a detailed analysis of the impact of interest rates on housing markets in 2024.",
        "Who is the CEO of Tesla?", 
        "Who is the CEO of Tesla?" # Duplicate to test cache
    ]

    results = []
    
    # Cache Simulation (Simple Set)
    cache = set()

    print(f"\nProcessing {len(test_cases)} test queries...\n")

    print(f"{'ID':<3} | {'Type':<12} | {'Model':<18} | {'Tokens':<6} | {'Carbon':<10} | {'Cost':<10}")
    print("-" * 80)

    total_bl_c = 0.0
    total_cs_c = 0.0

    for i, query in enumerate(test_cases):
        # --- BASELINE ---
        bl_tokens = len(query) // 4
        # Baseline Energy (mock): Tokens * 1.0 energy unit * Region Intensity
        bl_carbon = (bl_tokens / 1000.0) * 1.0 * BASELINE_REGION_CO2 
        bl_cost = (bl_tokens / 1000.0) * BASELINE_COST_PER_1K_TOKENS
        
        # --- CARBONSENSE ---
        # 1. Cache Check
        is_cache_hit = query in cache
        
        if is_cache_hit:
            cs_tokens = 0
            cs_carbon = 0.0
            cs_cost = 0.0
            cs_model = "CACHE HIT"
            technique = "Cache"
        else:
            cache.add(query)
            
            # 2. Analyze
            analysis = await analyzer.analyze(query)
            complexity_enum = analysis.complexity # Enum
            complexity_name = complexity_enum.name # String "SIMPLE", "MEDIUM", etc.
            
            # 3. Optimize Prompt
            # Pass empty context/metadata for simulation
            optimized = optimizer.optimize(query, [], {"complexity": complexity_name})
            cs_tokens = optimized.tokens
            
            # 4. Route & Select Model
            model_info = CARBONSENSE_MODELS.get(complexity_name, CARBONSENSE_MODELS["COMPLEX"])
            cs_model = model_info["name"]
            
            # Calc Impact
            # Energy = Tokens * Factor
            # Carbon = Energy * GreenRegion intensity
            cs_energy = (cs_tokens / 1000.0) * model_info["energy_factor"]
            cs_carbon = cs_energy * GREEN_REGION_CO2
            cs_cost = (cs_tokens / 1000.0) * model_info["cost_per_1k"]
            technique = "Opt+Route"

        # Accumulate totals
        total_bl_c += bl_carbon
        total_cs_c += cs_carbon

        # Print Row
        print(f"{i+1:<3} | {'Baseline':<12} | {BASELINE_MODEL:<18} | {bl_tokens:<6} | {bl_carbon:.4f} g   | ${bl_cost:.5f}")
        print(f"{'':<3} | {'CarbonSense':<12} | {cs_model:<18} | {cs_tokens:<6} | {cs_carbon:.4f} g   | ${cs_cost:.5f}")
        
        # Savings row
        saved_c = bl_carbon - cs_carbon
        saved_cost = bl_cost - cs_cost
        pct_c = (saved_c / bl_carbon * 100) if bl_carbon > 0 else 0
        print(f"{'':<3} | {'SAVINGS':<12} | {'':<18} | {'':<6} | -{pct_c:.1f}%      | -${saved_cost:.5f}")
        print("-" * 80)
    
    print("\n" + "="*80)
    final_savings = ((total_bl_c - total_cs_c)/total_bl_c)*100 if total_bl_c > 0 else 0
    print(f"TOTAL CARBON REDUCTION: {final_savings:.1f}%")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(run_benchmark())

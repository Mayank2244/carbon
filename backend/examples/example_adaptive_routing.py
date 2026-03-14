"""
Example: Adaptive Model Routing
Demonstrates the adaptive model selector with carbon tracking and escalation.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.modules.model_selector import (
    AdaptiveOrchestrator,
    QueryMetadata,
    ModelTier
)
from app.core.logging import get_logger

logger = get_logger(__name__)


async def main():
    """Run adaptive routing examples."""
    
    print("=" * 80)
    print("ADAPTIVE MODEL SELECTOR DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Initialize orchestrator
    orchestrator = AdaptiveOrchestrator(
        carbon_budget=1000.0,  # 1000g daily budget
        quality_threshold=0.7,
        enable_fallback=True
    )
    
    # Example queries with different complexity levels
    test_queries = [
        {
            "query": "What is Python?",
            "metadata": QueryMetadata(
                query="What is Python?",
                query_type="definition",
                complexity=0.2,
                estimated_tokens=100
            ),
            "expected_tier": ModelTier.TINY
        },
        {
            "query": "Explain how neural networks learn through backpropagation",
            "metadata": QueryMetadata(
                query="Explain how neural networks learn through backpropagation",
                query_type="explanation",
                complexity=0.5,
                estimated_tokens=300
            ),
            "expected_tier": ModelTier.SMALL
        },
        {
            "query": "Write a Python implementation of a transformer model with attention mechanism",
            "metadata": QueryMetadata(
                query="Write a Python implementation of a transformer model with attention mechanism",
                query_type="code_advanced",
                complexity=0.8,
                estimated_tokens=500
            ),
            "expected_tier": ModelTier.MEDIUM
        },
        {
            "query": "Conduct a comprehensive analysis of quantum computing's impact on cryptography",
            "metadata": QueryMetadata(
                query="Conduct a comprehensive analysis of quantum computing's impact on cryptography",
                query_type="research",
                complexity=0.95,
                estimated_tokens=800
            ),
            "expected_tier": ModelTier.LARGE
        }
    ]
    
    print("Testing queries with different complexity levels...")
    print()
    
    results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Query {i}/{len(test_queries)}")
        print(f"{'=' * 80}")
        print(f"Query: {test['query'][:70]}...")
        print(f"Expected Tier: {test['expected_tier'].value}")
        print(f"Complexity: {test['metadata'].complexity:.2f}")
        print()
        
        try:
            # Note: This will fail without actual API keys or local models
            # For demonstration, we'll show the selection logic
            selected_model = orchestrator.selector.select_model(test['metadata'])
            
            print(f"✓ Selected Model: {selected_model.name} ({selected_model.tier.value})")
            print(f"  Carbon/1k tokens: {selected_model.carbon_per_1k_tokens}g")
            print(f"  Cost/1M tokens: ${selected_model.cost_per_1m_tokens}")
            print(f"  Max tokens: {selected_model.max_tokens}")
            print(f"  Endpoint: {selected_model.endpoint}")
            
            # Estimate costs
            estimated_carbon = orchestrator.selector.estimate_carbon_cost(
                selected_model.name,
                test['metadata'].estimated_tokens
            )
            print(f"  Estimated carbon: {estimated_carbon:.2f}g")
            
            results.append({
                "query": test['query'][:50],
                "expected": test['expected_tier'].value,
                "selected": selected_model.tier.value,
                "carbon": estimated_carbon,
                "match": selected_model.tier == test['expected_tier']
            })
            
        except Exception as e:
            print(f"✗ Error: {e}")
            results.append({
                "query": test['query'][:50],
                "expected": test['expected_tier'].value,
                "selected": "error",
                "carbon": 0,
                "match": False
            })
    
    # Display summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print()
    
    print("Query Routing Results:")
    print("-" * 80)
    for i, result in enumerate(results, 1):
        match_symbol = "✓" if result['match'] else "✗"
        print(f"{i}. {match_symbol} {result['query'][:40]:40} | "
              f"Expected: {result['expected']:6} | "
              f"Selected: {result['selected']:6} | "
              f"Carbon: {result['carbon']:5.2f}g")
    
    # Calculate statistics
    total_carbon = sum(r['carbon'] for r in results)
    matches = sum(1 for r in results if r['match'])
    
    print()
    print("Statistics:")
    print(f"  Total queries: {len(results)}")
    print(f"  Correct routing: {matches}/{len(results)} ({matches/len(results)*100:.1f}%)")
    print(f"  Total carbon: {total_carbon:.2f}g")
    
    # Compare to baseline (always GPT-4)
    baseline_carbon = sum(test['metadata'].estimated_tokens * 0.02 for test in test_queries)  # 20g per 1k tokens
    savings = baseline_carbon - total_carbon
    savings_pct = (savings / baseline_carbon) * 100 if baseline_carbon > 0 else 0
    
    print(f"  Baseline (always GPT-4): {baseline_carbon:.2f}g")
    print(f"  Carbon saved: {savings:.2f}g ({savings_pct:.1f}%)")
    
    # Get usage stats
    stats = orchestrator.get_stats()
    print()
    print("Usage Statistics:")
    print(f"  Total queries processed: {stats.total_queries}")
    print(f"  Escalations: {stats.escalations}")
    print(f"  Total carbon: {stats.total_carbon_grams:.2f}g")
    print(f"  Total cost: ${stats.total_cost_usd:.4f}")
    
    if stats.total_queries > 0:
        print()
        print("Model Distribution:")
        for tier in ModelTier:
            pct = stats.get_tier_percentage(tier)
            count = stats.queries_by_tier.get(tier, 0)
            bar = "█" * int(pct / 2)  # Scale to 50 chars max
            print(f"  {tier.value:6}: {count:2} ({pct:5.1f}%) {bar}")
    
    print()
    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("Note: To test actual model generation, you need to:")
    print("  1. Set OPENAI_API_KEY and ANTHROPIC_API_KEY in .env")
    print("  2. Download local models (TinyLlama and Llama-3.2-3B)")
    print("  3. Run with --test-generation flag")
    print()


if __name__ == "__main__":
    asyncio.run(main())

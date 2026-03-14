"""
Validation Suite for Prompt Optimizer.
Measures compression rates and quality preservation.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to run as script
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.modules.prompt_optimizer.optimizer import PromptOptimizer
from app.modules.prompt_optimizer.evaluator import QualityEvaluator

def run_validation():
    print("Starting Prompt Optimizer Validation...\n")
    
    optimizer = PromptOptimizer()
    evaluator = QualityEvaluator()
    
    test_cases = [
        {
            "prompt": "You are a helpful assistant. Please explain what machine learning is in simple terms.",
            "type": "explanation",
            "metadata": {"complexity": "SIMPLE", "carbon_budget": 50}
        },
        {
            "prompt": "I would like you to write a python function to calculate fibonacci sequence.",
            "type": "code",
            "metadata": {"complexity": "MEDIUM", "carbon_budget": 50}
        },
        {
            "prompt": "Can you please compare the difference between TCP and UDP protocols?",
            "type": "comparison",
            "metadata": {"complexity": "MEDIUM", "carbon_budget": 50}
        },
        {
            "prompt": "Summarize the history of the Roman Empire for me.",
            "type": "summarize",
            "metadata": {"complexity": "complex", "carbon_budget": 100}
        },
        {
            "prompt": "Translate 'Hello world' to Spanish please.",
            "type": "translation",
            "metadata": {"complexity": "SIMPLE", "carbon_budget": 5}
        }
    ]
    
    total_reduction = 0.0
    total_similarity = 0.0
    count = len(test_cases)
    
    print(f"{'Original':<60} | {'Optimized':<40} | {'Ratio':<6}")
    print("-" * 115)
    
    for case in test_cases:
        # Optimization
        optimized = optimizer.optimize(case['prompt'], [], case['metadata'])
        
        # Quality Check (Simulated: comparing prompt intent preservation, not response)
        # In real scenario, we'd generate responses from both and compare those.
        # Here we check if semantic meaning of PROMPT is preserved.
        similarity = evaluator.evaluate_similarity(case['prompt'], optimized.text)
        
        print(f"{case['prompt'][:58]:<60} | {optimized.text.splitlines()[0][:38]:<40} | {optimized.compression_ratio:.1%}")
        
        total_reduction += optimized.compression_ratio
        total_similarity += similarity
        
    avg_reduction = total_reduction / count
    avg_sim = total_similarity / count
    
    print("-" * 115)
    print(f"\nRESULTS:")
    print(f"Average Compression: {avg_reduction:.1%}")
    print(f"Average Similarity:  {avg_sim:.3f}")
    
    if avg_reduction > 0.70:
        print("\n✅ SUCCESS: Target reduction > 70% achieved!")
    else:
        print(f"\n⚠️ WARNING: Reduction {avg_reduction:.1%} below target 70%")

if __name__ == "__main__":
    run_validation()

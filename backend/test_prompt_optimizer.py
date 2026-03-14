#!/usr/bin/env python3
"""
Standalone test for Prompt Optimizer - No dependencies on app config.
Demonstrates token reduction and optimization techniques.
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class OptimizedPrompt:
    """Result of optimization process."""
    text: str
    tokens: int
    original_tokens: int
    compression_ratio: float
    technique_used: str

class SimplePromptOptimizer:
    """Simplified prompt optimizer for testing."""
    
    UNNECESSARY_PHRASES = [
        "You are a helpful assistant", "You are an AI", "Please provide", 
        "I would like you to", "Can you please", "Could you", "Thank you for", 
        "I need help with", "I want to know", "Make sure to", "Please"
    ]
    
    def optimize(self, prompt: str) -> OptimizedPrompt:
        """Optimize a prompt by removing unnecessary words."""
        original_tokens = self._estimate_tokens(prompt)
        
        # Semantic compression
        compressed_text = self.compress_semantic(prompt)
        
        final_tokens = self._estimate_tokens(compressed_text)
        ratio = 1.0 - (final_tokens / original_tokens) if original_tokens > 0 else 0.0
        
        return OptimizedPrompt(
            text=compressed_text,
            tokens=final_tokens,
            original_tokens=original_tokens,
            compression_ratio=ratio,
            technique_used="semantic"
        )
    
    def compress_semantic(self, prompt: str) -> str:
        """Remove unnecessary politeness and filler words."""
        compressed = prompt
        for phrase in self.UNNECESSARY_PHRASES:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            compressed = pattern.sub("", compressed)
        
        # Remove redundant spaces
        compressed = " ".join(compressed.split())
        return compressed
    
    def _estimate_tokens(self, text: str) -> int:
        """Simple heuristic estimation (avg 4 chars/token)."""
        return len(text) // 4


def run_tests():
    """Run comprehensive tests on prompt optimizer."""
    optimizer = SimplePromptOptimizer()
    
    print("\n" + "="*70)
    print("  PROMPT OPTIMIZER - COMPRESSION TESTS")
    print("="*70)
    
    test_cases = [
        {
            "name": "Polite Query",
            "prompt": "Please can you help me explain what is machine learning? I would like to know more about it. Thank you."
        },
        {
            "name": "Verbose Question",
            "prompt": "You are a helpful assistant. Can you please tell me the difference between deep learning and machine learning? I need help with understanding this concept."
        },
        {
            "name": "Simple Query",
            "prompt": "What is artificial intelligence?"
        },
        {
            "name": "Complex Query",
            "prompt": "Please provide a detailed explanation of how neural networks work, including backpropagation. I want to know the mathematical foundations. Thank you for your help."
        }
    ]
    
    total_original = 0
    total_optimized = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*70}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'─'*70}")
        
        original = test['prompt']
        result = optimizer.optimize(original)
        
        print(f"\n📝 ORIGINAL ({result.original_tokens} tokens):")
        print(f"   \"{original}\"")
        
        print(f"\n✨ OPTIMIZED ({result.tokens} tokens):")
        print(f"   \"{result.text}\"")
        
        print(f"\n📊 METRICS:")
        print(f"   • Original tokens:  {result.original_tokens}")
        print(f"   • Optimized tokens: {result.tokens}")
        print(f"   • Tokens saved:     {result.original_tokens - result.tokens}")
        print(f"   • Compression:      {result.compression_ratio:.1%}")
        print(f"   • Technique:        {result.technique_used}")
        
        total_original += result.original_tokens
        total_optimized += result.tokens
    
    # Summary
    print(f"\n{'='*70}")
    print("  SUMMARY")
    print(f"{'='*70}")
    print(f"\n📈 OVERALL STATISTICS:")
    print(f"   • Total original tokens:  {total_original}")
    print(f"   • Total optimized tokens: {total_optimized}")
    print(f"   • Total tokens saved:     {total_original - total_optimized}")
    print(f"   • Average compression:    {(1 - total_optimized/total_original):.1%}")
    
    # Energy impact
    print(f"\n⚡ ENERGY IMPACT:")
    baseline_energy = total_original * 50 / 3_600_000  # 50 J/token baseline
    optimized_energy = total_optimized * 50 / 3_600_000
    saved_energy = baseline_energy - optimized_energy
    
    print(f"   • Baseline energy:   {baseline_energy*1000:.2f} Wh")
    print(f"   • Optimized energy:  {optimized_energy*1000:.2f} Wh")
    print(f"   • Energy saved:      {saved_energy*1000:.2f} Wh")
    print(f"   • Savings:           {(saved_energy/baseline_energy):.1%}")
    
    print(f"\n{'='*70}")
    print("✅ ALL TESTS COMPLETED")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    run_tests()

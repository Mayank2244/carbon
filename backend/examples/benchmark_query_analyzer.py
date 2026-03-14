"""
Benchmark Script for Query Analyzer.
Measures performance and accuracy on a sample dataset.
"""

import asyncio
import time
import statistics
from typing import List
from app.modules.query_analyzer import QueryAnalyzer

SAMPLE_QUERIES = [
    "What is the capital of France?",
    "Write a Python function to sort a list.",
    "Critical error in production database, help immediately!",
    "Analyze the Q3 financial report for revenue trends.",
    "How do I treat a headache?",
    "What did he say previously?",
    "Compare docker and kubernetes architecture.",
    "Generate a logo design for a coffee shop.",
    "Schedule a meeting for tomorrow morning.",
    "Why is the sky blue?",
    "Debug this java class for null pointer exceptions.",
    "Buy 50 shares of Apple stock now.",
    "Explain quantum computing to a 5 year old.",
    "Who won the 1994 World Cup?",
    "Create a marketing plan for the new product.",
    "Is the server down right now?",
    "Calculate the mortgage payment for a $500k house.",
    "What is the difference between virus and bacteria?",
    "Optimize this SQL query for better performance.",
    "When is the next flight to New York?",
    # Add more to reach ~50 mixed queries
    "Write a story about a robot.",
    "System crash urgent assistance needed.",
    "Review the code changes.",
    "What are the side effects of aspirin?",
    "Transfer $100 to savings account.",
    "Analyze the impact of inflation on bond yields.",
    "How does the immune system work?",
    "Install python 3.11 on ubuntu.",
    "What is the weather in Tokyo?",
    "Make a reservation for dinner tonight.",
] * 2  # Duplicate to increase count

async def run_benchmark():
    print("=" * 60)
    print("Query Analyzer Performance Benchmark")
    print("=" * 60)
    
    # Initialize
    print("Initializing Analyzer...")
    start_init = time.time()
    analyzer = QueryAnalyzer()
    init_time = time.time() - start_init
    print(f"Initialization (with model load): {init_time:.4f}s")
    
    latencies = []
    
    print(f"\nProcessing {len(SAMPLE_QUERIES)} queries...")
    
    for i, query in enumerate(SAMPLE_QUERIES):
        start_q = time.time()
        result = await analyzer.analyze(query)
        duration_ms = (time.time() - start_q) * 1000
        latencies.append(duration_ms)
        
        # Print first 5 results as sanity check
        if i < 5:
            print(f"\nQuery: {query[:50]}...")
            print(f"  -> {result.intent.value} | {result.complexity.value} | {result.domain.value} | {result.urgency.value}")
            print(f"  -> Time: {duration_ms:.2f}ms")

    # Statistics
    avg_latency = statistics.mean(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    p99_latency = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
    
    print("\n" + "=" * 60)
    print("Results")
    print("=" * 60)
    print(f"Total Queries:      {len(SAMPLE_QUERIES)}")
    print(f"Average Latency:    {avg_latency:.2f} ms")
    print(f"P95 Latency:        {p95_latency:.2f} ms")
    print(f"P99 Latency:        {p99_latency:.2f} ms")
    print(f"Throughput:         {1000/avg_latency:.1f} queries/sec")
    
    if avg_latency < 10:
        print("\n✅ PASSED: Average latency < 10ms")
    else:
        print(f"\n⚠️ WARNING: Average latency {avg_latency:.2f}ms > 10ms target")

if __name__ == "__main__":
    asyncio.run(run_benchmark())

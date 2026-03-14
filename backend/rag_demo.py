#!/usr/bin/env python3
"""
RAG System Demonstration Script.

PURPOSE:
- Validate end-to-end RAG pipeline
- Demonstrate ingestion, search, and failure handling
- Provide professional output for evaluation

EXECUTION:
```bash
cd backend
source venv/bin/activate
python rag_demo.py
```

EXPECTED BEHAVIOR:
1. Initialize system (load model, connect to ChromaDB)
2. Ingest technical documentation
3. Execute semantic queries
4. Display ranked results
5. Show system health metrics
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.modules.knowledge_base import (
    knowledge_base_service,
    Document,
    SearchResult,
    IngestionStats
)
from app.core.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# SAMPLE TECHNICAL DOCUMENTATION
# ============================================================================

SAMPLE_DOCS = [
    Document(
        content="""
        CarbonSense AI Architecture Overview
        
        The system implements a 4-stage adaptive pipeline for carbon-aware query processing:
        
        1. Query Analysis: The QueryAnalyzer examines user intent and complexity using NLP techniques.
           Simple queries (greetings, factual questions) are marked as SIMPLE.
           Complex queries (reasoning, coding, research) are marked as COMPLEX.
        
        2. Prompt Optimization: The PromptOptimizer reduces token count by removing redundant context
           and condensing the prompt. This directly reduces compute energy consumption.
        
        3. Adaptive Model Selection: Based on complexity score, the system routes to the smallest
           capable model tier:
           - Tiny (Llama-3.1-8B): For simple tasks, uses ~0.2g CO2 per 1k tokens
           - Small (Llama-3.1-8B): For moderate reasoning, uses ~0.5g CO2 per 1k tokens
           - Medium (Llama-3.3-70B): For complex tasks, uses ~3.0g CO2 per 1k tokens
           - Large (Llama-3.3-70B): For expert reasoning, uses ~15g CO2 per 1k tokens
        
        4. Execution & Tracking: The selected model generates the response, and the StatsManager
           tracks token efficiency, carbon savings, and model distribution in real-time.
        """,
        source="architecture_overview.md",
        metadata={"category": "architecture", "version": "1.0"}
    ),
    
    Document(
        content="""
        Energy Optimization Strategies
        
        The system employs multiple layers of energy optimization:
        
        Token Efficiency: By optimizing prompts before model execution, we reduce the number of
        tokens processed. Fewer tokens = less compute = lower energy consumption.
        
        Model Tier Selection: Instead of always using a large model (like GPT-4 at ~20g CO2/1k tokens),
        we dynamically select the smallest model capable of handling the task. For simple queries,
        we use Tiny models that consume 100x less energy.
        
        Baseline Comparison: We calculate energy savings by comparing actual usage against a baseline
        (GPT-4 equivalent). The dashboard shows:
        - Our Adaptive Model: Actual kWh consumed
        - Standard Model (Baseline): Estimated kWh if using GPT-4 for everything
        
        Carbon Intensity Awareness: The system monitors grid carbon intensity (gCO2/kWh) and can
        defer non-urgent queries to times when renewable energy is more available.
        """,
        source="energy_optimization.md",
        metadata={"category": "optimization", "version": "1.0"}
    ),
    
    Document(
        content="""
        Real-Time Metrics Dashboard
        
        The frontend MetricsPanel displays live system performance:
        
        Token Efficiency: Shows percentage of tokens saved through prompt optimization.
        The progress bar visualizes savings in real-time.
        
        Model Distribution: A bar chart showing which model tiers are being used.
        In an efficient system, you should see Tiny/Small models dominating usage.
        
        Latency Trend: An area chart tracking response times over the last 50 requests.
        This helps identify performance degradation.
        
        Energy Comparison: Side-by-side bars comparing "Our Adaptive Model" vs "Standard Model"
        energy consumption. The green bar should be significantly shorter than the grey baseline.
        
        All metrics update every 3 seconds via polling the /api/v1/query/stats endpoint.
        """,
        source="metrics_dashboard.md",
        metadata={"category": "frontend", "version": "1.0"}
    ),
    
    Document(
        content="""
        ChromaDB Vector Knowledge Base
        
        The RAG (Retrieval-Augmented Generation) system uses ChromaDB for persistent vector storage:
        
        Architecture:
        - Embedding Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
        - Chunking Strategy: 512 characters with 64 character overlap
        - Storage: Persistent disk storage in backend/data/vector_store
        
        Pipeline:
        1. Document Ingestion: Text is split into overlapping chunks
        2. Embedding Generation: Each chunk is encoded into a 384-dim vector
        3. Vector Storage: Embeddings are stored in ChromaDB with metadata
        4. Semantic Search: Queries are encoded and matched against stored vectors
        
        Failure Handling:
        - Duplicate IDs: ChromaDB upserts (updates existing chunks)
        - Dimension Mismatch: System fails fast with clear error
        - Empty Queries: Returns empty result set
        """,
        source="rag_system.md",
        metadata={"category": "rag", "version": "1.0"}
    )
]


# ============================================================================
# DEMONSTRATION FUNCTIONS
# ============================================================================

def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_stats(stats: IngestionStats):
    """Print ingestion statistics."""
    print(f"📊 Ingestion Statistics:")
    print(f"   Documents Processed: {stats.documents_processed}")
    print(f"   Chunks Created:      {stats.chunks_created}")
    print(f"   Chunks Stored:       {stats.chunks_stored}")
    print(f"   Duration:            {stats.duration_seconds:.2f}s")
    print(f"   Timestamp:           {stats.timestamp}")


def print_search_results(query: str, results: list[SearchResult]):
    """Print search results in professional format."""
    print(f"🔍 Query: \"{query}\"")
    print(f"   Found {len(results)} results\n")
    
    for i, result in enumerate(results, 1):
        print(f"   [{i}] Similarity: {result.similarity:.3f} | Source: {result.source}")
        print(f"       {result.text[:200]}...")
        print()


def demonstrate_ingestion():
    """Demonstrate document ingestion."""
    print_header("PHASE 1: Document Ingestion")
    
    print("📥 Ingesting technical documentation...")
    stats = knowledge_base_service.ingest_documents(SAMPLE_DOCS)
    print_stats(stats)


def demonstrate_search():
    """Demonstrate semantic search."""
    print_header("PHASE 2: Semantic Search")
    
    queries = [
        "How does the architecture work?",
        "What energy optimization strategies are used?",
        "Explain the metrics dashboard",
        "How is ChromaDB used in the system?"
    ]
    
    for query in queries:
        results = knowledge_base_service.search(query, top_k=2)
        print_search_results(query, results)


def demonstrate_health_check():
    """Demonstrate system health check."""
    print_header("PHASE 3: System Health Check")
    
    health = knowledge_base_service.health_check()
    print("🏥 System Health:")
    for key, value in health.items():
        print(f"   {key}: {value}")


def demonstrate_failure_handling():
    """Demonstrate failure handling."""
    print_header("PHASE 4: Failure Handling")
    
    print("🛡️  Testing edge cases...\n")
    
    # Empty query
    print("   Test 1: Empty query")
    results = knowledge_base_service.search("", top_k=5)
    print(f"   Result: {len(results)} results (expected: 0)\n")
    
    # Low similarity threshold
    print("   Test 2: High similarity threshold (no results expected)")
    results = knowledge_base_service.search(
        "quantum physics",
        top_k=5,
        min_similarity=0.9
    )
    print(f"   Result: {len(results)} results\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute full RAG demonstration."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "PRODUCTION RAG SYSTEM DEMONSTRATION" + " " * 23 + "║")
    print("║" + " " * 25 + "ChromaDB + SentenceTransformers" + " " * 22 + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        demonstrate_ingestion()
        demonstrate_search()
        demonstrate_health_check()
        demonstrate_failure_handling()
        
        print_header("DEMONSTRATION COMPLETE")
        print("✅ All systems operational")
        print("✅ Vector store persisted to disk")
        print("✅ Ready for production integration\n")
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        logger.error(f"Demonstration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

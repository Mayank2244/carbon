"""
GraphRAG Demo Script
Demonstrates the Knowledge Graph RAG system with example queries.
"""

import asyncio
import time
from app.db.neo4j import init_neo4j, close_neo4j
from app.db.redis import init_redis, close_redis
from app.core.logging import setup_logging, get_logger
from app.modules.graph_rag import GraphRAG

setup_logging()
logger = get_logger(__name__)


async def demo_query(graph_rag: GraphRAG, query: str):
    """
    Run a demo query and display results.
    
    Args:
        graph_rag: GraphRAG instance
        query: Query to process
    """
    logger.info("=" * 80)
    logger.info(f"Query: {query}")
    logger.info("=" * 80)
    
    start_time = time.time()
    response = await graph_rag.query(query)
    elapsed = time.time() - start_time
    
    logger.info(f"\n✓ Answer: {response.answer}")
    logger.info(f"\n📊 Metrics:")
    logger.info(f"  - Confidence: {response.confidence:.2f}")
    logger.info(f"  - Used GraphRAG: {response.used_graph_rag}")
    logger.info(f"  - Used Small LLM: {response.used_small_llm}")
    logger.info(f"  - Fallback to Full LLM: {response.fallback_to_full_llm}")
    logger.info(f"  - Entities Found: {response.entities_found}")
    logger.info(f"  - Paths Explored: {response.paths_explored}")
    logger.info(f"  - Nodes Traversed: {response.nodes_traversed}")
    logger.info(f"  - Query Time: {elapsed*1000:.2f}ms")
    logger.info(f"  - Estimated Carbon: {response.estimated_carbon_g:.2f}g CO2")
    
    if response.carbon_saved_g:
        logger.info(f"  - Carbon Saved: {response.carbon_saved_g:.2f}g CO2 (vs full LLM)")
    
    if response.citations:
        logger.info(f"\n📚 Citations: {', '.join(response.citations[:5])}")
    
    if response.graph_context:
        logger.info(f"\n🔍 Graph Context:")
        for i, entity in enumerate(response.graph_context.entities[:3], 1):
            logger.info(f"  {i}. {entity.normalized} (confidence: {entity.confidence:.2f})")
    
    logger.info("\n")


async def main():
    """Run GraphRAG demo with example queries."""
    
    logger.info("🚀 GraphRAG Demo - Knowledge Graph-based RAG System")
    logger.info("=" * 80)
    
    try:
        # Initialize connections
        logger.info("Initializing connections...")
        await init_neo4j()
        await init_redis()
        
        # Initialize GraphRAG
        graph_rag = GraphRAG()
        
        # Demo queries
        queries = [
            "What is machine learning?",
            "How does Python use neural networks?",
            "What tools are needed for computer vision?",
            "Explain deep learning and its relationship to AI",
            "What is the difference between SQL and NoSQL?",
            "How do transformers work in NLP?",
        ]
        
        logger.info(f"\nRunning {len(queries)} demo queries...\n")
        
        total_carbon_saved = 0.0
        rag_count = 0
        
        for query in queries:
            response = await demo_query(graph_rag, query)
            
            if response.used_graph_rag:
                rag_count += 1
                if response.carbon_saved_g:
                    total_carbon_saved += response.carbon_saved_g
            
            await asyncio.sleep(1)  # Brief pause between queries
        
        # Summary
        logger.info("=" * 80)
        logger.info("📈 Demo Summary")
        logger.info("=" * 80)
        logger.info(f"Total Queries: {len(queries)}")
        logger.info(f"Answered via GraphRAG: {rag_count} ({rag_count/len(queries)*100:.1f}%)")
        logger.info(f"Total Carbon Saved: {total_carbon_saved:.2f}g CO2")
        logger.info(f"Average Savings per Query: {total_carbon_saved/len(queries):.2f}g CO2")
        
        carbon_reduction = (total_carbon_saved / (len(queries) * 5.0)) * 100
        logger.info(f"Carbon Reduction: {carbon_reduction:.1f}% vs full LLM")
        
        logger.info("\n✅ Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
    finally:
        await close_redis()
        await close_neo4j()


if __name__ == "__main__":
    asyncio.run(main())

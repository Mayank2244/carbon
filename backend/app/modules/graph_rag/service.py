"""
Main GraphRAG implementation.
Orchestrates entity extraction, graph traversal, and answer generation.
"""

import time
from typing import Optional
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.modules.graph_rag.models import GraphContext, RAGResponse
from app.modules.graph_rag.entity_extractor import EntityExtractor
from app.modules.graph_rag.graph_traversal import GraphTraversal
from app.modules.graph_rag.confidence_scorer import ConfidenceScorer

logger = get_logger(__name__)


class GraphRAG:
    """
    Knowledge Graph-based RAG system.
    Answers queries using graph traversal and minimal LLM calls.
    """
    
    def __init__(
        self,
        confidence_threshold: Optional[float] = None,
        max_depth: Optional[int] = None,
        small_llm_model: Optional[str] = None
    ):
        """
        Initialize GraphRAG system.
        
        Args:
            confidence_threshold: Minimum confidence to answer (default from settings)
            max_depth: Maximum graph traversal depth (default from settings)
            small_llm_model: Small LLM model name (default from settings)
        """
        self.confidence_threshold = confidence_threshold or settings.graph_rag_confidence_threshold
        self.max_depth = max_depth or settings.graph_rag_max_depth
        self.small_llm_model = small_llm_model or settings.small_llm_model
        
        # Initialize components
        self.entity_extractor = EntityExtractor()
        self.graph_traversal = GraphTraversal(max_depth=self.max_depth)
        self.confidence_scorer = ConfidenceScorer(threshold=self.confidence_threshold)
        
        logger.info(
            f"GraphRAG initialized - threshold: {self.confidence_threshold}, "
            f"max_depth: {self.max_depth}, model: {self.small_llm_model}"
        )
    
    async def query(self, query: str) -> RAGResponse:
        """
        Executes the full GraphRAG pipeline for a user query.

        Workflow:
        1. Extract entities from query.
        2. Link entities to nodes in the Knowledge Graph.
        3. Traverse graph to find relevant paths and context.
        4. Calculate confidence based on graph coverage.
        5. Generate answer using a small LLM (high confidence) or fallback to full LLM.

        Args:
            query (str): The user's input query.

        Returns:
            RAGResponse: Structured answer with citations and graph metadata.
        """
        start_time = time.time()
        
        try:
            # Step 1: Extract entities
            logger.info(f"Processing query: {query}")
            entities = await self.entity_extractor.extract_entities(query)
            
            if not entities:
                logger.warning("No entities extracted, falling back to full LLM")
                return await self._fallback_to_full_llm(query, start_time)
            
            # Step 2: Link entities to graph
            entities = await self.entity_extractor.link_entities_to_graph(entities)
            
            # Step 3: Traverse graph to find relevant paths
            paths = await self.graph_traversal.find_paths(entities)
            
            if not paths:
                logger.warning("No relevant paths found, falling back to full LLM")
                return await self._fallback_to_full_llm(query, start_time)
            
            # Step 4: Assemble context
            context = GraphContext(
                query=query,
                entities=entities,
                paths=paths,
                total_nodes=len(set(n.name for p in paths for n in p.nodes)),
                total_relationships=sum(len(p.relationships) for p in paths),
                traversal_depth=max(p.length for p in paths) if paths else 0
            )
            
            # Step 5: Calculate confidence
            confidence = self.confidence_scorer.calculate_confidence(query, entities, context)
            
            # Step 6: Generate answer based on confidence
            if self.confidence_scorer.should_answer(confidence):
                logger.info(f"High confidence ({confidence:.2f}), using small LLM for synthesis")
                return await self._generate_with_small_llm(query, context, confidence, start_time)
            else:
                logger.info(f"Low confidence ({confidence:.2f}), falling back to full LLM")
                return await self._fallback_to_full_llm(query, start_time, context)
        
        except Exception as e:
            logger.error(f"GraphRAG error: {e}", exc_info=True)
            return await self._fallback_to_full_llm(query, start_time)
    
    async def _generate_with_small_llm(
        self,
        query: str,
        context: GraphContext,
        confidence: float,
        start_time: float
    ) -> RAGResponse:
        """
        Generate answer using small LLM with graph context.
        
        Args:
            query: User query
            context: Graph context
            confidence: Confidence score
            start_time: Query start time
            
        Returns:
            RAG response
        """
        # Prepare context for LLM
        context_text = context.get_context_text()
        
        # Call small LLM via Groq API
        prompt = f"""Based on the following knowledge graph context, answer the user's question concisely and accurately.

{context_text}

Question: {query}

Answer (be concise and cite specific concepts from the graph):"""
        
        try:
            answer = await self._call_groq_llm(prompt, max_tokens=200)
            
            # Extract citations from context
            citations = [node.name for path in context.paths for node in path.nodes]
            citations = list(set(citations))[:5]  # Top 5 unique citations
            
            query_time = (time.time() - start_time) * 1000
            
            return RAGResponse(
                query=query,
                answer=answer,
                confidence=confidence,
                used_graph_rag=True,
                used_small_llm=True,
                fallback_to_full_llm=False,
                graph_context=context,
                citations=citations,
                entities_found=len(context.entities),
                paths_explored=len(context.paths),
                nodes_traversed=context.total_nodes,
                query_time_ms=query_time,
                estimated_carbon_g=0.5,  # Small LLM estimate
                carbon_saved_g=4.5  # vs GPT-4
            )
        
        except Exception as e:
            logger.error(f"Small LLM call failed: {e}")
            return await self._fallback_to_full_llm(query, start_time, context)
    
    async def _fallback_to_full_llm(
        self,
        query: str,
        start_time: float,
        context: Optional[GraphContext] = None
    ) -> RAGResponse:
        """
        Triggers fallback to a larger, more capable LLM when graph confidence is low.

        Args:
            query (str): The original query.
            start_time (float): The timestamp when the original query started.
            context (Optional[GraphContext]): Any partial context retrieved from the graph.

        Returns:
            RAGResponse: Response indicating that fallback is required.
        """
        query_time = (time.time() - start_time) * 1000
        
        return RAGResponse(
            query=query,
            answer="[Fallback to full LLM required - GraphRAG confidence too low]",
            confidence=0.0,
            used_graph_rag=False,
            used_small_llm=False,
            fallback_to_full_llm=True,
            graph_context=context,
            citations=[],
            entities_found=len(context.entities) if context else 0,
            paths_explored=len(context.paths) if context else 0,
            nodes_traversed=context.total_nodes if context else 0,
            query_time_ms=query_time,
            estimated_carbon_g=5.0,  # Full LLM estimate
            carbon_saved_g=0.0
        )
    
    async def _call_groq_llm(self, prompt: str, max_tokens: int = 200) -> str:
        """
        Executes a call to the Groq API using the configured small model.

        Args:
            prompt (str): The formatted prompt to send.
            max_tokens (int): Maximum tokens to allow in response.

        Returns:
            str: The generated text response.
        """
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.small_llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

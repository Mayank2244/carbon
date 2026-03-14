from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.core.logging import get_logger
from app.modules.query_analyzer import QueryAnalyzer
from app.modules.prompt_optimizer.optimizer import PromptOptimizer
from app.modules.model_selector.adaptive_selector import QueryMetadata
from app.modules.model_selector.orchestrator import AdaptiveOrchestrator
from app.modules.cache_manager import CacheManager
from app.core.stats import stats_manager
from app.modules.knowledge_base import knowledge_base_service
from app.modules.carbon_api.carbon_api_client import CarbonAPIClient

logger = get_logger(__name__)
router = APIRouter(prefix="/query", tags=["query"])


# Initialize services
query_analyzer = QueryAnalyzer()
prompt_optimizer = PromptOptimizer()
orchestrator = AdaptiveOrchestrator()
cache_manager = CacheManager()
carbon_client = CarbonAPIClient(cache_manager=cache_manager)


class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    context: Optional[str] = None
    optimize_for: str = "carbon"
    use_cache: bool = True
    max_tokens: int = 1000
    temperature: float = 0.7
    use_rag: bool = True  # NEW: Enable/disable RAG


class QueryResponse(BaseModel):
    """Query response model."""
    query: str
    response: str
    model_used: str
    carbon_grams: float
    saved_gco2: float = 0.0
    tokens_used: int
    latency_ms: float
    cached: bool
    region: str = "unknown"
    metadata: dict


@router.post("/process", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
) -> QueryResponse:
    logger.info(f"Processing query: {request.query[:100]}...")
    
    # Check cache
    if request.use_cache and not request.context:
        cached_response = await cache_manager.get_query_response(request.query)
        if cached_response:
            logger.info("Returning cached response")
            cached_response["cached"] = True
            return QueryResponse(**cached_response)
    
    # RAG: Retrieve relevant context from knowledge base
    full_prompt = request.query
    rag_context_used = False
    
    if request.use_rag and not request.context:
        try:
            rag_results = knowledge_base_service.search(
                query=request.query,
                top_k=3,
                min_similarity=0.2
            )
            
            if rag_results:
                rag_context = "\n\n".join([
                    f"[Source: {r.source}]\n{r.text}" 
                    for r in rag_results
                ])
                full_prompt = f"Context from knowledge base:\n{rag_context}\n\nQuestion:\n{request.query}"
                rag_context_used = True
                logger.info(f"RAG: Retrieved {len(rag_results)} relevant chunks")
        except Exception as e:
            logger.warning(f"RAG retrieval failed, continuing without context: {e}")
    
    # Manual context (from PDF upload, etc.)
    elif request.context:
        full_prompt = f"Context:\n{request.context}\n\nQuestion:\n{request.query}"

    # 1. Analyze
    analysis = await query_analyzer.analyze(full_prompt)
    
    complexity_map = {
        "SIMPLE": 0.2,
        "MEDIUM": 0.5,
        "COMPLEX": 0.9
    }
    complexity_score = complexity_map.get(str(analysis.complexity).upper(), 0.5)
    
    # 2. Optimize Prompt
    optimized_prompt_obj = prompt_optimizer.optimize(
        prompt=full_prompt,
        context=[], 
        query_metadata={
            "complexity": str(analysis.complexity),
            "carbon_budget": 100.0
        }
    )
    optimized_query = optimized_prompt_obj.text
    
    # Dual-Audience Instruction: ONLY trigger when the user explicitly asks for it.
    # Trigger keywords signal the user wants structured technical + simple explanations.
    DUAL_AUDIENCE_TRIGGERS = {
        "in detail", "in details", "explain in detail", "detail explanation",
        "give me code", "show me code", "write code", "code example", "code snippet",
        "technical explanation", "technical details", "how does it work technically",
        "for both", "for everyone", "for all users", "technical and non-technical",
        "with code", "architecture", "implementation details", "deep dive",
        "step by step", "step-by-step", "breakdown", "full explanation",
    }
    raw_query_lower = request.query.lower()
    needs_dual_format = any(trigger in raw_query_lower for trigger in DUAL_AUDIENCE_TRIGGERS)

    final_query = optimized_query
    if needs_dual_format:
        dual_audience_instruction = (
            "\n\n---"
            "\nIMPORTANT: Please structure your response into two distinct sections:\n"
            "1. **For Non-Technical Users**: Provide a simple, easy-to-understand explanation without jargon.\n"
            "2. **For Technical Users**: Provide an in-depth, technical explanation with necessary details, code, or architecture logic if applicable."
        )
        final_query += dual_audience_instruction
    
    # 3. Generating
    orchestrator_metadata = QueryMetadata(
        query=final_query,
        query_type=analysis.intent.value,
        complexity=complexity_score,
        estimated_tokens=analysis.estimated_tokens
    )
    
    response_data = await orchestrator.generate_with_fallback(
        query=final_query,
        query_metadata=orchestrator_metadata
    )
    
    # Calculate savings using Physics (Joules) NOT Carbon
    # Baseline: GPT-4 class = 50 Joules/token
    BASELINE_JOULES_PER_TOKEN = 50.0
    baseline_energy_kwh = (response_data.tokens_used * BASELINE_JOULES_PER_TOKEN) / 3_600_000.0
    actual_energy_kwh = response_data.energy_kwh
    
    saved_energy_kwh = max(0.0, baseline_energy_kwh - actual_energy_kwh)
    
    # Calculate Carbon using LIVE Grid Intensity from StatsManager
    # This makes the carbon metrics dynamic while keeping energy metrics stable
    current_intensity = stats_manager.current_carbon_intensity
    
    actual_carbon = actual_energy_kwh * current_intensity
    saved_gco2 = saved_energy_kwh * current_intensity

    # 4. Construct Response
    query_res = QueryResponse(
        query=request.query,
        response=response_data.response_text,
        model_used=response_data.model_name,
        carbon_grams=actual_carbon,
        saved_gco2=saved_gco2,
        tokens_used=response_data.tokens_used,
        latency_ms=response_data.latency_ms,
        cached=False,
        region="local" if response_data.metadata.get("endpoint") == "local" else "cloud",
        metadata={
            "original_tokens": optimized_prompt_obj.original_tokens,
            "optimized_tokens": optimized_prompt_obj.tokens,
            "optimization_method": optimized_prompt_obj.technique_used,
            "complexity": str(analysis.complexity),
            "region": "local" if response_data.metadata.get("endpoint") == "local" else "cloud",
            "provider": response_data.metadata.get("endpoint", "unknown"),
            "rag_context_used": rag_context_used  # NEW: Track RAG usage
        }
    )

    # 5. Cache
    if request.use_cache:
        await cache_manager.cache_query_response(
            request.query,
            query_res.dict()
        )
    
    # Calculate token savings (Original - Optimized)
    original_tokens = optimized_prompt_obj.original_tokens
    final_tokens = response_data.tokens_used
    
    # We approximate "tokens saved" as the difference in prompt tokens from optimization
    # plus the potential savings from using a smaller model vs GPT-4 baseline (if applicable)
    # For now, let's strictly count Prompt Optimization savings
    tokens_saved = max(0, original_tokens - optimized_prompt_obj.tokens)
    
    # breakdown calculation
    optimization_savings_gco2 = 0.0
    model_selection_savings_gco2 = saved_gco2 # Default all to model selection if no split
    
    # Simple heuristic: optimization savings ratio = (tokens_saved / (tokens_used + tokens_saved))
    total_potential = response_data.tokens_used + tokens_saved
    if total_potential > 0:
        opt_ratio = tokens_saved / total_potential
        optimization_savings_gco2 = saved_gco2 * opt_ratio
        model_selection_savings_gco2 = saved_gco2 * (1 - opt_ratio)
    
    # 6. Record Stats
    # Format model name to include capacity/tier info, e.g. "Tiny (llama-3.1-8b)"
    tier_label = response_data.model_tier.value.title()
    model_display = f"{tier_label} ({response_data.model_name})"
    
    provider = response_data.metadata.get("endpoint", "unknown")
    region = "local" if provider == "local" else "cloud" # Or specific region if available
    
    stats_manager.record_request(
        model=model_display,
        tokens_used=response_data.tokens_used,
        tokens_saved=tokens_saved,
        carbon_used=actual_carbon,
        carbon_saved=saved_gco2,
        energy_used_kwh=actual_energy_kwh, # Pass explicit energy
        energy_saved_kwh=saved_energy_kwh, # Pass explicit energy
        latency=response_data.latency_ms,
        cached=False,
        provider=provider,
        region=region,
        savings_breakdown={
            "model": model_selection_savings_gco2,
            "optimization": optimization_savings_gco2
        }
    )
    
    return query_res


class FeedbackRequest(BaseModel):
    """Feedback request model."""
    query: str
    rating: int  # 1-5
    comment: Optional[str] = None

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit user feedback for RL training."""
    logger.info(f"Received feedback: {feedback.rating}/5 for '{feedback.query}'")
    reward = (feedback.rating - 3) / 2.0
    logger.info(f"RL Reward Signal: {reward}")
    return {"status": "success", "reward_calculated": reward}


@router.get("/stats")
async def get_stats() -> dict:
    """Get real-time system metrics for dashboard."""
    try:
        # Fetch latest carbon intensity (San Francisco as default server location)
        # In production, this would be the actual data center location
        carbon_data = await carbon_client.get_carbon_intensity(latitude=37.7749, longitude=-122.4194)
        if carbon_data:
            stats_manager.update_carbon_intensity(carbon_data.carbon_intensity)
    except Exception as e:
        logger.warning(f"Failed to update carbon stats: {e}")
        
    return stats_manager.get_live_metrics()

@router.get("/analytics")
async def get_analytics_data() -> dict:
    """Get historical analytics data."""
    return stats_manager.get_analytics_trends()

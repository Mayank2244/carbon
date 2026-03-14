
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from app.modules.query_analyzer.service import QueryAnalyzer
from app.modules.query_analyzer.models import QueryAnalysisResult, QueryComplexity, QueryIntent, QueryUrgency, QueryDomain
from app.modules.prompt_optimizer.optimizer import PromptOptimizer
from app.modules.cache_manager.service import CacheManager
from app.modules.carbon_router.service import CarbonRouter, RoutingDecision
from app.modules.model_selector.adaptive_selector import AdaptiveModelSelector, QueryMetadata as SelectorMetadata
from app.modules.rl_optimizer.service import RLOptimizer, RLState
from app.modules.carbon_api.carbon_api_client import CarbonAPIClient
from app.modules.rag_engine.service import RAGEngine, Document

# --- Layer 1: Query Analyzer ---
@pytest.mark.asyncio
async def test_query_analyzer():
    analyzer = QueryAnalyzer()
    query = "What is the capital of France?"
    result = await analyzer.analyze(query)
    
    assert isinstance(result, QueryAnalysisResult)
    assert result.query_text == query
    assert result.complexity in [QueryComplexity.SIMPLE, QueryComplexity.MEDIUM, QueryComplexity.COMPLEX]
    assert result.intent is not None
    assert result.confidence_score > 0.0

# --- Layer 2: Prompt Optimizer ---
def test_prompt_optimizer():
    optimizer = PromptOptimizer()
    prompt = "Please kindly explain to me what is the capital of France?"
    optimized = optimizer.optimize(prompt, [], {'complexity': 'SIMPLE', 'carbon_budget': 50})
    
    assert optimized.text is not None
    assert len(optimized.text) < len(prompt) * 1.5 # Should not expand too much even if adding verbosity
    assert optimized.compression_ratio >= 0.0

# --- Layer 3: Cache Manager ---
@pytest.mark.asyncio
async def test_cache_manager():
    # Mocking Redis and Chroma to avoid needing live services for unit test
    with patch('app.modules.cache_manager.service.get_redis') as mock_redis_getter:
        mock_redis = MagicMock()
        mock_redis_getter.return_value = mock_redis
        
        # Mocking Chroma
        with patch('chromadb.PersistentClient'):
            cache = CacheManager()
            # We can't easily test async get without a real async redis mock or complex setup
            # But we can test initialization and stats structure
            stats = await cache.get_stats()
            assert "l1_connected" in stats
            assert "l2_connected" in stats

# --- Layer 4: Carbon Router ---
@pytest.mark.asyncio
async def test_carbon_router():
    router = CarbonRouter()
    mock_analysis = QueryAnalysisResult(
        query_text="test",
        complexity=QueryComplexity.MEDIUM,
        intent=QueryIntent.FACTUAL,
        urgency=QueryUrgency.FLEXIBLE, 
        domain=QueryDomain.GENERAL,
        estimated_tokens=100,
        requires_context=False,
        confidence_score=0.9
    )
    
    decision = await router.route(mock_analysis)
    assert isinstance(decision, RoutingDecision)
    assert decision.selected_model is not None
    assert "region" in decision.metadata

# --- Layer 5: Model Selector ---
def test_model_selector():
    selector = AdaptiveModelSelector()
    meta = SelectorMetadata(
        query="test",
        complexity=0.5,
        estimated_tokens=150
    )
    model_config = selector.select_model(meta)
    assert model_config.name is not None
    assert model_config.tier is not None

# --- Layer 6: RL Optimizer ---
@pytest.mark.asyncio
async def test_rl_optimizer():
    rl = RLOptimizer()
    state = RLState(
        query_complexity=0.5,
        query_type="factual",
        context_required=False,
        estimated_tokens=100
    )
    action = await rl.select_action(state, ["model_a", "model_b"])
    assert action.model_name in ["model_a", "model_b"]

# --- Layer 7: Carbon API ---
@pytest.mark.asyncio
async def test_carbon_api():
    # Mock CacheManager
    mock_cache = AsyncMock() # CacheManager methods are async usually
    mock_cache.get.return_value = None
    
    client = CarbonAPIClient(mock_cache)
    
    # Mock HTTP requests using patch to avoid external calls
    with patch('httpx.AsyncClient') as MockClient:
        mock_instance = AsyncMock()
        MockClient.return_value = mock_instance
        
        # Context manager returns the instance itself
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "zone": "FR",
            "carbonIntensity": 50,
            "datetime": "2023-01-01T00:00:00Z",
            "updatedAt": "2023-01-01T00:00:00Z",
            "emissionFactorType": "lifecycle",
            "isEstimated": False,
            "estimationMethod": None
        }
        
        # AsyncMock for get method is automatic if mock_instance is AsyncMock, 
        # but we set return_value explicitly
        mock_instance.get.return_value = mock_response
        
        # Determine if we have keys. If not, fallback will be used.
        # This test ensures it runs without crashing, regardless of key presence.
        try:
            data = await client.get_carbon_intensity(48.8566, 2.3522)
            assert data.carbon_intensity >= 0
        except Exception as e:
            pytest.fail(f"Carbon API failed: {e}")

# --- Layer 8: RAG Engine ---
@pytest.mark.asyncio
async def test_rag_engine():
    rag = RAGEngine()
    doc = Document(content="CarbonSense is green.")
    await rag.add_documents([doc])
    
    result = await rag.retrieve("What is CarbonSense?")
    assert len(result.documents) == 1
    assert result.documents[0].content == "CarbonSense is green."

"""
Tests for Adaptive Model Selector
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.modules.model_selector import (
    AdaptiveModelSelector,
    ModelTier,
    ModelConfig,
    QueryMetadata,
    QualityEvaluator,
    QualityMetrics,
    LocalModelLoader,
    AdaptiveOrchestrator
)


class TestAdaptiveModelSelector:
    """Test cases for AdaptiveModelSelector."""
    
    def test_initialization(self):
        """Test selector initialization."""
        selector = AdaptiveModelSelector(carbon_budget=500.0)
        
        assert selector.carbon_budget == 500.0
        assert selector.carbon_used_today == 0.0
        assert len(selector.model_configs) == 4
        assert ModelTier.TINY in selector.model_configs
    
    def test_select_model_simple_query(self):
        """Test model selection for simple query."""
        selector = AdaptiveModelSelector()
        
        metadata = QueryMetadata(
            query="What is Python?",
            query_type="factual",
            complexity=0.2
        )
        
        model = selector.select_model(metadata)
        
        assert model.tier == ModelTier.TINY
        assert model.name == "TinyLlama-1.1B"
    
    def test_select_model_complex_query(self):
        """Test model selection for complex query."""
        selector = AdaptiveModelSelector()
        
        metadata = QueryMetadata(
            query="Explain quantum computing",
            query_type="expert_reasoning",
            complexity=0.9,
            required_capabilities=["expert_reasoning"]
        )
        
        model = selector.select_model(metadata)
        
        assert model.tier == ModelTier.LARGE
        assert "meta-llama" in model.name or "70B" in model.name
    
    def test_carbon_budget_enforcement(self):
        """Test carbon budget is enforced."""
        selector = AdaptiveModelSelector(carbon_budget=1.0)  # Very small budget
        
        # Use up budget
        selector.carbon_used_today = 0.9
        
        metadata = QueryMetadata(
            query="Test query",
            estimated_tokens=1000  # Would cost ~0.5g for tiny model
        )
        
        # Should still select a model (emergency mode)
        model = selector.select_model(metadata)
        assert model is not None
    
    def test_estimate_carbon_cost(self):
        """Test carbon cost estimation."""
        selector = AdaptiveModelSelector()
        
        # Tiny model: 0.5g per 1k tokens
        cost = selector.estimate_carbon_cost("TinyLlama-1.1B", 1000)
        assert cost == 0.5
        
        # Large model: 15g per 1k tokens (updated from 20g)
        cost = selector.estimate_carbon_cost("meta-llama/Meta-Llama-3-70B-Instruct", 1000)
        assert cost == 15.0
    
    def test_record_usage(self):
        """Test usage recording."""
        selector = AdaptiveModelSelector()
        
        selector.record_usage(ModelTier.TINY, 500)
        
        assert selector.stats.total_queries == 1
        assert selector.stats.queries_by_tier[ModelTier.TINY] == 1
        assert selector.stats.total_carbon_grams > 0
    
    def test_escalation_pattern_learning(self):
        """Test escalation pattern learning."""
        selector = AdaptiveModelSelector()
        
        # Record pattern
        selector.record_escalation_pattern("code_advanced", ModelTier.MEDIUM)
        selector.record_escalation_pattern("code_advanced", ModelTier.MEDIUM)
        
        assert "code_advanced" in selector.escalation_patterns
        assert len(selector.escalation_patterns["code_advanced"]) == 2


class TestQualityEvaluator:
    """Test cases for QualityEvaluator."""
    
    def test_initialization(self):
        """Test evaluator initialization."""
        evaluator = QualityEvaluator(quality_threshold=0.8)
        assert evaluator.quality_threshold == 0.8
    
    def test_evaluate_good_response(self):
        """Test evaluation of good response."""
        evaluator = QualityEvaluator()
        
        query = "What is machine learning?"
        response = "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves."
        
        metrics = evaluator.evaluate(query, response)
        
        assert metrics.overall_score > 0.5
        assert metrics.completeness_score > 0.5
        assert metrics.coherence_score > 0.5
    
    def test_evaluate_poor_response(self):
        """Test evaluation of poor response."""
        evaluator = QualityEvaluator()
        
        query = "Explain quantum computing"
        response = "I don't know."
        
        metrics = evaluator.evaluate(query, response)
        
        assert metrics.overall_score < 0.7
        assert not metrics.passed
        assert len(metrics.issues) > 0
    
    def test_completeness_check(self):
        """Test completeness checking."""
        evaluator = QualityEvaluator()
        
        # Complete response
        complete = "This is a complete sentence with proper ending."
        score = evaluator._check_completeness(complete, 10)
        assert score > 0.9
        
        # Incomplete response
        incomplete = "This is incomplete"
        score = evaluator._check_completeness(incomplete, 100)
        assert score < 0.5
    
    def test_should_escalate(self):
        """Test escalation decision."""
        evaluator = QualityEvaluator(quality_threshold=0.7)
        
        # Good metrics - no escalation
        good_metrics = QualityMetrics(
            completeness_score=0.9,
            coherence_score=0.9,
            relevance_score=0.9,
            length_score=0.9,
            overall_score=0.9,
            passed=True,
            issues=[]
        )
        assert not evaluator.should_escalate(good_metrics)
        
        # Poor metrics - escalate
        poor_metrics = QualityMetrics(
            completeness_score=0.3,
            coherence_score=0.3,
            relevance_score=0.3,
            length_score=0.3,
            overall_score=0.3,
            passed=False,
            issues=["incomplete"]
        )
        assert evaluator.should_escalate(poor_metrics)


class TestLocalModelLoader:
    """Test cases for LocalModelLoader."""
    
    def test_initialization(self):
        """Test loader initialization."""
        loader = LocalModelLoader(
            cache_dir="./test_models",
            idle_timeout=60,
            use_gpu=False
        )
        
        assert loader.cache_dir == "./test_models"
        assert loader.idle_timeout == 60
        assert not loader.use_gpu
    
    def test_get_loaded_models_empty(self):
        """Test getting loaded models when none loaded."""
        loader = LocalModelLoader()
        models = loader.get_loaded_models()
        assert models == []
    
    @patch('app.modules.model_selector.local_model_loader.AutoModelForCausalLM')
    @patch('app.modules.model_selector.local_model_loader.AutoTokenizer')
    def test_load_model(self, mock_tokenizer, mock_model):
        """Test model loading (mocked)."""
        loader = LocalModelLoader()
        
        # Mock the model and tokenizer
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model.from_pretrained.return_value = Mock()
        
        instance = loader.load_model("TinyLlama-1.1B")
        
        assert instance is not None
        assert instance.model_name == "TinyLlama-1.1B"
        assert "TinyLlama-1.1B" in loader.get_loaded_models()


class TestAdaptiveOrchestrator:
    """Test cases for AdaptiveOrchestrator."""
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = AdaptiveOrchestrator(
            carbon_budget=500.0,
            quality_threshold=0.8
        )
        
        assert orchestrator.selector.carbon_budget == 500.0
        assert orchestrator.quality_evaluator.quality_threshold == 0.8
    
    def test_get_stats(self):
        """Test getting usage statistics."""
        orchestrator = AdaptiveOrchestrator()
        stats = orchestrator.get_stats()
        
        assert stats.total_queries == 0
        assert stats.total_carbon_grams == 0.0
    
    @pytest.mark.asyncio
    async def test_generate_with_fallback_error_handling(self):
        """Test fallback chain error handling."""
        orchestrator = AdaptiveOrchestrator(enable_fallback=False)
        
        # This will fail without actual models, but should handle gracefully
        result = await orchestrator.generate_with_fallback(
            query="Test query",
            max_fallback_attempts=1
        )
        
        # Should return error response
        assert result is not None
        assert result.tokens_used >= 0


# Integration tests
class TestIntegration:
    """Integration tests for the full system."""
    
    def test_end_to_end_selection(self):
        """Test end-to-end model selection flow."""
        selector = AdaptiveModelSelector(carbon_budget=1000.0)
        
        # Simple query
        simple_metadata = QueryMetadata(
            query="What is 2+2?",
            query_type="factual",
            complexity=0.1
        )
        model = selector.select_model(simple_metadata)
        assert model.tier == ModelTier.TINY
        
        # Complex query
        complex_metadata = QueryMetadata(
            query="Design a distributed system",
            query_type="expert_reasoning",
            complexity=0.9
        )
        model = selector.select_model(complex_metadata)
        assert model.tier in [ModelTier.LARGE, ModelTier.MEDIUM]
    
    def test_carbon_tracking_across_queries(self):
        """Test carbon tracking across multiple queries."""
        selector = AdaptiveModelSelector(carbon_budget=100.0)
        
        # Process multiple queries
        for i in range(5):
            metadata = QueryMetadata(
                query=f"Query {i}",
                query_type="factual",
                estimated_tokens=100
            )
            model = selector.select_model(metadata)
            selector.record_usage(model.tier, 100)
        
        stats = selector.get_usage_stats()
        assert stats.total_queries == 5
        assert stats.total_carbon_grams > 0
        assert selector.carbon_used_today > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

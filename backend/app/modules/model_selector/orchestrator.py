"""
Orchestrator for adaptive model selection with fallback chain.
Combines all components to provide intelligent model routing.
"""

from typing import Optional, List
from dataclasses import dataclass

from app.core.logging import get_logger
from app.modules.model_selector.adaptive_selector import (
    AdaptiveModelSelector,
    ModelTier,
    ModelConfig,
    QueryMetadata,
    ModelResponse as AdaptiveModelResponse
)
from app.modules.model_selector.local_model_loader import LocalModelLoader
from app.modules.model_selector.quality_evaluator import QualityEvaluator
from app.modules.model_selector.api_integrations import APIIntegrations
from app.modules.model_selector.ab_testing import ABTestManager
from app.modules.model_selector.tuning import ThresholdTuner

logger = get_logger(__name__)


class AdaptiveOrchestrator:
    """
    Orchestrates adaptive model selection with quality-based fallback chain.
    Implements: tiny → small → medium → large escalation.
    """
    
    def __init__(
        self,
        carbon_budget: float = 1000.0,
        quality_threshold: float = 0.7,
        enable_fallback: bool = True,
        enable_ab_testing: bool = False,
        enable_auto_tuning: bool = True
    ):
        """
        Initialize adaptive orchestrator.
        
        Args:
            carbon_budget: Daily carbon budget in grams
            quality_threshold: Minimum quality score
            enable_fallback: Enable automatic fallback chain
            enable_ab_testing: Enable A/B testing experiments
            enable_auto_tuning: Enable automatic threshold tuning
        """
        self.selector = AdaptiveModelSelector(
            carbon_budget=carbon_budget,
            quality_threshold=quality_threshold
        )
        self.local_loader = LocalModelLoader()
        self.quality_evaluator = QualityEvaluator(quality_threshold=quality_threshold)
        self.api_client = APIIntegrations()
        self.enable_fallback = enable_fallback
        
        # Advanced features
        self.ab_tester = ABTestManager(experiment_rate=0.1, quality_evaluator=self.quality_evaluator) if enable_ab_testing else None
        self.tuner = ThresholdTuner(initial_threshold=quality_threshold) if enable_auto_tuning else None
        
        logger.info(
            f"AdaptiveOrchestrator initialized - "
            f"AB Testing: {enable_ab_testing}, Auto Tuning: {enable_auto_tuning}"
        )
    
    async def generate_with_fallback(
        self,
        query: str,
        query_metadata: Optional[QueryMetadata] = None,
        max_fallback_attempts: int = 3
    ) -> AdaptiveModelResponse:
        """
        Generate response with automatic fallback chain.
        
        Args:
            query: User query
            query_metadata: Query metadata (auto-inferred if None)
            max_fallback_attempts: Maximum fallback attempts
            
        Returns:
            Model response with metadata
        """
        if query_metadata is None:
            query_metadata = QueryMetadata(query=query)
            
        # Check for A/B testing opportunity
        if self.ab_tester and self.ab_tester.should_run_test(query):
            # Run shadow test (async ideally, but inline for now to ensure we capture result)
            # We'll compare the selected model against the next tier up
            # This logic mimics "should we have used a larger model?"
            pass  # To be implemented in next block
        
        # Track fallback chain
        attempted_tiers: List[ModelTier] = []
        last_error: Optional[str] = None
        
        # Try models in escalating order
        tier_order = [ModelTier.TINY, ModelTier.SMALL, ModelTier.MEDIUM, ModelTier.LARGE]
        
        for attempt in range(max_fallback_attempts):
            tier = ModelTier.TINY  # Default for error logging
            try:
                # Select model
                model_config = self.selector.select_model(query_metadata)
                tier = model_config.tier
                
                # Skip if already attempted
                if tier in attempted_tiers:
                    # Move to next tier
                    current_idx = tier_order.index(tier)
                    if current_idx + 1 < len(tier_order):
                        next_tier = tier_order[current_idx + 1]
                        # Temporarily override capabilities to force next tier
                        query_metadata.required_capabilities = self.selector.model_configs[next_tier].capabilities[:1]
                        continue
                    else:
                        # No more tiers to try
                        break
                
                attempted_tiers.append(tier)
                
                logger.info(
                    f"Attempt {attempt + 1}: Using {tier.value} model ({model_config.name})"
                )
                
                # Generate response
                response = await self._generate_with_model(model_config, query)
                
                # Get current threshold from tuner if active
                current_threshold = self.tuner.get_current_threshold() if self.tuner else self.quality_evaluator.quality_threshold
                
                # Evaluate quality (using dynamic threshold for decision, but evaluator uses its own internally)
                quality_metrics = self.quality_evaluator.evaluate(query, response.response_text)
                response.quality_score = quality_metrics.overall_score
                
                # Decide if passed based on dynamic threshold
                passed = quality_metrics.overall_score >= current_threshold
                
                # Update tuner
                if self.tuner:
                    self.tuner.update(quality_metrics.overall_score, not passed)
                
                # Check if quality is acceptable
                if passed or not self.enable_fallback:
                    # Success!
                    logger.info(
                        f"Response accepted - quality: {quality_metrics.overall_score:.2f} (threshold: {current_threshold:.2f})"
                    )
                    
                    # Run A/B Test if enabled and applicable
                    if self.ab_tester and self.ab_tester.should_run_test(query):
                        try:
                            # Test against next tier up
                            current_idx = tier_order.index(tier)
                            if current_idx + 1 < len(tier_order):
                                next_tier = tier_order[current_idx + 1]
                                next_config = self.selector.model_configs[next_tier]
                                
                                logger.info(f"Running A/B test: {tier.value} vs {next_tier.value}")
                                
                                # Generate with challenger
                                challenger_response = await self._generate_with_model(next_config, query)
                                
                                # Record comparison
                                self.ab_tester.evaluate_comparison(
                                    query=query,
                                    result_a={
                                        'text': response.response_text,
                                        'latency': response.latency_ms
                                    },
                                    result_b={
                                        'text': challenger_response.response_text,
                                        'latency': challenger_response.latency_ms
                                    },
                                    model_config_a=model_config,
                                    model_config_b=next_config
                                )
                        except Exception as e:
                            logger.error(f"A/B test failed: {e}")
                    
                    # Record usage
                    escalated_from = attempted_tiers[0] if len(attempted_tiers) > 1 else None
                    self.selector.record_usage(tier, response.tokens_used, escalated_from)
                    
                    # Learn from escalation pattern
                    if query_metadata.query_type and escalated_from:
                        self.selector.record_escalation_pattern(query_metadata.query_type, tier)
                    
                    response.escalated_from = escalated_from
                    return response
                
                else:
                    # Quality check failed, try next tier
                    reason = self.quality_evaluator.get_escalation_reason(quality_metrics)
                    logger.warning(
                        f"{tier.value} model failed quality check: {reason}"
                    )
                    last_error = reason
                    
                    # Force next tier by updating capabilities
                    current_idx = tier_order.index(tier)
                    if current_idx + 1 < len(tier_order):
                        next_tier = tier_order[current_idx + 1]
                        query_metadata.required_capabilities = self.selector.model_configs[next_tier].capabilities[:1]
                    
            except Exception as e:
                logger.error(f"Error with {tier.value} model: {e}", exc_info=True)
                last_error = str(e)
                continue
        
        # All attempts failed
        error_msg = f"All fallback attempts failed. Last error: {last_error}"
        logger.error(error_msg)
        
        # Return error response
        return AdaptiveModelResponse(
            model_tier=attempted_tiers[-1] if attempted_tiers else ModelTier.TINY,
            model_name="error",
            response_text=f"[ERROR] {error_msg}",
            tokens_used=0,
            latency_ms=0.0,
            carbon_grams=0.0,
            cost_usd=0.0,
            quality_score=0.0,
            metadata={"error": error_msg, "attempted_tiers": [t.value for t in attempted_tiers]}
        )
    
    async def _generate_with_model(
        self,
        model_config: ModelConfig,
        query: str
    ) -> AdaptiveModelResponse:
        """
        Generate response using specified model.
        
        Args:
            model_config: Model configuration
            query: User query
            
        Returns:
            Model response
        """
        import time
        start_time = time.time()
        
        # Determine if local or API model
        if model_config.endpoint == 'local':
            # Use local model
            response_text = self.local_loader.generate(
                model_key=model_config.name,
                prompt=query,
                max_tokens=model_config.max_tokens,
                temperature=0.7
            )
            
            # Estimate tokens (rough approximation)
            tokens_used = len(response_text.split()) * 1.3  # ~1.3 tokens per word
            
        else:
            # Use API model
            provider = model_config.endpoint  # 'groq' or 'huggingface'
            
            # Fallback for legacy configs if any
            if "api.openai.com" in provider:
                provider = "openai"
            elif "api.anthropic.com" in provider:
                provider = "anthropic"
            
            api_response = await self.api_client.call_model(
                provider=provider,
                model=model_config.name,
                prompt=query,
                max_tokens=model_config.max_tokens,
                temperature=0.7
            )
            
            response_text = api_response.text
            tokens_used = api_response.tokens_used
        
        latency = (time.time() - start_time) * 1000
        
        # Calculate costs
        # Energy (kWh) = (Tokens * J/Token) / 3,600,000 J/kWh
        joules_total = tokens_used * getattr(model_config, 'joules_per_token', 10.0)
        energy_kwh = joules_total / 3_600_000.0
        
        # Carbon (g) = Energy (kWh) * Intensity (g/kWh)
        # Using 475 as default here, but will be refined in query.py with live stats
        carbon_grams = energy_kwh * 475.0
        
        cost_usd = (tokens_used / 1_000_000) * model_config.cost_per_1m_tokens
        
        return AdaptiveModelResponse(
            model_tier=model_config.tier,
            model_name=model_config.name,
            response_text=response_text,
            tokens_used=int(tokens_used),
            latency_ms=latency,
            carbon_grams=carbon_grams,
            energy_kwh=energy_kwh,
            cost_usd=cost_usd,
            metadata={"endpoint": model_config.endpoint}
        )
    
    def get_stats(self):
        """Get usage statistics."""
        return self.selector.get_usage_stats()
    
    def get_loaded_models(self):
        """Get currently loaded local models."""
        return self.local_loader.get_loaded_models()

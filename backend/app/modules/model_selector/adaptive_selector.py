"""
Adaptive Model Selector - Routes queries to the smallest capable model.
Optimizes for carbon efficiency while maintaining quality standards.
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, date

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class ModelTier(str, Enum):
    """Model tier enumeration."""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass
class ModelConfig:
    """Configuration for a model tier."""
    tier: ModelTier
    name: str
    params: float  # Number of parameters (or 'unknown' as float('inf'))
    capabilities: List[str]
    max_tokens: int
    joules_per_token: float # Energy in Joules per token (Research-based)
    carbon_per_1k_tokens: float  # DEPRECATED: usage derived from joules now
    cost_per_1m_tokens: float  # USD
    endpoint: str
    
    def __post_init__(self):
        """Convert string params to float if needed."""
        if isinstance(self.params, str) and self.params == 'unknown':
            self.params = float('inf')


@dataclass
class QueryMetadata:
    """Metadata about a query for routing decisions."""
    query: str
    query_type: Optional[str] = None  # 'factual', 'reasoning', 'creative', etc.
    complexity: Optional[float] = None  # 0.0 to 1.0
    required_capabilities: List[str] = field(default_factory=list)
    estimated_tokens: int = 500
    max_tokens: Optional[int] = None


@dataclass
class ModelResponse:
    """Response from a model with metadata."""
    model_tier: ModelTier
    model_name: str
    response_text: str
    tokens_used: int
    latency_ms: float
    carbon_grams: float
    cost_usd: float
    energy_kwh: float = 0.0 # NEW: Explicit energy tracking
    quality_score: Optional[float] = None
    escalated_from: Optional[ModelTier] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageStats:
    """Usage statistics for the adaptive selector."""
    total_queries: int = 0
    queries_by_tier: Dict[ModelTier, int] = field(default_factory=dict)
    escalations: int = 0
    total_carbon_grams: float = 0.0
    total_cost_usd: float = 0.0
    carbon_saved_vs_baseline_grams: float = 0.0
    
    def get_tier_percentage(self, tier: ModelTier) -> float:
        """Get percentage of queries handled by a tier."""
        if self.total_queries == 0:
            return 0.0
        return (self.queries_by_tier.get(tier, 0) / self.total_queries) * 100
    
    def get_escalation_rate(self) -> float:
        """Get escalation rate as percentage."""
        if self.total_queries == 0:
            return 0.0
        return (self.escalations / self.total_queries) * 100


class AdaptiveModelSelector:
    """
    Adaptive model selector that routes queries to the smallest capable model.
    Tracks carbon usage, enforces budgets, and learns from escalation patterns.
    """
    
    # Default model tier configurations
    # Energy estimates based on research (Strubell et al., Hugging Face)
    # Hardware: Efficient LPUs / Optimized H100s
    DEFAULT_MODEL_TIERS = {
        ModelTier.TINY: ModelConfig(
            tier=ModelTier.TINY,
            name='llama-3.1-8b-instant',
            params=8e9,
            capabilities=['factual', 'simple_explanation', 'definition'],
            max_tokens=1024,
            joules_per_token=1.5, # Very efficient
            carbon_per_1k_tokens=0.2, # Placeholder
            cost_per_1m_tokens=0.0,
            endpoint='groq'
        ),
        ModelTier.SMALL: ModelConfig(
            tier=ModelTier.SMALL,
            name='llama-3.1-8b-instant',
            params=8e9,
            capabilities=['explanation', 'reasoning', 'code_simple'],
            max_tokens=4096,
            joules_per_token=1.8,
            carbon_per_1k_tokens=0.25,
            cost_per_1m_tokens=0.0,
            endpoint='groq'
        ),
        ModelTier.MEDIUM: ModelConfig(
            tier=ModelTier.MEDIUM,
            name='llama-3.3-70b-versatile',
            params=70e9,
            capabilities=['complex_reasoning', 'code_advanced', 'creative'],
            max_tokens=8192,
            joules_per_token=8.0, 
            carbon_per_1k_tokens=1.3,
            cost_per_1m_tokens=0.0,
            endpoint='groq'
        ),
        ModelTier.LARGE: ModelConfig(
            tier=ModelTier.LARGE,
            name='llama-3.3-70b-versatile',
            params=70e9,
            capabilities=['expert_reasoning', 'research', 'complex_creative'],
            max_tokens=8192,
            joules_per_token=10.0, # ~2.7Wh/1k tokens
            carbon_per_1k_tokens=1.5,
            cost_per_1m_tokens=0.9,
            endpoint='groq'
        )
    }
    
    def __init__(
        self,
        model_configs: Optional[Dict[ModelTier, ModelConfig]] = None,
        carbon_budget: float = 1000.0,  # grams per day
        quality_threshold: float = 0.7,
        enable_escalation: bool = True
    ):
        """
        Initialize adaptive model selector.
        
        Args:
            model_configs: Custom model configurations (uses defaults if None)
            carbon_budget: Daily carbon budget in grams
            quality_threshold: Minimum quality score to accept response
            enable_escalation: Whether to enable automatic escalation
        """
        self.model_configs = model_configs or self.DEFAULT_MODEL_TIERS
        self.carbon_budget = carbon_budget
        self.quality_threshold = quality_threshold
        self.enable_escalation = enable_escalation
        
        # Usage tracking
        self.stats = UsageStats()
        self.carbon_used_today = 0.0
        self.budget_reset_time = datetime.now() + timedelta(days=1)
        
        # Escalation patterns (learn which query types need larger models)
        self.escalation_patterns: Dict[str, List[ModelTier]] = {}
        
        logger.info(
            f"AdaptiveModelSelector initialized - "
            f"budget: {carbon_budget}g/day, "
            f"quality_threshold: {quality_threshold}, "
            f"tiers: {list(self.model_configs.keys())}"
        )
    
    def select_model(self, query_metadata: QueryMetadata) -> ModelConfig:
        """
        Select the smallest model capable of handling the query.
        
        Args:
            query_metadata: Query metadata with capabilities and complexity
            
        Returns:
            Selected model configuration
        """
        # Check if we need to reset daily budget
        self._check_budget_reset()
        
        # Infer capabilities if not provided
        if not query_metadata.required_capabilities:
            query_metadata.required_capabilities = self._infer_capabilities(query_metadata)
        
        # Check escalation patterns for this query type
        suggested_tier = self._check_escalation_patterns(query_metadata)
        if suggested_tier:
            logger.info(f"Using learned pattern: starting with {suggested_tier}")
            return self.model_configs[suggested_tier]
        
        # Start with smallest model and find first match
        tier_order = [ModelTier.TINY, ModelTier.SMALL, ModelTier.MEDIUM, ModelTier.LARGE]
        
        for tier in tier_order:
            config = self.model_configs[tier]
            
            # Check if model has required capabilities
            if self._has_capabilities(config, query_metadata.required_capabilities):
                # Check if we have budget for this model
                estimated_carbon = self.estimate_carbon_cost(
                    config.name,
                    query_metadata.estimated_tokens
                )
                
                if self.check_budget(estimated_carbon):
                    logger.info(
                        f"Selected {tier.value} model ({config.name}) - "
                        f"estimated carbon: {estimated_carbon:.2f}g"
                    )
                    return config
                else:
                    logger.warning(
                        f"Insufficient budget for {tier.value} "
                        f"(need {estimated_carbon:.2f}g, have {self.carbon_budget - self.carbon_used_today:.2f}g)"
                    )
        
        # If no model fits budget, use smallest anyway (emergency mode)
        logger.warning("No model within budget, using smallest model in emergency mode")
        return self.model_configs[ModelTier.TINY]
    
    def estimate_carbon_cost(self, model_name: str, tokens: int) -> float:
        """
        Estimate carbon cost for a model request.
        
        Args:
            model_name: Model name
            tokens: Estimated token count
            
        Returns:
            Estimated carbon cost in grams
        """
        # Find model config by name
        for config in self.model_configs.values():
            if config.name == model_name:
                return (tokens / 1000) * config.carbon_per_1k_tokens
        
        # Default estimate if model not found
        logger.warning(f"Model {model_name} not found, using default carbon estimate")
        return (tokens / 1000) * 5.0
    
    def check_budget(self, estimated_cost: float) -> bool:
        """
        Check if estimated cost fits within remaining budget.
        
        Args:
            estimated_cost: Estimated carbon cost in grams
            
        Returns:
            True if within budget, False otherwise
        """
        remaining = self.carbon_budget - self.carbon_used_today
        return estimated_cost <= remaining
    
    def record_usage(
        self,
        model_tier: ModelTier,
        tokens_used: int,
        escalated_from: Optional[ModelTier] = None
    ):
        """
        Record model usage for tracking and learning.
        
        Args:
            model_tier: Tier of model used
            tokens_used: Actual tokens used
            escalated_from: Previous tier if escalated
        """
        config = self.model_configs[model_tier]
        
        # Calculate actual costs
        carbon_cost = (tokens_used / 1000) * config.carbon_per_1k_tokens
        monetary_cost = (tokens_used / 1_000_000) * config.cost_per_1m_tokens
        
        # Update carbon usage
        self.carbon_used_today += carbon_cost
        
        # Update stats
        self.stats.total_queries += 1
        self.stats.queries_by_tier[model_tier] = self.stats.queries_by_tier.get(model_tier, 0) + 1
        self.stats.total_carbon_grams += carbon_cost
        self.stats.total_cost_usd += monetary_cost
        
        # Track escalations
        if escalated_from:
            self.stats.escalations += 1
        
        # Calculate carbon saved vs always using GPT-4 baseline
        gpt4_carbon = (tokens_used / 1000) * 20.0  # Assume GPT-4 uses ~20g per 1k tokens
        self.stats.carbon_saved_vs_baseline_grams += (gpt4_carbon - carbon_cost)
        
        logger.info(
            f"Recorded usage - tier: {model_tier.value}, "
            f"tokens: {tokens_used}, carbon: {carbon_cost:.2f}g, "
            f"cost: ${monetary_cost:.4f}"
        )
    
    def record_escalation_pattern(self, query_type: str, final_tier: ModelTier):
        """
        Record escalation pattern to learn from.
        
        Args:
            query_type: Type of query
            final_tier: Final tier that successfully handled the query
        """
        if query_type not in self.escalation_patterns:
            self.escalation_patterns[query_type] = []
        
        self.escalation_patterns[query_type].append(final_tier)
        
        # Keep only last 10 patterns per type
        if len(self.escalation_patterns[query_type]) > 10:
            self.escalation_patterns[query_type] = self.escalation_patterns[query_type][-10:]
        
        logger.info(f"Recorded escalation pattern: {query_type} -> {final_tier.value}")
    
    def get_usage_stats(self) -> UsageStats:
        """
        Get current usage statistics.
        
        Returns:
            Usage statistics
        """
        return self.stats
    
    def reset_daily_budget(self):
        """Reset daily carbon budget."""
        logger.info(f"Resetting daily budget - used: {self.carbon_used_today:.2f}g")
        self.carbon_used_today = 0.0
        self.budget_reset_time = datetime.now() + timedelta(days=1)
    
    def _check_budget_reset(self):
        """Check if daily budget should be reset."""
        if datetime.now() >= self.budget_reset_time:
            self.reset_daily_budget()
    
    def _has_capabilities(self, config: ModelConfig, required: List[str]) -> bool:
        """
        Check if model has required capabilities.
        
        Args:
            config: Model configuration
            required: Required capabilities
            
        Returns:
            True if model has all required capabilities
        """
        if not required:
            return True
        
        return any(cap in config.capabilities for cap in required)
    
    def _infer_capabilities(self, query_metadata: QueryMetadata) -> List[str]:
        """
        Infer required capabilities from query metadata.
        
        Args:
            query_metadata: Query metadata
            
        Returns:
            List of inferred capabilities
        """
        capabilities = []
        
        # Use query type if available
        if query_metadata.query_type:
            type_map = {
                'factual': ['factual'],
                'definition': ['definition'],
                'simple_explanation': ['simple_explanation'],
                'explanation': ['explanation'],
                'reasoning': ['reasoning'],
                'complex_reasoning': ['complex_reasoning'],
                'code_simple': ['code_simple'],
                'code_advanced': ['code_advanced'],
                'creative': ['creative'],
                'complex_creative': ['complex_creative'],
                'research': ['research'],
                'expert_reasoning': ['expert_reasoning']
            }
            capabilities = type_map.get(query_metadata.query_type, [])
        
        # Use complexity as fallback
        if not capabilities and query_metadata.complexity is not None:
            if query_metadata.complexity < 0.3:
                capabilities = ['factual', 'simple_explanation']
            elif query_metadata.complexity < 0.6:
                capabilities = ['explanation', 'reasoning']
            elif query_metadata.complexity < 0.8:
                capabilities = ['complex_reasoning', 'code_advanced']
            else:
                capabilities = ['expert_reasoning', 'research']
        
        # Default to simple capabilities
        if not capabilities:
            capabilities = ['factual']
        
        return capabilities
    
    def _check_escalation_patterns(self, query_metadata: QueryMetadata) -> Optional[ModelTier]:
        """
        Check if we have learned patterns for this query type.
        
        Args:
            query_metadata: Query metadata
            
        Returns:
            Suggested tier based on patterns, or None
        """
        if not query_metadata.query_type:
            return None
        
        patterns = self.escalation_patterns.get(query_metadata.query_type, [])
        if not patterns:
            return None
        
        # If most recent patterns show escalation, start with higher tier
        recent_patterns = patterns[-3:]  # Last 3 patterns
        if len(recent_patterns) >= 2:
            # If majority needed medium or higher, start there
            higher_tiers = [t for t in recent_patterns if t in [ModelTier.MEDIUM, ModelTier.LARGE]]
            if len(higher_tiers) >= 2:
                return ModelTier.MEDIUM
        
        return None

"""Model selector module initialization."""

from app.modules.model_selector.service import ModelSelector, ModelRequest, ModelResponse
from app.modules.model_selector.adaptive_selector import (
    AdaptiveModelSelector,
    ModelConfig,
    ModelTier,
    QueryMetadata,
    ModelResponse as AdaptiveModelResponse,
    UsageStats
)
from app.modules.model_selector.local_model_loader import LocalModelLoader
from app.modules.model_selector.quality_evaluator import QualityEvaluator, QualityMetrics
from app.modules.model_selector.api_integrations import APIIntegrations, APIResponse
from app.modules.model_selector.orchestrator import AdaptiveOrchestrator
from app.modules.model_selector.ab_testing import ABTestManager, ABTestResult
from app.modules.model_selector.tuning import ThresholdTuner

__all__ = [
    # Original exports
    "ModelSelector",
    "ModelRequest",
    "ModelResponse",
    # Adaptive selector exports
    "AdaptiveModelSelector",
    "ModelConfig",
    "ModelTier",
    "QueryMetadata",
    "AdaptiveModelResponse",
    "UsageStats",
    "LocalModelLoader",
    "QualityEvaluator",
    "QualityMetrics",
    "APIIntegrations",
    "APIResponse",
    "AdaptiveOrchestrator",
    # Advanced features
    "ABTestManager",
    "ABTestResult",
    "ThresholdTuner"
]

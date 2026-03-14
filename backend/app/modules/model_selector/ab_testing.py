"""
A/B Testing Framework - Compare model outputs to optimize routing.
Allows running shadow tests and comparing quality between tiers.
"""

import random
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from app.core.logging import get_logger
from app.modules.model_selector.adaptive_selector import ModelTier, ModelConfig
from app.modules.model_selector.quality_evaluator import QualityEvaluator

logger = get_logger(__name__)


@dataclass
class ABTestResult:
    """Result of an A/B test comparison."""
    query: str
    timestamp: datetime
    model_a: str
    model_b: str
    tier_a: ModelTier
    tier_b: ModelTier
    response_a: str
    response_b: str
    quality_a: float
    quality_b: float
    latency_a: float
    latency_b: float
    winner: Optional[str] = None  # 'model_a', 'model_b', or 'tie'
    carbon_diff: float = 0.0  # carbon(a) - carbon(b)


class ABTestManager:
    """
    Manages A/B testing of models.
    Supports shadow mode (run B in background) and direct comparison.
    """
    
    def __init__(
        self,
        experiment_rate: float = 0.1,  # 10% of queries
        quality_evaluator: Optional[QualityEvaluator] = None
    ):
        """
        Initialize A/B test manager.
        
        Args:
            experiment_rate: Fraction of queries to engage in testing
            quality_evaluator: Evaluator for scoring responses
        """
        self.experiment_rate = experiment_rate
        self.quality_evaluator = quality_evaluator or QualityEvaluator()
        self.results: List[ABTestResult] = []
        
        logger.info(f"ABTestManager initialized - rate: {experiment_rate}")
    
    def should_run_test(self, query: str) -> bool:
        """
        Determine if we should run an A/B test for this query.
        
        Args:
            query: User query
            
        Returns:
            True if test should run
        """
        # Simple random sampling
        # Could be enhanced to hash query for deterministic consistency
        return random.random() < self.experiment_rate
    
    def evaluate_comparison(
        self,
        query: str,
        result_a: Dict[str, Any],  # Expects dict with text, latency, model info
        result_b: Dict[str, Any],
        model_config_a: ModelConfig,
        model_config_b: ModelConfig
    ) -> ABTestResult:
        """
        Evaluate and record comparison between two model outputs.
        
        Args:
            query: Original query
            result_a: Result from model A (baseline)
            result_b: Result from model B (challenger)
            model_config_a: Config for model A
            model_config_b: Config for model B
            
        Returns:
            Test result object
        """
        # Evaluate quality
        metrics_a = self.quality_evaluator.evaluate(query, result_a['text'])
        metrics_b = self.quality_evaluator.evaluate(query, result_b['text'])
        
        score_a = metrics_a.overall_score
        score_b = metrics_b.overall_score
        
        # Determine winner
        winner = 'tie'
        margin = 0.1  # Significant difference threshold
        
        if score_a > score_b + margin:
            winner = 'model_a'
        elif score_b > score_a + margin:
            winner = 'model_b'
        elif model_config_b.carbon_per_1k_tokens < model_config_a.carbon_per_1k_tokens:
            # If quality is similar, the "better" one is the more eco-friendly one
            # But strictly speaking, "winner" usually refers to quality
            # Let's keep quality as primary winner metric, but note efficient choice
            pass
        
        # Calculate carbon difference
        # Estimate: typical 100 tokens out + 50 in
        est_tokens = 150 
        carbon_a = (est_tokens / 1000) * model_config_a.carbon_per_1k_tokens
        carbon_b = (est_tokens / 1000) * model_config_b.carbon_per_1k_tokens
        
        test_result = ABTestResult(
            query=query,
            timestamp=datetime.now(),
            model_a=model_config_a.name,
            model_b=model_config_b.name,
            tier_a=model_config_a.tier,
            tier_b=model_config_b.tier,
            response_a=result_a['text'],
            response_b=result_b['text'],
            quality_a=score_a,
            quality_b=score_b,
            latency_a=result_a['latency'],
            latency_b=result_b['latency'],
            winner=winner,
            carbon_diff=carbon_a - carbon_b
        )
        
        self.results.append(test_result)
        
        # Log summary
        logger.info(
            f"A/B Test completed: {winner} won. "
            f"A({model_config_a.tier.value}): {score_a:.2f}, "
            f"B({model_config_b.tier.value}): {score_b:.2f}"
        )
        
        return test_result
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get aggregate stats from A/B tests.
        
        Returns:
            Dictionary with win rates and comparisons
        """
        if not self.results:
            return {"status": "no testing data"}
            
        total = len(self.results)
        wins_a = len([r for r in self.results if r.winner == 'model_a'])
        wins_b = len([r for r in self.results if r.winner == 'model_b'])
        ties = len([r for r in self.results if r.winner == 'tie'])
        
        return {
            "total_tests": total,
            "wins_model_a_pct": (wins_a / total) * 100,
            "wins_model_b_pct": (wins_b / total) * 100,
            "ties_pct": (ties / total) * 100,
            "avg_quality_diff": sum(r.quality_a - r.quality_b for r in self.results) / total
        }

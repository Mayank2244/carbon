"""
Automatic Threshold Tuning - Optimizes quality thresholds based on feedback.
Adjusts sensitivity to balance quality vs carbon efficiency.
"""

from typing import Dict, List, Optional
from datetime import datetime
import statistics

from app.core.logging import get_logger
from app.modules.model_selector.quality_evaluator import QualityMetrics

logger = get_logger(__name__)


class ThresholdTuner:
    """
    Automatically tunes quality thresholds.
    Uses feedback loop to find optimal balance point.
    """
    
    def __init__(
        self,
        initial_threshold: float = 0.7,
        min_threshold: float = 0.5,
        max_threshold: float = 0.9,
        learning_rate: float = 0.01,
        window_size: int = 20
    ):
        """
        Initialize threshold tuner.
        
        Args:
            initial_threshold: Starting threshold
            min_threshold: Minimum allowed threshold
            max_threshold: Maximum allowed threshold
            learning_rate: Step size for adjustments
            window_size: Number of samples to consider for update
        """
        self.current_threshold = initial_threshold
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.learning_rate = learning_rate
        self.window_size = window_size
        
        # History of evaluations: (score, was_accepted_by_user)
        # Note: was_accepted_by_user would ideally come from explicit feedback
        # Lacking that, we use "did not escalate" as proxy for acceptance
        self.history: List[float] = []
        self.escalation_rate_history: List[bool] = []
        
        logger.info(f"ThresholdTuner initialized - current: {initial_threshold}")
    
    def update(self, quality_score: float, escalated: bool):
        """
        Update tuner with new observation.
        
        Args:
            quality_score: Comparison score
            escalated: Whether the query was escalated (failed checks)
        """
        self.history.append(quality_score)
        self.escalation_rate_history.append(escalated)
        
        # Keep window size fixed
        if len(self.history) > self.window_size:
            self.history.pop(0)
            self.escalation_rate_history.pop(0)
            
            # Periodically tune (every window_size updates)
            if len(self.history) == self.window_size:
                self._tune_threshold()
    
    def _tune_threshold(self):
        """Adjust threshold based on recent performance."""
        avg_score = statistics.mean(self.history)
        escalation_rate = sum(self.escalation_rate_history) / len(self.escalation_rate_history)
        
        old_threshold = self.current_threshold
        
        # Tuning Logic:
        # Target escalation rate: ~10-15% (implies we are pushing boundaries of smaller models)
        # If escalation rate > 20%, we are too strict or models are too weak -> LOWER threshold?
        # WAIT: If escalation rate is high, it means many queries are failing specific checks.
        # If we lower threshold, we accept more "bad" answers.
        # If we raise threshold, we escalate MORE.
        
        # Correct logic:
        # If escalation rate is too high (>20%), and user complaints are low (assumed),
        # maybe our threshold is too strict. We should lower it to pass more queries.
        # If escalation rate is too low (<5%), we are likely using models that are "too good" (or threshold is too low),
        # but since we start small, low escalation meant small models are working great!
        # Actually, if escalation is low, we might be able to RAISE threshold to ensure even HIGHER quality
        # without incurring too much cost? No, that increases cost.
        
        # Let's optimize for Carbon Efficiency:
        # We want the lowest threshold that still guarantees "Good Enough" quality.
        # "Good Enough" is hard to define without explicit user feedback.
        # But we can look at the average quality scores.
        
        # Heuristic:
        # If scores are consistently high (avg > threshold + 0.15), we can raise threshold slightly to be safer?
        # No, if scores are high, we are happy.
        
        # Let's use target escalation rate of 10%.
        target_escalation = 0.10
        
        if escalation_rate > target_escalation + 0.05:
            # Too many escalations (costly). Maybe we are too strict.
            # Lower threshold to accept marginally lower quality (but cheaper) results.
            self.current_threshold -= self.learning_rate
            logger.info(f"High escalation ({escalation_rate:.1%}). Lowering threshold.")
            
        elif escalation_rate < target_escalation - 0.05:
            # Very few escalations. We are accepting almost everything.
            # We can afford to be stricter to improve quality.
            self.current_threshold += self.learning_rate
            logger.info(f"Low escalation ({escalation_rate:.1%}). Raising threshold.")
            
        # Clamp values
        self.current_threshold = max(self.min_threshold, min(self.max_threshold, self.current_threshold))
        
        if abs(old_threshold - self.current_threshold) > 1e-6:
            logger.info(f"Tuned threshold: {old_threshold:.3f} -> {self.current_threshold:.3f}")
            
    def get_current_threshold(self) -> float:
        """Get the currently tuned threshold."""
        return self.current_threshold

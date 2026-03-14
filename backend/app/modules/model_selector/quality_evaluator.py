"""
Quality Evaluator - Assesses response quality to determine if fallback is needed.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class QualityMetrics:
    """Quality assessment metrics for a response."""
    completeness_score: float  # 0.0 to 1.0
    coherence_score: float  # 0.0 to 1.0
    relevance_score: float  # 0.0 to 1.0
    length_score: float  # 0.0 to 1.0
    overall_score: float  # 0.0 to 1.0
    passed: bool
    issues: List[str]


class QualityEvaluator:
    """
    Evaluates response quality to determine if fallback to larger model is needed.
    Uses heuristics to assess completeness, coherence, and relevance.
    """
    
    def __init__(self, quality_threshold: float = 0.7):
        """
        Initialize quality evaluator.
        
        Args:
            quality_threshold: Minimum score to pass quality check
        """
        self.quality_threshold = quality_threshold
        logger.info(f"QualityEvaluator initialized - threshold: {quality_threshold}")
    
    def evaluate(
        self,
        query: str,
        response: str,
        expected_min_length: int = 50,
        expected_max_length: int = 2000
    ) -> QualityMetrics:
        """
        Evaluate response quality.
        
        Args:
            query: Original query
            response: Model response
            expected_min_length: Minimum expected response length
            expected_max_length: Maximum expected response length
            
        Returns:
            Quality metrics
        """
        issues = []
        
        # 1. Completeness check
        completeness_score = self._check_completeness(response, expected_min_length)
        if completeness_score < 0.5:
            issues.append("Response too short or incomplete")
        
        # 2. Coherence check
        coherence_score = self._check_coherence(response)
        if coherence_score < 0.5:
            issues.append("Response lacks coherence")
        
        # 3. Relevance check
        relevance_score = self._check_relevance(query, response)
        if relevance_score < 0.5:
            issues.append("Response not relevant to query")
        
        # 4. Length validation
        length_score = self._check_length(response, expected_min_length, expected_max_length)
        if length_score < 0.5:
            issues.append("Response length inappropriate")
        
        # Calculate overall score (weighted average)
        overall_score = (
            completeness_score * 0.3 +
            coherence_score * 0.25 +
            relevance_score * 0.3 +
            length_score * 0.15
        )
        
        passed = overall_score >= self.quality_threshold
        
        metrics = QualityMetrics(
            completeness_score=completeness_score,
            coherence_score=coherence_score,
            relevance_score=relevance_score,
            length_score=length_score,
            overall_score=overall_score,
            passed=passed,
            issues=issues
        )
        
        logger.info(
            f"Quality evaluation - overall: {overall_score:.2f}, "
            f"passed: {passed}, issues: {len(issues)}"
        )
        
        return metrics
    
    def _check_completeness(self, response: str, min_length: int) -> float:
        """
        Check if response is complete.
        
        Args:
            response: Response text
            min_length: Minimum expected length
            
        Returns:
            Completeness score (0.0 to 1.0)
        """
        score = 1.0
        
        # Check minimum length
        if len(response) < min_length:
            score *= len(response) / min_length
        
        # Check for incomplete sentences
        if response and not response.rstrip().endswith(('.', '!', '?', '"', "'")):
            score *= 0.7
        
        # Check for truncation indicators
        truncation_indicators = ['...', '[truncated]', '[incomplete]']
        if any(ind in response.lower() for ind in truncation_indicators):
            score *= 0.5
        
        return min(score, 1.0)
    
    def _check_coherence(self, response: str) -> float:
        """
        Check response coherence and structure.
        
        Args:
            response: Response text
            
        Returns:
            Coherence score (0.0 to 1.0)
        """
        score = 1.0
        
        # Check for proper sentence structure
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Check average sentence length (too short = incoherent)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_sentence_length < 3:
            score *= 0.5
        
        # Check for repeated phrases (sign of model confusion)
        words = response.lower().split()
        if len(words) > 10:
            # Check for excessive repetition
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.4:  # Less than 40% unique words
                score *= 0.6
        
        # Check for error messages or confusion indicators
        confusion_indicators = [
            "i don't understand",
            "i'm not sure",
            "i cannot",
            "error",
            "invalid",
            "sorry, i"
        ]
        if any(ind in response.lower() for ind in confusion_indicators):
            score *= 0.7
        
        return min(score, 1.0)
    
    def _check_relevance(self, query: str, response: str) -> float:
        """
        Check if response is relevant to the query.
        
        Args:
            query: Original query
            response: Response text
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        score = 1.0
        
        # Extract key terms from query (simple approach)
        query_words = set(re.findall(r'\b\w{4,}\b', query.lower()))
        response_words = set(re.findall(r'\b\w{4,}\b', response.lower()))
        
        if not query_words:
            return 1.0  # Can't judge without key terms
        
        # Check overlap of key terms
        overlap = query_words & response_words
        overlap_ratio = len(overlap) / len(query_words)
        
        # Expect at least 30% overlap for relevance
        if overlap_ratio < 0.3:
            score *= overlap_ratio / 0.3
        
        # Check for generic/evasive responses
        generic_phrases = [
            "i'm an ai",
            "as an ai",
            "i don't have access",
            "i cannot provide",
            "beyond my capabilities"
        ]
        if any(phrase in response.lower() for phrase in generic_phrases):
            score *= 0.6
        
        return min(score, 1.0)
    
    def _check_length(
        self,
        response: str,
        min_length: int,
        max_length: int
    ) -> float:
        """
        Check if response length is appropriate.
        
        Args:
            response: Response text
            min_length: Minimum expected length
            max_length: Maximum expected length
            
        Returns:
            Length score (0.0 to 1.0)
        """
        length = len(response)
        
        if length < min_length:
            # Too short
            return length / min_length
        elif length > max_length:
            # Too long (might be rambling)
            excess = length - max_length
            penalty = min(excess / max_length, 0.5)
            return 1.0 - penalty
        else:
            # Good length
            return 1.0
    
    def should_escalate(self, metrics: QualityMetrics) -> bool:
        """
        Determine if response should trigger escalation to larger model.
        
        Args:
            metrics: Quality metrics
            
        Returns:
            True if should escalate, False otherwise
        """
        return not metrics.passed
    
    def get_escalation_reason(self, metrics: QualityMetrics) -> str:
        """
        Get human-readable reason for escalation.
        
        Args:
            metrics: Quality metrics
            
        Returns:
            Escalation reason
        """
        if metrics.passed:
            return "No escalation needed"
        
        reasons = []
        
        if metrics.completeness_score < 0.5:
            reasons.append("incomplete response")
        if metrics.coherence_score < 0.5:
            reasons.append("poor coherence")
        if metrics.relevance_score < 0.5:
            reasons.append("low relevance")
        if metrics.length_score < 0.5:
            reasons.append("inappropriate length")
        
        if reasons:
            return f"Quality issues: {', '.join(reasons)}"
        else:
            return f"Overall quality score ({metrics.overall_score:.2f}) below threshold ({self.quality_threshold})"

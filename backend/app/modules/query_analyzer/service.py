"""
Query Analyzer Module (Lightweight)
Analyzes incoming queries using simple heuristics to avoid heavy NLP dependencies.
"""

import time
import re
from typing import Dict, Any, List, Tuple

from app.core.logging import get_logger
from app.core.exceptions import QueryAnalysisException
from app.modules.query_analyzer.models import (
    QueryAnalysisResult,
    QueryComplexity,
    QueryIntent,
    QueryUrgency,
    QueryDomain
)

logger = get_logger(__name__)


class QueryAnalyzer:
    """
    Lightweight Query Analyzer for classification and metadata extraction.

    This class provides heuristics-based analysis of incoming queries to determine
    complexity, intent, urgency, and domain without relying on heavy NLP models.
    It uses keyword matching and basic text analysis for high efficiency.

    Attributes:
        domain_keywords (dict): Mapping of domains to their characteristic keywords.
        urgency_keywords (set): Set of keywords indicating high urgency.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        # Domain Keywords
        self.domain_keywords = {
            QueryDomain.TECH: {
                "code", "python", "java", "api", "database", "server", "algorithm",
                "debug", "error", "compile", "function", "class", "variable", "aws",
                "cloud", "docker", "kubernetes", "linux", "html", "css", "javascript"
            },
            QueryDomain.MEDICAL: {
                "symptom", "doctor", "medicine", "pain", "treatment", "diagnosis",
                "health", "disease", "virus", "infection", "therapy", "drug", "dose"
            },
            QueryDomain.FINANCE: {
                "money", "stock", "market", "price", "cost", "invest", "bank",
                "tax", "revenue", "profit", "loss", "budget", "crypto", "bitcoin",
                "dollar", "currency"
            }
        }
        
        # Urgency Keywords
        self.urgency_keywords = {
            "urgent", "immediately", "asap", "now", "critical", "emergency", "help"
        }
    
    async def analyze(self, query: str) -> QueryAnalysisResult:
        """
        Analyze a query to extract classified metadata and intent.

        Args:
            query (str): The raw user query string.

        Returns:
            QueryAnalysisResult: A structured object containing classifications,
                estimated tokens, and processing metadata.
        """
        if not query or not query.strip():
            return self._create_empty_result()
            
        try:
            start_time = time.time()
            text_lower = query.lower()
            
            # Extract classifications
            complexity = self._classify_complexity(query)
            intent = self._classify_intent(text_lower)
            urgency = self._classify_urgency(text_lower)
            domain = self._classify_domain(text_lower)
            requires_context = self._check_context_requirement(text_lower)
            estimated_tokens = len(query.split())
            
            confidence = 0.8
            
            processing_time = (time.time() - start_time) * 1000  # ms
            
            result = QueryAnalysisResult(
                query_text=query,
                complexity=complexity,
                intent=intent,
                urgency=urgency,
                domain=domain,
                estimated_tokens=estimated_tokens,
                requires_context=requires_context,
                confidence_score=confidence,
                metadata={
                    "processing_time_ms": round(processing_time, 2),
                    "char_count": len(query),
                    "analysis_mode": "lightweight"
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Query analysis failed: {str(e)}")
            # Return simple default instead of crashing
            return self._create_empty_result()

    def _classify_complexity(self, text: str) -> QueryComplexity:
        """
        Classifies query complexity based on word count.

        Args:
            text (str): The query text.

        Returns:
            QueryComplexity: SIMPLE, MEDIUM, or COMPLEX.
        """
        words = len(text.split())
        if words < 8:
            return QueryComplexity.SIMPLE
        elif words < 25:
            return QueryComplexity.MEDIUM
        else:
            return QueryComplexity.COMPLEX

    def _classify_intent(self, text: str) -> QueryIntent:
        """
        Classifies query intent using keyword detection.

        Args:
            text (str): Lowercased query text.

        Returns:
            QueryIntent: CREATIVE, ANALYTICAL, TRANSACTIONAL, or FACTUAL.
        """
        if any(w in text for w in ["write", "create", "generate", "design", "make", "build", "construct", "code", "develop", "implement"]):
            return QueryIntent.CREATIVE
        if any(w in text for w in ["why", "how", "analyze", "explain", "compare", "evaluate"]):
            return QueryIntent.ANALYTICAL
        if any(w in text for w in ["buy", "order", "book"]):
            return QueryIntent.TRANSACTIONAL
        return QueryIntent.FACTUAL

    def _classify_urgency(self, text: str) -> QueryUrgency:
        """
        Determines query urgency based on time-sensitive keywords.

        Args:
            text (str): Lowercased query text.

        Returns:
            QueryUrgency: URGENT, TIME_SENSITIVE, or FLEXIBLE.
        """
        if any(w in text for w in self.urgency_keywords):
            return QueryUrgency.URGENT
        if any(w in text for w in ["today", "now", "tonight"]):
            return QueryUrgency.TIME_SENSITIVE
        return QueryUrgency.FLEXIBLE

    def _classify_domain(self, text: str) -> QueryDomain:
        """
        Detects the query domain by matching against specific keyword sets.

        Args:
            text (str): Lowercased query text.

        Returns:
            QueryDomain: Detected domain (e.g., TECH, MEDICAL, FINANCE) or GENERAL.
        """
        counts = {domain: 0 for domain in QueryDomain}
        for domain, keywords in self.domain_keywords.items():
            for kw in keywords:
                if kw in text:
                    counts[domain] += 1
        
        specific_counts = {k: v for k, v in counts.items() if k != QueryDomain.GENERAL}
        if not specific_counts:
            return QueryDomain.GENERAL
            
        best_domain = max(specific_counts, key=specific_counts.get)
        if counts[best_domain] > 0:
            return best_domain
        return QueryDomain.GENERAL

    def _check_context_requirement(self, text: str) -> bool:
        """
        Heuristically determines if the query requires previous context.

        Args:
            text (str): Lowercased query text.

        Returns:
            bool: True if context-dependent phrases are detected.
        """
        context_phrases = ["previous", "earlier", "above", "last one", "that one", "it", "they"]
        if any(phrase in text for phrase in context_phrases):
            return True
        return False

    def _create_empty_result(self) -> QueryAnalysisResult:
        """Creates a default result for empty or failed queries."""
        return QueryAnalysisResult(
            query_text="",
            complexity=QueryComplexity.SIMPLE,
            intent=QueryIntent.UNKNOWN,
            urgency=QueryUrgency.FLEXIBLE,
            domain=QueryDomain.GENERAL,
            estimated_tokens=0,
            requires_context=False,
            confidence_score=0.0
        )

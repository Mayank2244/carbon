"""
Comprehensive tests for Query Analyzer Module.
"""

import pytest
import asyncio
from app.modules.query_analyzer import (
    QueryAnalyzer,
    QueryComplexity,
    QueryIntent,
    QueryUrgency,
    QueryDomain
)

@pytest.fixture(scope="module")
def analyzer():
    """Initialize analyzer once for all tests."""
    return QueryAnalyzer()

@pytest.mark.asyncio
async def test_complexity_classification(analyzer):
    """Test complexity classification logic."""
    # Simple
    res1 = await analyzer.analyze("What is the weather?")
    assert res1.complexity == QueryComplexity.SIMPLE
    
    # Medium
    res2 = await analyzer.analyze("Explain how the photosynthesis process works in plants.")
    assert res2.complexity == QueryComplexity.MEDIUM
    
    # Complex (High depth, technical terms)
    res3 = await analyzer.analyze(
        "Analyze the algorithmic efficiency of the new database sharding strategy considering latency and throughput constraints in a distributed system."
    )
    assert res3.complexity == QueryComplexity.COMPLEX

@pytest.mark.asyncio
async def test_intent_classification(analyzer):
    """Test intent classification logic."""
    # Factual
    res1 = await analyzer.analyze("Who is the CEO of Apple?")
    assert res1.intent == QueryIntent.FACTUAL
    
    # Creative
    res2 = await analyzer.analyze("Write a poem about the ocean.")
    assert res2.intent == QueryIntent.CREATIVE
    
    # Analytical
    res3 = await analyzer.analyze("Compare Python and Java performance.")
    assert res3.intent == QueryIntent.ANALYTICAL
    
    # Transactional
    res4 = await analyzer.analyze("Book a flight to London.")
    assert res4.intent == QueryIntent.TRANSACTIONAL

@pytest.mark.asyncio
async def test_urgency_classification(analyzer):
    """Test urgency classification logic."""
    # Urgent
    res1 = await analyzer.analyze("Help! System is down urgent.")
    assert res1.urgency == QueryUrgency.URGENT
    
    # Time-sensitive
    res2 = await analyzer.analyze("What is the stock price today?")
    assert res2.urgency == QueryUrgency.TIME_SENSITIVE
    
    # Flexible
    res3 = await analyzer.analyze("Tell me a history of Rome.")
    assert res3.urgency == QueryUrgency.FLEXIBLE

@pytest.mark.asyncio
async def test_domain_classification(analyzer):
    """Test domain classification logic."""
    # Tech
    res1 = await analyzer.analyze("How to debug a Python memory leak?")
    assert res1.domain == QueryDomain.TECH
    
    # Medical
    res2 = await analyzer.analyze("What are the symptoms of flu?")
    assert res2.domain == QueryDomain.MEDICAL
    
    # Finance
    res3 = await analyzer.analyze("Invest in stock market index funds.")
    assert res3.domain == QueryDomain.FINANCE
    
    # General
    res4 = await analyzer.analyze("What is the capital of France?")
    assert res4.domain == QueryDomain.GENERAL

@pytest.mark.asyncio
async def test_context_requirement(analyzer):
    """Test context requirement detection."""
    # Context needed (pronouns)
    res1 = await analyzer.analyze("What does it do?")
    assert res1.requires_context is True
    
    # Context needed (explicit)
    res2 = await analyzer.analyze("and the previous answer")
    assert res2.requires_context is True
    
    # No context needed
    res3 = await analyzer.analyze("Define gravity.")
    assert res3.requires_context is False

@pytest.mark.asyncio
async def test_empty_query(analyzer):
    """Test handling of empty queries."""
    res = await analyzer.analyze("")
    assert res.estimated_tokens == 0
    assert res.confidence_score == 0.0

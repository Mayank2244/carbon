"""
Database models for CarbonSense AI system.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base
from app.modules.query_analyzer.models import QueryComplexity, QueryIntent, QueryUrgency, QueryDomain


class Query(Base):
    """Model for storing user queries with detailed metadata."""
    
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    query_hash = Column(String(64), unique=True, index=True, nullable=False)
    
    # Classification Metadata
    complexity = Column(String(20), nullable=True)  # Enum: SIMPLE, MEDIUM, COMPLEX
    intent = Column(String(50), nullable=True)      # Enum: FACTUAL, CREATIVE, etc.
    urgency = Column(String(20), nullable=True)     # Enum: URGENT, FLEXIBLE
    domain = Column(String(50), nullable=True)      # Enum: TECH, MEDICAL, etc.
    
    # User Context
    user_id = Column(String(100), index=True, nullable=True)
    session_id = Column(String(100), index=True, nullable=True)
    
    # Meta
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    responses = relationship("ModelResponse", back_populates="query")
    carbon_metrics = relationship("CarbonMetrics", back_populates="query")
    routing_decision = relationship("RoutingDecision", back_populates="query", uselist=False)
    
    def __repr__(self) -> str:
        return f"<Query(id={self.id}, hash={self.query_hash[:8]}, intent={self.intent})>"


class ModelResponse(Base):
    """Model for storing AI model responses."""
    
    __tablename__ = "model_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False, index=True)
    
    model_name = Column(String(100), nullable=False)
    response_text = Column(Text, nullable=False)
    
    # Performance Metrics
    tokens_used = Column(Integer, nullable=True)
    latency_ms = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)
    
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    query = relationship("Query", back_populates="responses")
    
    def __repr__(self) -> str:
        return f"<ModelResponse(id={self.id}, model={self.model_name})>"


class CarbonMetrics(Base):
    """Model for storing carbon emission metrics."""
    
    __tablename__ = "carbon_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False, index=True)
    
    model_name = Column(String(100), nullable=False)
    
    # Emissions Data
    carbon_grams = Column(Float, nullable=False)
    energy_kwh = Column(Float, nullable=True)
    region = Column(String(50), nullable=True)
    
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    query = relationship("Query", back_populates="carbon_metrics")
    
    def __repr__(self) -> str:
        return f"<CarbonMetrics(id={self.id}, carbon={self.carbon_grams}g)>"


class RoutingDecision(Base):
    """Model for storing routing decisions."""
    
    __tablename__ = "routing_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False, index=True)
    
    selected_model = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    alternative_models = Column(JSON, nullable=True)
    
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    query = relationship("Query", back_populates="routing_decision")
    
    def __repr__(self) -> str:
        return f"<RoutingDecision(id={self.id}, model={self.selected_model})>"


class CacheEntry(Base):
    """Model for storing cache metadata and analytics."""
    
    __tablename__ = "cache_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    query_hash = Column(String(64), nullable=False, index=True)
    
    # Analytics
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self) -> str:
        return f"<CacheEntry(id={self.id}, key={self.cache_key}, hits={self.hit_count})>"


class User(Base):
    """Model for storing user accounts."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class RLFeedback(Base):
    """Model for storing reinforcement learning feedback."""
    
    __tablename__ = "rl_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False, index=True)
    routing_decision_id = Column(Integer, ForeignKey("routing_decisions.id"), nullable=False, index=True)
    
    reward_score = Column(Float, nullable=False)
    feedback_type = Column(String(50), nullable=True) # explicit, implicit
    user_satisfaction = Column(Float, nullable=True) # 0.0 to 1.0
    
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self) -> str:
        return f"<RLFeedback(id={self.id}, reward={self.reward_score})>"

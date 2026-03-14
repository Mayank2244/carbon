"""
Configuration management for CarbonSense AI system.
Loads settings from environment variables using Pydantic Settings.
"""

from typing import List
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    app_name: str = Field(default="CarbonSense AI", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="production", alias="ENVIRONMENT")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    
    # Database Configuration
    database_url: str = Field(..., alias="DATABASE_URL")
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")
    
    # Redis Configuration
    redis_url: str = Field(..., alias="REDIS_URL")
    redis_max_connections: int = Field(default=50, alias="REDIS_MAX_CONNECTIONS")
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")
    
    # AI Model API Keys
    groq_api_key: str = Field(..., alias="GROQ_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")  # Optional, using Groq instead
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")  # Optional, using Groq instead
    huggingface_api_key: str = Field(default="", alias="HUGGINGFACE_API_KEY")
    
    # Model Endpoints
    groq_model: str = Field(default="llama-3.1-8b-instant", alias="GROQ_MODEL")
    anthropic_model: str = Field(default="claude-3-opus-20240229", alias="ANTHROPIC_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    huggingface_model: str = Field(default="meta-llama/Meta-Llama-3-70B-Instruct", alias="HUGGINGFACE_MODEL")
    gemini_model: str = Field(default="gemini-pro", alias="GEMINI_MODEL")
    
    # RAG & Chroma Configuration
    chroma_db_path: str = Field(default="./data/chroma", alias="CHROMA_DB_PATH")
    vector_dimension: int = Field(default=1536, alias="VECTOR_DIMENSION")
    max_context_length: int = Field(default=4096, alias="MAX_CONTEXT_LENGTH")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", alias="SECRET_KEY")
    top_k_results: int = Field(default=5, alias="TOP_K_RESULTS")
    
    # RL Optimizer Settings
    rl_learning_rate: float = Field(default=0.001, alias="RL_LEARNING_RATE")
    rl_discount_factor: float = Field(default=0.95, alias="RL_DISCOUNT_FACTOR")
    rl_exploration_rate: float = Field(default=0.1, alias="RL_EXPLORATION_RATE")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    
    # CORS Settings
    cors_origins: List[str] = Field(
        default="http://localhost:3000,http://localhost:5173,http://localhost:8000,https://*.trycloudflare.com",
        alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, alias="METRICS_PORT")
    
    # Carbon API Configuration
    electricity_maps_api_key: str = Field(default="", alias="ELECTRICITY_MAPS_API_KEY")
    watttime_username: str = Field(default="", alias="WATTTIME_USERNAME")
    watttime_password: str = Field(default="", alias="WATTTIME_PASSWORD")
    climatiq_api_key: str = Field(default="", alias="CLIMATIQ_API_KEY")
    carbon_cache_ttl: int = Field(default=900, alias="CARBON_CACHE_TTL")  # 15 minutes
    
    # Neo4j Configuration
    neo4j_uri: str = Field(default="bolt://neo4j:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")
    
    # GraphRAG Configuration
    graph_rag_confidence_threshold: float = Field(default=0.8, alias="GRAPH_RAG_CONFIDENCE_THRESHOLD")
    graph_rag_max_depth: int = Field(default=3, alias="GRAPH_RAG_MAX_DEPTH")
    small_llm_model: str = Field(default="llama-3.2-1b-preview", alias="SMALL_LLM_MODEL")

    # Optimization Configuration
    carbon_budget_daily_grams: float = Field(default=1000.0, alias="CARBON_BUDGET_DAILY_GRAMS")
    model_idle_timeout_seconds: int = Field(default=300, alias="MODEL_IDLE_TIMEOUT_SECONDS")
    quality_threshold: float = Field(default=0.7, alias="QUALITY_THRESHOLD")
    enable_model_warmup: bool = Field(default=True, alias="ENABLE_MODEL_WARMUP")
    tiny_model_always_loaded: bool = Field(default=True, alias="TINY_MODEL_ALWAYS_LOADED")
    local_model_cache_dir: str = Field(default="./models", alias="LOCAL_MODEL_CACHE_DIR")
    use_gpu_if_available: bool = Field(default=True, alias="USE_GPU_IF_AVAILABLE")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if isinstance(v, list):
            return v  # Already a list from environment
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()

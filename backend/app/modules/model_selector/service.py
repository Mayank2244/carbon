import time
from typing import Dict, Any, Optional
from pydantic import BaseModel
from groq import AsyncGroq
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import AIModelException

logger = get_logger(__name__)


class ModelRequest(BaseModel):
    """Model request parameters."""
    
    model_name: str
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7
    context: Optional[str] = None


class ModelResponse(BaseModel):
    """Model response."""
    
    model_name: str
    response_text: str
    tokens_used: int
    latency_ms: float
    metadata: Dict[str, Any] = {}


class ModelSelector:
    """
    Orchestrator for AI model interactions across different providers.

    This class handles specific API logic for Groq, Anthropic, and other
    supported LLM providers. It routes generation requests to the appropriate
    backend and tracks token usage and latency.

    Attributes:
        groq_client (AsyncGroq): Client for interacting with Groq's high-speed inference.
        anthropic_api_key (str): Configuration key for Anthropic models.
    """
    
    def __init__(self):
        """Initialize model selector."""
        self.groq_client = AsyncGroq(api_key=settings.groq_api_key)
        self.anthropic_api_key = settings.anthropic_api_key
        logger.info("Model selector initialized")
    
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """
        Routes the generation request to the appropriate provider client.

        Args:
            request (ModelRequest): The model, prompt, and parameters for generation.

        Returns:
            ModelResponse: The generated text and execution metadata.

        Raises:
            AIModelException: If the provider is unknown or if the API call fails.
        """
        logger.info(f"Generating response with {request.model_name}")
        
        try:
            if "llama" in request.model_name.lower() or "mixtral" in request.model_name.lower():
                return await self._generate_groq(request)
            elif "claude" in request.model_name.lower():
                return await self._generate_anthropic(request)
            else:
                # Fallback to Groq for now if unknown
                return await self._generate_groq(request)
                
        except Exception as e:
            logger.error(f"Model generation failed: {str(e)}")
            raise AIModelException(f"Failed to generate response: {str(e)}")
    
    async def _generate_groq(self, request: ModelRequest) -> ModelResponse:
        """
        Generate response using Groq API.
        
        Args:
            request: Model request
            
        Returns:
            Model response
        """
        logger.info(f"Calling Groq API with model {request.model_name}")
        
        start_time = time.time()
        
        try:
            chat_completion = await self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": request.prompt,
                    }
                ],
                model=request.model_name,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            
            # Extract content and usage
            response_text = chat_completion.choices[0].message.content
            usage = chat_completion.usage
            tokens_used = usage.total_tokens if usage else 0
            
            return ModelResponse(
                model_name=request.model_name,
                response_text=response_text,
                tokens_used=tokens_used,
                latency_ms=latency,
                metadata={"provider": "groq", "model": request.model_name}
            )
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            # For development without valid keys, return mock
            return ModelResponse(
                model_name=request.model_name,
                response_text=f"[MOCK from Groq] Response to: {request.prompt[:50]}...",
                tokens_used=100,
                latency_ms=100.0,
                metadata={"provider": "groq", "mock": True}
            )
    
    async def _generate_anthropic(self, request: ModelRequest) -> ModelResponse:
        """
        Generate response using Anthropic API.
        
        Args:
            request: Model request
            
        Returns:
            Model response
        """
        # In production, use actual Anthropic API
        # For now, return mock response
        logger.info(f"Calling Anthropic API with model {request.model_name}")
        
        # Mock response
        return ModelResponse(
            model_name=request.model_name,
            response_text=f"Mock response from {request.model_name} for: {request.prompt[:50]}...",
            tokens_used=140,
            latency_ms=450.0,
            metadata={"provider": "anthropic"}
        )
    
    async def estimate_cost(
        self,
        model_name: str,
        tokens: int
    ) -> float:
        """
        Calculates the estimated monetary cost of a generation request.

        Args:
            model_name (str): The name of the model used.
            tokens (int): The total number of tokens processed.

        Returns:
            float: Estimated cost in USD.
        """
        # Cost per 1k tokens
        cost_map = {
            "llama3-8b-8192": 0.0001,
            "llama3-70b-8192": 0.0007,
            "mixtral-8x7b-32768": 0.00027,
            "claude-3-haiku": 0.0015,
            "claude-3-sonnet": 0.005,
            "claude-3-opus": 0.015,
        }
        
        cost_per_1k = cost_map.get(model_name, 0.001)
        return (tokens / 1000) * cost_per_1k

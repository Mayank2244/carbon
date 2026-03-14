"""
API Integrations - Unified client for external model providers.
Supports Groq, Hugging Face, and Gemini with retry logic and cost tracking.
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from groq import AsyncGroq
from huggingface_hub import AsyncInferenceClient
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


@dataclass
class APIResponse:
    """Response from an API model."""
    text: str
    tokens_used: int
    latency_ms: float
    model_name: str
    provider: str
    metadata: Dict[str, Any]


class APIIntegrations:
    """
    Unified API client for external model providers.
    Handles Groq, Hugging Face, and Gemini with proper error handling and retry logic.
    """
    
    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        huggingface_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None
    ):
        """
        Initialize API integrations.
        
        Args:
            groq_api_key: Groq API key (uses settings if None)
            huggingface_api_key: Hugging Face API key (uses settings if None)
            gemini_api_key: Gemini API key (uses settings if None)
        """
        self.groq_api_key = groq_api_key or getattr(settings, 'groq_api_key', None)
        self.huggingface_api_key = huggingface_api_key or getattr(settings, 'huggingface_api_key', None)
        self.gemini_api_key = gemini_api_key or getattr(settings, 'gemini_api_key', None)
        
        # Initialize Groq client
        if self.groq_api_key:
            self.groq_client = AsyncGroq(api_key=self.groq_api_key)
            logger.info("Groq client initialized")
        else:
            self.groq_client = None
            logger.warning("Groq API key not provided")

        # Initialize Hugging Face client
        if self.huggingface_api_key:
            self.hf_client = AsyncInferenceClient(token=self.huggingface_api_key)
            logger.info("Hugging Face client initialized")
        else:
            self.hf_client = None
            logger.warning("Hugging Face API key not provided")

        # Initialize Gemini client
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.has_gemini = True
            logger.info("Gemini client initialized")
        else:
            self.has_gemini = False
            logger.warning("Gemini API key not provided")
        
        logger.info("APIIntegrations initialized")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def call_groq(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> APIResponse:
        """
        Call Groq API with retry logic.
        """
        if not self.groq_client:
            raise ValueError("Groq client not initialized - API key missing")
        
        logger.info(f"Calling Groq API - model: {model}")
        start_time = time.time()
        
        try:
            response = await self.groq_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            latency = (time.time() - start_time) * 1000
            
            # Extract response
            text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            logger.info(
                f"Groq response received - tokens: {tokens_used}, "
                f"latency: {latency:.0f}ms"
            )
            
            return APIResponse(
                text=text,
                tokens_used=tokens_used,
                latency_ms=latency,
                model_name=model,
                provider="groq",
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model": response.model
                }
            )
            
        except Exception as e:
            logger.error(f"Groq API error: {e}", exc_info=True)
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def call_huggingface(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> APIResponse:
        """
        Call Hugging Face Inference API with retry logic.
        """
        if not self.hf_client:
            raise ValueError("Hugging Face client not initialized - API key missing")
        
        logger.info(f"Calling HF API - model: {model}")
        start_time = time.time()
        
        try:
            response = await self.hf_client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            latency = (time.time() - start_time) * 1000
            
            # Extract response
            text = response.choices[0].message.content
            # HF API might not always return fine-grained token usage, use estimate if missing
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else len(text.split()) * 1.3
            
            logger.info(
                f"HF response received - tokens: {int(tokens_used)}, "
                f"latency: {latency:.0f}ms"
            )
            
            return APIResponse(
                text=text,
                tokens_used=int(tokens_used),
                latency_ms=latency,
                model_name=model,
                provider="huggingface",
                metadata={
                    "model": model
                }
            )
            
        except Exception as e:
            logger.error(f"Hugging Face API error: {e}", exc_info=True)
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def call_gemini(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> APIResponse:
        """
        Call Google Gemini API with retry logic.
        """
        if not self.has_gemini:
            raise ValueError("Gemini client not initialized - API key missing")
        
        logger.info(f"Calling Gemini API - model: {model}")
        start_time = time.time()
        
        try:
            # Map common model names to Gemini specific ones if needed
            # For now assume 'gemini-pro' or 'gemini-1.5-pro'
            gemini_model = genai.GenerativeModel(model)
            
            config = genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Note: genai.generate_content is synchronous for now, assume running in thread/sync context
            # Or use async wrapper if available (latest SDK supports async)
            response = await gemini_model.generate_content_async(
                prompt,
                generation_config=config
            )
            
            latency = (time.time() - start_time) * 1000
            
            text = response.text
            # Estimate tokens if not provided (Gemini usually provides usage metadata)
            # Recent SDKs have usage_metadata
            tokens_used = 0
            if hasattr(response, 'usage_metadata'):
                tokens_used = response.usage_metadata.total_token_count
            else:
                tokens_used = len(text.split()) * 1.3
            
            logger.info(
                f"Gemini response received - tokens: {int(tokens_used)}, "
                f"latency: {latency:.0f}ms"
            )
            
            return APIResponse(
                text=text,
                tokens_used=int(tokens_used),
                latency_ms=latency,
                model_name=model,
                provider="gemini",
                metadata={
                    "model": model
                }
            )
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            raise

    async def call_model(
        self,
        provider: str,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> APIResponse:
        """
        Call a model based on provider.
        
        Args:
            provider: Provider name ('groq', 'huggingface', 'gemini')
            model: Model name
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            API response
        """
        if provider.lower() == "groq":
            return await self.call_groq(model, prompt, max_tokens, temperature, **kwargs)
        elif provider.lower() in ["huggingface", "hf"]:
            return await self.call_huggingface(model, prompt, max_tokens, temperature, **kwargs)
        elif provider.lower() == "gemini":
            return await self.call_gemini(model, prompt, max_tokens, temperature, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")

"""
Local Model Loader - Manages loading and lifecycle of local LLM models.
Implements lazy loading, memory management, and automatic cleanup.
"""

import os
import time
import threading
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

import torch
import psutil
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class ModelInstance:
    """Represents a loaded model instance with metadata."""
    
    def __init__(self, model: Any, tokenizer: Any, model_name: str):
        self.model = model
        self.tokenizer = tokenizer
        self.model_name = model_name
        self.last_used = datetime.now()
        self.load_time = datetime.now()
        self.usage_count = 0
    
    def update_usage(self):
        """Update usage timestamp and counter."""
        self.last_used = datetime.now()
        self.usage_count += 1
    
    def is_idle(self, timeout_seconds: int) -> bool:
        """Check if model has been idle for longer than timeout."""
        idle_time = (datetime.now() - self.last_used).total_seconds()
        return idle_time > timeout_seconds


class LocalModelLoader:
    """
    Manages loading and lifecycle of local LLM models.
    Implements lazy loading, memory management, and automatic cleanup.
    """
    
    # Model name mappings
    MODEL_MAPPINGS = {
        'TinyLlama-1.1B': 'TinyLlama/TinyLlama-1.1B-Chat-v1.0',
        'Llama-3.2-3B': 'meta-llama/Llama-3.2-3B-Instruct',
    }
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        idle_timeout: int = 300,  # 5 minutes
        keep_tiny_loaded: bool = True,
        use_gpu: bool = True,
        use_quantization: bool = True
    ):
        """
        Initialize local model loader.
        
        Args:
            cache_dir: Directory to cache models (default: ./models)
            idle_timeout: Seconds before unloading idle models
            keep_tiny_loaded: Keep tiny model always in memory
            use_gpu: Use GPU if available
            use_quantization: Use 4-bit quantization to save memory
        """
        self.cache_dir = cache_dir or getattr(settings, 'local_model_cache_dir', './models')
        self.idle_timeout = idle_timeout
        self.keep_tiny_loaded = keep_tiny_loaded
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.use_quantization = use_quantization
        
        # Create cache directory
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Loaded models cache
        self._models: Dict[str, ModelInstance] = {}
        self._lock = threading.Lock()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        
        logger.info(
            f"LocalModelLoader initialized - "
            f"cache_dir: {self.cache_dir}, "
            f"gpu: {self.use_gpu}, "
            f"quantization: {self.use_quantization}, "
            f"idle_timeout: {idle_timeout}s"
        )
    
    def load_model(self, model_key: str) -> ModelInstance:
        """
        Load a model (lazy loading - only loads if not already in memory).
        
        Args:
            model_key: Model key (e.g., 'TinyLlama-1.1B')
            
        Returns:
            Loaded model instance
        """
        with self._lock:
            # Check if already loaded
            if model_key in self._models:
                logger.info(f"Model {model_key} already loaded, reusing")
                self._models[model_key].update_usage()
                return self._models[model_key]
            
            # Load the model
            logger.info(f"Loading model {model_key}...")
            start_time = time.time()
            
            model_name = self.MODEL_MAPPINGS.get(model_key, model_key)
            
            try:
                # Configure quantization if enabled
                quantization_config = None
                if self.use_quantization:
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
                
                # Load tokenizer
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=self.cache_dir,
                    trust_remote_code=True
                )
                
                # Load model
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    cache_dir=self.cache_dir,
                    quantization_config=quantization_config,
                    device_map="auto" if self.use_gpu else "cpu",
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if self.use_gpu else torch.float32
                )
                
                load_time = time.time() - start_time
                
                # Create instance
                instance = ModelInstance(model, tokenizer, model_key)
                self._models[model_key] = instance
                
                # Log memory usage
                memory_info = self._get_memory_info()
                logger.info(
                    f"Model {model_key} loaded in {load_time:.2f}s - "
                    f"Memory: {memory_info['used_gb']:.2f}GB / {memory_info['total_gb']:.2f}GB "
                    f"({memory_info['percent']:.1f}%)"
                )
                
                return instance
                
            except Exception as e:
                logger.error(f"Failed to load model {model_key}: {e}", exc_info=True)
                raise
    
    def generate(
        self,
        model_key: str,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text using a local model.
        
        Args:
            model_key: Model key
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        instance = self.load_model(model_key)
        
        try:
            # Tokenize input
            inputs = instance.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            )
            
            # Move to device
            if self.use_gpu:
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = instance.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    pad_token_id=instance.tokenizer.eos_token_id,
                    **kwargs
                )
            
            # Decode output
            generated_text = instance.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            # Remove input prompt from output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            instance.update_usage()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Generation failed with {model_key}: {e}", exc_info=True)
            raise
    
    def unload_model(self, model_key: str):
        """
        Unload a model from memory.
        
        Args:
            model_key: Model key to unload
        """
        with self._lock:
            if model_key not in self._models:
                logger.warning(f"Model {model_key} not loaded, cannot unload")
                return
            
            # Don't unload tiny model if configured to keep it
            if self.keep_tiny_loaded and model_key == 'TinyLlama-1.1B':
                logger.info(f"Keeping {model_key} loaded (keep_tiny_loaded=True)")
                return
            
            logger.info(f"Unloading model {model_key}")
            
            # Delete model and free memory
            del self._models[model_key]
            
            # Force garbage collection
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            memory_info = self._get_memory_info()
            logger.info(
                f"Model {model_key} unloaded - "
                f"Memory: {memory_info['used_gb']:.2f}GB / {memory_info['total_gb']:.2f}GB"
            )
    
    def warmup_models(self, model_keys: list[str]):
        """
        Pre-load models during low traffic periods.
        
        Args:
            model_keys: List of model keys to warm up
        """
        logger.info(f"Warming up models: {model_keys}")
        
        for model_key in model_keys:
            try:
                self.load_model(model_key)
            except Exception as e:
                logger.error(f"Failed to warm up {model_key}: {e}")
    
    def get_loaded_models(self) -> list[str]:
        """
        Get list of currently loaded models.
        
        Returns:
            List of loaded model keys
        """
        with self._lock:
            return list(self._models.keys())
    
    def _cleanup_loop(self):
        """Background thread to cleanup idle models."""
        while True:
            try:
                time.sleep(60)  # Check every minute
                self._cleanup_idle_models()
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}", exc_info=True)
    
    def _cleanup_idle_models(self):
        """Unload models that have been idle for too long."""
        with self._lock:
            models_to_unload = []
            
            for model_key, instance in self._models.items():
                if instance.is_idle(self.idle_timeout):
                    # Don't unload tiny model if configured to keep it
                    if self.keep_tiny_loaded and model_key == 'TinyLlama-1.1B':
                        continue
                    
                    models_to_unload.append(model_key)
        
        # Unload outside of lock to avoid deadlock
        for model_key in models_to_unload:
            logger.info(f"Unloading idle model: {model_key}")
            self.unload_model(model_key)
    
    def _get_memory_info(self) -> Dict[str, float]:
        """
        Get current memory usage information.
        
        Returns:
            Dictionary with memory stats
        """
        if self.use_gpu and torch.cuda.is_available():
            # GPU memory
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            
            return {
                'used_gb': allocated,
                'reserved_gb': reserved,
                'total_gb': total,
                'percent': (allocated / total) * 100
            }
        else:
            # System RAM
            memory = psutil.virtual_memory()
            return {
                'used_gb': memory.used / 1024**3,
                'total_gb': memory.total / 1024**3,
                'percent': memory.percent
            }

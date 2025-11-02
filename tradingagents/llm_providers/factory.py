"""LLM Provider factory for creating LLM instances from configuration."""

from typing import Dict, Any, Optional, List
import logging

from .base import LLMProvider, BaseLLM
from .openai_provider import OpenAIProvider
from .deepseek_provider import DeepSeekProvider
from .anthropic_provider import AnthropicProvider
from .openrouter_provider import OpenRouterProvider

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory for creating LLM instances from multiple providers"""
    
    _providers: Dict[str, LLMProvider] = {}
    _initialized = False
    
    @classmethod
    def _initialize_providers(cls):
        """Initialize available providers"""
        if cls._initialized:
            return
        
        # Register providers
        cls._providers["openai"] = OpenAIProvider()
        cls._providers["deepseek"] = DeepSeekProvider()
        
        # OpenRouter - unified access to multiple models
        try:
            cls._providers["openrouter"] = OpenRouterProvider()
        except Exception as e:
            logger.warning(f"OpenRouter provider not available: {e}")
        
        # Anthropic requires langchain-anthropic
        try:
            cls._providers["anthropic"] = AnthropicProvider()
        except ImportError:
            logger.warning("Anthropic provider not available. Install with: pip install langchain-anthropic")
        
        cls._initialized = True
    
    @classmethod
    def get_provider(cls, provider_name: str) -> Optional[LLMProvider]:
        """Get a provider by name"""
        cls._initialize_providers()
        return cls._providers.get(provider_name.lower())
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """List all available providers"""
        cls._initialize_providers()
        return list(cls._providers.keys())
    
    @classmethod
    def create_llm(
        cls,
        model_config: str,
        provider: Optional[str] = None,
        **kwargs
    ) -> BaseLLM:
        """
        Create an LLM instance from configuration.
        
        Args:
            model_config: Model configuration string. Can be:
                        - "provider:model" (e.g., "openai:gpt-4o-mini")
                        - "model" (will auto-detect provider)
            provider: Explicit provider name (overrides model_config)
            **kwargs: Additional parameters for LLM initialization
        
        Returns:
            BaseLLM instance
        
        Raises:
            ValueError: If provider/model is not found
        """
        cls._initialize_providers()
        
        # Extract model name first (might have provider prefix)
        model = model_config
        if ":" in model_config:
            # Extract model part if format is "provider:model"
            _, model = model_config.split(":", 1)
        
        # Initialize provider_obj
        provider_obj = None
        
        # If explicit provider specified, use it
        if provider:
            provider_obj = cls.get_provider(provider)
            if not provider_obj:
                raise ValueError(f"Provider '{provider}' not available. Available: {cls.list_providers()}")
            # Use the extracted model (without provider prefix)
        else:
            # Try to extract provider from model_config
            if ":" in model_config:
                provider_name, model_name = model_config.split(":", 1)
                provider_obj = cls.get_provider(provider_name)
                if not provider_obj:
                    raise ValueError(f"Provider '{provider_name}' not found")
                model = model_name
            else:
                # Auto-detect provider by trying each one
                model = model_config
                provider_obj = None
                
                for prov_name, prov_obj in cls._providers.items():
                    if prov_obj.validate_model(model):
                        provider_obj = prov_obj
                        logger.info(f"Auto-detected provider '{prov_name}' for model '{model}'")
                        break
                
                if not provider_obj:
                    # Default to OpenAI if no match found
                    logger.warning(f"No provider found for model '{model}', defaulting to OpenAI")
                    provider_obj = cls._providers.get("openai")
        
        if not provider_obj:
            raise ValueError(f"Could not determine provider for model '{model}'")
        
        # Create LLM instance
        return provider_obj.create_llm(model, **kwargs)
    
    @classmethod
    def get_default_models(cls, provider: str) -> Dict[str, str]:
        """Get default models for a provider"""
        cls._initialize_providers()
        provider_obj = cls.get_provider(provider)
        if provider_obj:
            return provider_obj.default_models
        return {}
    
    @classmethod
    def get_available_models(cls, provider: str) -> List[str]:
        """Get available models for a provider"""
        cls._initialize_providers()
        provider_obj = cls.get_provider(provider)
        if provider_obj:
            return provider_obj.get_available_models()
        return []


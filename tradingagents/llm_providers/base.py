"""Base classes for LLM provider abstraction."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standardized LLM response format"""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None  # tokens, prompt_tokens, completion_tokens
    metadata: Optional[Dict[str, Any]] = None


class BaseLLM(ABC):
    """Base class for all LLM implementations - LangChain compatible interface"""
    
    def __init__(self, model: str, **kwargs):
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    def invoke(self, messages: Union[str, List[Dict[str, str]]], **kwargs) -> LLMResponse:
        """
        Invoke the LLM with messages.
        
        Args:
            messages: Can be a string (single prompt) or list of message dicts
                     with 'role' and 'content' keys
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            LLMResponse object
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name"""
        pass


class LLMProvider(ABC):
    """Provider factory and configuration"""
    
    @abstractmethod
    def create_llm(self, model: str, **kwargs) -> BaseLLM:
        """Create an LLM instance"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models from this provider"""
        pass
    
    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """Check if a model is available from this provider"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name"""
        pass
    
    @property
    @abstractmethod
    def default_models(self) -> Dict[str, str]:
        """Return default models (deep_think, quick_think)"""
        pass


"""Anthropic (Claude) provider implementation."""

from typing import List, Dict, Any, Union
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel

from .base import BaseLLM, LLMProvider, LLMResponse
from ..dataflows.config import get_api_key


try:
    from langchain_anthropic import ChatAnthropic
    LANGCHAIN_ANTHROPIC_AVAILABLE = True
except ImportError:
    LANGCHAIN_ANTHROPIC_AVAILABLE = False


class AnthropicLLM(BaseLLM):
    """Anthropic Claude LLM wrapper"""
    
    def __init__(self, model: str, api_key: str = None, **kwargs):
        super().__init__(model, **kwargs)
        self.api_key = api_key or get_api_key("anthropic_api_key", "ANTHROPIC_API_KEY")
        
        if not LANGCHAIN_ANTHROPIC_AVAILABLE:
            raise ImportError("langchain-anthropic is required. Install with: pip install langchain-anthropic")
        
        # Initialize LangChain ChatAnthropic
        self._llm = ChatAnthropic(
            model=model,
            anthropic_api_key=self.api_key,
            **kwargs
        )
    
    @property
    def provider_name(self) -> str:
        return "anthropic"
    
    def invoke(self, messages: Union[str, List[Dict[str, str]]], **kwargs) -> LLMResponse:
        """Invoke Anthropic LLM"""
        # Convert string to messages format
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # Convert to LangChain format
        langchain_messages = []
        system_message = None
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                system_message = content  # Anthropic handles system messages separately
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
        
        # Invoke LangChain LLM
        invoke_kwargs = kwargs.copy()
        if system_message:
            invoke_kwargs['system'] = system_message
        
        response = self._llm.invoke(langchain_messages, **invoke_kwargs)
        
        # Extract content
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Extract usage if available
        usage = None
        if hasattr(response, 'response_metadata'):
            usage = response.response_metadata.get('usage', {})
        
        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.provider_name,
            usage=usage,
            metadata={"raw_response": str(response)}
        )
    
    # LangChain compatibility
    @property
    def llm(self) -> BaseChatModel:
        """Return underlying LangChain LLM for direct use"""
        return self._llm


class AnthropicProvider(LLMProvider):
    """Anthropic provider factory"""
    
    @property
    def provider_name(self) -> str:
        return "anthropic"
    
    @property
    def default_models(self) -> Dict[str, str]:
        return {
            "deep_think": "claude-3-5-sonnet",  # Use version without date for latest
            "quick_think": "claude-3-5-haiku",  # Use version without date for latest
            "embedding": None  # Anthropic doesn't have separate embeddings
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of Anthropic models"""
        return [
            # Claude 3.5 series (latest versions - recommended)
            "claude-3-5-sonnet",
            "claude-3-5-haiku",
            # Claude 3.5 series (dated versions - may not be available)
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            # Claude 3 series
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]
    
    def validate_model(self, model: str) -> bool:
        """Check if model is a valid Anthropic model"""
        return model in self.get_available_models()
    
    def create_llm(self, model: str, api_key: str = None, **kwargs) -> AnthropicLLM:
        """Create Anthropic LLM instance"""
        return AnthropicLLM(model=model, api_key=api_key, **kwargs)


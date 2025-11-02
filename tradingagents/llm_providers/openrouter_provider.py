"""OpenRouter provider implementation - unified access to multiple LLM models."""

from typing import List, Dict, Any, Union, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel

from .base import BaseLLM, LLMProvider, LLMResponse
from ..dataflows.config import get_api_key


try:
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class OpenRouterLLM(BaseLLM):
    """OpenRouter LLM wrapper - uses OpenAI-compatible API with model routing"""
    
    def __init__(self, model: str, api_key: str = None, base_url: str = None, **kwargs):
        super().__init__(model, **kwargs)
        self.api_key = api_key or get_api_key("openrouter_api_key", "OPENROUTER_API_KEY")
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("langchain-openai is required for OpenRouter provider")
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
        
        # OpenRouter uses OpenAI-compatible API, so we can use ChatOpenAI
        # OpenRouter supports optional HTTP headers for tracking
        # Note: LangChain's ChatOpenAI may not support default_headers directly,
        # but OpenRouter works without them too
        
        # Create client with OpenRouter base URL
        # Headers can be added via environment variables if needed
        self._llm = ChatOpenAI(
            model=model,
            openai_api_key=self.api_key,
            base_url=self.base_url,
            **kwargs
        )
        
        # Note: OpenRouter accepts HTTP-Referer and X-Title headers for analytics
        # These can be set via environment variables if needed:
        # OPENROUTER_HTTP_REFERER=https://github.com/asmaamohamed0264/AlpacaTradingAgent
        # OPENROUTER_X_TITLE=AlpacaTradingAgent
    
    @property
    def provider_name(self) -> str:
        return "openrouter"
    
    def invoke(self, messages: Union[str, List[Dict[str, str]]], **kwargs) -> LLMResponse:
        """Invoke OpenRouter LLM"""
        # Convert string to messages format
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # Convert to LangChain format
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
        
        # Invoke LLM
        response = self._llm.invoke(langchain_messages, **kwargs)
        
        # Extract content
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Extract usage if available
        usage = None
        if hasattr(response, 'response_metadata'):
            usage = response.response_metadata.get('token_usage', {})
        
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


class OpenRouterProvider(LLMProvider):
    """OpenRouter provider factory - unified access to 100+ models"""
    
    @property
    def provider_name(self) -> str:
        return "openrouter"
    
    @property
    def default_models(self) -> Dict[str, str]:
        return {
            "deep_think": "anthropic/claude-3.5-sonnet",
            "quick_think": "openai/gpt-4o-mini",
            "embedding": None  # OpenRouter may have embeddings, check their API
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of popular OpenRouter models"""
        return [
            # OpenAI models
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "openai/gpt-4-turbo",
            "openai/gpt-3.5-turbo",
            # Anthropic models
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3.5-haiku",
            "anthropic/claude-3-opus",
            # Google models
            "google/gemini-pro-1.5",
            "google/gemini-flash-1.5",
            # DeepSeek models
            "deepseek/deepseek-chat",
            "deepseek/deepseek-coder",
            # Mistral models
            "mistralai/mixtral-8x7b-instruct",
            "mistralai/mistral-large",
            # Meta models
            "meta-llama/llama-3-70b-instruct",
            "meta-llama/llama-3-8b-instruct",
            # Other popular models
            "perplexity/llama-3-sonar-large-32k-online",
            "qwen/qwen-2.5-72b-instruct",
            "x-ai/grok-beta",
        ]
    
    def validate_model(self, model: str) -> bool:
        """Check if model format is valid for OpenRouter"""
        # OpenRouter models are in format "provider/model-name" or "provider:model-name"
        # Accept both formats and let OpenRouter handle validation
        if "/" in model or ":" in model:
            return True
        # Also accept standalone model names that might be OpenRouter compatible
        return True  # Let OpenRouter API handle validation
    
    def create_llm(self, model: str, api_key: str = None, base_url: str = None, **kwargs) -> OpenRouterLLM:
        """Create OpenRouter LLM instance"""
        # Normalize model name if needed
        # OpenRouter uses format "provider/model-name" (e.g., "openai/gpt-4o-mini")
        # If user provides just model name, try to infer provider
        if "/" not in model and ":" not in model:
            # Try to auto-detect provider from model name
            if any(prefix in model for prefix in ["gpt", "o3", "o4"]):
                model = f"openai/{model}"
            elif any(prefix in model for prefix in ["claude"]):
                model = f"anthropic/{model}"
            elif any(prefix in model for prefix in ["deepseek"]):
                model = f"deepseek/{model}"
            elif any(prefix in model for prefix in ["gemini"]):
                model = f"google/{model}"
            else:
                # Default to OpenAI format
                model = f"openai/{model}"
        
        # Replace colon with slash for consistency
        if ":" in model:
            model = model.replace(":", "/")
        
        return OpenRouterLLM(model=model, api_key=api_key, base_url=base_url, **kwargs)


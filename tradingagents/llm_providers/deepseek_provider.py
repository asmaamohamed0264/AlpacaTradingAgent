"""DeepSeek provider implementation."""

from typing import List, Dict, Any, Union
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel

from .base import BaseLLM, LLMProvider, LLMResponse
from ..dataflows.config import get_api_key


try:
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class DeepSeekLLM(BaseLLM):
    """DeepSeek LLM wrapper - uses OpenAI-compatible API"""
    
    def __init__(self, model: str, api_key: str = None, base_url: str = None, **kwargs):
        super().__init__(model, **kwargs)
        self.api_key = api_key or get_api_key("deepseek_api_key", "DEEPSEEK_API_KEY")
        self.base_url = base_url or "https://api.deepseek.com/v1"
        
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("langchain-openai is required for DeepSeek provider")
        
        # DeepSeek uses OpenAI-compatible API, so we can use ChatOpenAI
        self._llm = ChatOpenAI(
            model=model,
            openai_api_key=self.api_key,
            base_url=self.base_url,
            **kwargs
        )
    
    @property
    def provider_name(self) -> str:
        return "deepseek"
    
    def invoke(self, messages: Union[str, List[Dict[str, str]]], **kwargs) -> LLMResponse:
        """Invoke DeepSeek LLM"""
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


class DeepSeekProvider(LLMProvider):
    """DeepSeek provider factory"""
    
    @property
    def provider_name(self) -> str:
        return "deepseek"
    
    @property
    def default_models(self) -> Dict[str, str]:
        return {
            "deep_think": "deepseek-chat",
            "quick_think": "deepseek-chat",
            "embedding": None  # DeepSeek may not have embeddings
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of DeepSeek models"""
        return [
            "deepseek-chat",      # Main chat model
            "deepseek-coder",     # Code-focused model
            "deepseek-reasoner",  # Reasoning model (if available)
        ]
    
    def validate_model(self, model: str) -> bool:
        """Check if model is a valid DeepSeek model"""
        return model in self.get_available_models()
    
    def create_llm(self, model: str, api_key: str = None, base_url: str = None, **kwargs) -> DeepSeekLLM:
        """Create DeepSeek LLM instance"""
        return DeepSeekLLM(model=model, api_key=api_key, base_url=base_url, **kwargs)


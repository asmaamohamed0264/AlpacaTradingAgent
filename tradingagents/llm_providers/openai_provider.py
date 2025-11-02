"""OpenAI provider implementation."""

from typing import List, Dict, Any, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel

from .base import BaseLLM, LLMProvider, LLMResponse
from ..dataflows.config import get_api_key


class OpenAILLM(BaseLLM):
    """OpenAI LLM wrapper compatible with LangChain"""
    
    def __init__(self, model: str, api_key: str = None, **kwargs):
        super().__init__(model, **kwargs)
        self.api_key = api_key or get_api_key("openai_api_key", "OPENAI_API_KEY")
        
        # Initialize LangChain ChatOpenAI
        self._llm = ChatOpenAI(
            model=model,
            openai_api_key=self.api_key,
            **kwargs
        )
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    def invoke(self, messages: Union[str, List[Dict[str, str]]], **kwargs) -> LLMResponse:
        """Invoke OpenAI LLM"""
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
        
        # Invoke LangChain LLM
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


class OpenAIProvider(LLMProvider):
    """OpenAI provider factory"""
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    @property
    def default_models(self) -> Dict[str, str]:
        return {
            "deep_think": "o3-mini",
            "quick_think": "gpt-4o-mini",
            "embedding": "text-embedding-ada-002"
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of OpenAI models"""
        return [
            # GPT-4 series
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            # GPT-3.5 series
            "gpt-3.5-turbo",
            # O-series (reasoning)
            "o3",
            "o3-mini",
            # GPT-5 series (if available)
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
        ]
    
    def validate_model(self, model: str) -> bool:
        """Check if model is a valid OpenAI model"""
        return model in self.get_available_models()
    
    def create_llm(self, model: str, api_key: str = None, **kwargs) -> OpenAILLM:
        """Create OpenAI LLM instance"""
        return OpenAILLM(model=model, api_key=api_key, **kwargs)


"""
Runtime fallback wrapper for LLM models that catches API errors and retries with safe models.
"""

from typing import Any, List, Union
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from ..dataflows.config import get_api_key


# Safe fallback models in order of preference (widely available)
SAFE_FALLBACK_MODELS = [
    "gpt-3.5-turbo",      # Most widely available
    "gpt-4-turbo",        # Second most common
    "gpt-4o",             # Third option
]


class FallbackLLMWrapper:
    """
    Wraps a LangChain ChatModel to catch API errors and retry with safe fallback models.
    
    This wrapper catches PermissionDeniedError (403) and NotFoundError (404) at runtime
    and automatically retries with models that are more widely available.
    """
    
    def __init__(self, wrapped_llm: BaseChatModel, original_model: str, original_provider: str = "openai"):
        """
        Initialize the fallback wrapper.
        
        Args:
            wrapped_llm: The original LLM instance to wrap
            original_model: Original model name for logging
            original_provider: Provider name for logging
        """
        self._wrapped_llm = wrapped_llm
        self.original_model = original_model
        self.original_provider = original_provider
        self._fallback_llms = {}  # Cache for fallback LLMs
        self._fallback_index = 0  # Track which fallback model we're trying
    
    def _get_fallback_llm(self, model_name: str, **kwargs) -> ChatOpenAI:
        """Get or create a fallback LLM instance"""
        if model_name not in self._fallback_llms:
            api_key = get_api_key("openai_api_key", "OPENAI_API_KEY")
            # Remove temperature if model doesn't support it
            fallback_kwargs = kwargs.copy()
            no_temp_models = ["o3", "o4-mini", "gpt-5", "gpt-5-mini", "gpt-5-nano"]
            if not any(prefix in model_name for prefix in no_temp_models):
                if "temperature" not in fallback_kwargs:
                    fallback_kwargs["temperature"] = 0.2
            
            self._fallback_llms[model_name] = ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                **fallback_kwargs
            )
        return self._fallback_llms[model_name]
    
    def invoke(self, messages: Union[str, List[BaseMessage], List[dict]], config: dict = None, **kwargs):
        """
        Invoke the LLM with automatic fallback on errors.
        
        Tries the original model first, then falls back to safe models if API errors occur.
        """
        try:
            # Try original model first
            return self._wrapped_llm.invoke(messages, config=config, **kwargs)
        
        except Exception as e:
            # Check if this is a model availability error (403 or 404)
            error_str = str(e).lower()
            error_code = None
            
            # Try to extract error code from exception attributes
            if hasattr(e, 'status_code'):
                error_code = e.status_code
            elif hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                error_code = e.response.status_code
            
            # Also check for PermissionDeniedError or NotFoundError exception types
            exception_type = type(e).__name__
            if "PermissionDenied" in exception_type:
                error_code = 403
            elif "NotFound" in exception_type:
                error_code = 404
            
            # Check error string for common patterns
            if error_code is None:
                if "403" in error_str or "permission denied" in error_str or "does not have access" in error_str:
                    error_code = 403
                elif "404" in error_str or "not found" in error_str or "does not exist" in error_str:
                    error_code = 404
            
            # Check for model-related error messages
            is_model_error = (
                "model" in error_str or 
                "access" in error_str or 
                "not available" in error_str or
                "does not have access" in error_str or
                error_code in [403, 404]  # If we have a 403/404, likely model-related
            )
            
            # Only fallback for 403/404 errors related to model availability
            if error_code in [403, 404] and is_model_error:
                print(f"[LLM] ⚠️  Runtime error ({error_code}) with {self.original_provider}/{self.original_model}: {str(e)[:200]}")
                print(f"[LLM] 🔄 Attempting fallback to safe models...")
                
                # Try fallback models in order
                for fallback_model in SAFE_FALLBACK_MODELS:
                    try:
                        print(f"[LLM] 🔄 Trying fallback model: {fallback_model}")
                        fallback_llm = self._get_fallback_llm(fallback_model, **kwargs)
                        result = fallback_llm.invoke(messages, config=config, **kwargs)
                        print(f"[LLM] ✅ Successfully used fallback model: {fallback_model}")
                        return result
                    except Exception as fallback_error:
                        error_str_fb = str(fallback_error).lower()
                        if "403" in error_str_fb or "404" in error_str_fb:
                            print(f"[LLM] ⚠️  Fallback model {fallback_model} also unavailable, trying next...")
                            continue
                        else:
                            # Different error (rate limit, network, etc.) - re-raise
                            raise fallback_error
                
                # All fallbacks failed
                print(f"[LLM] ❌ All fallback models failed. Original error: {str(e)[:500]}")
                raise e
            
            else:
                # Not a model availability error - re-raise original exception
                raise e
    
    def __getattr__(self, name):
        """Delegate all other attributes to wrapped LLM"""
        return getattr(self._wrapped_llm, name)
    
    # Proxy common LangChain methods
    def stream(self, messages, **kwargs):
        """Stream method proxy"""
        try:
            return self._wrapped_llm.stream(messages, **kwargs)
        except Exception as e:
            # Fallback doesn't work with streaming, so just re-raise
            raise e
    
    def bind_tools(self, tools, **kwargs):
        """Bind tools method proxy"""
        return self._wrapped_llm.bind_tools(tools, **kwargs)
    
    def with_structured_output(self, schema, **kwargs):
        """Structured output method proxy"""
        return self._wrapped_llm.with_structured_output(schema, **kwargs)


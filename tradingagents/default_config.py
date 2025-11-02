import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    # "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_dir": "data/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "deep_think_llm": "o3-mini",
    "quick_think_llm": "gpt-4o-mini",
    # LLM Provider settings - can be "openai", "deepseek", "anthropic", "openrouter"
    # Can also use format "provider:model" (e.g., "deepseek:deepseek-chat")
    # OpenRouter models: "openrouter:anthropic/claude-3.5-sonnet" or "openrouter:openai/gpt-4o-mini"
    "llm_provider": "openai",  # Default provider
    "deep_think_provider": None,  # None = use llm_provider
    "quick_think_provider": None,  # None = use llm_provider
    # Debate and discussion settings
    "max_debate_rounds": 4,
    "max_risk_discuss_rounds": 3,
    "max_recur_limit": 200,
    # Trading settings
    "allow_shorts": False,  # False = Investment mode (BUY/HOLD/SELL), True = Trading mode (LONG/NEUTRAL/SHORT)
    # Execution settings
    "parallel_analysts": True,  # True = Run analysts in parallel for faster execution, False = Sequential execution
    # Tool settings
    "online_tools": True,
    # API keys (these will be overridden by environment variables if present)
    "openai_api_key": None,
    "deepseek_api_key": None,
    "anthropic_api_key": None,
    "openrouter_api_key": None,
    "finnhub_api_key": None,
    "alpaca_api_key": None,
    "alpaca_secret_key": None,
    "alpaca_use_paper": "True",  # Set to "True" to use paper trading, "False" for live trading
    "coindesk_api_key": None,
}

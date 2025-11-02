"""
webui/components/config_panel.py - Configuration panel for the web UI.
"""

import dash_bootstrap_components as dbc
from dash import html
from datetime import datetime

def create_config_panel():
    """Create the configuration panel for the web UI."""
    return dbc.Card(
        dbc.CardBody([
            html.H4("Analysis Configuration", className="mb-3"),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Input(
                        id="ticker-input",
                        type="text",
                        placeholder="Enter stock symbols (e.g., AAPL,NVDA)",
                        value="NVDA, AMD, TSLA",
                        className="mb-2"
                    ),
                ], width=12),
            ]),
            html.H5("Select Analysts:", className="mt-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Checkbox(id="analyst-market", label="Market Analyst", value=True, className="mb-2"),
                ], width=6),
                dbc.Col([
                    dbc.Checkbox(id="analyst-social", label="Social Media Analyst", value=True, className="mb-2"),
                ], width=6),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Checkbox(id="analyst-news", label="News Analyst", value=True, className="mb-2"),
                ], width=6),
                dbc.Col([
                    dbc.Checkbox(id="analyst-fundamentals", label="Fundamentals Analyst", value=True, className="mb-2"),
                ], width=6),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Checkbox(id="analyst-macro", label="Macro Analyst", value=True, className="mb-2"),
                ], width=6),
                dbc.Col([
                    # Empty column for alignment
                ], width=6),
            ]),
            html.H5("Research Depth:", className="mt-3"),
            # 50/50 split for research depth selection and information
            dbc.Row([
                dbc.Col([
                    dbc.RadioItems(
                        id="research-depth",
                        options=[
                            {"label": "Shallow", "value": "Shallow"},
                            {"label": "Medium", "value": "Medium"},
                            {"label": "Deep", "value": "Deep"},
                        ],
                        value="Shallow",
                        inline=False,
                        className="mb-3"
                    ),
                ], width=6),
                dbc.Col([
                    # Interactive research depth information
                    html.Div(id="research-depth-info", className="mb-3"),
                ], width=6),
            ]),
            # Execution Mode section removed - always use sequential execution
            html.H5("Trading Mode:", className="mt-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Switch(
                        id="allow-shorts",
                        label="Allow Shorts (Trading Mode)",
                        value=False,
                        className="mb-2"
                    ),
                ], width=6),
                dbc.Col([
                    html.Div(id="trading-mode-info", className="mb-3"),
                ], width=6),
            ]),
            html.H5("Scheduling Configuration:", className="mt-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Switch(
                        id="loop-enabled",
                        label="Enable Loop Mode",
                        value=False,
                        className="mb-2"
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("Loop Interval (minutes)", className="mb-1"),
                    dbc.Input(
                        id="loop-interval",
                        type="number",
                        placeholder="60",
                        value=60,
                        min=1,
                        max=1440,  # Max 24 hours
                        className="mb-2"
                    ),
                ], width=6),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Switch(
                        id="market-hour-enabled",
                        label="Trade at Market Hour",
                        value=False,
                        className="mb-2"
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("Trading Hours (e.g., 10,15 for 10AM & 3PM)", className="mb-1"),
                    dbc.Input(
                        id="market-hours-input",
                        type="text",
                        placeholder="e.g., 11,13",
                        value="",
                        className="mb-2"
                    ),
                ], width=6),
            ]),
            # Market hours validation message
            html.Div(id="market-hours-validation", className="mb-2"),
            # Add scheduling mode information display
            html.Div(id="scheduling-mode-info", className="mb-3"),
            html.H5("Automated Trading:", className="mt-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Switch(
                        id="trade-after-analyze",
                        label="Trade After Analyze",
                        value=False,
                        className="mb-2"
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("Order Amount ($)", className="mb-1"),
                    dbc.Input(
                        id="trade-dollar-amount",
                        type="number",
                        placeholder="4500",
                        value=4500,
                        min=1,
                        max=10000000,
                        className="mb-2"
                    ),
                ], width=6),
            ]),
            # Add trading mode information display
            html.Div(id="trade-after-analyze-info", className="mb-3"),
            html.H5("LLM Quick Thinker Model:", className="mt-3"),
            dbc.Select(
                id="quick-llm",
                options=[
                    # OpenAI Models
                    {"label": "🤖 OpenAI - gpt-5", "value": "gpt-5"},
                    {"label": "🤖 OpenAI - gpt-5-mini", "value": "gpt-5-mini"},
                    {"label": "🤖 OpenAI - gpt-5-nano", "value": "gpt-5-nano"},
                    {"label": "🤖 OpenAI - gpt-4.1", "value": "gpt-4.1"},
                    {"label": "🤖 OpenAI - gpt-4.1-nano", "value": "gpt-4.1-nano"},
                    {"label": "🤖 OpenAI - gpt-4.1-mini", "value": "gpt-4.1-mini"},
                    {"label": "🤖 OpenAI - gpt-4o", "value": "gpt-4o"},
                    {"label": "🤖 OpenAI - gpt-4o-mini", "value": "gpt-4o-mini"},
                    {"label": "🤖 OpenAI - o3-mini", "value": "o3-mini"},
                    {"label": "🤖 OpenAI - o3", "value": "o3"},
                    {"label": "🤖 OpenAI - o1", "value": "o1"},
                    # DeepSeek Models
                    {"label": "💎 DeepSeek - deepseek-chat", "value": "deepseek:deepseek-chat"},
                    {"label": "💎 DeepSeek - deepseek-coder", "value": "deepseek:deepseek-coder"},
                    # OpenRouter Models (via OpenRouter)
                    {"label": "🌐 OpenRouter - OpenAI gpt-4o-mini", "value": "openrouter:openai/gpt-4o-mini"},
                    {"label": "🌐 OpenRouter - OpenAI gpt-4o", "value": "openrouter:openai/gpt-4o"},
                    {"label": "🌐 OpenRouter - Claude 3.5 Haiku", "value": "openrouter:anthropic/claude-3.5-haiku"},
                    {"label": "🌐 OpenRouter - Claude 3.5 Sonnet", "value": "openrouter:anthropic/claude-3.5-sonnet"},
                    {"label": "🌐 OpenRouter - Google Gemini Flash", "value": "openrouter:google/gemini-flash-1.5"},
                    {"label": "🌐 OpenRouter - Google Gemini Pro", "value": "openrouter:google/gemini-pro-1.5"},
                    {"label": "🌐 OpenRouter - DeepSeek Chat", "value": "openrouter:deepseek/deepseek-chat"},
                    # Anthropic Models (direct) - Use latest versions first
                    {"label": "🔷 Anthropic - Claude 3.5 Sonnet (latest)", "value": "anthropic:claude-3-5-sonnet"},
                    {"label": "🔷 Anthropic - Claude 3.5 Haiku (latest)", "value": "anthropic:claude-3-5-haiku"},
                    {"label": "🔷 Anthropic - Claude 3.5 Sonnet (dated)", "value": "anthropic:claude-3-5-sonnet-20241022"},
                    {"label": "🔷 Anthropic - Claude 3.5 Haiku (dated)", "value": "anthropic:claude-3-5-haiku-20241022"},
                ],
                value="gpt-4o-mini",
                className="mb-2"
            ),
            html.P([
                "💡 Tip: Selectează un model cu provider prefix (ex: 'deepseek:deepseek-chat') pentru a folosi acel provider. ",
                "Modelele fără prefix vor folosi provider-ul default (setat în Environment Settings)."
            ], className="text-muted small mb-3"),
            html.H5("LLM Deep Thinker Model:", className="mt-3"),
            dbc.Select(
                id="deep-llm",
                options=[
                    # OpenAI Models
                    {"label": "🤖 OpenAI - gpt-5", "value": "gpt-5"},
                    {"label": "🤖 OpenAI - gpt-5-mini", "value": "gpt-5-mini"},
                    {"label": "🤖 OpenAI - gpt-5-nano", "value": "gpt-5-nano"},
                    {"label": "🤖 OpenAI - gpt-4.1", "value": "gpt-4.1"},
                    {"label": "🤖 OpenAI - gpt-4o", "value": "gpt-4o"},
                    {"label": "🤖 OpenAI - o3-mini", "value": "o3-mini"},
                    {"label": "🤖 OpenAI - o3", "value": "o3"},
                    {"label": "🤖 OpenAI - o1", "value": "o1"},
                    # DeepSeek Models
                    {"label": "💎 DeepSeek - deepseek-chat", "value": "deepseek:deepseek-chat"},
                    {"label": "💎 DeepSeek - deepseek-coder", "value": "deepseek:deepseek-coder"},
                    # OpenRouter Models (via OpenRouter)
                    {"label": "🌐 OpenRouter - Claude 3.5 Sonnet", "value": "openrouter:anthropic/claude-3.5-sonnet"},
                    {"label": "🌐 OpenRouter - Claude 3.5 Haiku", "value": "openrouter:anthropic/claude-3.5-haiku"},
                    {"label": "🌐 OpenRouter - OpenAI gpt-4o", "value": "openrouter:openai/gpt-4o"},
                    {"label": "🌐 OpenRouter - OpenAI o3-mini", "value": "openrouter:openai/o3-mini"},
                    {"label": "🌐 OpenRouter - Google Gemini Pro", "value": "openrouter:google/gemini-pro-1.5"},
                    # Anthropic Models (direct) - Use latest versions first
                    {"label": "🔷 Anthropic - Claude 3.5 Sonnet (latest)", "value": "anthropic:claude-3-5-sonnet"},
                    {"label": "🔷 Anthropic - Claude 3.5 Haiku (latest)", "value": "anthropic:claude-3-5-haiku"},
                    {"label": "🔷 Anthropic - Claude 3.5 Sonnet (dated)", "value": "anthropic:claude-3-5-sonnet-20241022"},
                    {"label": "🔷 Anthropic - Claude 3.5 Haiku (dated)", "value": "anthropic:claude-3-5-haiku-20241022"},
                ],
                value="gpt-4o-mini",
                className="mb-3"
            ),
            # Dynamic Start/Stop button
            html.Div(id="control-button-container", children=[
                dbc.Button(
                    "Start Analysis",
                    id="control-btn",
                    color="primary",
                    size="lg",
                    className="w-100 mt-2"
                )
            ]),
            html.Div(id="result-text", className="mt-3")
        ]),
        className="mb-4",
    ) 

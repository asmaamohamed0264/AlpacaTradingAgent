from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from typing import List
from typing import Annotated
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import RemoveMessage
from langchain_core.tools import tool
from datetime import date, timedelta, datetime
import functools
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from langchain_openai import ChatOpenAI
import tradingagents.dataflows.interface as interface
from tradingagents.default_config import DEFAULT_CONFIG
import json
import time
from functools import wraps


def timing_wrapper(analyst_type):
    """Decorator to time function calls and track them for UI display"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Start timing
            start_time = time.time()
            
            # Get the function (tool) name
            tool_name = func.__name__
            
            # Format tool inputs for display
            input_summary = {}
            
            # Get function signature to map args to parameter names
            import inspect
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())
            
            # Map positional args to parameter names
            for i, arg in enumerate(args):
                if i < len(param_names):
                    param_name = param_names[i]
                    # Truncate long string arguments for display
                    if isinstance(arg, str) and len(arg) > 100:
                        input_summary[param_name] = arg[:97] + "..."
                    else:
                        input_summary[param_name] = arg
            
            # Add keyword arguments
            for key, value in kwargs.items():
                if isinstance(value, str) and len(value) > 100:
                    input_summary[key] = value[:97] + "..."
                else:
                    input_summary[key] = value

            print(f"[{analyst_type}] 🔧 Starting tool '{tool_name}' with inputs: {input_summary}")
            
            # Notify the state management system of tool call execution
            try:
                from webui.utils.state import app_state
                import datetime
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                
                # Execute the original function first to get the result
                result = func(*args, **kwargs)
                
                # Calculate execution time
                elapsed = time.time() - start_time
                print(f"[{analyst_type}] ✅ Tool '{tool_name}' completed in {elapsed:.2f}s")
                
                # Format the result for display (truncate if too long)
                result_summary = result
                
                # Store the complete tool call information including the output
                # Get current symbol from app_state for filtering
                current_symbol = getattr(app_state, 'analyzing_symbol', None) or getattr(app_state, 'current_symbol', None)
                
                tool_call_info = {
                    "timestamp": timestamp,
                    "tool_name": tool_name,
                    "inputs": input_summary,
                    "output": result_summary,
                    "execution_time": f"{elapsed:.2f}s",
                    "status": "success",
                    "agent_type": analyst_type,  # Add agent type for filtering
                    "symbol": current_symbol  # Add symbol for filtering
                }
                
                app_state.tool_calls_log.append(tool_call_info)
                app_state.tool_calls_count = len(app_state.tool_calls_log)
                app_state.needs_ui_update = True
                print(f"[TOOL TRACKER] Registered tool call: {tool_name} for {analyst_type} (Total: {app_state.tool_calls_count})")
                
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"[{analyst_type}] ❌ Tool '{tool_name}' failed after {elapsed:.2f}s: {str(e)}")
                
                # Store the failed tool call information
                try:
                    from webui.utils.state import app_state
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    
                    # Get current symbol from app_state for filtering
                    current_symbol = getattr(app_state, 'analyzing_symbol', None) or getattr(app_state, 'current_symbol', None)
                    
                    tool_call_info = {
                        "timestamp": timestamp,
                        "tool_name": tool_name,
                        "inputs": input_summary,
                        "output": f"ERROR: {str(e)}",
                        "execution_time": f"{elapsed:.2f}s",
                        "status": "error",
                        "agent_type": analyst_type,  # Add agent type for filtering
                        "symbol": current_symbol  # Add symbol for filtering
                    }
                    
                    app_state.tool_calls_log.append(tool_call_info)
                    app_state.tool_calls_count = len(app_state.tool_calls_log)
                    app_state.needs_ui_update = True
                    print(f"[TOOL TRACKER] Registered failed tool call: {tool_name} for {analyst_type} (Total: {app_state.tool_calls_count})")
                except Exception as track_error:
                    print(f"[TOOL TRACKER] Failed to track failed tool call: {track_error}")
                
                raise  # Re-raise the exception
                
        return wrapper
    return decorator


def create_msg_delete():
    def delete_messages(state):
        """To prevent message history from overflowing, regularly clear message history after a stage of the pipeline is done"""
        messages = state["messages"]
        return {"messages": [RemoveMessage(id=m.id) for m in messages]}

    return delete_messages


class Toolkit:
    _config = DEFAULT_CONFIG.copy()

    @classmethod
    def update_config(cls, config):
        """Update the class-level configuration."""
        cls._config.update(config)

    @property
    def config(self):
        """Access the configuration."""
        return self._config

    def __init__(self, config=None):
        if config:
            self.update_config(config)

    @staticmethod
    @tool
    @timing_wrapper("NEWS")
    def get_reddit_news(
        curr_date: Annotated[str, "Date you want to get news for in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve global news from Reddit within a specified time frame.
        Args:
            curr_date (str): Date you want to get news for in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing the latest global news from Reddit in the specified time frame.
        """
        
        global_news_result = interface.get_reddit_global_news(curr_date, 7, 5)

        return global_news_result

    @staticmethod
    @tool
    @timing_wrapper("NEWS")
    def get_finnhub_news(
        ticker: Annotated[
            str,
            "Search query of a company, e.g. 'AAPL, TSM, etc.",
        ],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news about a given stock from Finnhub within a date range
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing news about the company within the date range from start_date to end_date
        """

        end_date_str = end_date

        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        look_back_days = (end_date - start_date).days

        finnhub_news_result = interface.get_finnhub_news(
            ticker, end_date_str, look_back_days
        )

        return finnhub_news_result

    @staticmethod
    @tool
    @timing_wrapper("SOCIAL")
    def get_reddit_stock_info(
        ticker: Annotated[
            str,
            "Ticker of a company. e.g. AAPL, TSM",
        ],
        curr_date: Annotated[str, "Current date you want to get news for"],
    ) -> str:
        """
        Retrieve the latest news about a given stock from Reddit, given the current date.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): current date in yyyy-mm-dd format to get news for
        Returns:
            str: A formatted dataframe containing the latest news about the company on the given date
        """

        stock_news_results = interface.get_reddit_company_news(ticker, curr_date, 7, 5)

        return stock_news_results

    @staticmethod
    @tool
    @timing_wrapper("MARKET")
    def get_alpaca_data(
        symbol: Annotated[str, "ticker symbol of the company"],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
        timeframe: Annotated[str, "Timeframe for data: 1Min, 5Min, 15Min, 1Hour, 1Day"] = "1Day",
    ) -> str:
        """
        Retrieve the stock price data for a given ticker symbol from Alpaca.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
            timeframe (str): Timeframe for data (1Min, 5Min, 15Min, 1Hour, 1Day)
        Returns:
            str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
        """

        result_data = interface.get_alpaca_data(symbol, start_date, end_date, timeframe)

        return result_data

    @staticmethod
    @tool
    @timing_wrapper("MARKET")
    def get_stockstats_indicators_report(
        symbol: Annotated[str, "ticker symbol of the company"],
        indicator: Annotated[
            str, "technical indicator to get the analysis and report of"
        ],
        curr_date: Annotated[
            str, "The current trading date you are trading on, YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "how many days to look back"] = 30,
    ) -> str:
        """
        Retrieve stock stats indicators for a given ticker symbol and indicator.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            indicator (str): Technical indicator to get the analysis and report of
            curr_date (str): The current trading date you are trading on, YYYY-mm-dd
            look_back_days (int): How many days to look back, default is 30
        Returns:
            str: A formatted dataframe containing the stock stats indicators for the specified ticker symbol and indicator.
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, False
        )

        return result_stockstats

    @staticmethod
    @tool
    @timing_wrapper("MARKET")
    def get_stockstats_indicators_report_online(
        symbol: Annotated[str, "ticker symbol of the company"],
        indicator: Annotated[
            str, "technical indicator to get the analysis and report of"
        ],
        curr_date: Annotated[
            str, "The current trading date you are trading on, YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "how many days to look back"] = 30,
    ) -> str:
        """
        Retrieve stock stats indicators for a given ticker symbol and indicator.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            indicator (str): Technical indicator to get the analysis and report of, or 'all' for comprehensive report
            curr_date (str): The current trading date you are trading on, YYYY-mm-dd
            look_back_days (int): How many days to look back, default is 30
        Returns:
            str: A formatted report containing the stock stats indicators for the specified ticker symbol and indicator.
        """

        if indicator.lower() == 'all':
            # Handle comprehensive indicator report
            key_indicators = [
                'close_10_ema',     # 10-day Exponential Moving Average
                'close_20_sma',     # 20-day Simple Moving Average  
                'close_50_sma',     # 50-day Simple Moving Average
                'rsi_14',           # 14-day Relative Strength Index
                'macd',             # Moving Average Convergence Divergence
                'boll_ub',          # Bollinger Bands Upper Band
                'boll_lb',          # Bollinger Bands Lower Band
                'volume_delta'      # Volume Delta
            ]
            
            results = []
            results.append(f"# Comprehensive Technical Indicators Report for {symbol} on {curr_date}")
            results.append("")
            
            for ind in key_indicators:
                try:
                    result = interface.get_stockstats_indicator(symbol, ind, curr_date, True)
                    # Clean up the result format
                    if result.startswith(f"## {ind} for"):
                        # Extract just the value part
                        value_part = result.split(": ")[-1]
                        indicator_name = ind.replace('_', ' ').title()
                        results.append(f"**{indicator_name}:** {value_part}")
                    else:
                        results.append(f"**{ind}:** {result}")
                except Exception as e:
                    results.append(f"**{ind}:** Error - {str(e)}")
            
            results.append("")
            results.append("## EOD Trading Analysis")
            results.append("These indicators provide key signals for end-of-day trading decisions:")
            results.append("- **EMAs/SMAs:** Trend direction and support/resistance levels")
            results.append("- **RSI:** Overbought (>70) or oversold (<30) conditions")  
            results.append("- **MACD:** Momentum and trend change signals")
            results.append("- **Bollinger Bands:** Volatility and price extremes")
            
            return "\n".join(results)
        else:
            # For single indicator, use the existing method
            result_stockstats = interface.get_stockstats_indicator(
                symbol, indicator, curr_date, True
            )
            return result_stockstats

    @staticmethod
    @tool
    @timing_wrapper("FUNDAMENTALS")
    def get_finnhub_company_insider_sentiment(
        ticker: Annotated[str, "ticker symbol for the company"],
        curr_date: Annotated[
            str,
            "current date of you are trading at, yyyy-mm-dd",
        ],
    ):
        """
        Retrieve insider sentiment information about a company (retrieved from public SEC information) for the past 30 days
        Args:
            ticker (str): ticker symbol of the company
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the sentiment in the past 30 days starting at curr_date
        """

        data_sentiment = interface.get_finnhub_company_insider_sentiment(
            ticker, curr_date, 30
        )

        return data_sentiment

    @staticmethod
    @tool
    @timing_wrapper("FUNDAMENTALS")
    def get_finnhub_company_insider_transactions(
        ticker: Annotated[str, "ticker symbol"],
        curr_date: Annotated[
            str,
            "current date you are trading at, yyyy-mm-dd",
        ],
    ):
        """
        Retrieve insider transaction information about a company (retrieved from public SEC information) for the past 30 days
        Args:
            ticker (str): ticker symbol of the company
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the company's insider transactions/trading information in the past 30 days
        """

        data_trans = interface.get_finnhub_company_insider_transactions(
            ticker, curr_date, 30
        )

        return data_trans

    @staticmethod
    @tool
    @timing_wrapper("FUNDAMENTALS")
    def get_simfin_balance_sheet(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency of the company's financial history: annual/quarterly",
        ],
        curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
    ):
        """
        Retrieve the most recent balance sheet of a company
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency of the company's financial history: annual / quarterly
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the company's most recent balance sheet
        """

        data_balance_sheet = interface.get_simfin_balance_sheet(ticker, freq, curr_date)

        return data_balance_sheet

    @staticmethod
    @tool
    @timing_wrapper("FUNDAMENTALS")
    def get_simfin_cashflow(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency of the company's financial history: annual/quarterly",
        ],
        curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
    ):
        """
        Retrieve the most recent cash flow statement of a company
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency of the company's financial history: annual / quarterly
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
                str: a report of the company's most recent cash flow statement
        """

        data_cashflow = interface.get_simfin_cashflow(ticker, freq, curr_date)

        return data_cashflow

    @staticmethod
    @tool
    def get_coindesk_news(
        ticker: Annotated[str, "Ticker symbol, e.g. 'BTCUSD', 'ETH', etc."],
        num_sentences: Annotated[int, "Number of sentences to include from news body."] = 5,
    ):
        """
        Retrieve news for a cryptocurrency.
        This function checks if the ticker is a crypto pair (like BTCUSD) and extracts the base currency.
        Then it fetches news for that cryptocurrency from CryptoCompare.

        Args:
            ticker (str): Ticker symbol for the cryptocurrency.
            num_sentences (int): Number of sentences to extract from the body of each news article.

        Returns:
            str: Formatted string containing news.
        """
        return interface.get_coindesk_news(ticker, num_sentences)

    @staticmethod
    @tool
    @timing_wrapper("FUNDAMENTALS")
    def get_simfin_income_stmt(
        ticker: Annotated[str, "ticker symbol"],
        freq: Annotated[
            str,
            "reporting frequency of the company's financial history: annual/quarterly",
        ],
        curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
    ):
        """
        Retrieve the most recent income statement of a company
        Args:
            ticker (str): ticker symbol of the company
            freq (str): reporting frequency of the company's financial history: annual / quarterly
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
                str: a report of the company's most recent income statement
        """

        data_income_stmt = interface.get_simfin_income_statements(
            ticker, freq, curr_date
        )

        return data_income_stmt

    @staticmethod
    @tool
    @timing_wrapper("NEWS")
    def get_google_news(
        query: Annotated[str, "Query to search with"],
        curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news from Google News based on a query and date range.
        Args:
            query (str): Query to search with
            curr_date (str): Current date in yyyy-mm-dd format
            look_back_days (int): How many days to look back
        Returns:
            str: A formatted string containing the latest news from Google News based on the query and date range.
        """

        google_news_results = interface.get_google_news(query, curr_date, 7)

        return google_news_results

    @staticmethod
    @tool
    @timing_wrapper("SOCIAL")
    def get_stock_news_openai(
        ticker: Annotated[str, "the company's ticker"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news about a given stock by using OpenAI's news API.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest news about the company on the given date.
        """

        openai_news_results = interface.get_stock_news_openai(ticker, curr_date)

        return openai_news_results

    @staticmethod
    @tool
    @timing_wrapper("NEWS")
    def get_global_news_openai(
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest macroeconomics news on a given date using OpenAI's macroeconomics news API.
        Args:
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest macroeconomic news on the given date.
        """

        openai_news_results = interface.get_global_news_openai(curr_date)

        return openai_news_results

    @staticmethod
    @tool
    @timing_wrapper("FUNDAMENTALS")
    def get_fundamentals_openai(
        ticker: Annotated[str, "the company's ticker"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest fundamental information about a given stock on a given date by using OpenAI's news API.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): Current date in yyyy-mm-dd format
        Returns:
            str: A formatted string containing the latest fundamental information about the company on the given date.
        """

        openai_fundamentals_results = interface.get_fundamentals_openai(
            ticker, curr_date
        )

        return openai_fundamentals_results

    @staticmethod
    @tool
    @timing_wrapper("FUNDAMENTALS")
    def get_earnings_calendar(
        ticker: Annotated[str, "Stock or crypto ticker symbol"],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve earnings calendar data for stocks or major events for crypto.
        For stocks: Shows earnings dates, EPS estimates vs actuals, revenue estimates vs actuals, and surprise analysis.
        For crypto: Shows major protocol events, upgrades, and announcements that could impact price.
        
        Args:
            ticker (str): Stock ticker (e.g. AAPL, TSLA) or crypto ticker (e.g. BTCUSD, ETH, SOL)
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
            
        Returns:
            str: Formatted earnings calendar data with estimates, actuals, and surprise analysis
        """
        
        earnings_calendar_results = interface.get_earnings_calendar(
            ticker, start_date, end_date
        )
        
        return earnings_calendar_results

    @staticmethod
    @tool
    @timing_wrapper("FUNDAMENTALS")
    def get_earnings_surprise_analysis(
        ticker: Annotated[str, "Stock ticker symbol"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
        lookback_quarters: Annotated[int, "Number of quarters to analyze"] = 8,
    ) -> str:
        """
        Analyze historical earnings surprises to identify patterns and trading implications.
        Shows consistency of beats/misses, magnitude of surprises, and seasonal patterns.
        
        Args:
            ticker (str): Stock ticker symbol, e.g. AAPL, TSLA
            curr_date (str): Current date in yyyy-mm-dd format
            lookback_quarters (int): Number of quarters to analyze (default 8 = ~2 years)
            
        Returns:
            str: Analysis of earnings surprise patterns with trading implications
        """
        
        earnings_surprise_results = interface.get_earnings_surprise_analysis(
            ticker, curr_date, lookback_quarters
        )
        
        return earnings_surprise_results

    @staticmethod
    @tool
    @timing_wrapper("MACRO")
    def get_macro_analysis(
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
        lookback_days: Annotated[int, "Number of days to look back for data"] = 90,
    ) -> str:
        """
        Retrieve comprehensive macro economic analysis including Fed funds, CPI, PPI, NFP, GDP, PMI, Treasury curve, VIX.
        Provides economic indicators, yield curve analysis, and Fed policy updates with trading implications.
        
        Args:
            curr_date (str): Current date in yyyy-mm-dd format
            lookback_days (int): Number of days to look back for data (default 90)
            
        Returns:
            str: Comprehensive macro economic analysis with trading implications
        """
        
        macro_analysis_results = interface.get_macro_analysis(
            curr_date, lookback_days
        )
        
        return macro_analysis_results

    @staticmethod
    @tool
    def get_economic_indicators(
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
        lookback_days: Annotated[int, "Number of days to look back for data"] = 90,
    ) -> str:
        """
        Retrieve key economic indicators report including Fed funds, CPI, PPI, unemployment, NFP, GDP, PMI, VIX.
        
        Args:
            curr_date (str): Current date in yyyy-mm-dd format
            lookback_days (int): Number of days to look back for data (default 90)
            
        Returns:
            str: Economic indicators report with analysis and interpretations
        """
        
        economic_indicators_results = interface.get_economic_indicators(
            curr_date, lookback_days
        )
        
        return economic_indicators_results

    @staticmethod
    @tool
    def get_yield_curve_analysis(
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve Treasury yield curve analysis including inversion signals and recession indicators.
        
        Args:
            curr_date (str): Current date in yyyy-mm-dd format
            
        Returns:
            str: Treasury yield curve data with inversion analysis
        """
        
        yield_curve_results = interface.get_yield_curve_analysis(curr_date)
        
        return yield_curve_results

    @staticmethod
    @tool
    @timing_wrapper("FUNDAMENTALS")
    def get_defillama_fundamentals(
        ticker: Annotated[str, "Crypto ticker symbol (without USD/USDT suffix)"],
        lookback_days: Annotated[int, "Number of days to look back for data"] = 30,
    ):
        """
        Retrieve fundamental data for a cryptocurrency from DeFi Llama.
        This includes TVL (Total Value Locked), TVL change over lookback period,
        fees collected, and revenue data.
        
        Args:
            ticker (str): Crypto ticker symbol (e.g., BTC, ETH, UNI)
            lookback_days (int): Number of days to look back for data
            
        Returns:
            str: A markdown-formatted report of crypto fundamentals from DeFi Llama
        """
        
        defillama_results = interface.get_defillama_fundamentals(
            ticker, lookback_days
        )
        
        return defillama_results

    @staticmethod
    @tool
    def get_alpaca_data_report(
        symbol: Annotated[str, "ticker symbol of the company"],
        curr_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        look_back_days: Annotated[int, "how many days to look back"],
        timeframe: Annotated[str, "Timeframe for data: 1Min, 5Min, 15Min, 1Hour, 1Day"] = "1Day",
    ) -> str:
        """
        Retrieve Alpaca data for a given ticker symbol.
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
            curr_date (str): The current trading date in YYYY-mm-dd format
            look_back_days (int): How many days to look back
            timeframe (str): Timeframe for data (1Min, 5Min, 15Min, 1Hour, 1Day)
        Returns:
            str: A formatted dataframe containing the Alpaca data for the specified ticker symbol.
        """

        result_alpaca = interface.get_alpaca_data_window(
            symbol, curr_date, look_back_days, timeframe
        )

        return result_alpaca

    @staticmethod
    @tool
    @timing_wrapper("MARKET")
    def get_stock_data_table(
        symbol: Annotated[str, "ticker symbol of the company"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
        look_back_days: Annotated[int, "how many days to look back"] = 90,
        timeframe: Annotated[str, "Timeframe for data: 1Min, 5Min, 15Min, 1Hour, 1Day"] = "1Day",
    ) -> str:
        """
        Retrieve comprehensive stock data table for a given ticker symbol over a lookback period.
        Returns a clean table with Date, Open, High, Low, Close, Volume, VWAP columns for EOD trading analysis.
        
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, NVDA
            curr_date (str): The current trading date in YYYY-mm-dd format
            look_back_days (int): How many days to look back (default 60)
            timeframe (str): Timeframe for data (1Min, 5Min, 15Min, 1Hour, 1Day)
            
        Returns:
            str: A comprehensive table containing Date, OHLCV, VWAP data for the lookback period
        """

        # Get the raw data from the interface
        raw_result = interface.get_alpaca_data_window(
            symbol, curr_date, look_back_days, timeframe
        )
        
        # Parse and reformat the timestamp column to be more readable
        import re
        
        try:
            # Use regex to replace complex timestamps with simple dates
            # Pattern: 2025-07-08 04:00:00+00:00 -> 2025-07-08
            timestamp_pattern = r'(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}:\d{2}[+\-]\d{2}:\d{2}'
            
            # Replace the header line
            result = raw_result.replace('timestamp', 'Date')
            
            # Replace all timestamp values with just the date
            result = re.sub(timestamp_pattern, r'\1', result)
            
            # Also clean up any remaining timezone info
            result = re.sub(r'\s+\d{2}:\d{2}:\d{2}[+\-]\d{2}:\d{2}', '', result)
            
            # Update the title
            result = result.replace('Stock data for', 'Stock Data Table for')
            result = result.replace('from 2025-', f'({look_back_days}-day lookback)\nFrom 2025-')
            
            return result
                
        except Exception as e:
            # Fallback to original if any processing fails
            return raw_result

    @staticmethod
    @tool
    @timing_wrapper("MARKET")
    def get_indicators_table(
        symbol: Annotated[str, "ticker symbol of the company"],
        curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
        look_back_days: Annotated[int, "how many days to look back"] = 90,
    ) -> str:
        """
        Retrieve comprehensive technical indicators table for a given ticker symbol over a lookback period.
        Returns a full table with Date and all key technical indicators calculated over the specified time window.
        Includes: EMAs, SMAs, RSI, MACD, Bollinger Bands, Stochastic, Williams %R, OBV, MFI, ATR.
        
        Args:
            symbol (str): Ticker symbol of the company, e.g. AAPL, NVDA
            curr_date (str): The current trading date in YYYY-mm-dd format
            look_back_days (int): How many days to look back (default 60)
            
        Returns:
            str: A comprehensive table containing Date and all technical indicators for the lookback period
        """
        
        # Define the key indicators optimized for EOD trading
        key_indicators = [
            'close_8_ema',      # 8-day EMA (faster trend detection for EOD)
            'close_21_ema',     # 21-day EMA (key swing level)
            'close_50_sma',     # 50-day SMA (major trend)
            'rsi_14',           # 14-day RSI (optimal for daily signals)
            'macd',             # MACD Line (12,26,9 default)
            'macds',            # MACD Signal Line
            'macdh',            # MACD Histogram
            'boll_ub',          # Bollinger Upper (20,2 default)
            'boll_lb',          # Bollinger Lower (20,2 default)
            'kdjk_9',           # Stochastic %K (9-period for EOD)
            'kdjd_9',           # Stochastic %D (9-period for EOD)
            'wr_14',            # Williams %R (14-period)
            'atr_14',           # ATR (14-period for position sizing)
            'obv'               # On-Balance Volume (volume confirmation)
        ]
        
        # Get indicator data for each indicator across the time window
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Calculate date range
        curr_dt = pd.to_datetime(curr_date)
        start_dt = curr_dt - pd.Timedelta(days=look_back_days)
        
        results = []
        results.append(f"# Technical Indicators Table for {symbol}")
        results.append(f"**Period:** {start_dt.strftime('%Y-%m-%d')} to {curr_date} ({look_back_days} days lookback)")
        results.append(f"**Showing:** Last 25 trading days for EOD analysis")
        results.append("")
        
        # Create table header
        header_row = "| Date | " + " | ".join([ind.replace('_', ' ').title() for ind in key_indicators]) + " |"
        separator_row = "|------|" + "|".join(["------" for _ in key_indicators]) + "|"
        
        results.append(header_row)
        results.append(separator_row)
        
        # Generate dates for the lookback period - only trading days
        dates = []
        trading_days_found = 0
        days_back = 0
        
        # Get the last 45 trading days (roughly 9 weeks of trading data)
        while trading_days_found < 45 and days_back <= look_back_days:
            date = curr_dt - pd.Timedelta(days=days_back)
            # Skip weekends (Saturday=5, Sunday=6)
            if date.weekday() < 5:  # Monday=0, Friday=4
                dates.append(date.strftime("%Y-%m-%d"))
                trading_days_found += 1
            days_back += 1
        
        # Reverse to get chronological order, then take the most recent portion
        dates = dates[::-1]
        recent_dates = dates[-25:] if len(dates) > 25 else dates  # Show last 25 trading days
        
        # For each date, get all indicator values
        for date in recent_dates:
            row_values = [date]
            
            for indicator in key_indicators:
                try:
                    # Get indicator value for this date using the window method
                    value = interface.get_stock_stats_indicators_window(
                        symbol, indicator, date, 1, True  # Get just this date's value
                    )
                    # Extract just the numeric value from the response
                    if ":" in value:
                        numeric_part = value.split(":")[-1].strip().split("(")[0].strip()
                        try:
                            float_val = float(numeric_part)
                            if indicator in ['rsi_14', 'kdjk', 'kdjd', 'wr_14']:
                                row_values.append(f"{float_val:.1f}")
                            elif 'macd' in indicator:
                                row_values.append(f"{float_val:.3f}")
                            else:
                                row_values.append(f"{float_val:.2f}")
                        except:
                            row_values.append("N/A")
                    else:
                        row_values.append("N/A")
                except:
                    row_values.append("N/A")
            
            # Format the table row
            table_row = "| " + " | ".join(row_values) + " |"
            results.append(table_row)
        
        results.append("")
        results.append("## Key EOD Trading Signals Analysis:")
        results.append("- **Trend Structure:** 8-EMA > 21-EMA > 50-SMA = Strong uptrend | Price above all EMAs = Bullish")
        results.append("- **Momentum:** RSI 30-50 = Accumulation zone | RSI 50-70 = Trending | RSI >70 = Overbought")
        results.append("- **MACD Signals:** MACD > Signal = Bullish momentum | Histogram growing = Acceleration")
        results.append("- **Bollinger Bands:** Price at Upper Band = Breakout potential | Price at Lower Band = Support test")
        results.append("- **Stochastic:** %K crossing above %D in oversold (<20) = Buy signal | In overbought (>80) = Sell signal")
        results.append("- **Williams %R:** Values -20 to -80 = Normal range | Below -80 = Oversold (buy) | Above -20 = Overbought (sell)")
        results.append("- **ATR:** Use for position sizing (1-2x ATR for stop loss) | Higher ATR = More volatile")
        results.append("")
        results.append("**EOD Strategy:** Look for trend + momentum + volume confirmation for overnight positions")
        
        return "\n".join(results)

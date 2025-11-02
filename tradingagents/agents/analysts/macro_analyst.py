from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from langchain_core.messages import AIMessage, ToolMessage

# Import prompt capture utility
try:
    from webui.utils.prompt_capture import capture_agent_prompt
except ImportError:
    # Fallback for when webui is not available
    def capture_agent_prompt(report_type, prompt_content, symbol=None):
        pass

# Import safe chain invoke helper
from tradingagents.agents.utils.agent_utils import safe_chain_invoke


def create_macro_analyst(llm, toolkit):
    def macro_analyst_node(state):
        # print(f"[MACRO] Starting macro economic analysis for {state['trade_date']}")
        start_time = time.time()
        
        try:
            current_date = state["trade_date"]
            ticker = state.get("company_of_interest", "MARKET")
            
            # print(f"[MACRO] Analyzing macro environment on {current_date}")
            
            # Macro analysis uses the same tools regardless of online/offline mode
            # since it's focused on economic data rather than company-specific data
            if toolkit.config["online_tools"]:
                tools = [
                    toolkit.get_macro_analysis,
                    toolkit.get_economic_indicators,
                    toolkit.get_yield_curve_analysis
                ]
                # print(f"[MACRO] Using online macro tools: FRED API + Economic Indicators")
            else:
                # For offline mode, we still use the same tools but they may use cached data
                tools = [
                    toolkit.get_macro_analysis,
                    toolkit.get_economic_indicators,
                    toolkit.get_yield_curve_analysis
                ]
                # print(f"[MACRO] Using offline macro tools: Cached Economic Data")

            system_message = (
                "You are an EOD TRADING macro analyst focused on identifying macroeconomic factors and events that could drive overnight and next-day market movements. "
                "Your analysis should focus on after-hours macro catalysts and data releases that create EOD trading opportunities across different sectors and asset classes.\n\n"
                "**EOD TRADING MACRO FOCUS:**\n"
                "1. **Next-Day Economic Data Releases**: Overnight and pre-market data (CPI, NFP, GDP, PMI) that could create market gaps\n"
                "2. **Federal Reserve Schedule**: FOMC meetings, Fed speak, policy announcements affecting overnight positioning\n"
                "3. **Market Risk Sentiment**: After-hours VIX levels, yield curve changes, sector rotation patterns for next day\n"
                "4. **Overnight Sector Rotation Drivers**: Macro themes driving overnight money flows between sectors\n"
                "5. **Currency & Commodity Impacts**: Overnight USD strength, oil prices, gold affecting different stock sectors\n"
                "6. **Geopolitical Events**: Elections, trade decisions, central bank actions with after-hours timing\n\n"
                "**EOD TRADING MACRO ANALYSIS REQUIREMENTS:**\n"
                "- **Event Calendar**: Specific times for economic releases, Fed events, geopolitical meetings (focusing on overnight/pre-market)\n"
                "- **Market Impact Assessment**: Which data releases typically create overnight gaps >2% (EOD-worthy)\n"
                "- **Sector Implications**: How macro data affects different sectors (tech, banks, energy, etc.) for overnight trades\n"
                "- **Risk-On/Risk-Off Signals**: Macro conditions favoring growth vs. defensive stocks for overnight positioning\n"
                "- **Volatility Forecast**: Expected overnight market volatility during macro events (VIX implications)\n"
                "- **Time-Sensitive Catalysts**: Macro events with clear overnight/pre-market implications for next-day trades\n\n"
                "**AVOID:** Long-term economic forecasts, quarterly outlooks, annual trends. Focus on actionable macro insights "
                "for EOD traders with specific times, expected overnight market reactions, and sector-specific implications for next trading day. "
                "Provide timing-specific macro analysis that EOD traders can use to position for overnight economic events and policy announcements.\n\n"
                "Make sure to append a Markdown table organizing:\n"
                "| Date/Time | Economic Event | Expected Impact | Affected Sectors | EOD Trade Implication |\n"
                "|-----------|----------------|-----------------|------------------|----------------------|\n"
                "| [Specific Date/Time] | [Data Release/Fed Event] | [High/Med/Low + Direction] | [Sectors Most Affected] | [Long/Short/Neutral Bias] |"
            )

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a helpful AI assistant, collaborating with other assistants."
                        " Use the provided tools to progress towards answering the question."
                        " If you are unable to fully answer, that's OK; another assistant with different tools"
                        " will help where you left off. Execute what you can to make progress."
                        " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                        " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                        " You have access to the following tools: {tool_names}.\n{system_message}"
                        "For your reference, the current date is {current_date}. "
                        "Focus on macroeconomic conditions that affect overall market sentiment and sector rotation. "
                        "If tools fail due to missing API keys, provide a general macro analysis based on current market knowledge.",
                    ),
                    MessagesPlaceholder(variable_name="messages"),
                ]
            )

            # print(f"[MACRO] Setting up prompt and chain...")
            prompt = prompt.partial(system_message=system_message)
            prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
            prompt = prompt.partial(current_date=current_date)

            # Capture the COMPLETE resolved prompt that gets sent to the LLM
            try:
                # Get the formatted messages with all variables resolved
                messages_history = list(state["messages"])
                formatted_messages = prompt.format_messages(messages=messages_history)
                
                # Extract the complete system message (first message)
                if formatted_messages and hasattr(formatted_messages[0], 'content'):
                    complete_prompt = formatted_messages[0].content
                else:
                    # Fallback: manually construct the complete prompt
                    tool_names_str = ", ".join([tool.name for tool in tools])
                    complete_prompt = f"""You are a helpful AI assistant, collaborating with other assistants. Use the provided tools to progress towards answering the question. If you are unable to fully answer, that's OK; another assistant with different tools will help where you left off. Execute what you can to make progress. If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable, prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop. You have access to the following tools: {tool_names_str}.

{system_message}

For your reference, the current date is {current_date}. Focus on macroeconomic conditions that affect overall market sentiment and sector rotation. If tools fail due to missing API keys, provide a general macro analysis based on current market knowledge."""
                
                capture_agent_prompt("macro_report", complete_prompt, ticker)
            except Exception as e:
                print(f"[MACRO] Warning: Could not capture complete prompt: {e}")
                # Fallback to system message only
                capture_agent_prompt("macro_report", system_message, ticker)

            chain = prompt | llm.bind_tools(tools)
            
            # print(f"[MACRO] Invoking LLM chain...")
            # Maintain a copy of the conversation history for iterative tool use
            messages_history = list(state["messages"])

            # First response from the LLM with safe fallback handling
            result = safe_chain_invoke(chain, prompt, llm, tools, messages_history, "MACRO")
            
            # Track tool failures to provide graceful fallback
            tool_failures = []
            successful_tools = []

            # Loop to automatically execute any requested tool calls
            max_iterations = 10  # Prevent infinite loops
            iteration_count = 0
            
            while getattr(result, "additional_kwargs", {}).get("tool_calls") and iteration_count < max_iterations:
                iteration_count += 1
                # print(f"[MACRO] Tool execution iteration {iteration_count}")
                
                for tool_call in result.additional_kwargs["tool_calls"]:
                    # Handle different tool call structures
                    if isinstance(tool_call, dict):
                        tool_name = tool_call.get("name") or tool_call.get("function", {}).get("name")
                        tool_args = tool_call.get("args", {}) or tool_call.get("function", {}).get("arguments", {})
                        if isinstance(tool_args, str):
                            try:
                                tool_args = json.loads(tool_args)
                            except json.JSONDecodeError:
                                tool_args = {}
                    else:
                        # Handle LangChain ToolCall objects
                        tool_name = getattr(tool_call, 'name', None)
                        tool_args = getattr(tool_call, 'args', {})

                    tool_fn = next((t for t in tools if t.name == tool_name), None)

                    if tool_fn is None:
                        tool_result = f"Tool '{tool_name}' not found."
                        print(f"[MACRO] ⚠️ {tool_result}")
                        tool_failures.append(tool_name)
                    else:
                        try:
                            if hasattr(tool_fn, "invoke"):
                                tool_result = tool_fn.invoke(tool_args)
                            else:
                                tool_result = tool_fn.run(**tool_args)
                            
                            successful_tools.append(tool_name)
                            
                            # Check if tool returned an actual error message (be more specific)
                            # Only flag as error if the entire result is an error, not if it contains error sections
                            if isinstance(tool_result, str) and (
                                tool_result.lower().startswith("error") or 
                                (len(tool_result) < 200 and (
                                    "api key not found" in tool_result.lower() or
                                    "failed to fetch" in tool_result.lower() or
                                    "connection error" in tool_result.lower()
                                ))
                            ):
                                print(f"[MACRO] ⚠️ Tool '{tool_name}' returned error: {tool_result[:100]}...")
                                tool_failures.append(tool_name)
                            elif isinstance(tool_result, str) and len(tool_result) > 100:
                                # This is likely a valid report, even if it contains some error sections
                                # Don't flag as a complete failure
                                print(f"[MACRO] 📊 Tool '{tool_name}' returned report with {len(tool_result)} characters")
                            else:
                                print(f"[MACRO] ✅ Tool '{tool_name}' completed successfully")
                                
                        except Exception as tool_err:
                            tool_result = f"Error running tool '{tool_name}': {str(tool_err)}"
                            tool_failures.append(tool_name)

                    tool_call_id = tool_call.get("id") or tool_call.get("tool_call_id")
                    ai_tool_call_msg = AIMessage(content="", additional_kwargs={"tool_calls": [tool_call]})
                    tool_msg = ToolMessage(content=str(tool_result), tool_call_id=tool_call_id)
                    messages_history.extend([ai_tool_call_msg, tool_msg])

                # Get next response from LLM (with safe fallback)
                try:
                    result = safe_chain_invoke(chain, prompt, llm, tools, messages_history, "MACRO")
                except Exception as e:
                    print(f"[MACRO] ❌ Error in LLM chain iteration {iteration_count}: {e}")
                    break
            
            # If we had tool failures, let the LLM know and ask for a general analysis
            if tool_failures and not successful_tools:
                print(f"[MACRO] All tools failed ({tool_failures}), requesting general macro analysis")
                fallback_prompt = f"""
Please provide a general macro economic analysis for {current_date} based on your knowledge of current market conditions.
Focus on general trends in:
- Federal Reserve policy and interest rates
- Inflation environment 
- Employment trends
- Market volatility
- Economic growth outlook
- Trading implications for different asset classes

Make sure to include a summary table at the end.
"""
                messages_history.append(AIMessage(content=fallback_prompt))
                try:
                    # Get final response without tools
                    chain_no_tools = prompt.partial(tool_names="") | llm
                    result = chain_no_tools.invoke(messages_history)
                except Exception as e:
                    print(f"[MACRO] ❌ Error in fallback analysis: {e}")
                    # Provide a minimal fallback report
                    result = type('MockResult', (), {
                        'content': f"""
# Macro Economic Analysis - {current_date}

## Analysis Status
⚠️ **Limited Analysis**: Economic data tools unavailable (FRED API key required)

## General Market Environment
Based on current market conditions as of {current_date}:

### Federal Reserve Policy
- Monitor FOMC meetings and policy statements
- Watch for changes in federal funds rate guidance
- Consider impact on different sectors

### Market Conditions  
- **Growth Stocks**: Sensitive to interest rate changes
- **Financial Sector**: Generally benefits from rising rates
- **Utilities/REITs**: Pressure from rising rates
- **Technology**: Vulnerable to rate uncertainty

### Trading Recommendations
- **Defensive**: Consider defensive sectors during uncertainty
- **Quality Focus**: Emphasize companies with strong fundamentals
- **Diversification**: Maintain balanced exposure across sectors

| Indicator | Status | Impact |
|-----------|--------|--------|
| FRED Data | ❌ Unavailable | High |
| Analysis Quality | ⚠️ Limited | Medium |
| Recommendation | 📊 General Guidance | Medium |

**Note**: For complete macro analysis, configure FRED_API_KEY environment variable.
"""
                    })()
            
            elapsed_time = time.time() - start_time
            # print(f"[MACRO] ✅ Analysis completed in {elapsed_time:.2f} seconds")
            # print(f"[MACRO] Generated report length: {len(result.content)} characters")
            # print(f"[MACRO] Tool success/failure: {len(successful_tools)} successful, {len(tool_failures)} failed")

            # Append final message for downstream agents
            messages_history.append(result)

            return {
                "messages": messages_history,
                "macro_report": result.content,
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = f"Error in macro analysis for {current_date}: {str(e)}"
            print(f"[MACRO] ❌ {error_msg}")
            print(f"[MACRO] ❌ Failed after {elapsed_time:.2f} seconds")
            
            # Import traceback for detailed error logging
            import traceback
            print(f"[MACRO] ❌ Full traceback:")
            traceback.print_exc()
            
            # Return a minimal report with error information that still allows the analysis to continue
            fallback_report = f"""
# Macro Economic Analysis Error

**Date:** {state.get('trade_date', 'Unknown')}
**Error:** {str(e)}
**Duration:** {elapsed_time:.2f} seconds

## Error Details
The macro economic analysis encountered an error and could not complete successfully. This may be due to:
- FRED API rate limits or timeouts
- Network connectivity issues  
- Missing API keys (FRED_API_KEY required)
- Invalid date ranges or data unavailability

## General Market Guidance
⚠️ **PROCEED WITH CAUTION** - Unable to perform detailed macro economic analysis.

### Manual Check Recommendations
- Monitor Federal Reserve policy updates manually
- Check recent CPI and employment data releases
- Observe Treasury yield curve for inversion signals
- Watch VIX levels for market volatility assessment
- Review latest FOMC meeting minutes

### General Trading Implications
- **Rising Rate Environment**: Favor financials, pressure growth stocks
- **Inflation Concerns**: Consider commodity exposure, real assets
- **Economic Uncertainty**: Increase defensive positioning
- **Market Volatility**: Adjust position sizing accordingly

| Indicator | Status | Recommendation |
|-----------|--------|----------------|
| Economic Data | ❌ Unavailable | Manual Review Required |
| Yield Curve | ❌ Unavailable | Monitor Treasury.gov |
| Fed Policy | ❌ Unavailable | Check Federal Reserve Website |
| Analysis Status | ❌ Failed | ⚠️ Use General Guidance |
| Overall Recommendation | ⚠️ Limited Analysis | Proceed with Caution |

**Configuration Note**: Set FRED_API_KEY environment variable for complete macro analysis.
"""
            
            # Ensure we return proper message structure even in error case
            return {
                "messages": [result if 'result' in locals() and result else AIMessage(content="Macro analysis encountered an error.")],
                "macro_report": fallback_report,
            }

    return macro_analyst_node 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, ToolMessage
import time
import json

# Import prompt capture utility
try:
    from webui.utils.prompt_capture import capture_agent_prompt
except ImportError:
    # Fallback for when webui is not available
    def capture_agent_prompt(report_type, prompt_content, symbol=None):
        pass


def create_news_analyst(llm, toolkit):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        is_crypto = "/" in ticker or "USD" in ticker.upper() or "USDT" in ticker.upper()

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_global_news_openai, toolkit.get_google_news]
        else:
            if is_crypto:
                tools = [
                    toolkit.get_coindesk_news,
                    toolkit.get_reddit_news,
                    toolkit.get_google_news,
                ]
            else:
                tools = [
                    toolkit.get_finnhub_news,
                    toolkit.get_reddit_news,
                    toolkit.get_google_news,
                ]

        system_message = (
            f"You are an EOD TRADING news analyst specializing in identifying news events and market developments that could drive overnight and next-day price movements for {ticker}. Focus on after-hours catalysts and sentiment shifts that create EOD trading opportunities."
            + " **EOD TRADING NEWS ANALYSIS:** \n"
            + "1. **Overnight Catalyst Identification:** After-hours events, announcements, data releases that could create next-day gaps or moves \n"
            + "2. **End-of-Day Sentiment Shifts:** Changes in market narrative, analyst sentiment, or sector rotation trends affecting overnight positions \n"
            + "3. **Event Timing:** Specific dates/times for earnings, FDA approvals, product launches, economic data that EOD traders should know \n"
            + "4. **After-Hours Momentum Drivers:** Breaking news creating overnight price momentum suitable for next-day positioning \n"
            + "5. **Overnight Risk Events:** Geopolitical developments, Fed decisions, sector-specific risks that could impact overnight positions \n"
            + "6. **Pre-Market Analysis:** How similar companies are reacting to news - sector momentum and relative strength patterns for next day \n"
            + "**ANALYSIS PRIORITIES:** \n"
            + "- Focus on actionable news with clear timing implications for overnight trades \n"
            + "- Identify both bullish and bearish catalysts affecting next trading day \n"
            + "- Assess news impact magnitude (minor <2%, moderate 2-5%, major >5% overnight/next-day moves) \n"
            + "- Consider news durability (will impact persist through next day or just overnight?) \n"
            + "- Analyze market reaction patterns to similar news in overnight/pre-market sessions \n"
            + f"**IMPORTANT:** When using get_global_news_openai, ALWAYS pass ticker_context='{ticker}' to get {('crypto-relevant global news (regulation, institutional adoption, DeFi developments)' if is_crypto else 'sector-relevant global news')} instead of generic macro news.\n"
            + "**AVOID:** Generic market commentary, long-term trends, intraday noise. Focus on EOD-relevant news with overnight impact potential.\n"
            + """ Make sure to append a Markdown table at the end organizing:
| News Event | Date/Time | Impact Level | Price Direction | EOD Trading Implication |
|------------|-----------|--------------|----------------|------------------------|\n
| [Specific Event] | [Date/Time] | [High/Med/Low] | [Bullish/Bearish/Neutral] | [Entry/Exit/Hold Strategy] |

Provide specific, actionable news analysis for EOD trading decisions with clear timing and impact assessment."""
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
                    "For your reference, the current date is {current_date}. We are looking at the ticekr: {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

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

For your reference, the current date is {current_date}. We are looking at the ticekr: {ticker}"""
            
            capture_agent_prompt("news_report", complete_prompt, ticker)
        except Exception as e:
            print(f"[NEWS] Warning: Could not capture complete prompt: {e}")
            # Fallback to system message only
            capture_agent_prompt("news_report", system_message, ticker)

        chain = prompt | llm.bind_tools(tools)
        
        # Copy the incoming conversation history so we can append to it when the model makes tool calls
        messages_history = list(state["messages"])

        # First LLM response
        result = chain.invoke(messages_history)

        # Handle iterative tool calls until the model stops requesting them
        while getattr(result, "additional_kwargs", {}).get("tool_calls"):
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

                # Find the matching tool by name
                tool_fn = next((t for t in tools if t.name == tool_name), None)

                if tool_fn is None:
                    tool_result = f"Tool '{tool_name}' not found."
                    print(f"[NEWS] ⚠️ {tool_result}")
                else:
                    try:
                        # LangChain Tool objects expose `.run` (string IO) as well as `.invoke` (dict/kwarg IO)
                        if hasattr(tool_fn, "invoke"):
                            tool_result = tool_fn.invoke(tool_args)
                        else:
                            tool_result = tool_fn.run(**tool_args)
                        
                    except Exception as tool_err:
                        tool_result = f"Error running tool '{tool_name}': {str(tool_err)}"

                # Append the assistant tool call and tool result messages so the LLM can continue the conversation
                tool_call_id = tool_call.get("id") or tool_call.get("tool_call_id")
                ai_tool_call_msg = AIMessage(
                    content="",
                    additional_kwargs={"tool_calls": [tool_call]},
                )
                tool_msg = ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call_id,
                )

                messages_history.append(ai_tool_call_msg)
                messages_history.append(tool_msg)

            # Ask the LLM to continue with the new context
            result = chain.invoke(messages_history)
        
        # Check if the result already contains FINAL TRANSACTION PROPOSAL
        if "FINAL TRANSACTION PROPOSAL:" not in result.content:
            # Create a simple prompt that includes the analysis content directly
            final_prompt = f"""Based on the following news analysis for {ticker}, please provide your final trading recommendation considering the overall news sentiment and implications.

Analysis:
{result.content}

You must conclude with: FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** followed by a brief justification."""
            
            # Use a simple chain without tools for the final recommendation
            final_chain = llm
            final_result = final_chain.invoke(final_prompt)
            
            # Combine the analysis with the final proposal
            combined_content = result.content + "\n\n" + final_result.content
            result = AIMessage(content=combined_content)

        return {
            "messages": [result],
            "news_report": result.content,
        }

    return news_analyst_node

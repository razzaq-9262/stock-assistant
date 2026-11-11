"""AI harness: coordinates the model, tools and permissions.

Flow: user question -> Claude decides which tool to call -> we run the tool
-> result goes back to Claude -> Claude explains in plain language.
Only whitelisted tools can be called (permissions).
"""
import json
import os

from tools import calculations, fundamental, technical
from sandbox.runner import run_code

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

SYSTEM_PROMPT = (
    "You are a stock market assistant. Use the tools to fetch real data, "
    "then explain results clearly for beginners. Always state your data "
    "source (Yahoo Finance via yfinance) and any assumptions. "
    "This is educational information, not financial advice."
)

TOOLS = [
    {
        "name": "technical_analysis",
        "description": "Trend, RSI and volume summary for one ticker.",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"},
                           "period": {"type": "string", "default": "6mo"}},
            "required": ["ticker"],
        },
    },
    {
        "name": "fundamental_analysis",
        "description": "Valuation and company performance numbers.",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    },
    {
        "name": "compare_stocks",
        "description": "Compare return and risk of several tickers.",
        "input_schema": {
            "type": "object",
            "properties": {"tickers": {"type": "array",
                                       "items": {"type": "string"}}},
            "required": ["tickers"],
        },
    },
    {
        "name": "what_if",
        "description": "Project investment growth over years.",
        "input_schema": {
            "type": "object",
            "properties": {"amount": {"type": "number"},
                           "annual_return_pct": {"type": "number"},
                           "years": {"type": "integer"}},
            "required": ["amount", "annual_return_pct", "years"],
        },
    },
    {
        "name": "run_python",
        "description": "Run a short Python snippet in the sandbox.",
        "input_schema": {
            "type": "object",
            "properties": {"code": {"type": "string"}},
            "required": ["code"],
        },
    },
]


def execute_tool(name: str, args: dict):
    """Run one whitelisted tool and return JSON-friendly output."""
    if name == "technical_analysis":
        df = technical.add_indicators(
            technical.get_prices(args["ticker"], args.get("period", "6mo")))
        return technical.trend_summary(df)
    if name == "fundamental_analysis":
        return fundamental.get_fundamentals(args["ticker"])
    if name == "compare_stocks":
        return calculations.compare_stocks(args["tickers"]).to_dict("records")
    if name == "what_if":
        return calculations.project_value(
            args["amount"], args["annual_return_pct"], args["years"]
        ).to_dict("records")
    if name == "run_python":
        return run_code(args["code"])
    return {"error": f"Tool '{name}' is not allowed"}


def ask(question: str, history=None) -> str:
    """Send a question to Claude and loop until it gives a final answer."""
    import anthropic

    client = anthropic.Anthropic()
    messages = list(history or []) + [{"role": "user", "content": question}]

    for _ in range(6):  # safety limit on tool-call rounds
        resp = client.messages.create(
            model=MODEL, max_tokens=1500, system=SYSTEM_PROMPT,
            tools=TOOLS, messages=messages)
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                try:
                    out = execute_tool(block.name, block.input)
                except Exception as exc:  # report errors back to the model
                    out = {"error": str(exc)}
                results.append({"type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(out, default=str)})
        messages.append({"role": "user", "content": results})
    return "Sorry, the analysis took too many steps. Please try a simpler question."

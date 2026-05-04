"""Shared MCP + LangChain agent setup for the CLI client and Streamlit UI."""

from __future__ import annotations

import sys
from pathlib import Path

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to tools. "
    "For arithmetic that mixes operations (for example (3+5)*12), call the evaluate "
    "tool once and pass the full expression as a single string argument. "
    "Otherwise you may use add or multiply, but never nest one tool call inside "
    "another tool's arguments; use at most one tool per assistant turn."
)


def mcp_connections(
    root: Path,
    *,
    use_weather: bool,
    weather_url: str,
) -> dict:
    cfg: dict = {
        "math": {
            "command": sys.executable,
            "args": [str(root / "mathserver.py")],
            "transport": "stdio",
            "cwd": str(root),
        },
    }
    if use_weather:
        cfg["weather"] = {
            "url": weather_url.strip(),
            "transport": "streamable-http",
        }
    return cfg


async def build_mcp_agent(
    root: Path,
    *,
    model: str = "llama-3.3-70b-versatile",
    use_weather: bool = True,
    weather_url: str = "http://127.0.0.1:8000/mcp",
):
    client = MultiServerMCPClient(mcp_connections(root, use_weather=use_weather, weather_url=weather_url))
    tools = await client.get_tools()
    llm = ChatGroq(model=model)
    return create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)

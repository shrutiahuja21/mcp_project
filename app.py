"""
MCP chat assistant UI (Streamlit).

Run from the project directory:
  uv run streamlit run app.py

Start the weather MCP server separately if you enable it in the sidebar:
  uv run python weather.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from chat_assistant import build_mcp_agent

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")


def _content_str(message: AIMessage | HumanMessage) -> str:
    content = getattr(message, "content", None)
    if isinstance(content, str) and content.strip():
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text" and block.get("text"):
                    parts.append(str(block["text"]))
                elif "text" in block:
                    parts.append(str(block["text"]))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts).strip()
    return ""


def _render_message(msg: HumanMessage | AIMessage | ToolMessage | SystemMessage) -> None:
    if isinstance(msg, SystemMessage):
        return
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content if isinstance(msg.content, str) else str(msg.content))
        return
    if isinstance(msg, AIMessage):
        text = _content_str(msg)
        with st.chat_message("assistant"):
            if text:
                st.markdown(text)
            if getattr(msg, "tool_calls", None):
                with st.expander("Tool calls", expanded=False):
                    st.json(msg.tool_calls)
        return
    if isinstance(msg, ToolMessage):
        with st.chat_message("assistant"):
            with st.expander(f"Tool result: `{msg.name}`", expanded=False):
                st.code(str(msg.content))


@st.cache_resource(show_spinner="Connecting to MCP servers…")
def _load_agent(*, model: str, use_weather: bool, weather_url: str):
    return asyncio.run(
        build_mcp_agent(_ROOT, model=model, use_weather=use_weather, weather_url=weather_url)
    )


def main() -> None:
    st.set_page_config(page_title="MCP Chat", page_icon="💬", layout="centered")
    st.title("MCP chat assistant")
    st.caption("Math tools via stdio MCP · optional weather via streamable HTTP · Groq LLM")

    with st.sidebar:
        st.subheader("Settings")
        model = st.text_input("Groq model", value="llama-3.3-70b-versatile")
        use_weather = st.checkbox("Enable weather MCP", value=False)
        weather_url = st.text_input("Weather MCP URL", value="http://127.0.0.1:8000/mcp")
        if st.button("New chat"):
            st.session_state.pop("lc_messages", None)
            st.rerun()
        if st.button("Reconnect MCP (clear cache)"):
            st.cache_resource.clear()
            st.session_state.pop("lc_messages", None)
            st.rerun()

    if "lc_messages" not in st.session_state:
        st.session_state.lc_messages = []

    weather_enabled = use_weather
    try:
        agent = _load_agent(model=model, use_weather=use_weather, weather_url=weather_url)
    except Exception as exc:
        if use_weather:
            st.warning(
                "Weather MCP is unreachable. Falling back to math-only mode. "
                "Start weather server and click 'Reconnect MCP' to re-enable it."
            )
            weather_enabled = False
            agent = _load_agent(model=model, use_weather=False, weather_url=weather_url)
        else:
            st.error(f"Failed to initialize MCP agent: {exc}")
            return

    if weather_enabled:
        st.caption(f"Weather MCP: connected to `{weather_url}`")
    else:
        st.caption("Weather MCP: disabled")

    for msg in st.session_state.lc_messages:
        _render_message(msg)

    if prompt := st.chat_input("Message the assistant…"):
        with st.spinner("Running agent…"):
            msgs = [*st.session_state.lc_messages, HumanMessage(content=prompt)]
            try:
                result = asyncio.run(agent.ainvoke({"messages": msgs}))
            except Exception as e:
                st.error(f"Request failed: {e}")
                return
            st.session_state.lc_messages = list(result["messages"])
        st.rerun()


if __name__ == "__main__":
    main()

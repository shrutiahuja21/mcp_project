import asyncio

from dotenv import load_dotenv

from chat_assistant import build_mcp_agent
from venv_bootstrap import ensure_project_venv, project_root

ensure_project_venv()

_ROOT = project_root()
load_dotenv(_ROOT / ".env")


async def main() -> None:
    agent = await build_mcp_agent(
        _ROOT,
        model="llama-3.3-70b-versatile",
        use_weather=True,
        weather_url="http://127.0.0.1:8000/mcp",
    )
    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3+5)*12?"}]}
    )
    print("Math response:", math_response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())

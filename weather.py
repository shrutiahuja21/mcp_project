from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather", host="127.0.0.1", port=8000)


@mcp.tool()
async def get_weather(location: str) -> str:
    """Get the weather location"""
    return f"It is always raining in California (demo) for {location}."


if __name__ == "__main__":
    print("Starting weather MCP server at http://127.0.0.1:8000/mcp")
    mcp.run(transport="streamable-http")
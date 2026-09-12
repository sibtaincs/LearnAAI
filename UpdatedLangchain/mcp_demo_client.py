"""Simple MCP client example.

This file shows how a custom Python client connects to an MCP server, discovers tools,
then calls them programmatically.

This is useful when you want to integrate MCP into your own app or agent workflow.
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    # Point this at your server file.
    # This approach starts the server as a subprocess and speaks MCP over stdio.
    server = StdioServerParameters(
        command=sys.executable,
        args=["UpdatedLangchain/mcp_demo_server.py"],
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Ask the server which tools it exposes.
            tools = await session.list_tools()
            print("Available MCP tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Call the Tavily search tool.
            result = await session.call_tool(
                "search_tavily",
                {
                    "query": "best family-friendly Airbnb in Bali",
                    "max_results": 2,
                },
            )
            print("\nTavily result:")
            print(result)

            # Call the Airbnb browser tool.
            result = await session.call_tool(
                "open_airbnb_search",
                {
                    "city": "Bali",
                    "check_in": "2026-10-01",
                    "check_out": "2026-10-05",
                    "guests": 2,
                },
            )
            print("\nAirbnb result:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())

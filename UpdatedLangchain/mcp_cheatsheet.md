# MCP Cheat Sheet

## Core idea

MCP = Model Context Protocol

It standardizes how AI apps connect to tools and data sources.

Instead of writing custom wrappers for every service, you expose a tool interface once and let the model call it through the protocol.

---

## Typical architecture

- Client / Host: Claude Desktop, Cursor, custom Python app, VS Code
- MCP Server: exposes tools and resources
- Protocol: defines discovery, request, and response formats
- Tool / Resource: actual external functionality

---

## Python server pattern

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")

@mcp.tool()
def get_weather(city: str) -> str:
    return f"Weather in {city}: 24°C and sunny"

if __name__ == "__main__":
    mcp.run()
```

---

## Important concepts

### Tool
A callable action the model can execute.

Example:
- `search_tavily(query)`
- `open_airbnb_search(city)`
- `run_sql(query)`

### Resource
A readable data source.

Example:
- `weather://tokyo`
- `db://customers/42`
- `docs://project-guide`

### Prompt
A reusable prompt template.

---

## Playwright MCP config example

```json
{
  "servers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

Use this for browser-based tasks in IDEs or local agents.

---

## Tavily API example

```python
import os
import httpx

api_key = os.getenv("TAVILY_API_KEY")
response = httpx.post(
    "https://api.tavily.com/search",
    json={
        "api_key": api_key,
        "query": "best neighborhoods in Bali",
        "max_results": 3,
    },
    timeout=30,
)
```

This gives the model live web research to ground its answer.

---

## Airbnb browser flow

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.airbnb.com")
    print(page.title())
```

This is useful when you need real browser context, not just a text API.

---

## Client pattern

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server = StdioServerParameters(command="python", args=["server.py"])

async with stdio_client(server) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
```

This is how a custom app connects to a server and calls tools programmatically.

---

## Typical agent flow

1. User asks a question.
2. LLM selects the best tool.
3. Client executes the tool over MCP.
4. Tool returns results.
5. LLM reasons over the result.
6. Final answer is generated.

---

## Production notes

- keep tools small and focused
- validate inputs and secrets
- return structured JSON where possible
- set up retries and timeouts
- containerize with Docker for deployment

---

## Best phrase to remember

MCP turns external systems into discoverable, standard tools that an LLM can call safely and consistently.

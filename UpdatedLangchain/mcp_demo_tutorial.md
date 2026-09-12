# MCP Demo Tutorial for Python + Playwright + Tavily + Airbnb

This tutorial is tailored to the setup already in this workspace, especially the Playwright MCP config in `.vscode/mcp.json` and the Python project in `UpdatedLangchain/`.

---

## What this project demonstrates

This demo shows how to combine:

- an MCP server written in Python
- a Tavily search tool for web research
- a Playwright browser tool for interacting with Airbnb
- a custom client that connects to the server programmatically

The goal is to show how MCP standardizes the connection between an LLM and external tools without writing custom adapter code for every provider.

---

## 1) Why MCP matters

Without MCP, a model may need separate code paths for:

- web search
- browser automation
- database access
- APIs
- business tools

MCP solves that by giving all tools a common interface, so the LLM can call them in a predictable, discoverable way.

This is the same idea Krish Naik highlights: one standard protocol instead of many custom wrappers.

---

## 2) Project structure in this workspace

The repo already contains a Playwright MCP config:

- `.vscode/mcp.json`
- `UpdatedLangchain/mcp-playwright.json`

This is a good starting point for browser-based tools.

In this tutorial, we extend that idea with:

- `UpdatedLangchain/mcp_demo_server.py` — the Python MCP server
- `UpdatedLangchain/mcp_demo_client.py` — the client that connects to it

---

## 3) Install the required Python packages

From the repo root:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install mcp playwright httpx
python -m playwright install
```

If you want to use Tavily, create an environment variable:

```powershell
$env:TAVILY_API_KEY="your-api-key"
```

---

## 4) Build the Python MCP server

Open `UpdatedLangchain/mcp_demo_server.py`.

This file does three important things:

1. creates an MCP server using `FastMCP`
2. exposes a Tavily search tool
3. exposes a Playwright Airbnb browser tool

Key pattern:

```python
mcp = FastMCP("airbnb-tavily-demo")

@mcp.tool()
def search_tavily(query: str, max_results: int = 5) -> str:
    ...
```

That decorator tells the MCP framework: "expose this function as a tool for the LLM to call."

---

## 5) What the Tavily tool does

The `search_tavily` tool sends a request to the Tavily API and returns structured results:

- title
- url
- content snippet
- answer summary

This makes it easy for an agent to rank sources, compare options, and continue reasoning.

Example:

```python
result = search_tavily("best family-friendly Airbnb in Bali")
```

The LLM can then decide whether to search again, narrow the query, or open Airbnb in a browser.

---

## 6) What the Airbnb tool does

The `open_airbnb_search` tool uses Playwright to open Airbnb and navigate the page.

This is useful for:

- checking how the page behaves in real life
- verifying UI changes
- extracting visible text from a live website
- testing browser-driven workflows

Important note:

Airbnb is a real website with dynamic UI structure, so selectors and page layouts can change. This demo keeps the browser flow simple and resilient instead of trying to scrape every detail.

---

## 7) Run the server

Start the server from the project root:

```bash
python UpdatedLangchain/mcp_demo_server.py
```

This launches the MCP server and exposes the tool list to connected clients.

---

## 8) Connect a client

The file `UpdatedLangchain/mcp_demo_client.py` shows how to connect to the server using Python.

This is the client-side workflow:

1. start the server as a subprocess
2. initialize the MCP session
3. list available tools
4. call a tool by name
5. print the result

That is the core of real MCP integration.

---

## 9) How to call tools from code

Here is a small example:

```python
result = await session.call_tool(
    "search_tavily",
    {"query": "best neighborhoods in Lisbon for a family trip", "max_results": 3},
)
```

This is exactly the pattern an LLM agent would use:

- decide on a tool
- send arguments
- receive formatted output
- continue the chain of reasoning

---

## 10) Connect to Playwright MCP in VS Code

Your workspace already has Playwright MCP config in `.vscode/mcp.json`:

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

This makes browser automation available to tools inside the editor environment.

For a richer setup, you can pair a browser tool with your Python MCP server and an LLM-powered agent.

---

## 11) A real agent flow

A realistic workflow looks like this:

1. User asks: "Find a family-friendly Airbnb in Bali for 2 adults and 2 kids."
2. LLM calls `search_tavily` to research neighborhoods.
3. LLM calls `open_airbnb_search` to inspect the site in a browser.
4. LLM compares the results and produces a recommendation.
5. The result is an answer based on live web data and browser context.

This is where MCP becomes valuable: the agent can use multiple tools in a controlled, standard way.

---

## 12) Deployment with Docker

For production, the MCP server can be containerized:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir mcp playwright httpx
RUN python -m playwright install

CMD ["python", "UpdatedLangchain/mcp_demo_server.py"]
```

Then build and run:

```bash
docker build -t mcp-demo .
docker run -it mcp-demo
```

This is ideal when you want the tool server to be portable, isolated, and easy to deploy.

---

## 13) Best practices

- keep tool functions small and explicit
- validate API keys before making calls
- return structured data instead of free-form text when possible
- handle browser selectors defensively
- separate research and browser tasks cleanly
- keep the LLM reasoning loop simple and explainable

---

## 14) Final takeaway

This demo shows the heart of MCP:

- the server exposes tools in a standard way
- the client discovers them without custom integration code
- the LLM can call them as needed
- external systems like Tavily and Airbnb become part of the agent workflow

That is the real power of MCP.

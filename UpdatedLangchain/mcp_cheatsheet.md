# MCP Cheat Sheet in Simple Words

## What is MCP?

MCP means **Model Context Protocol**.

MCP is a common way for an AI app to use outside tools.

Examples:

- A web-search tool
- A browser tool
- A database tool
- A file-reading tool
- A weather API

Think of MCP like a standard plug. An AI app can connect to many tools when each tool follows the same MCP rules.

## The Four Main Parts

### 1. User

The user asks for something:

```text
Find a family-friendly place to stay in Bali.
```

### 2. AI model

The model understands the request and chooses which tool it needs.

### 3. MCP client

The client connects the AI model to MCP servers. Examples include:

- Claude Desktop
- A Python application
- VS Code
- An AI agent

### 4. MCP server

The server provides the tools. In this project, the custom server provides:

- `search_tavily`
- `open_airbnb_search`
- `plan_airbnb_trip`

## How a Request Works

```text
User asks a question
        |
        v
AI chooses a tool
        |
        v
MCP client sends the request
        |
        v
MCP server runs the tool
        |
        v
Tool sends back a result
        |
        v
AI writes the final answer
```

The model does not need to know every API detail. It sees the tool name, description, and input fields.

## Tool, Resource, and Prompt

### Tool

A tool is an action that the AI can run.

Examples:

```text
search_tavily(query)
open_airbnb_search(city, check_in, check_out)
run_sql(query)
```

### Resource

A resource is information that the AI can read.

Examples:

```text
weather://bali
docs://project-guide
database://customers/42
```

### Prompt

A prompt is a saved instruction template that can be reused.

## A Very Small Python MCP Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-server")


@mcp.tool()
def get_weather(city: str) -> str:
    """Return a simple weather message."""
    return f"Weather in {city}: sunny"


if __name__ == "__main__":
    mcp.run()
```

The `@mcp.tool()` line publishes the Python function as an MCP tool.

## This Project's Server

File:

```text
UpdatedLangchain/mcp_demo_server.py
```

It contains three tools:

| Tool | Simple meaning |
| --- | --- |
| `search_tavily` | Search the web using Tavily. |
| `open_airbnb_search` | Open Airbnb in a Playwright browser. |
| `plan_airbnb_trip` | Combine travel research into a simple plan. |

## Install the Project

Open PowerShell in the project folder:

```powershell
cd "C:\Users\sibta\OneDrive\Documents\LearnAAI"
```

Create the Python environment if needed:

```powershell
python -m venv .venv
```

Install the Python packages:

```powershell
.\.venv\Scripts\python.exe -m pip install "mcp[cli]" mcp-use langchain-groq python-dotenv httpx playwright
```

Install the Chromium browser used by Playwright:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

Check Node.js because Playwright MCP and MCP Inspector use Node:

```powershell
node --version
npm --version
```

Use Node 22.19 or newer for the latest MCP Inspector.

## Add API Keys

Create `.env` in the project root:

```dotenv
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
GROQ_MODEL=qwen/qwen3.6-27b
```

Keep `.env` private. Never commit it to Git or paste real keys into documentation.

## Run the Small Python Client

The small client tests MCP without using the AI model:

```powershell
.\.venv\Scripts\python.exe .\UpdatedLangchain\mcp_demo_client.py
```

Use this when you want to check the server connection first.

## Run the Full Groq Agent

```powershell
.\.venv\Scripts\python.exe .\UpdatedLangchain\grok_mcp_agent.py
```

The agent connects to:

1. The Playwright MCP server.
2. The custom Python MCP server.
3. The Groq model.

It then asks the tools to research a trip and writes a recommendation.

## Playwright MCP

Playwright MCP gives the AI browser tools such as:

- Open a web page
- Click a button
- Fill a form
- Read page content
- Take a screenshot
- Switch browser tabs

The basic configuration is:

```json
{
  "playwright": {
    "command": "npx",
    "args": ["@playwright/mcp@latest"]
  }
}
```

## Tavily Search

Tavily is an API made for AI web research.

The custom server sends it:

```python
{
    "api_key": api_key,
    "query": query,
    "max_results": 5,
}
```

Tavily is usually better for research than asking a browser to repeatedly search Google or Bing. Search engines can block automated browsers.

## Open MCP Inspector

MCP Inspector lets you test tools by hand in a web page.

Use a forward slash in the npm package name:

```powershell
npx -y @modelcontextprotocol/inspector .\.venv\Scripts\python.exe .\UpdatedLangchain\mcp_demo_server.py
```

Do not use this incorrect form:

```powershell
npx -y @modelcontextprotocol\inspector ...
```

When Inspector starts, open the complete URL printed in the terminal. It usually begins with:

```text
http://127.0.0.1:6274/?MCP_INSPECTOR_API_TOKEN=
```

Keep the Inspector terminal open while using the page.

In Inspector, select **STDIO** and enter:

**Command**

```text
C:\Users\sibta\OneDrive\Documents\LearnAAI\.venv\Scripts\python.exe
```

**Arguments**

```text
C:\Users\sibta\OneDrive\Documents\LearnAAI\UpdatedLangchain\mcp_demo_server.py
```

Then click **Connect**.

## Test a Tool in Inspector

Test `plan_airbnb_trip` first:

```json
{
  "city": "Bali",
  "budget": "moderate"
}
```

Test `search_tavily` next:

```json
{
  "query": "family friendly neighborhoods in Bali",
  "max_results": 3
}
```

Test `open_airbnb_search` last:

```json
{
  "city": "Bali",
  "check_in": "2026-10-01",
  "check_out": "2026-10-05",
  "guests": 2
}
```

## Add to Claude Desktop

Claude Desktop can start this local MCP server.

Open:

```text
%APPDATA%\Claude\claude_desktop_config.json
```

Add this configuration and restart Claude Desktop:

```json
{
  "mcpServers": {
    "airbnb-tavily-demo": {
      "command": "C:\\Users\\sibta\\OneDrive\\Documents\\LearnAAI\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\sibta\\OneDrive\\Documents\\LearnAAI\\UpdatedLangchain\\mcp_demo_server.py"
      ]
    }
  }
}
```

Then ask Claude:

```text
List the tools from the airbnb-tavily-demo MCP server.
```

## ChatGPT Note

A local Windows stdio server usually cannot be added directly to ChatGPT web.

ChatGPT MCP connections generally need an authenticated public HTTPS MCP server. For local testing, use:

- MCP Inspector
- Claude Desktop
- The Python client
- The Groq agent

Do not expose this development server to the internet without authentication.

## What Each Project File Does

| File | Job |
| --- | --- |
| `mcp_demo_server.py` | Publishes the custom tools. |
| `mcp_demo_client.py` | Tests the MCP connection directly. |
| `grok_mcp_agent.py` | Uses Groq to choose and call tools. |
| `mcp_demo_tutorial.md` | Step-by-step learning tutorial. |
| `mcp_cheatsheet.md` | This quick reference. |
| `MCP_DEVELOPER_GUIDE.md` | Full installation and development guide. |
| `claude_desktop_config.example.json` | Claude Desktop configuration example. |
| `.env` | Local API keys and settings. |

## Simple Troubleshooting

### Tool says Tavily key is missing

Add this to `.env`:

```dotenv
TAVILY_API_KEY=your_tavily_key
```

### Inspector page does not open

Check that:

1. The Inspector terminal is still running.
2. You opened the complete tokenized URL.
3. Node.js is version 22.19 or newer.

### npm says `ENOENT` for Inspector

Use `/` between the package scope and name:

```powershell
@modelcontextprotocol/inspector
```

### Browser search returns 429 or `ERR_ABORTED`

Google and Bing may block automated browsers. Use Tavily for web search and use Playwright for known pages.

### Groq says the model is blocked

Set `GROQ_MODEL` to a model enabled in your Groq project:

```powershell
$env:GROQ_MODEL="your-enabled-model"
```

## Remember This

```text
MCP gives an AI standard tools.
The MCP server provides the tools.
The MCP client connects to the tools.
The AI model decides when to use them.
```

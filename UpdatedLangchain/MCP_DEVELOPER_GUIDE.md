# MCP Travel Planner Developer Guide

## 1. Purpose

This document explains how the MCP travel-planning project works, how to install it, how to run each component, and how to troubleshoot the common failures.

The project demonstrates an agent that can:

1. Receive a travel-planning request.
2. Use Groq for language-model reasoning.
3. Discover tools through the Model Context Protocol.
4. Search the web with Tavily.
5. Open browser pages with Playwright.
6. Inspect Airbnb pages.
7. Combine tool results into a travel recommendation.

The model does not directly contain the Tavily or Playwright integration. MCP exposes those integrations as tools that the model can discover and call.

## 2. What MCP Means

MCP stands for **Model Context Protocol**.

MCP is a standard communication protocol between an AI application and external capabilities such as:

- APIs
- databases
- files
- browsers
- internal business services
- custom Python functions

An MCP server publishes capabilities. An MCP client connects to that server and discovers the capabilities. An AI agent uses the discovered capabilities while answering a user request.

```text
AI application / agent
        |
        v
     MCP client
        |
        +--> MCP server: Tavily and Airbnb tools
        |
        +--> MCP server: Playwright browser tools
```

## 3. Project Components

### 3.1 Custom MCP server

File:

```text
UpdatedLangchain/mcp_demo_server.py
```

This is a Python MCP server built with FastMCP. It exposes:

| Tool | Responsibility |
| --- | --- |
| `search_tavily` | Sends a search request to the Tavily API. |
| `open_airbnb_search` | Opens Airbnb through Playwright and reports the page state. |
| `plan_airbnb_trip` | Provides a simple research workflow combining travel information. |

The server communicates over standard input/output, also called **stdio**. The MCP client or Inspector starts this Python process and exchanges JSON-RPC messages with it.

### 3.2 Python MCP client

File:

```text
UpdatedLangchain/mcp_demo_client.py
```

This is the small client example. It demonstrates the lower-level MCP workflow:

1. Start the Python MCP server.
2. Establish a stdio connection.
3. Create a client session.
4. List available tools.
5. Call a tool.
6. Display the result.

### 3.3 Groq MCP agent

File:

```text
UpdatedLangchain/grok_mcp_agent.py
```

This is the complete AI workflow. It uses:

- `ChatGroq` for model reasoning
- `MCPClient` for MCP connections
- `MCPAgent` for tool-aware execution
- Playwright MCP for browser tools
- the custom Python MCP server for Tavily and Airbnb tools

The agent receives a structured travel prompt and decides which tools to call.

### 3.4 Playwright MCP server

The project connects to the official Playwright MCP server through `npx`:

```json
{
  "playwright": {
    "command": "npx",
    "args": ["@playwright/mcp@latest"]
  }
}
```

This server exposes browser operations such as:

- navigate to a URL
- click an element
- fill a form
- take a screenshot
- inspect the page
- select an option
- wait for page content
- manage browser tabs

### 3.5 MCP Inspector

MCP Inspector is a browser-based development tool for manually connecting to an MCP server, listing tools, viewing schemas, and calling tools without using the Groq agent.

It is useful for testing one tool at a time before debugging the complete agent.

## 4. Prerequisites

Install the following software:

| Software | Purpose | Recommended version |
| --- | --- | --- |
| Python | Runs the custom MCP server and agent | 3.14 or newer supported by the project |
| Node.js | Runs Playwright MCP and MCP Inspector | 22.19 or newer |
| npm | Installs JavaScript MCP packages | Installed with Node.js |
| Git | Source control | Current version |
| VS Code | Development environment | Current version |
| Chromium | Playwright browser runtime | Installed through Playwright |

Check the installed versions:

```powershell
python --version
node --version
npm --version
git --version
```

The current project uses Python 3.14 and Node 24 successfully.

## 5. Install Python

On Windows, install Python from the official Python website or with the Windows Package Manager:

```powershell
winget install Python.Python.3.14
```

Open a new terminal after installation and check:

```powershell
python --version
```

If Windows uses another Python installation, use the project virtual environment commands shown below rather than relying on the global `python` command.

## 6. Install Node.js

Install Node.js LTS:

```powershell
winget install --id OpenJS.NodeJS.LTS -e --source winget
```

Close and reopen PowerShell or VS Code after installation. Verify:

```powershell
node --version
npm --version
```

The latest MCP Inspector requires a modern Node version. If the command reports Node 20 or older, upgrade Node before running Inspector.

## 7. Create or Activate the Python Environment

From the repository root:

```powershell
cd "C:\Users\sibta\OneDrive\Documents\LearnAAI"
```

Create a virtual environment if `.venv` does not exist:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

The prompt should show the environment name, usually `(venv)` or `(LearnAAI)`.

The project also supports calling the virtual-environment interpreter directly without activation:

```powershell
.\.venv\Scripts\python.exe
```

Using the direct path is recommended when MCP launches a subprocess on Windows.

## 8. Install Python Dependencies

The project dependencies are defined in `pyproject.toml`.

Install the project with `uv` if `uv` is available:

```powershell
uv sync
```

Alternatively, install the requirements with pip:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Install the core MCP packages if they are not already installed:

```powershell
.\.venv\Scripts\python.exe -m pip install "mcp[cli]" mcp-use langchain-groq python-dotenv httpx playwright
```

The important Python packages are:

- `mcp`: Python MCP SDK and FastMCP server support
- `mcp-use`: MCP client and agent integration with LangChain
- `langchain-groq`: Groq integration for LangChain
- `python-dotenv`: Loads `.env` values
- `httpx`: Sends HTTP requests to Tavily
- `playwright`: Controls Chromium

## 9. Install the Playwright Browser

Python packages alone do not install the browser executable. Install Chromium separately:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

To install all supported Playwright browsers instead:

```powershell
.\.venv\Scripts\python.exe -m playwright install
```

Test that the Playwright package is available:

```powershell
.\.venv\Scripts\python.exe -c "from playwright.sync_api import sync_playwright; print('playwright_ok')"
```

## 10. Configure Environment Variables

Create or update `.env` in the repository root.

Use placeholders while documenting the project:

```dotenv
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
GROQ_MODEL=qwen/qwen3.6-27b
```

The code accepts either `GROQ_API_KEY` or the lowercase `groq_api_key`, but uppercase names are preferred.

Never commit `.env` to Git. Confirm that `.gitignore` includes:

```text
.env
.env.*
```

If an API key has been pasted into a public issue, chat, screenshot, commit, or shared document, revoke it and create a replacement key.

## 11. How the Custom Server Starts

When the custom server runs directly, this code starts the MCP stdio transport:

```python
if __name__ == "__main__":
    mcp.run()
```

Run it directly for a basic startup check:

```powershell
.\.venv\Scripts\python.exe .\UpdatedLangchain\mcp_demo_server.py
```

A stdio MCP server may appear to do nothing in the terminal because it is waiting for JSON-RPC messages. That is normal. Do not type ordinary text into the process. Stop it with `Ctrl+C` after the startup check.

The server should be started by an MCP client or Inspector for real tool calls.

## 12. How the Python Client Works

The client starts the server as a subprocess and opens an MCP session. The important sequence is:

```text
start subprocess
      |
      v
create stdio transport
      |
      v
initialize MCP session
      |
      v
list tools
      |
      v
call selected tool
```

Run the small client example:

```powershell
.\.venv\Scripts\python.exe .\UpdatedLangchain\mcp_demo_client.py
```

This is the best first code-level test because it does not require Groq model reasoning.

## 13. How the Groq Agent Works

Run the complete agent with:

```powershell
.\.venv\Scripts\python.exe .\UpdatedLangchain\grok_mcp_agent.py
```

The agent performs these steps:

### Step 1: Load configuration

`load_dotenv()` loads values from `.env`.

### Step 2: Build the MCP configuration

The agent creates two connections:

1. Playwright MCP through `npx`.
2. The custom Python server through the project virtual environment.

The custom server configuration uses an absolute Python path to avoid Windows path and quoting problems.

### Step 3: Build the Groq model

The agent reads the API key and selects a model. The default verified model is:

```text
qwen/qwen3.6-27b
```

The code also sets a small output-token limit because the project has a strict Groq output quota:

```python
max_tokens=900
```

Override the model when necessary:

```powershell
$env:GROQ_MODEL="your-enabled-model"
.\.venv\Scripts\python.exe .\UpdatedLangchain\grok_mcp_agent.py
```

### Step 4: Initialize the MCP agent

The agent calls:

```python
await agent.initialize()
```

During initialization, the MCP client starts both servers and discovers their capabilities.

### Step 5: Send the travel request

The prompt includes:

- destination
- check-in date
- check-out date
- number of guests
- budget style
- required research steps

### Step 6: Select tools

The Groq model decides whether to call:

- `search_tavily`
- `open_airbnb_search`
- Playwright browser tools
- `plan_airbnb_trip`

### Step 7: Return the recommendation

The agent combines tool results and returns a concise travel recommendation.

## 14. How to Use MCP Inspector

### 14.1 Start Inspector

The normal command is:

```powershell
npx -y @modelcontextprotocol/inspector .\.venv\Scripts\python.exe .\UpdatedLangchain\mcp_demo_server.py
```

Important: the npm package scope uses `/`, not `\`:

```text
@modelcontextprotocol/inspector
```

Do not write:

```text
@modelcontextprotocol\inspector
```

That makes npm look for a local folder instead of downloading the package.

### 14.2 Open the Inspector URL

The terminal prints a URL similar to:

```text
http://127.0.0.1:6274/?MCP_INSPECTOR_API_TOKEN=YOUR_TOKEN
```

Open the complete URL printed by your terminal. The token is part of the session URL.

Keep the terminal open. Inspector stops when its terminal process stops.

### 14.3 Connect to the Python server

In Inspector, choose the STDIO transport and enter:

**Command**

```text
C:\Users\sibta\OneDrive\Documents\LearnAAI\.venv\Scripts\python.exe
```

**Arguments**

```text
C:\Users\sibta\OneDrive\Documents\LearnAAI\UpdatedLangchain\mcp_demo_server.py
```

Click **Connect**.

### 14.4 Test tools manually

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

Testing tools individually makes it clear whether a problem is in MCP, Tavily, Playwright, or Groq.

## 15. MCP Inspector Native-Dependency Workaround

If `npx` fails with:

```text
Cannot find native binding
```

Install Inspector in a clean temporary directory:

```powershell
$installRoot = Join-Path $env:TEMP "mcp-inspector-clean"
Remove-Item -Recurse -Force $installRoot -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $installRoot | Out-Null
npm install --prefix $installRoot --include=optional --no-package-lock @modelcontextprotocol/inspector@latest
& (Join-Path $installRoot "node_modules\.bin\mcp-inspector.cmd") .\.venv\Scripts\python.exe .\UpdatedLangchain\mcp_demo_server.py
```

This was the verified workaround in this workspace.

## 16. VS Code MCP Configuration

The workspace contains:

```text
.vscode/mcp.json
```

It configures the Playwright server for VS Code:

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

This lets VS Code provide Playwright MCP tools in environments that support the workspace MCP configuration.

The Python agent has its own configuration in `grok_mcp_agent.py` because it also needs the custom Python server.

## 17. Testing Checklist

Run these checks in order:

### Syntax check

```powershell
.\.venv\Scripts\python.exe -m py_compile .\UpdatedLangchain\mcp_demo_server.py .\UpdatedLangchain\mcp_demo_client.py .\UpdatedLangchain\grok_mcp_agent.py
```

### Dependency check

```powershell
.\.venv\Scripts\python.exe -c "import mcp, mcp_use, playwright, httpx, dotenv, langchain_groq; print('dependencies_ok')"
```

### Browser check

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

### Direct client check

```powershell
.\.venv\Scripts\python.exe .\UpdatedLangchain\mcp_demo_client.py
```

### Inspector check

Start Inspector and confirm that the three custom tools are visible.

### Agent check

```powershell
.\.venv\Scripts\python.exe .\UpdatedLangchain\grok_mcp_agent.py
```

## 18. Troubleshooting

### Inspector page does not load

Check that the Inspector terminal is still running. Confirm the terminal printed:

```text
MCP Inspector Web is up and running
```

Use the complete tokenized URL and prefer:

```text
http://127.0.0.1:6274
```

### `ENOENT` for `@modelcontextprotocol\inspector`

Use `/` in the package name:

```powershell
npx -y @modelcontextprotocol/inspector ...
```

### `styleText` export error

Upgrade Node.js. The latest Inspector requires a modern Node runtime.

### Native binding error

Use the clean temporary install in section 15.

### Tavily key missing

Add this to `.env`:

```dotenv
TAVILY_API_KEY=your_tavily_key
```

The custom server calls `load_dotenv()` so Inspector-launched processes can read the repository environment file.

### Groq model not found

Set `GROQ_MODEL` to a model enabled for the Groq project. The model list can contain models that are visible but blocked by project permissions.

### Groq model permission blocked

Open the Groq project model settings and enable the selected model, or choose another enabled model through `GROQ_MODEL`.

### Groq output-token limit

The agent uses `max_tokens=900` because the project previously rejected the default 2,048-token request.

### Google or Bing browser errors

Automated browser requests can receive HTTP 429, `ERR_ABORTED`, bot checks, or redirects. Use Tavily for search and Playwright for known destination or listing pages. Do not depend on repeated search-engine navigation.

### Agent recursion limit

If the model repeatedly retries blocked browser searches, it may reach the LangGraph recursion limit. Configure Tavily first, reduce unnecessary browser-search instructions, and test the tools individually in Inspector.

## 19. Expected Successful Initialization

A healthy agent startup includes messages similar to:

```text
Created 2 new sessions
Created 27 LangChain tools from client
Found 27 tools across all connectors
Agent initialization complete
```

The 27 tools consist of the Playwright browser tools plus the three custom Python tools.

## 20. Responsibility Summary

| Component | Main responsibility |
| --- | --- |
| Groq | Understands the request and chooses tools. |
| `MCPAgent` | Runs the tool-aware agent loop. |
| `MCPClient` | Connects the application to MCP servers. |
| FastMCP server | Publishes custom Python functions as MCP tools. |
| Tavily | Provides API-based web research. |
| Playwright MCP | Provides browser automation capabilities. |
| MCP Inspector | Manually tests MCP connections and tools. |
| `.env` | Stores local credentials and configuration. |
| `.venv` | Isolates Python packages for this project. |

## 21. Recommended Developer Workflow

Use this order when changing the project:

1. Edit the custom tool in `mcp_demo_server.py`.
2. Run the Python syntax check.
3. Start Inspector.
4. Call the changed tool manually.
5. Confirm its return value is structured and useful.
6. Run the standalone Python client.
7. Run the full Groq agent.
8. Check that the agent uses the tool correctly.
9. Update the tutorial or this developer guide if behavior changes.

This isolates failures early and avoids debugging the model, MCP transport, browser, and external APIs at the same time.

## 22. Current Project State

The project has achieved the following:

- Custom Python MCP server implemented.
- Tavily search tool implemented.
- Airbnb Playwright tool implemented.
- Python MCP client implemented.
- Groq MCP agent implemented.
- `.env` loading added to the agent and server.
- Windows virtual-environment subprocess path configured.
- Playwright Chromium installed.
- MCP Inspector installed and started successfully through a clean npm directory.
- MCP initialization verified with two active server sessions.
- 27 MCP tools discovered by the agent.
- Groq model access verified with `qwen/qwen3.6-27b`.

The remaining external setup items are:

- provide a valid `TAVILY_API_KEY`
- use the tokenized Inspector URL
- avoid search engines that block automated navigation
- rotate any credentials that have been exposed in shared files or logs

## 23. Add the Server to Claude Desktop

Claude Desktop can launch local stdio MCP servers directly.

### 23.1 Find the Claude configuration file

On Windows, close Claude Desktop and open:

```text
%APPDATA%\Claude\claude_desktop_config.json
```

Create the file if it does not exist.

### 23.2 Add the custom server

Use the example configuration at:

```text
UpdatedLangchain/claude_desktop_config.example.json
```

The important server entry is:

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

Windows paths need double backslashes in JSON. Do not use the Inspector URL in Claude Desktop; Claude launches the stdio server directly.

### 23.3 Restart and verify

Restart Claude Desktop and ask:

```text
List the tools provided by the airbnb-tavily-demo MCP server.
```

Claude should discover:

- `search_tavily`
- `open_airbnb_search`
- `plan_airbnb_trip`

Then test the server with:

```text
Use plan_airbnb_trip for Bali with a moderate budget.
```

The server now loads `.env` from the repository path, so Claude does not need to start in the project directory.

### 23.4 Claude troubleshooting

If Claude cannot start the server:

1. Confirm the Python executable path exists.
2. Confirm the MCP server script path exists.
3. Run the same command manually in PowerShell.
4. Confirm Node.js is available if the Playwright server is enabled.
5. Confirm `TAVILY_API_KEY` is present in `.env`.
6. Review Claude Desktop MCP logs.

Start with only `airbnb-tavily-demo` enabled. Add the Playwright server after the custom server works.

## 24. Add the Server to ChatGPT

ChatGPT integrations depend on the account plan, workspace settings, and current MCP connector support. A local Windows stdio command normally cannot be registered directly in the ChatGPT web application.

ChatGPT MCP connections generally require a remotely reachable MCP server using an HTTP-based transport. This local command is for Claude Desktop, Inspector, and local Python clients:

```text
python UpdatedLangchain/mcp_demo_server.py
```

It is not automatically reachable by ChatGPT over the internet.

To use this project with ChatGPT, the usual architecture is:

```text
ChatGPT
   |
   | HTTPS MCP connection
   v
Public authenticated MCP endpoint
   |
   v
Python MCP server
   |
   +--> Tavily
   +--> Playwright
```

You would need to:

1. Run the MCP server with an HTTP-capable transport.
2. Deploy it to a service with a public HTTPS URL.
3. Add authentication and request validation.
4. Keep API keys on the server, never in the ChatGPT request.
5. Register the HTTPS endpoint in the ChatGPT connector or developer tools interface available to your account.

Do not expose a development server directly to the public internet without authentication. Do not use a temporary tunnel as a production deployment.

For local development, use Claude Desktop, MCP Inspector, `mcp_demo_client.py`, or `grok_mcp_agent.py`.

## 25. Host Selection Summary

| Host | Local stdio server | Public HTTPS server | Recommended use |
| --- | --- | --- | --- |
| MCP Inspector | Yes | Yes | Tool-by-tool testing |
| Claude Desktop | Yes | Depends on connector support | Local desktop assistant |
| Python `MCPClient` | Yes | Yes | Application development |
| ChatGPT web | Usually no | Typically required | Hosted MCP integration |

For this project, use Claude Desktop or MCP Inspector first. Move to ChatGPT after the server has an authenticated HTTPS deployment.

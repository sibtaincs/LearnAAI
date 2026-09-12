# MCP Travel Planner: Project Progress

## What We Built

This project is a Python MCP travel-planning demo that combines:

- Groq as the language model
- `mcp-use` as the MCP client and agent framework
- A custom Python MCP server
- Tavily web search
- Playwright browser automation
- Airbnb page inspection
- MCP Inspector for manually testing tools

The workflow is designed so the language model does not directly own the integrations. Instead, the model discovers and calls tools exposed through MCP.

```text
User request
    |
    v
Groq + MCPAgent
    |
    v
MCPClient
    |
    +--> Playwright MCP server
    |       |
    |       +--> Browser automation
    |
    +--> Custom Python MCP server
            |
            +--> Tavily search tool
            +--> Airbnb Playwright tool
            +--> Travel-planning helper tool
```

## Files Created or Updated

### `mcp_demo_server.py`

The custom MCP server is located at:

`UpdatedLangchain/mcp_demo_server.py`

It exposes three tools:

| Tool | Purpose |
| --- | --- |
| `search_tavily` | Searches the web through Tavily and returns compact results. |
| `open_airbnb_search` | Opens Airbnb with Playwright and returns the page state. |
| `plan_airbnb_trip` | Runs a small research-oriented travel-planning workflow. |

The server uses FastMCP and communicates over standard input/output, which is the normal local MCP transport.

The server also loads the repository `.env` file when it starts. This is important because MCP Inspector launches the server as a separate process.

### `mcp_demo_client.py`

This is the minimal Python MCP client example. It demonstrates how to:

1. Start the server as a subprocess.
2. Create an MCP session.
3. Discover the available tools.
4. Call a tool directly.
5. Print the tool result.

### `grok_mcp_agent.py`

This is the full agent example at:

`UpdatedLangchain/grok_mcp_agent.py`

It:

1. Loads the Groq key from `.env`.
2. Builds the MCP server configuration.
3. Connects to both Playwright MCP and the custom Python MCP server.
4. Discovers the tools.
5. Sends the travel-planning request to Groq.
6. Allows the model to choose MCP tools.
7. Prints the final recommendation.

The code uses the repository virtual environment directly on Windows:

```text
.venv\Scripts\python.exe
```

This avoids accidentally starting the server with a different system Python installation.

### `mcp_demo_tutorial.md`

This contains the step-by-step tutorial for the Python MCP server, Tavily, Playwright, Airbnb, and the agent workflow.

### `mcp_cheatsheet.md`

This contains the one-page MCP reference with the key concepts, commands, and code patterns.

## Environment Setup

The project uses a virtual environment in `.venv` and Python 3.14.

The important packages are declared in `pyproject.toml`:

- `mcp`
- `mcp-use`
- `langchain-groq`
- `python-dotenv`
- `playwright`
- `httpx`

Install the browser runtime once:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

The `.env` file is used for credentials. The code accepts both uppercase and lowercase Groq variable names:

```text
GROQ_API_KEY=...
```

or:

```text
groq_api_key=...
```

For Tavily, add:

```text
TAVILY_API_KEY=...
```

## Problems We Solved

### 1. Async API usage

The original agent called asynchronous methods without awaiting them. The agent now correctly uses:

```python
await agent.initialize()
await agent.run(prompt)
```

### 2. `.env` loading

The Groq key was stored in `.env`, but the application did not initially load it. `python-dotenv` is now used by both the agent and the standalone MCP server.

### 3. Windows subprocess paths

The custom MCP server is started with the absolute path to the project virtual environment and the absolute path to the server script. This avoids Windows quoting problems and system-Python mismatches.

### 4. MCP stdio startup

The MCP stdio startup issue was isolated to the launch configuration. The working configuration uses the Python executable as the command and the server script as its argument:

```python
{
    "command": "C:/path/to/.venv/Scripts/python.exe",
    "args": ["C:/path/to/UpdatedLangchain/mcp_demo_server.py"]
}
```

### 5. Groq model availability

The original model name, `llama-3.3-70b-versatile`, was not available to this Groq project. The live model list was checked, and `qwen/qwen3.6-27b` successfully accepted a test completion.

The agent now prefers:

```text
qwen/qwen3.6-27b
```

A custom model can still be selected with:

```text
GROQ_MODEL=your-model-id
```

### 6. Groq output-token quota

The project enforced a 1,000 output-token limit for the working model, while LangChain requested 2,048 tokens by default. The agent now sets:

```python
max_tokens=900
```

This keeps the request below the verified project limit.

### 7. MCP Inspector package syntax

On Windows, this is incorrect because the backslash is interpreted as a local path:

```powershell
npx -y @modelcontextprotocol\inspector ...
```

The package name must use a forward slash:

```powershell
npx -y @modelcontextprotocol/inspector ...
```

### 8. Node.js compatibility

The latest MCP Inspector requires a modern Node.js version. The machine was upgraded from Node 20 to Node 24, which satisfies the requirement.

### 9. Inspector native dependency installation

The default `npx` installation encountered an npm optional-dependency/native-binding problem. Inspector was successfully installed in a clean temporary npm directory with optional dependencies enabled.

## How to Open MCP Inspector

From the project root, the direct command is:

```powershell
npx -y @modelcontextprotocol/inspector .\.venv\Scripts\python.exe .\UpdatedLangchain\mcp_demo_server.py
```

If npm reports the native-binding error again, use the clean installation approach:

```powershell
$installRoot = Join-Path $env:TEMP "mcp-inspector-clean"
Remove-Item -Recurse -Force $installRoot -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $installRoot | Out-Null
npm install --prefix $installRoot --include=optional --no-package-lock @modelcontextprotocol/inspector@latest
& (Join-Path $installRoot "node_modules\.bin\mcp-inspector.cmd") .\.venv\Scripts\python.exe .\UpdatedLangchain\mcp_demo_server.py
```

Inspector starts at a URL similar to:

```text
http://127.0.0.1:6274/?MCP_INSPECTOR_API_TOKEN=YOUR_SESSION_TOKEN
```

Use the complete URL printed by the terminal. The session token is required.

Keep the Inspector terminal open while using the web interface. Closing that terminal stops the Inspector server.

## How to Connect Inside Inspector

Use these connection values:

**Transport:** `STDIO`

**Command:**

```text
C:\Users\sibta\OneDrive\Documents\LearnAAI\.venv\Scripts\python.exe
```

**Arguments:**

```text
C:\Users\sibta\OneDrive\Documents\LearnAAI\UpdatedLangchain\mcp_demo_server.py
```

After clicking **Connect**, the following tools should be visible:

- `search_tavily`
- `open_airbnb_search`
- `plan_airbnb_trip`

Example input for `plan_airbnb_trip`:

```json
{
  "city": "Bali",
  "budget": "moderate"
}
```

Example input for `open_airbnb_search`:

```json
{
  "city": "Bali",
  "check_in": "2026-10-01",
  "check_out": "2026-10-05",
  "guests": 2
}
```

## Verified Results

The end-to-end agent successfully reached the MCP layer and reported:

```text
Created 2 new sessions
Created 27 LangChain tools from client
Found 27 tools across all connectors
Agent initialization complete
```

The discovered tools included:

- 24 Playwright browser tools
- `search_tavily`
- `open_airbnb_search`
- `plan_airbnb_trip`

The custom server also passed a Python syntax check:

```text
server_compile_ok
```

## Current Limitations

### Tavily credential

The custom server returns a helpful missing-key message when `TAVILY_API_KEY` is not configured. Add the key to `.env` before testing `search_tavily`.

### Search-engine blocking

Google and Bing may return HTTP 429, `ERR_ABORTED`, or bot-protection responses when automated browser navigation is used. This is an external website restriction, not an MCP protocol failure.

The agent should prefer the Tavily API for research and use Playwright for targeted page interaction rather than repeatedly navigating search engines.

### Agent recursion

If the model keeps retrying blocked browser searches, the agent can reach its recursion limit. A stable production workflow should:

- use Tavily first when its key is configured
- avoid generic Google/Bing search navigation
- use browser tools for known destination or listing pages
- keep the number of agent steps limited

### API key security

Never commit `.env` to git. Any API keys that have been pasted into logs, chat, screenshots, or shared files should be revoked and replaced.

## Recommended Next Run

1. Add `TAVILY_API_KEY` to `.env`.
2. Open MCP Inspector.
3. Connect using the STDIO values above.
4. Call `search_tavily` directly first.
5. Call `plan_airbnb_trip` next.
6. Test `open_airbnb_search` only after Chromium is installed.
7. Run the full Groq agent after the individual tools work.

Run the full agent with:

```powershell
.\.venv\Scripts\python.exe UpdatedLangchain\grok_mcp_agent.py
```

## Final State

The project now has a complete educational MCP stack:

- a custom Python MCP server
- a standalone Python MCP client
- a Groq-powered MCP agent
- Playwright browser integration
- Tavily search integration
- MCP Inspector support
- setup documentation and a cheat sheet

The remaining work is configuration and external-service reliability: provide the Tavily key, use the Inspector session URL, and avoid relying on search engines that block automated browser traffic.

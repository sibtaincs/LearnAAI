"""Full end-to-end MCP travel planning agent for this repository.

This version is designed to behave like a real travel planning workflow:
1. research destinations using Tavily search
2. inspect Airbnb via Playwright browser tooling
3. compare neighborhoods and lodging fit
4. produce a concise recommendation for the user

The key point is that the LLM does not directly call the websites or APIs itself.
Instead, MCP exposes the tools to the model in a standardized way, and the model
selects which tool to call based on the user request.
"""

import asyncio
import os
from pathlib import Path
from typing import Any

import groq
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient

# Load environment variables from the repo's .env file.
load_dotenv()


# ---------------------------------------------------------------------------
# 1) MCP server configuration
# ---------------------------------------------------------------------------
# This config is purposely aligned with the workspace. It connects the agent to:
# - a local Python MCP server we created for Tavily + Airbnb helpers
# - the browser automation server (Playwright)

def build_mcp_config() -> dict[str, Any]:
    """Return the MCP config accessed by the travel-planning agent."""
    repo_root = Path(__file__).resolve().parent.parent
    server_script = repo_root / "UpdatedLangchain" / "mcp_demo_server.py"
    venv_python = repo_root / ".venv" / "Scripts" / "python.exe"

    return {
        "mcpServers": {
            "playwright": {
                "command": "npx",
                "args": ["@playwright/mcp@latest"],
            },
            "airbnb_tavily_demo": {
                "command": str(venv_python),
                "args": [str(server_script)],
            },
        }
    }


# ---------------------------------------------------------------------------
# 2) LLM configuration
# ---------------------------------------------------------------------------
# This repo already includes Groq support through langchain-groq.
# In a real production setup, you would store GROQ_API_KEY in your environment or secret manager.
def build_llm() -> ChatGroq:
    """Build the reasoning model for the agent."""
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("groq_api_key")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Set it in the environment or .env before running this demo."
        )

    preferred_model = os.getenv("GROQ_MODEL") or os.getenv("groq_model") or "qwen/qwen3.6-27b"

    try:
        client = groq.Groq(api_key=api_key)
        available = getattr(client.models.list(), "data", [])
        available_ids = {model.id for model in available}

        for candidate in (preferred_model, "qwen/qwen3.6-27b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b", "groq/compound", "groq/compound-mini"):
            if candidate in available_ids:
                model_name = candidate
                break
        else:
            model_name = preferred_model if available_ids else preferred_model
    except Exception:
        model_name = preferred_model

    return ChatGroq(
        model=model_name,
        temperature=0,
        max_tokens=900,
        api_key=api_key,
    )


# ---------------------------------------------------------------------------
# 3) Travel-planning prompt
# ---------------------------------------------------------------------------
def build_trip_prompt(city: str, check_in: str, check_out: str, guests: int, budget: str) -> str:
    """Create a realistic structured prompt for the travel-planning agent."""
    return f"""
    You are a travel planner and local research assistant.

    Plan a family-friendly trip for:
    - city: {city}
    - arrival: {check_in}
    - departure: {check_out}
    - guests: {guests}
    - budget style: {budget}

    You must do the following in order:
    1. Use web search to identify the best neighborhoods for families in {city}.
    2. Compare a few neighborhoods by convenience, safety, family appeal, and value.
    3. Use browser tools to inspect Airbnb-related pages when needed.
    4. Recommend the best area and explain why it fits this trip.
    5. Give a short final recommendation with 2-3 neighborhoods and a practical summary.

    Be concise but useful. Prefer actionable recommendations over generic travel advice.
    """


# ---------------------------------------------------------------------------
# 4) Agent runner
# ---------------------------------------------------------------------------
async def run_airbnb_agent_async(
    city: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
    budget: str = "moderate",
) -> str:
    """Run the full MCP-powered Airbnb travel planning workflow asynchronously."""
    client = MCPClient(config=build_mcp_config())
    llm = build_llm()

    # A custom system prompt makes the agent behave like a grounded planner instead of a free-form chatbot.
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=10,
        verbose=True,
        pretty_print=True,
        system_prompt=(
            "You are an agent that researches travel options using MCP tools. "
            "Use web research first, then browser tools when needed, and then provide a "
            "clear recommendation based on evidence."
        ),
    )

    await agent.initialize()

    prompt = build_trip_prompt(city, check_in, check_out, guests, budget)
    return await agent.run(prompt)


async def main() -> None:
    # Full example: a realistic travel-planning request using the MCP tool stack.
    print("\nStarting end-to-end MCP travel planner...\n")
    result = await run_airbnb_agent_async(
        city="Bali",
        check_in="2026-10-01",
        check_out="2026-10-05",
        guests=2,
        budget="moderate",
    )

    print("\nFinal travel recommendation from the MCP agent:\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

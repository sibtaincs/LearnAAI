"""Demo MCP server combining Tavily search and a Playwright-based Airbnb browser flow.

This file shows how to build a small Python MCP server that exposes tools to an LLM.
It is designed to work with the MCP ecosystem and is intentionally documented with
comments so beginners can follow the flow step by step.

How it works:
1. The server exposes one tool for Tavily web search.
2. The server exposes another tool for opening Airbnb in a browser.
3. An MCP client can discover and call these tools dynamically.
4. The LLM can decide which tool to use based on the user request.
"""

import os
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright

load_dotenv()

# Create the MCP server instance.
# The server name is what the client will see when it discovers tools.
mcp = FastMCP("airbnb-tavily-demo")


@mcp.tool()
def search_tavily(query: str, max_results: int = 5) -> str:
    """Search the web using the Tavily API.

    Args:
        query: The text to search for.
        max_results: Number of results to return.

    Returns:
        A compact JSON-style string containing research results.
    """
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return (
            "TAVILY_API_KEY is missing. Add it to your environment before using "
            "this tool. Example: $env:TAVILY_API_KEY='your_key_here'"
        )

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "include_answer": True,
        "include_raw_content": False,
    }

    try:
        response = httpx.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Keep the output easy for an LLM to read.
        results = []
        for item in data.get("results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")[:400],
                }
            )

        answer = data.get("answer", "")
        return {
            "answer": answer,
            "results": results,
        }
    except Exception as exc:  # pragma: no cover - this is a demo tool
        return {"error": f"Tavily request failed: {exc}"}


@mcp.tool()
def open_airbnb_search(city: str, check_in: str, check_out: str, guests: int = 2) -> str:
    """Open Airbnb in a browser and return a quick summary of the page state.

    This is a good example of how an MCP tool can interact with a browser UI using
    Playwright. The LLM can decide to use this when it needs to inspect a real web page,
    not just use a text search API.
    """
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()

            # Go to the Airbnb homepage.
            page.goto("https://www.airbnb.com/", wait_until="domcontentloaded")

            # Try to fill generic search fields if the page exposes them.
            # Airbnb's UI can change often, so keep this friendly and resilient.
            try:
                page.get_by_placeholder("Where to?").fill(city)
            except Exception:
                pass

            try:
                page.locator('button:has-text("Search")').click()
            except Exception:
                pass

            # Give the page a moment to render.
            page.wait_for_timeout(3000)

            return {
                "city": city,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "title": page.title(),
                "url": page.url,
                "description": "Airbnb page opened successfully via Playwright.",
            }
    except Exception as exc:  # pragma: no cover - demo example
        return {"error": f"Playwright Airbnb flow failed: {exc}"}


@mcp.tool()
def plan_airbnb_trip(city: str, budget: str = "moderate") -> str:
    """Create a simple travel-planning workflow for Airbnb + web research.

    In a real agent system, you would call Tavily first to gather destination data,
    then use Playwright to inspect the actual Airbnb page, and then summarize the best option.
    """
    search_query = f"best neighborhoods in {city} for a {budget} trip"
    tavily_results = search_tavily(search_query, max_results=3)
    return {
        "city": city,
        "budget": budget,
        "research": tavily_results,
        "next_step": "Open Airbnb search page for the destination and compare listings.",
    }


if __name__ == "__main__":
    # This is what starts the MCP server.
    # A client can connect to this process and list the tools exposed by the server.
    mcp.run()

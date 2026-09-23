from mcp.server.fastmcp import FastMCP

mcp= FastMCP("math")
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b  
@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b


#the transport is stdio, arguments to tell the servicer to;
#use standard input and output  to receive and send message to tool functions call
if __name__ == "__main__":
    mcp.run(transport="stdio")



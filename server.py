from fastmcp import  FastMCP

app = FastMCP("my server")

@app.tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@app.tool
def subtract(a: int, b: int) -> int:
    """Subtract one number from another."""
    return a - b

if __name__ == "__main__":
    app.run(transport="http", host="0.0.0.0", port=8000, path="/")
    # app.http_app(path="/api/mcp/")
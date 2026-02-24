from fastapi import FastAPI
from pydantic import BaseModel
from client import MCPClient

app = FastAPI()
client = MCPClient(["python", "server.py"])

class ToolCallRequest(BaseModel):
    name: str
    arguments: dict

@app.get("/tools")
def get_tools():
    return client.list_tools()

@app.post("/call")
def call_tool(request: ToolCallRequest):
    return client.call_tool(request.name, request.arguments)
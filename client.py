import subprocess
import json
import requests
import re

class MCPClient:
    """MCP Client using subprocess for local servers."""
    def __init__(self, command):
        self.proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self._request_id = 0
        self._initialize()

    def _next_id(self):
        self._request_id += 1
        return self._request_id

    def send(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._next_id()
        }
        if params:
            payload["params"] = params
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()
        response = self.proc.stdout.readline()
        if response:
            return json.loads(response)
        return {"error": "No response from server"}

    def _initialize(self):
        # MCP initialization handshake
        self.send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "mcp-inspector", "version": "1.0.0"}
        })
        notif = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        self.proc.stdin.write(json.dumps(notif) + "\n")
        self.proc.stdin.flush()

    def list_tools(self):
        result = self.send("tools/list")
        if "result" in result and "tools" in result["result"]:
            return result["result"]["tools"]
        return []

    def call_tool(self, name, arguments):
        result = self.send("tools/call", {"name": name, "arguments": arguments})
        if "result" in result:
            return result["result"]
        return result


class MCPHttpClient:
    """MCP Client using HTTP for remote deployed servers (FastMCP SSE)."""
    
    def __init__(self, base_url, bearer_token):
        self.base_url = base_url.rstrip("/")
        self.bearer_token = bearer_token
        self._request_id = 0
        self._session_id = None
        self._initialize()

    def _next_id(self):
        self._request_id += 1
        return self._request_id

    def _parse_sse_response(self, text):
        """Parse SSE response and extract JSON data."""
        for line in text.strip().split("\n"):
            if line.startswith("data: "):
                return json.loads(line[6:])
        return {"error": "No data in SSE response"}

    def send(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._next_id()
        }
        if params:
            payload["params"] = params
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        url = f"{self.base_url}/mcp"
        if self._session_id:
            url = f"{url}?sessionId={self._session_id}"
        
        response = requests.post(url, json=payload, headers=headers)
        
        # Extract session ID from response if present
        if not self._session_id:
            # Try to get session ID from the response
            match = re.search(r'sessionId=([a-zA-Z0-9_-]+)', response.text)
            if match:
                self._session_id = match.group(1)
        
        if response.status_code == 200:
            return self._parse_sse_response(response.text)
        return {"error": f"HTTP {response.status_code}: {response.text}"}

    def _initialize(self):
        # MCP initialization handshake
        result = self.send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "mcp-inspector-http", "version": "1.0.0"}
        })
        # Extract session ID from initialize response if available
        if "result" in result:
            # Send initialized notification
            self.send("notifications/initialized")

    def list_tools(self):
        result = self.send("tools/list")
        if "result" in result and "tools" in result["result"]:
            return result["result"]["tools"]
        return []

    def call_tool(self, name, arguments):
        result = self.send("tools/call", {"name": name, "arguments": arguments})
        if "result" in result:
            return result["result"]
        return result
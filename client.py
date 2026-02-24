import subprocess
import json

class MCPClient:
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
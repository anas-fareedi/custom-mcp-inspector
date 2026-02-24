import streamlit as st
import json
from client import MCPHttpClient
import os
from dotenv import load_dotenv
load_dotenv()

st.title("🛠 MCP Inspector (Python Edition)")

# Sidebar for server configuration
st.sidebar.header("Server Configuration")

# Remote FastMCP Cloud
default_url = "https://my-mcp-server1.fastmcp.app"
default_token = os.getenv("MCP_TOKEN")

server_url = st.sidebar.text_input("Server URL", default_url)
bearer_token = st.sidebar.text_input("Bearer Token", default_token, type="password")

if not bearer_token:
    st.warning("Please enter your Bearer token in the sidebar")
    st.stop()

# Create client (no caching to avoid stale connections)
try:
    client = MCPHttpClient(server_url, bearer_token)
    tools = client.list_tools()
except Exception as e:
    st.error(f"Failed to connect to server: {e}")
    st.stop()

if not tools:
    st.warning("No tools available from the server")
    st.stop()

st.success(f"Connected! Found {len(tools)} tools")

tool_names = [tool["name"] for tool in tools]

selected_tool = st.selectbox("Select Tool", tool_names)

current_tool = next((t for t in tools if t["name"] == selected_tool), None)
if current_tool:
    st.caption(current_tool.get("description", ""))
    if "inputSchema" in current_tool:
        props = current_tool["inputSchema"].get("properties", {})
        if props:
            st.markdown("**Parameters:**")
            for name, schema in props.items():
                st.markdown(f"- `{name}` ({schema.get('type', 'any')}): {schema.get('description', '')}")

example_json = '{"a": 5, "b": 3}'
st.markdown("**Example input:** `" + example_json + "`")

arguments = st.text_area("Arguments (JSON format)", example_json)

if st.button("Run Tool"):
    try:
        parsed_args = json.loads(arguments)
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e}")
        st.info('Use double quotes for keys and strings, e.g., `{"a": 5, "b": 3}`')
        st.stop()
    
    try:
        with st.spinner("Calling tool..."):
            response = client.call_tool(selected_tool, parsed_args)
        st.json(response)
    except Exception as e:
        st.error(f"Error calling tool: {e}")

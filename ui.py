import streamlit as st
import requests
import json

st.title("🛠 MCP Inspector (Python Edition)")

try:
    tools = requests.get("http://localhost:8000/tools").json()
except Exception as e:
    st.error(f"Failed to connect to backend: {e}")
    st.info("Make sure the backend is running: `uvicorn inspector:app --reload`")
    st.stop()

if not tools:
    st.warning("No tools available from the server")
    st.stop()

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
        st.info("Use double quotes for keys and strings, e.g., `{\"a\": 5, \"b\": 3}`")
        st.stop()
    try:
        response = requests.post(
            "http://localhost:8000/call",
            json={
                "name": selected_tool,
                "arguments": parsed_args
            }
        ).json()
        st.json(response)
    except Exception as e:
        st.error(f"Error calling tool: {e}")
        
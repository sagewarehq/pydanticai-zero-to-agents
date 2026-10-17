"""Building block · MCP: plug in any MCP server as tools.

The agent starts mcp_server.py as a subprocess (stdio) and gets its tools.
For a remote server, pass a URL instead: MCPToolset('https://example.com/mcp'),
or use the `MCP('https://...')` capability, which can also use the provider's
native MCP support.

    uv run building_blocks/mcp_client.py
"""

import os
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

holidays = MCPToolset(Path(__file__).with_name('mcp_server.py'))

agent = Agent(os.getenv('MODEL', 'openai:gpt-5-mini'), toolsets=[holidays])

result = agent.run_sync('When is the next long weekend in the Philippines?')
print(result.output)

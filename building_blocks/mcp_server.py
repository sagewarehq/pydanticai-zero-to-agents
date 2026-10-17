"""An MCP server: Philippine public holidays, exposed as tools.

MCP (Model Context Protocol) is a standard way to package tools so any agent
or app (Pydantic AI, Claude, Cursor, ...) can use them. This one is built with
FastMCP and is used by mcp_client.py.

    uv run building_blocks/mcp_server.py   # runs over stdio; normally an agent starts it for you
"""

from datetime import date

import httpx
from fastmcp import FastMCP

mcp = FastMCP('ph-holidays')


@mcp.tool
def holidays(year: int) -> list[dict]:
    """All Philippine public holidays in a year."""
    r = httpx.get(f'https://date.nager.at/api/v3/PublicHolidays/{year}/PH')
    return [{'date': h['date'], 'name': h['localName'], 'english': h['name']} for h in r.json()]


@mcp.tool
def today() -> str:
    """Today's date."""
    return date.today().isoformat()


if __name__ == '__main__':
    mcp.run(show_banner=False, log_level='WARNING')

"""Beyond to_web(): your own frontend, over AG-UI.

`agent.to_web()` gives you a ready-made chat. When you want your own UI, serve
the agent over AG-UI (an open protocol for streaming agent events to a
frontend) and build whatever you like on top. Here the agent has a data tool
and a `show_chart` tool; the React app turns `show_chart` calls into live
charts. The tool's arguments *are* the UI contract.

    uv run uvicorn server:app --app-dir beyond/custom_ui --port 9100 --reload

See README.md in this folder for the frontend.
"""

import os
from typing import Literal

import httpx
from pydantic import BaseModel
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.ui.ag_ui import AGUIAdapter
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route

agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    instructions=(
        'You are a helpful data assistant. Act on requests with sensible defaults instead of asking '
        'clarifying questions. For country statistics, get real numbers with `fetch_world_bank`; never '
        'invent data. To visualize anything, call `show_chart` — never write chart code. After a chart, '
        'state the key insight in one or two sentences; do not mention the chart itself or add labels '
        'like "Takeaway:".'
    ),
)


class Dataset(BaseModel):
    label: str
    data: list[float | None]


@agent.tool_plain
async def fetch_world_bank(country: str, indicator: str, start_year: int, end_year: int) -> dict[str, float | None]:
    """Fetch yearly values of a World Bank indicator for a country.

    Args:
        country: ISO3 country code, e.g. PHL, USA, or a comma-separated list like PHL;VNM.
        indicator: World Bank indicator code, e.g. SP.POP.TOTL (population), NY.GDP.MKTP.CD (GDP, US$),
            NY.GDP.PCAP.CD (GDP per capita), SP.DYN.LE00.IN (life expectancy), FP.CPI.TOTL.ZG (inflation).
        start_year: First year, inclusive.
        end_year: Last year, inclusive.

    Returns:
        A mapping of "<country> <year>" to value (None when not yet published).
    """
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(
            f'https://api.worldbank.org/v2/country/{country}/indicator/{indicator}',
            params={'format': 'json', 'date': f'{start_year}:{end_year}', 'per_page': 1000},
        )
    body = r.json()
    if len(body) < 2 or not body[1]:
        raise ModelRetry(f'No data for country={country!r} indicator={indicator!r}: {body}')
    rows = sorted(body[1], key=lambda row: (row['countryiso3code'], row['date']))
    return {f'{row["countryiso3code"]} {row["date"]}': row['value'] for row in rows}


@agent.tool_plain
def show_chart(
    type: Literal['line', 'bar', 'pie', 'doughnut'],
    title: str,
    labels: list[str],
    datasets: list[Dataset],
    y_label: str | None = None,
    source: str | None = None,
) -> str:
    """Render a chart in the user's chat. Prefer readable units (e.g. millions) over raw large numbers.

    Args:
        type: Chart type.
        title: Chart title.
        labels: X-axis labels (or slice labels for pie/doughnut).
        datasets: One or more series, each the same length as `labels`.
        y_label: Y-axis label including units, e.g. "Population (millions)".
        source: Data source attribution, e.g. "World Bank (SP.POP.TOTL)".
    """
    return 'Chart displayed to the user.'


async def run_agent(request: Request):
    return await AGUIAdapter.dispatch_request(request, agent=agent)


app = Starlette(routes=[Route('/', run_agent, methods=['POST'])])

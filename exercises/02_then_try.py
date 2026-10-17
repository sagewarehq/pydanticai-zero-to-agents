"""Exercise 02 · Then try: a tool that does something real.

Two tools that call a real API (Open-Meteo, free, no key). The model chains
them on its own: find the city's coordinates, then fetch the forecast.

    uv run exercises/02_then_try.py
"""

import os

import httpx
from pydantic_ai import Agent, ModelRetry

agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    instructions='You are a practical weather assistant for travellers in the Philippines.',
)


@agent.tool_plain
def find_city(name: str) -> dict:
    """Look up a city's latitude and longitude."""
    r = httpx.get('https://geocoding-api.open-meteo.com/v1/search', params={'name': name, 'count': 1})
    results = r.json().get('results')
    if not results:
        # ModelRetry sends the message back to the model so it can fix its call.
        raise ModelRetry(f'No city called {name!r}. Try a different spelling or a nearby city.')
    city = results[0]
    return {'name': city['name'], 'country': city.get('country'), 'lat': city['latitude'], 'lon': city['longitude']}


@agent.tool_plain
def forecast(lat: float, lon: float, days: int = 3) -> dict:
    """Daily forecast: max/min temperature (°C) and chance of rain (%)."""
    r = httpx.get(
        'https://api.open-meteo.com/v1/forecast',
        params={
            'latitude': lat,
            'longitude': lon,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_probability_max',
            'timezone': 'Asia/Manila',
            'forecast_days': days,
        },
    )
    return r.json()['daily']


result = agent.run_sync('I land in Cebu tomorrow. Should I pack an umbrella?')
print(result.output)

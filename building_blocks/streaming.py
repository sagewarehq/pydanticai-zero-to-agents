"""Building block · Streaming: text, structured output and events, live.

Three ways to watch an agent work instead of waiting for the final answer.

    uv run building_blocks/streaming.py
"""

import asyncio
import os

from pydantic import BaseModel
from pydantic_ai import (
    Agent,
    AgentRunResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    TextPartDelta,
)

MODEL = os.getenv('MODEL', 'openai:gpt-5-mini')


async def stream_text():
    agent = Agent(MODEL)
    async with agent.run_stream('Write a 4-line poem about jeepneys.') as result:
        async for delta in result.stream_text(delta=True):
            print(delta, end='', flush=True)
    print('\n')


class Itinerary(BaseModel):
    city: str
    stops: list[str] = []


async def stream_structured():
    # Partial, validated objects arrive while the model is still writing.
    agent = Agent(MODEL, output_type=Itinerary)
    async with agent.run_stream('A 5-stop food crawl in Binondo, Manila.') as result:
        async for partial in result.stream_output():
            print(f'\r{len(partial.stops)} stops so far…', end='', flush=True)
    print(f'\n{await result.get_output()}\n')


async def stream_events():
    # Every step of the run: tool calls, tool results, text deltas, the final result.
    agent = Agent(MODEL)

    @agent.tool_plain
    def jeepney_fare(km: float) -> float:
        """Minimum fare is ₱13 for the first 4 km, then ₱1.80 per km."""
        return 13 + max(0, km - 4) * 1.8

    async with agent.run_stream_events('How much is a 10 km jeepney ride?') as events:
        async for event in events:
            if isinstance(event, FunctionToolCallEvent):
                print(f'→ calling {event.part.tool_name}({event.part.args})')
            elif isinstance(event, FunctionToolResultEvent):
                print(f'← {event.part.content}')
            elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                print(event.delta.content_delta, end='', flush=True)
            elif isinstance(event, AgentRunResultEvent):
                print(f'\n[done, {event.result.usage.total_tokens} tokens]')


async def main():
    await stream_text()
    await stream_structured()
    await stream_events()


asyncio.run(main())

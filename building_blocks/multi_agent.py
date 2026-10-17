"""Building block · Multi-agent: delegation.

A planner agent hands specialist work to other agents through tools. Each
specialist has its own instructions and its own typed output, so the planner
gets data back, not prose. Passing `usage=ctx.usage` keeps one token budget.

    uv run building_blocks/multi_agent.py
"""

import os

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, UsageLimits

MODEL = os.getenv('MODEL', 'openai:gpt-5-mini')


class Spot(BaseModel):
    name: str
    why: str


class Budget(BaseModel):
    lodging_per_night: float
    food_per_day: float
    transport_total: float
    total: float


scout = Agent(
    MODEL, name='scout', output_type=list[Spot], instructions='You are a local guide. Suggest real places only.'
)
accountant = Agent(
    MODEL, name='accountant', output_type=Budget, instructions='Estimate realistic PHP costs for a budget traveller.'
)

planner = Agent(
    MODEL,
    name='planner',
    instructions='Plan short trips in the Philippines. Use your specialists, then write a day-by-day plan with costs.',
)


@planner.tool
async def find_spots(ctx: RunContext, city: str, interests: str) -> list[Spot]:
    """Ask the local guide for places to visit."""
    result = await scout.run(f'Top 5 spots in {city} for someone into {interests}.', usage=ctx.usage)
    return result.output


@planner.tool
async def estimate_budget(ctx: RunContext, city: str, nights: int, travellers: int) -> Budget:
    """Ask the accountant for a cost estimate."""
    result = await accountant.run(
        f'{nights} nights in {city} for {travellers} people, travelling from Manila.', usage=ctx.usage
    )
    return result.output


result = planner.run_sync(
    'Weekend in Siargao for two, we love surfing and food.',
    usage_limits=UsageLimits(request_limit=15),
)
print(result.output)
print(f'\n{result.usage.requests} model requests across all three agents.')

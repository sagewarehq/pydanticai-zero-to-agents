"""Exercise 04 · Then try: bring in your tools and your types.

The expense logger from the slide, but it actually logs. Exercise 2's idea
(tools) plus exercise 3's idea (a Pydantic model) behind exercise 4's web UI.

`deps` is how you hand your own objects (a DB connection, a user, a ledger) to
tools. Tools that take `RunContext` as the first argument get `ctx.deps`.

    uv run exercises/04_then_try.py      # then open http://127.0.0.1:8000

Try: "Lunch at Jollibee ₱189", "Grab home 320", "How much on food so far?"
"""

import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext


class Expense(BaseModel):
    merchant: str
    amount: float
    category: Literal['Food', 'Transport', 'Bills', 'Shopping', 'Other']
    day: date


@dataclass
class Ledger:
    expenses: list[Expense] = field(default_factory=list)


agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    deps_type=Ledger,
    instructions='You log my expenses in PHP. Log anything that looks like a purchase. Reply in one short line.',
)


@agent.instructions
def today() -> str:
    return f'Today is {date.today():%A, %B %d, %Y}.'


@agent.tool
def log_expense(ctx: RunContext[Ledger], expense: Expense) -> str:
    """Save an expense to the ledger."""
    ctx.deps.expenses.append(expense)
    return f'Logged #{len(ctx.deps.expenses)}'


@agent.tool
def summary(ctx: RunContext[Ledger]) -> dict:
    """Totals per category, plus every expense logged so far."""
    totals: dict[str, float] = defaultdict(float)
    for e in ctx.deps.expenses:
        totals[e.category] += e.amount
    return {'totals': totals, 'grand_total': sum(totals.values()), 'expenses': ctx.deps.expenses}


app = agent.to_web(deps=Ledger())

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)

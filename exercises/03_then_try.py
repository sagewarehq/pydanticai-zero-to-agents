"""Exercise 03 · Then try: pull fields out of something messy.

A group chat after a barkada trip. Richer types do the heavy lifting:
`Literal` constrains categories, `Field(description=...)` tells the model what
you mean, and `list[...]` gets you every expense at once. If the model returns
something invalid, Pydantic AI sends the validation error back and it retries.

    uv run exercises/03_then_try.py
"""

import os
from collections import defaultdict
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent


class Expense(BaseModel):
    merchant: str
    amount: float = Field(description='Amount in PHP. Convert other currencies at the rate mentioned, if any.')
    category: Literal['Food', 'Transport', 'Lodging', 'Activities', 'Other']
    paid_by: str
    split_between: list[str] = Field(description='Everyone sharing this expense, including the payer.')


class Trip(BaseModel):
    expenses: list[Expense]


CHAT = """
[Fri 9:02] Ana: booked the Airbnb in Moalboal! 7,500 for 2 nights, all 4 of us
[Fri 13:40] Ben: paid the bus from Cebu South terminal, 180 each x4 = 720
[Sat 8:15] Carla: canyoneering at Kawasan, 1,500 per head, I paid for me and Dan
[Sat 12:30] Ana: lunch at Shaka 2,140 (I covered, everyone ate)
[Sat 19:00] Dan: lechon run!! ₱1,200, Ben didn't eat cause he's vegetarian lol
"""

agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    output_type=Trip,
    instructions='Extract every shared expense from the group chat.',
)
trip = agent.run_sync(CHAT).output

balance: dict[str, float] = defaultdict(float)
for e in trip.expenses:
    print(
        f'{e.category:<11} ₱{e.amount:>8,.2f}  {e.merchant:<28} paid by {e.paid_by}, split {len(e.split_between)} ways'
    )
    balance[e.paid_by] += e.amount
    for person in e.split_between:
        balance[person] -= e.amount / len(e.split_between)

print('\nWho owes whom (negative = owes the group):')
for person, amount in sorted(balance.items(), key=lambda kv: kv[1]):
    print(f'  {person:<6} {amount:>+10,.2f}')

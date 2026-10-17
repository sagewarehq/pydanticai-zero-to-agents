"""Exercise 03 · Make it answer in data.

Ask for a Pydantic model instead of text. You get back a validated object
your code can use, not a string you have to parse.

    uv run exercises/03_expense.py
"""

import os

from pydantic import BaseModel
from pydantic_ai import Agent


class Expense(BaseModel):
    merchant: str
    amount: float
    category: str


agent = Agent(os.getenv('MODEL', 'openai:gpt-5-mini'), output_type=Expense)

result = agent.run_sync('Grab to Makati, ₱245, paid with GCash')
print(result.output)
print(f'It is a real object: {result.output.amount * 2 = }')

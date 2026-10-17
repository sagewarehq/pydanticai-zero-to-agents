"""Building block · Evals: score your agent against test cases.

"It worked when I tried it" is not a test. An eval is a dataset of inputs with
expected outputs, plus evaluators that score each run. Change the prompt or
the model, rerun, and compare the numbers.

    uv run building_blocks/evals.py
"""

import os
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, IsInstance


class Expense(BaseModel):
    merchant: str
    amount: float
    category: Literal['Food', 'Transport', 'Bills', 'Shopping', 'Other']


agent = Agent(os.getenv('MODEL', 'openai:gpt-5-mini'), output_type=Expense)


async def parse_expense(text: str) -> Expense:
    return (await agent.run(text)).output


@dataclass
class FieldsMatch(Evaluator[str, Expense]):
    """One score per field, so the report shows *what* the agent gets wrong."""

    def evaluate(self, ctx: EvaluatorContext[str, Expense]) -> dict[str, bool]:
        exp = ctx.expected_output
        return {
            'amount': abs(ctx.output.amount - exp.amount) < 0.01,
            'category': ctx.output.category == exp.category,
            'merchant': exp.merchant.lower() in ctx.output.merchant.lower(),
        }


dataset = Dataset(
    name='expense-parsing',
    cases=[
        Case(
            name='grab',
            inputs='Grab to Makati, ₱245, paid with GCash',
            expected_output=Expense(merchant='Grab', amount=245, category='Transport'),
        ),
        Case(
            name='jollibee',
            inputs='jollibee 2pc chickenjoy 189',
            expected_output=Expense(merchant='Jollibee', amount=189, category='Food'),
        ),
        Case(
            name='meralco',
            inputs='Paid Meralco bill: PHP 3,412.50',
            expected_output=Expense(merchant='Meralco', amount=3412.5, category='Bills'),
        ),
        Case(
            name='shopee',
            inputs='shopee haul 1.2k (phone case + cables)',
            expected_output=Expense(merchant='Shopee', amount=1200, category='Shopping'),
        ),
        Case(
            name='taglish',
            inputs='nagbayad ako ng 60 pesos sa tricycle pauwi',
            expected_output=Expense(merchant='Tricycle', amount=60, category='Transport'),
        ),
        Case(
            name='usd',
            inputs='Netflix $15.49 (use ₱58/USD)',
            expected_output=Expense(merchant='Netflix', amount=898.42, category='Bills'),
        ),
    ],
    evaluators=[IsInstance(type_name='Expense'), FieldsMatch()],
)

report = dataset.evaluate_sync(parse_expense)
report.print(include_input=True, include_output=True)

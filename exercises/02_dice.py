"""Exercise 02 · Give it a tool.

A tool is a plain Python function. The model reads its name, signature and
docstring, and decides when to call it.

    uv run exercises/02_dice.py
"""

import os
import random

from pydantic_ai import Agent

agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    instructions='Roll a die. Say if the guess won.',
)


@agent.tool_plain
def roll_die() -> str:
    """Roll a six-sided die."""
    return str(random.randint(1, 6))


result = agent.run_sync('My guess is 4.')
print(result.output)

# See exactly what happened: the request, the tool call, the tool result, the answer.
for message in result.all_messages():
    for part in message.parts:
        print(f'  {type(part).__name__:<16} {getattr(part, "content", None) or getattr(part, "args", "")}')

"""Exercise 01 · Hello, agent.

Your first inference call: a model, an instruction and a question.

    uv run exercises/01_hello.py
"""

import os

from pydantic_ai import Agent

agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    instructions='Be helpful and concise.',
)

result = agent.run_sync('Where is Cebu?')
print(result.output)

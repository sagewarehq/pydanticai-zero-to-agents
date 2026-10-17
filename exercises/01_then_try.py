"""Exercise 01 · Then try: rewrite the instructions, swap the model.

The same question, three personalities. Instructions shape *how* the model
answers; the model string decides *who* answers. Both can be overridden per run.

    uv run exercises/01_then_try.py
    MODEL=anthropic:claude-haiku-4-5 uv run exercises/01_then_try.py
"""

import os

from pydantic_ai import Agent

agent = Agent(os.getenv('MODEL', 'openai:gpt-5-mini'))

PERSONAS = {
    'Tour guide': 'You are an enthusiastic Cebuano tour guide. Two sentences max.',
    'Tita': 'You are a Filipino tita at a family reunion. Answer, then ask when they are getting married.',
    'Haiku': 'Answer only in a single haiku.',
}

for name, instructions in PERSONAS.items():
    result = agent.run_sync('Where is Cebu?', instructions=instructions)
    print(f'--- {name} ---\n{result.output}\n')

# Swapping providers is one string. Uncomment if you have the key:
# result = agent.run_sync('Where is Cebu?', model='anthropic:claude-haiku-4-5')
# result = agent.run_sync('Where is Cebu?', model='openrouter:openai/gpt-5-mini')

"""Building block · 20+ providers.

The model is just a string: "provider:model-name". Swap it per agent, per run,
or chain providers so a failure on one falls through to the next.

    uv run building_blocks/providers.py

Only providers you have keys for are tried. OpenRouter is the easy way to try
many models with one key (some are free, but free models may train on your data).
"""

import os

from pydantic_ai import Agent
from pydantic_ai.models.fallback import FallbackModel

CANDIDATES = {
    'openai:gpt-5-mini': 'OPENAI_API_KEY',
    'anthropic:claude-haiku-4-5': 'ANTHROPIC_API_KEY',
    'google:gemini-3-flash-preview': 'GEMINI_API_KEY',
    'groq:llama-3.3-70b-versatile': 'GROQ_API_KEY',
    'openrouter:openai/gpt-5-mini': 'OPENROUTER_API_KEY',
}
available = [model for model, key in CANDIDATES.items() if os.getenv(key)]
print(f'Models with keys set: {available}\n')

agent = Agent(instructions='Answer in one sentence.')

# 1. Same agent, different model per run.
for model in available:
    result = agent.run_sync('What is the best Filipino dessert?', model=model)
    print(f'{model:<32} {result.output}')

# 2. Fallback: try the first model, and if the request fails, the next one.
fallback = FallbackModel('openai:gpt-this-model-does-not-exist', *available)
result = agent.run_sync('Say "fallback worked" and name yourself.', model=fallback)
print(f'\nFallbackModel → {result.response.model_name}: {result.output}')

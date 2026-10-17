"""Building block · Tools: web search.

Your own functions are tools (exercise 2). Some tools come built in: the
`WebSearch` capability uses the provider's native search when the model
supports it. For OpenAI that means the Responses API (`openai-responses:`).

    uv run building_blocks/web_search.py
"""

from pydantic_ai import Agent
from pydantic_ai.capabilities import WebSearch

agent = Agent(
    'openai-responses:gpt-5-mini',
    instructions='Answer in three bullet points, each with its source.',
    capabilities=[WebSearch(user_location={'country': 'PH'})],
)

result = agent.run_sync('What is the latest news about PythonAsia or the Python community in the Philippines?')
print(result.output)

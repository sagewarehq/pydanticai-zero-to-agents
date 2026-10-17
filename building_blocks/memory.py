"""Building block · Memory: message history and saved state.

An agent run is stateless. Memory is just the message list you pass back in.
Save it as JSON and the conversation survives a restart.

    uv run building_blocks/memory.py          # chat; quit with Ctrl+D
    uv run building_blocks/memory.py          # run again: it remembers
    uv run building_blocks/memory.py --fresh  # forget everything
"""

import os
import sys
from pathlib import Path

from pydantic_ai import Agent, ModelMessagesTypeAdapter

HISTORY = Path(__file__).with_name('.memory.json')

agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    instructions='You are a friendly study buddy. Keep replies short and remember what the user tells you.',
)

if '--fresh' in sys.argv:
    HISTORY.unlink(missing_ok=True)

history = ModelMessagesTypeAdapter.validate_json(HISTORY.read_bytes()) if HISTORY.exists() else []
print(f'Loaded {len(history)} messages. Try "My name is ..." then restart and ask "What is my name?"\n')

while True:
    try:
        prompt = input('you › ')
    except (EOFError, KeyboardInterrupt):
        break
    result = agent.run_sync(prompt, message_history=history)
    print(f'bot › {result.output}\n')
    history = result.all_messages()
    HISTORY.write_bytes(ModelMessagesTypeAdapter.dump_json(history, indent=2))

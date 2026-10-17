"""Exercise 04 · Put a face on it.

One line turns your agent into a web chat you can open in a browser.

    uv run exercises/04_chat.py

Then open http://127.0.0.1:8000. (On the slide it's `uvicorn chat:app`; that
works too if you name the file chat.py.)
"""

import os

from pydantic_ai import Agent

agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    instructions='You log my expenses.',
)

app = agent.to_web()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)

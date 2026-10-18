"""Exercise 05 · Ask before acting.

The rover rule: routine moves run on their own, risky ones wait until a human
confirms. `requires_approval=True` pauses the tool call, and the
`HandleDeferredToolCalls` capability asks you in the terminal, then carries on
with the run. Say no and the model is told so, instead of the money moving.

    uv run exercises/05_approval.py
"""

import os

from pydantic_ai import Agent, ToolDenied
from pydantic_ai.capabilities import HandleDeferredToolCalls


async def ask_human(ctx, requests):
    approvals = {}
    for call in requests.approvals:
        ok = input(f'Approve {call.tool_name}({call.args})? [y/N] ')
        approvals[call.tool_call_id] = True if ok.strip().lower() == 'y' else ToolDenied('The user said no.')
    return requests.build_results(approvals=approvals)


agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    # Without the second sentence, models tend to ask "are you sure?" in text instead of calling the tool.
    instructions='You help me pay my bills. Just call the tool: it asks me to confirm before any money moves.',
    capabilities=[HandleDeferredToolCalls(handler=ask_human)],
)


@agent.tool_plain(requires_approval=True)
def send_payment(recipient: str, amount: float) -> str:
    """Send money via GCash."""
    return f'Sent ₱{amount:,.2f} to {recipient}.'


result = agent.run_sync('Pay Meralco ₱3,450.')
print(result.output)

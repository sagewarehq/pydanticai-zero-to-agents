"""Exercise 05 · Then try: ask only above ₱1,000.

`requires_approval=True` asks every time, which gets old fast. Decide inside
the tool instead: small payments go straight through, and anything above
₱1,000 raises `ApprovalRequired` to pause for a human. Once you approve, the
tool runs again with `ctx.tool_call_approved` set, so it skips the check.

    uv run exercises/05_then_try.py

Four bills go in. Maynilad and Globe pay themselves; you only get asked about
Meralco and the condo dues. Try saying no to one.
"""

import os

from pydantic_ai import Agent, ApprovalRequired, RunContext, ToolDenied
from pydantic_ai.capabilities import HandleDeferredToolCalls

LIMIT = 1_000


async def ask_human(ctx, requests):
    approvals = {}
    for call in requests.approvals:
        args = call.args_as_dict()
        ok = input(f'Pay ₱{args["amount"]:,.2f} to {args["recipient"]}? [y/N] ')
        approvals[call.tool_call_id] = True if ok.strip().lower() == 'y' else ToolDenied('The user said no.')
    return requests.build_results(approvals=approvals)


agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    instructions='You help me pay my bills. Pay each bill separately, then summarize what was paid and what was not.',
    capabilities=[HandleDeferredToolCalls(handler=ask_human)],
)


@agent.tool
def send_payment(ctx: RunContext, recipient: str, amount: float) -> str:
    """Send money via GCash."""
    if amount > LIMIT and not ctx.tool_call_approved:
        raise ApprovalRequired()
    print(f'  → sent ₱{amount:,.2f} to {recipient}')
    return f'Sent ₱{amount:,.2f} to {recipient}.'


result = agent.run_sync('Pay my bills: Meralco ₱3,450, Maynilad ₱680, Globe ₱999 and condo dues ₱5,200.')
print(result.output)

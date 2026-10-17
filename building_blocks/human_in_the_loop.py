"""Building block · Human in the loop: a person approves before an action runs.

Small reimbursements go through; anything over ₱1,000 pauses the run and asks
you. The run doesn't block while it waits: it ends with `DeferredToolRequests`,
and you resume it later (seconds or days) with the decisions.

    uv run building_blocks/human_in_the_loop.py
"""

import os

from pydantic_ai import (
    Agent,
    ApprovalRequired,
    DeferredToolRequests,
    DeferredToolResults,
    RunContext,
    ToolDenied,
)

agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    output_type=[str, DeferredToolRequests],
    instructions='You process expense reimbursements. Submit each one separately.',
)


def needs_approval(ctx: RunContext, employee: str, amount: float, reason: str) -> None:
    if amount > 1000 and not ctx.tool_call_approved:
        raise ApprovalRequired()


@agent.tool(args_validator=needs_approval)
def reimburse(ctx: RunContext, employee: str, amount: float, reason: str) -> str:
    """Send a reimbursement in PHP."""
    return f'Sent ₱{amount:,.2f} to {employee}'


result = agent.run_sync('Reimburse Ana ₱350 for a Grab ride, and Ben ₱4,800 for a team dinner at Manam.')

while isinstance(result.output, DeferredToolRequests):
    decisions = DeferredToolResults()
    for call in result.output.approvals:
        answer = input(f'Approve {call.tool_name}({call.args})? [y/N] ')
        decisions.approvals[call.tool_call_id] = answer.strip().lower() == 'y' or ToolDenied('Rejected by finance.')
    result = agent.run_sync(message_history=result.all_messages(), deferred_tool_results=decisions)

print(result.output)

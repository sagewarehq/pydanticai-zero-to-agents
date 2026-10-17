"""Capstone · A minimal agentic harness: a coding agent in your terminal.

Everything from the workshop in one ~200-line file:

    the loop       the agent calls tools until the job is done; you chat in turns
    tools          read, write and edit files, run shell commands
    context        instructions + a live file listing + AGENTS.md, rebuilt every run
    guardrails     a workspace jail, human approval, usage limits, timeouts
    memory         message history carried across turns
    streaming      tool calls and text printed as they happen

    uv run harness/harness.py              # works in ./playground
    uv run harness/harness.py ~/my-project # or point it anywhere

Try: "make a fizzbuzz.py and run it", "add type hints to fizzbuzz.py",
"write a test for it with pytest and run it". Commands: /clear, /exit.
"""

import asyncio
import os
import subprocess
import sys
from collections.abc import AsyncIterable
from dataclasses import dataclass, field
from pathlib import Path

from pydantic_ai import (
    Agent,
    AgentStreamEvent,
    ApprovalRequired,
    DeferredToolRequests,
    DeferredToolResults,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    ModelMessage,
    ModelRetry,
    PartDeltaEvent,
    PartStartEvent,
    RunContext,
    TextPart,
    TextPartDelta,
    ToolDenied,
    ToolFailed,
    UsageLimits,
)

DIM, BOLD, GREEN, YELLOW, RESET = '\033[2m', '\033[1m', '\033[32m', '\033[33m', '\033[0m'
IGNORED = {'.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache'}


@dataclass
class Workspace:
    """Dependencies for every tool: where we work, and what the user trusts."""

    root: Path
    trusted: set[str] = field(default_factory=set)

    def path(self, relative: str) -> Path:
        p = (self.root / relative).resolve()
        if not p.is_relative_to(self.root):
            raise ToolFailed(f'{relative} is outside the workspace.')
        return p

    def approve(self, ctx: RunContext['Workspace'], tool: str) -> None:
        """Pause the run for a human unless they already said yes (or 'always')."""
        if not ctx.tool_call_approved and tool not in self.trusted:
            raise ApprovalRequired()


agent = Agent(
    os.getenv('MODEL', 'openai:gpt-5-mini'),
    name='harness',
    deps_type=Workspace,
    output_type=[str, DeferredToolRequests],
    instructions=(
        'You are a careful coding agent working inside a single project directory. '
        'Look before you leap: list and read files before changing them. Prefer edit_file for small changes. '
        'After changing code, run it or its tests to check your work. Keep replies short.'
    ),
)


@agent.instructions
def project_context(ctx: RunContext[Workspace]) -> str:
    """Context engineering: show the model where it is, fresh on every request."""
    files = sorted(str(p.relative_to(ctx.deps.root)) for p in walk(ctx.deps.root))
    context = f'Workspace: {ctx.deps.root}\nFiles ({len(files)}):\n' + '\n'.join(files[:100])
    notes = ctx.deps.root / 'AGENTS.md'
    if notes.exists():
        context += f'\n\nProject notes from AGENTS.md:\n{notes.read_text()}'
    return context


def walk(root: Path):
    for p in root.iterdir():
        if p.name in IGNORED:
            continue
        if p.is_dir():
            yield from walk(p)
        else:
            yield p


@agent.tool
def read_file(ctx: RunContext[Workspace], path: str) -> str:
    """Read a text file, with line numbers."""
    p = ctx.deps.path(path)
    if not p.is_file():
        raise ToolFailed(f'No such file: {path}')
    return '\n'.join(f'{i:>4} {line}' for i, line in enumerate(p.read_text().splitlines(), 1))


@agent.tool
def write_file(ctx: RunContext[Workspace], path: str, content: str) -> str:
    """Create or overwrite a file."""
    ctx.deps.approve(ctx, 'write_file')
    p = ctx.deps.path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f'Wrote {len(content.splitlines())} lines to {path}'


@agent.tool
def edit_file(ctx: RunContext[Workspace], path: str, old: str, new: str) -> str:
    """Replace one exact, unique snippet of a file with new text."""
    p = ctx.deps.path(path)
    text = p.read_text()
    if text.count(old) != 1:
        # ModelRetry: the model made a fixable mistake, let it try again.
        raise ModelRetry(f'`old` must appear exactly once in {path}; found {text.count(old)}. Read the file first.')
    ctx.deps.approve(ctx, 'edit_file')
    p.write_text(text.replace(old, new))
    return f'Edited {path}'


@agent.tool(timeout=90)
def run(ctx: RunContext[Workspace], command: str) -> str:
    """Run a shell command in the workspace and return its exit code and output."""
    ctx.deps.approve(ctx, 'run')
    proc = subprocess.run(command, shell=True, cwd=ctx.deps.root, capture_output=True, text=True, timeout=60)
    output = (proc.stdout + proc.stderr)[-4000:]  # the tail is usually what matters
    return f'exit code {proc.returncode}\n{output}'


async def show(ctx: RunContext[Workspace], events: AsyncIterable[AgentStreamEvent]) -> None:
    """Print what the agent is doing, as it does it."""
    async for event in events:
        if isinstance(event, PartStartEvent) and isinstance(event.part, TextPart):
            print(event.part.content, end='', flush=True)
        elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
            print(event.delta.content_delta, end='', flush=True)
        elif isinstance(event, FunctionToolCallEvent):
            args = event.part.args_as_dict()
            summary = args.get('command') or args.get('path') or ''
            print(f'{DIM}  ⚙ {event.part.tool_name} {summary}{RESET}')
        elif isinstance(event, FunctionToolResultEvent) and event.part.outcome == 'failed':
            print(f'{YELLOW}  ✗ {event.part.content}{RESET}')


def ask_human(requests: DeferredToolRequests, ws: Workspace) -> DeferredToolResults:
    decisions = DeferredToolResults()
    for call in requests.approvals:
        args = call.args_as_dict()
        print(f'\n{YELLOW}{BOLD}Approve {call.tool_name}?{RESET}')
        for key, value in args.items():
            text = str(value)
            print(f'  {key}: ' + (text if len(text) < 400 else text[:400] + f'… ({len(text)} chars)'))
        answer = input(f'{YELLOW}[y]es / [n]o / [a]lways for {call.tool_name} › {RESET}').strip().lower()
        if answer == 'a':
            ws.trusted.add(call.tool_name)
        decisions.approvals[call.tool_call_id] = answer in ('y', 'a') or ToolDenied(
            'The user said no. Ask them what to do instead.'
        )
    return decisions


async def turn(prompt: str, history: list[ModelMessage], ws: Workspace) -> list[ModelMessage]:
    """One user turn = one agent run, plus a resumed run after each round of approvals."""
    limits = UsageLimits(request_limit=25)
    result = await agent.run(prompt, message_history=history, deps=ws, event_stream_handler=show, usage_limits=limits)
    while isinstance(result.output, DeferredToolRequests):
        decisions = ask_human(result.output, ws)
        result = await agent.run(
            message_history=result.all_messages(),
            deferred_tool_results=decisions,
            deps=ws,
            event_stream_handler=show,
            usage_limits=limits,
        )
    print(f'\n{DIM}[{result.usage.total_tokens:,} tokens]{RESET}\n')
    return result.all_messages()


async def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'playground').resolve()
    root.mkdir(parents=True, exist_ok=True)
    ws = Workspace(root)
    history: list[ModelMessage] = []
    print(f'{BOLD}harness{RESET} in {root}  {DIM}(/clear, /exit){RESET}\n')

    while True:
        try:
            prompt = input(f'{GREEN}› {RESET}').strip()
        except (EOFError, KeyboardInterrupt):
            break
        if prompt == '/exit':
            break
        if prompt == '/clear':
            history = []
            print(f'{DIM}history cleared{RESET}\n')
            continue
        if prompt:
            history = await turn(prompt, history, ws)


if __name__ == '__main__':
    asyncio.run(main())

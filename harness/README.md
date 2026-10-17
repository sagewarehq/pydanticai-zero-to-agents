# The harness

A model on its own can only produce text. A **harness** is everything around it
that lets it act: the loop, the tools, the context it sees, and the guardrails
that keep it safe. `harness.py` is a small coding agent you can read in one
sitting, so you can see every part.

```sh
uv run harness/harness.py              # works inside ./playground
uv run harness/harness.py ~/my-project # or anywhere else
```

```
› make a fizzbuzz.py that prints 1 to 15, then run it
  ⚙ write_file fizzbuzz.py

Approve write_file?
  path: fizzbuzz.py
  content: for i in range(1, 16): ...
[y]es / [n]o / [a]lways for write_file › a
  ⚙ run python3 fizzbuzz.py
...
```

## Anatomy

| Part | In `harness.py` | Building block |
|---|---|---|
| **The loop** | `agent.run(...)` keeps calling tools until the model answers; `main()` loops over your turns | [Exercise 02](../exercises/02_dice.py) |
| **Tools** | `read_file`, `write_file`, `edit_file`, `run` | [Exercise 02](../exercises/02_then_try.py) |
| **Dependencies** | `Workspace` is passed to every tool as `ctx.deps` | [Exercise 04](../exercises/04_then_try.py) |
| **Context** | `@agent.instructions` rebuilds the file listing and `AGENTS.md` before every model request | [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) |
| **Self-correction** | `ModelRetry` when an edit target is ambiguous; `ToolFailed` when a file is missing | [Exercise 02](../exercises/02_then_try.py) |
| **Guardrails** | `Workspace.path()` jails file access, `ApprovalRequired` asks you first, `UsageLimits` caps the loop, `timeout=` caps a command | [Human in the loop](../building_blocks/human_in_the_loop.py) |
| **Memory** | `history` is passed back in every turn; `/clear` forgets | [Memory](../building_blocks/memory.py) |
| **Streaming** | `event_stream_handler=show` prints tool calls and text as they happen | [Streaming](../building_blocks/streaming.py) |

## Make it yours

- **A different job.** Swap the tools and instructions and it stops being a
  coding agent: a research agent (add `WebSearch()`), a data analyst (tools
  over a SQLite file), an ops assistant (an MCP server for your infra).
- **Persist sessions.** Save `history` with `ModelMessagesTypeAdapter`, like
  [memory.py](../building_blocks/memory.py).
- **Plug in MCP servers.** `Agent(..., toolsets=[MCPToolset(...)])` adds a
  whole toolbox in one line. See [mcp_client.py](../building_blocks/mcp_client.py).
- **Sub-agents.** Give it a `research` tool that runs a second agent with a
  clean context. See [multi_agent.py](../building_blocks/multi_agent.py).
- **Put a face on it.** Replace the terminal loop with `agent.to_web()`, or
  your own UI over AG-UI (see [beyond/custom_ui](../beyond/custom_ui)).
- **Measure it.** Write evals for the tasks you care about. See
  [evals.py](../building_blocks/evals.py).

> ⚠ `run` executes real shell commands on your machine. Approvals are on by
> default; only answer `a` (always) for a workspace you don't mind losing.

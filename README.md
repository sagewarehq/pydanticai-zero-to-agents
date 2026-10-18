# Zero to Agents

**Building an agentic harness with [Pydantic AI](https://ai.pydantic.dev).**
Reference code for the 6-hour hands-on sprint at PythonAsia 2026, Philippines.

> Knowing gives you the silhouette. Doing fills the form.

Every file here is a small, standalone script you can run, read top to
bottom, and copy into your own project. Start with the four exercises, then
pick the building blocks your idea needs.

## Setup

You need Python 3.12+ and an API key for one model provider.

```sh
git clone https://github.com/sagewarehq/pydanticai-zero-to-agents
cd pydanticai-zero-to-agents
uv sync
cp .env.example .env         # then add your key
uv run --env-file .env exercises/01_hello.py
```

No [uv](https://docs.astral.sh/uv/)? `pip install "pydantic-ai[ag-ui]" fastmcp numpy`, export your key
(`export OPENAI_API_KEY=...`) and run files with `python`.

Examples default to `openai:gpt-5-mini`. To use another provider, set `MODEL`:

```sh
MODEL=anthropic:claude-haiku-4-5 uv run exercises/01_hello.py
MODEL=google:gemini-3-flash-preview uv run exercises/01_hello.py
MODEL=openrouter:openai/gpt-5-mini uv run exercises/01_hello.py   # one key, many models
```

No key? [OpenRouter](https://openrouter.ai/) has free models.
⚠ Free models use your prompts and outputs for training.

## Exercises: from one call to a chat app

| # | Exercise | You'll use | Slide code | Then try |
|---|---|---|---|---|
| 01 | Hello, agent | `agent.run_sync()` | [01_hello.py](exercises/01_hello.py) | [Three personas, swap models](exercises/01_then_try.py) |
| 02 | Give it a tool | `@agent.tool_plain` | [02_dice.py](exercises/02_dice.py) | [A real API: Cebu weather](exercises/02_then_try.py) |
| 03 | Answer in data | `output_type=` | [03_expense.py](exercises/03_expense.py) | [Split a barkada trip from a group chat](exercises/03_then_try.py) |
| 04 | Put a face on it | `agent.to_web()` | [04_chat.py](exercises/04_chat.py) | [An expense logger that actually logs](exercises/04_then_try.py) |
| 05 | Ask before acting | `requires_approval=True` | [05_approval.py](exercises/05_approval.py) | [Ask only above ₱1,000](exercises/05_then_try.py) |

Run any of them with `uv run exercises/<file>.py`.

## Building blocks

Pick the blocks your idea needs. Each one is a runnable example; the docs link
goes deeper.

| Block | What it shows | Example | Docs |
|---|---|---|---|
| Quickstart | The `Agent` class and how to run it | [01_hello.py](exercises/01_hello.py) | [agent](https://ai.pydantic.dev/agent/#introduction) |
| Tools | Your functions, retries, plus built-in web search | [02_then_try.py](exercises/02_then_try.py), [web_search.py](building_blocks/web_search.py) | [tools](https://ai.pydantic.dev/tools/) |
| Typed output | Validated Pydantic objects, not loose text | [03_then_try.py](exercises/03_then_try.py) | [output](https://ai.pydantic.dev/output/) |
| Web UI | A ready-made chat interface | [04_then_try.py](exercises/04_then_try.py) | [web](https://ai.pydantic.dev/web/) |
| 20+ providers | Per-run model swap, `FallbackModel` | [providers.py](building_blocks/providers.py) | [models](https://ai.pydantic.dev/models/) |
| Memory | Message history, saved to JSON across restarts | [memory.py](building_blocks/memory.py) | [message history](https://ai.pydantic.dev/message-history/) |
| MCP | Build an MCP server, plug it into an agent | [mcp_server.py](building_blocks/mcp_server.py), [mcp_client.py](building_blocks/mcp_client.py) | [MCP](https://ai.pydantic.dev/mcp/overview/) |
| Streaming | Text, partial structured output, and events | [streaming.py](building_blocks/streaming.py) | [streaming](https://ai.pydantic.dev/output/#streaming-text) |
| Human in the loop | Approve big payments before they run | [05_then_try.py](exercises/05_then_try.py), [human_in_the_loop.py](building_blocks/human_in_the_loop.py) | [deferred tools](https://ai.pydantic.dev/deferred-tools/#human-in-the-loop-tool-approval) |
| Multi-agent | A planner delegating to typed specialists | [multi_agent.py](building_blocks/multi_agent.py) | [multi-agent](https://ai.pydantic.dev/multi-agent-applications/) |
| Embeddings | RAG over your notes in ~40 lines | [embeddings_rag.py](building_blocks/embeddings_rag.py) | [embeddings](https://ai.pydantic.dev/embeddings/) |
| Evals | Score an agent against test cases | [evals.py](building_blocks/evals.py) | [evals](https://ai.pydantic.dev/evals/) |

## The harness

[`harness/`](harness) puts the blocks together: a ~200-line coding agent for
your terminal with tools, project context, approvals, usage limits, memory and
streaming. Read its [README](harness/README.md) for the anatomy and ideas for
turning it into your own thing.

```sh
uv run harness/harness.py
```

## Beyond `to_web()`

[`beyond/custom_ui/`](beyond/custom_ui) serves an agent over
[AG-UI](https://docs.ag-ui.com) to a React app, where tool calls become live
charts of World Bank data.

## The rest of the sprint

1. **Skim** the building blocks that grab you.
2. **Read** an article or two in between.
3. **Decide** what to build, starting from the closest exercise.
4. **Build** it. Remix the exercises freely.
5. **Demo** your best work, in about five minutes.

## Resources

**For the sprint**

- [Pydantic AI documentation](https://ai.pydantic.dev/): the library, with code examples
- [Awesome Pydantic](https://github.com/kludex/awesome-pydantic): a curated list of good things built on Pydantic
- [OpenRouter](https://openrouter.ai/): one API key for many providers, including free models

**Further reading**

- [Learnings from building a minimal coding agent](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/), Mario Zechner
- [The importance of agent harnesses](https://www.philschmid.de/agent-harness-2026), Phil Schmid
- [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), Anthropic
- [The new skill is context engineering](https://www.philschmid.de/context-engineering), Phil Schmid
- [Tools: code is all you need](https://lucumr.pocoo.org/2025/7/3/tools/), Armin Ronacher

---

Go fill the form. Then show the room.

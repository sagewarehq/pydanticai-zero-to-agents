# Beyond `to_web()`: your own frontend over AG-UI

A chat app where the agent answers with **real charts from real data**. Ask
"Compare GDP per capita of PH, VN, TH and ID since 2000" and it fetches World
Bank data, then calls `show_chart`, which the frontend renders with Chart.js.

## Run it

Needs Node + [pnpm](https://pnpm.io) in addition to the workshop setup.

```sh
cd beyond/custom_ui
(cd frontend && pnpm install)   # first time only
uvx honcho start                # backend on :9100, frontend on :9000
```

Open http://localhost:9000.

## How it fits together

```
React (frontend/src)  ──POST /api──▶  Vite proxy  ──▶  server.py (Starlette)
       ▲                                                   │
       └──── AG-UI events (SSE): text, tool calls ◀────────┘  AGUIAdapter.dispatch_request
```

- **`server.py`**: a normal Pydantic AI agent. `AGUIAdapter.dispatch_request`
  turns a run into an AG-UI event stream. That's the whole integration.
- **`show_chart`** returns nothing interesting to the model. Its typed
  arguments (`type`, `labels`, `datasets`, ...) are the payload the UI renders.
  This is "generative UI": the model picks the component and fills its props.
- **`frontend/src/App.tsx`** uses `@ag-ui/client`'s `HttpAgent` and renders
  each message: text as markdown, `show_chart` calls as `<ChartCard>`, other
  tools as a status pill.

Want the same widget inside Claude or ChatGPT? Wrap `ChartCard` as an
MCP App ([modelcontextprotocol.io](https://modelcontextprotocol.io)) later; the
contract stays the same.

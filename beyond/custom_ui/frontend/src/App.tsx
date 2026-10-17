import { HttpAgent, type Message } from '@ag-ui/client'
import { useEffect, useRef, useState } from 'react'
import Markdown from 'react-markdown'
import { ChartCard, ChartSkeleton, type ChartSpec } from './ChartCard'

const SUGGESTIONS = [
  'Chart the Philippine population, 2006–2025',
  'Compare GDP per capita of PH, VN, TH and ID since 2000',
  'Life expectancy in Japan vs. the US over the last 30 years',
  'Explain AG-UI in one paragraph',
]

type ChatItem =
  | { kind: 'user' | 'text'; id: string; content: string }
  | { kind: 'tool'; id: string; name: string; args: string; done: boolean }

function toChat(messages: readonly Message[]): ChatItem[] {
  const done = new Set(messages.flatMap((m) => (m.role === 'tool' ? [m.toolCallId] : [])))
  return messages.flatMap((m): ChatItem[] => {
    if (m.role === 'user' && typeof m.content === 'string') return [{ kind: 'user', id: m.id, content: m.content }]
    if (m.role !== 'assistant') return []
    return [
      ...(m.content ? [{ kind: 'text' as const, id: m.id, content: m.content }] : []),
      ...(m.toolCalls ?? []).map((tc) => ({
        kind: 'tool' as const,
        id: tc.id,
        name: tc.function.name,
        args: tc.function.arguments,
        done: done.has(tc.id),
      })),
    ]
  })
}

function parse<T>(json: string): T | null {
  try {
    return JSON.parse(json) as T
  } catch {
    return null
  }
}

function ToolItem({ item }: { item: Extract<ChatItem, { kind: 'tool' }> }) {
  if (item.name === 'show_chart') {
    const spec = parse<ChartSpec>(item.args)
    return spec?.datasets ? <ChartCard spec={spec} /> : <ChartSkeleton />
  }
  const args = parse<Record<string, unknown>>(item.args)
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-stone-200 bg-white px-3 py-1 text-xs text-stone-500 dark:border-stone-800 dark:bg-stone-900 dark:text-stone-400">
      {item.done ? (
        <span className="text-durian-600">✓</span>
      ) : (
        <span className="size-3 animate-spin rounded-full border-2 border-stone-300 border-t-durian-500" />
      )}
      <span className="font-medium text-stone-700 dark:text-stone-300">{item.name}</span>
      {args && <span className="truncate font-mono">{Object.values(args).join(' · ')}</span>}
    </div>
  )
}

export default function App() {
  const agent = useRef(new HttpAgent({ url: '/api' })).current
  const [messages, setMessages] = useState<ChatItem[]>([])
  const [input, setInput] = useState('')
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottom = useRef<HTMLDivElement>(null)
  const textarea = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, running])

  async function send(text: string) {
    if (!text.trim() || running) return
    agent.addMessage({ id: crypto.randomUUID(), role: 'user', content: text.trim() })
    setMessages(toChat(agent.messages))
    setInput('')
    setError(null)
    setRunning(true)
    try {
      await agent.runAgent({}, { onMessagesChanged: ({ messages }) => setMessages(toChat(messages)) })
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setRunning(false)
      textarea.current?.focus()
    }
  }

  function reset() {
    agent.abortRun()
    agent.setMessages([])
    setMessages([])
    setError(null)
  }

  const last = messages.at(-1)
  const waiting = running && last?.kind !== 'text' && !(last?.kind === 'tool' && !last.done)

  return (
    <div className="flex h-dvh flex-col bg-stone-50 text-stone-900 dark:bg-stone-950 dark:text-stone-100">
      <header className="flex items-center justify-between border-b border-stone-200/70 px-5 py-3 backdrop-blur dark:border-stone-800">
        <div className="flex items-center gap-2.5">
          <Logo />
          <span className="font-semibold tracking-tight">zero to agents</span>
          <span className="flex items-center gap-1.5 rounded-full bg-stone-100 px-2 py-0.5 text-xs text-stone-500 dark:bg-stone-900 dark:text-stone-400">
            <span className={`size-1.5 rounded-full ${running ? 'animate-pulse bg-amber-400' : 'bg-durian-500'}`} />
            {running ? 'Thinking' : 'Ready'}
          </span>
        </div>
        {messages.length > 0 && (
          <button
            onClick={reset}
            className="rounded-lg px-3 py-1.5 text-sm text-stone-500 transition hover:bg-stone-200/60 hover:text-stone-900 dark:hover:bg-stone-800 dark:hover:text-stone-100"
          >
            New chat
          </button>
        )}
      </header>

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl px-4 py-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center pt-[15vh] text-center">
              <Logo className="size-12" />
              <h1 className="mt-5 text-3xl font-semibold tracking-tight">What can I help with?</h1>
              <p className="mt-2 text-stone-500 dark:text-stone-400">Pydantic AI, streamed over AG-UI.</p>
              <div className="mt-8 grid w-full max-w-xl gap-2 sm:grid-cols-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="rounded-xl border border-stone-200 bg-white px-4 py-3 text-left text-sm text-stone-600 shadow-sm transition hover:-translate-y-0.5 hover:border-durian-300 hover:shadow-md dark:border-stone-800 dark:bg-stone-900 dark:text-stone-300 dark:hover:border-durian-700"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((m) =>
                m.kind === 'user' ? (
                  <div key={m.id} className="flex justify-end">
                    <div className="max-w-[80%] whitespace-pre-wrap rounded-2xl rounded-br-md bg-durian-600 px-4 py-2.5 text-white shadow-sm">
                      {m.content}
                    </div>
                  </div>
                ) : m.kind === 'tool' ? (
                  <div key={m.id} className="pl-10">
                    <ToolItem item={m} />
                  </div>
                ) : (
                  <div key={m.id} className="flex gap-3">
                    <Logo className="mt-1 size-7 shrink-0" />
                    <div
                      className={`prose prose-stone min-w-0 max-w-none dark:prose-invert prose-pre:rounded-xl prose-pre:bg-stone-900 ${running && m === last ? 'cursor' : ''}`}
                    >
                      <Markdown>{m.content}</Markdown>
                    </div>
                  </div>
                ),
              )}
              {waiting && (
                <div className="flex gap-3">
                  <Logo className="mt-1 size-7 shrink-0" />
                  <div className="flex items-center gap-1 pt-3">
                    {[0, 150, 300].map((d) => (
                      <span key={d} className="size-2 animate-bounce rounded-full bg-durian-400" style={{ animationDelay: `${d}ms` }} />
                    ))}
                  </div>
                </div>
              )}
              {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
                  {error}
                </div>
              )}
            </div>
          )}
          <div ref={bottom} />
        </div>
      </main>

      <footer className="px-4 pb-5">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            send(input)
          }}
          className="mx-auto flex max-w-3xl items-end gap-2 rounded-2xl border border-stone-200 bg-white p-2 shadow-lg shadow-stone-200/50 transition focus-within:border-durian-400 focus-within:ring-4 focus-within:ring-durian-100 dark:border-stone-800 dark:bg-stone-900 dark:shadow-none dark:focus-within:ring-durian-900"
        >
          <textarea
            ref={textarea}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
                e.preventDefault()
                send(input)
              }
            }}
            rows={1}
            autoFocus
            placeholder="Ask for a chart…"
            className="field-sizing-content max-h-48 flex-1 resize-none bg-transparent px-3 py-2 outline-none placeholder:text-stone-400"
          />
          {running ? (
            <button
              type="button"
              onClick={() => agent.abortRun()}
              title="Stop"
              className="grid size-10 place-items-center rounded-xl bg-stone-900 text-white transition hover:bg-stone-700 dark:bg-stone-100 dark:text-stone-900"
            >
              <span className="size-3 rounded-sm bg-current" />
            </button>
          ) : (
            <button
              disabled={!input.trim()}
              title="Send"
              className="grid size-10 place-items-center rounded-xl bg-durian-600 text-white transition hover:bg-durian-700 disabled:bg-stone-200 disabled:text-stone-400 dark:disabled:bg-stone-800"
            >
              <svg viewBox="0 0 20 20" fill="currentColor" className="size-5">
                <path d="M10 3a1 1 0 0 1 .7.3l5 5a1 1 0 0 1-1.4 1.4L11 6.4V16a1 1 0 1 1-2 0V6.4L5.7 9.7a1 1 0 0 1-1.4-1.4l5-5A1 1 0 0 1 10 3Z" />
              </svg>
            </button>
          )}
        </form>
        <p className="mt-2 text-center text-xs text-stone-400">Enter to send · Shift+Enter for a new line</p>
      </footer>
    </div>
  )
}

function Logo({ className = 'size-6' }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <path
        d="M16 2l3 4 5-1 1 5 4 3-3 4 1 5-5 1-2 4-4-2-4 2-2-4-5-1 1-5-3-4 4-3 1-5 5 1z"
        className="fill-durian-400 dark:fill-durian-500"
      />
      <circle cx="16" cy="16" r="7" className="fill-durian-600 dark:fill-durian-700" />
      <circle cx="16" cy="16" r="3" className="fill-amber-300" />
    </svg>
  )
}

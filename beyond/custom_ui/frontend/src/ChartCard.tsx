import 'chart.js/auto'
import { Chart as ChartJS } from 'chart.js'
import { Chart } from 'react-chartjs-2'

export type ChartSpec = {
  type: 'line' | 'bar' | 'pie' | 'doughnut'
  title: string
  labels: string[]
  datasets: { label: string; data: (number | null)[] }[]
  y_label?: string | null
  source?: string | null
}

const PALETTE = ['#7a9216', '#f59e0b', '#0d9488', '#e11d48', '#0284c7', '#7c3aed', '#b8d23a', '#78716c']

const dark = window.matchMedia('(prefers-color-scheme: dark)').matches
ChartJS.defaults.color = dark ? '#a8a29e' : '#78716c'
ChartJS.defaults.borderColor = dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)'
ChartJS.defaults.font.family = 'Inter, ui-sans-serif, system-ui, sans-serif'

const compact = new Intl.NumberFormat(undefined, { notation: 'compact', maximumFractionDigits: 2 })
const full = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 })

export function ChartCard({ spec }: { spec: ChartSpec }) {
  const radial = spec.type === 'pie' || spec.type === 'doughnut'
  const datasets = spec.datasets.map((d, i) => {
    const color = PALETTE[i % PALETTE.length]
    if (radial) return { ...d, backgroundColor: spec.labels.map((_, j) => PALETTE[j % PALETTE.length]), borderWidth: 0 }
    return {
      ...d,
      borderColor: color,
      backgroundColor: spec.type === 'bar' ? color : `${color}22`,
      fill: spec.type === 'line' && spec.datasets.length === 1,
      tension: 0.3,
      pointRadius: 0,
      pointHoverRadius: 5,
      borderWidth: 2,
      borderRadius: 6,
    }
  })

  return (
    <figure className="not-prose w-full rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-stone-800 dark:bg-stone-900">
      <figcaption className="mb-4 font-semibold tracking-tight">{spec.title}</figcaption>
      <div className="h-72">
        <Chart
          type={spec.type}
          data={{ labels: spec.labels, datasets }}
          options={{
            maintainAspectRatio: false,
            interaction: { mode: radial ? 'nearest' : 'index', intersect: false },
            plugins: {
              legend: {
                display: radial || spec.datasets.length > 1,
                position: 'bottom',
                labels: { usePointStyle: true, boxWidth: 8 },
              },
              tooltip: {
                padding: 10,
                cornerRadius: 8,
                callbacks: {
                  label: (ctx) => ` ${ctx.dataset.label}: ${full.format(Number(ctx.raw))}`,
                },
              },
            },
            scales: radial
              ? {}
              : {
                  x: { grid: { display: false } },
                  y: {
                    title: { display: !!spec.y_label, text: spec.y_label ?? '' },
                    ticks: { callback: (v) => compact.format(Number(v)) },
                  },
                },
          }}
        />
      </div>
      {spec.source && <p className="mt-3 text-xs text-stone-400">Source: {spec.source}</p>}
    </figure>
  )
}

export function ChartSkeleton() {
  return (
    <div className="w-full animate-pulse rounded-2xl border border-stone-200 bg-white p-5 dark:border-stone-800 dark:bg-stone-900">
      <div className="mb-4 h-4 w-48 rounded bg-stone-200 dark:bg-stone-800" />
      <div className="flex h-72 items-end gap-2">
        {[40, 55, 45, 70, 60, 80, 75, 90].map((h, i) => (
          <div key={i} className="flex-1 rounded-t bg-stone-100 dark:bg-stone-800" style={{ height: `${h}%` }} />
        ))}
      </div>
    </div>
  )
}

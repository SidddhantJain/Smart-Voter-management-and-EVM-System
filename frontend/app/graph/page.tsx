"use client"

import React, { useEffect, useMemo, useState } from 'react'
import { apiFetch } from '../../lib/auth'

type GraphNode = { id: string; label: string; kind: string }
type GraphEdge = { source: string; target: string; relation: string }

const LEVEL_ORDER = ['central', 'state', 'local', 'voter'] as const
const KIND_STYLES: Record<string, string> = {
  central: 'fill-cyan-300 stroke-cyan-100',
  state: 'fill-amber-300 stroke-amber-100',
  local: 'fill-violet-300 stroke-violet-100',
  voter: 'fill-slate-200 stroke-slate-50',
}

export default function GraphPage() {
  const [nodes, setNodes] = useState<GraphNode[]>([])
  const [edges, setEdges] = useState<GraphEdge[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch('/api/v1/graph/network')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setNodes(data.nodes ?? [])
        setEdges(data.edges ?? [])
      } catch (e: any) {
        setError(e?.message || String(e))
      }
    }
    load()
  }, [])

  const positioned = useMemo(() => {
    const width = 960
    const height = 540
    const layerGap = 110
    const topOffset = 70
    const centerX = width / 2
    const byKind = LEVEL_ORDER.map((kind) => ({
      kind,
      items: nodes.filter((node) => node.kind === kind),
    }))

    return byKind.flatMap(({ kind, items }, layerIndex) => {
      const rowY = topOffset + layerIndex * layerGap
      const spread = Math.max(width - 140, 240)
      const count = Math.max(items.length, 1)
      return items.map((node, index) => {
        const x = count === 1 ? centerX : 70 + (spread * index) / (count - 1)
        return {
          ...node,
          kind,
          x,
          y: rowY,
        }
      })
    })
  }, [nodes])

  const nodeMap = useMemo(() => new Map(positioned.map((node) => [node.id, node])), [positioned])
  const connectedIds = useMemo(() => {
    const ids = new Set<string>()
    edges.forEach((edge) => {
      ids.add(edge.source)
      ids.add(edge.target)
    })
    return ids
  }, [edges])

  const levelCounts = useMemo(
    () => LEVEL_ORDER.map((kind) => ({ kind, count: nodes.filter((node) => node.kind === kind).length })),
    [nodes]
  )

  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900 to-slate-950 p-6 shadow-2xl shadow-cyan-950/20">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300/80">Network graph</p>
        <h2 className="mt-2 text-3xl font-semibold">Central to state to local constituency mindmap</h2>
        <p className="mt-3 max-w-3xl text-slate-300">
          This view renders the seeded graph as a layered hierarchy: central authority, state branches, local constituencies, and voter leaves.
        </p>
        {error && <p className="mt-4 text-rose-300">{error}</p>}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_0.6fr]">
        <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-4">
          <div className="mb-3 flex items-center justify-between text-sm text-slate-300">
            <span>{nodes.length} nodes</span>
            <span>{edges.length} edges</span>
          </div>
          <svg viewBox="0 0 960 540" className="h-[540px] w-full rounded-2xl bg-slate-950/70">
            {edges.map((edge, index) => {
              const source = nodeMap.get(edge.source)
              const target = nodeMap.get(edge.target)
              if (!source || !target) return null
              const midY = (source.y + target.y) / 2
              return (
                <path
                  key={`${edge.source}-${edge.target}-${index}`}
                  d={`M ${source.x} ${source.y + 18} C ${source.x} ${midY}, ${target.x} ${midY}, ${target.x} ${target.y - 18}`}
                  fill="none"
                  stroke="rgba(103,232,249,0.36)"
                  strokeWidth="2"
                />
              )
            })}
            {positioned.map((node) => (
              <g key={node.id} opacity={connectedIds.has(node.id) ? 1 : 0.45}>
                <circle cx={node.x} cy={node.y} r={node.kind === 'central' ? 28 : 22} className={KIND_STYLES[node.kind] ?? KIND_STYLES.voter} strokeWidth="2" />
                <text x={node.x} y={node.y + 40} textAnchor="middle" fill="#e2e8f0" fontSize="11">
                  {node.label}
                </text>
              </g>
            ))}
          </svg>
        </div>

        <aside className="space-y-4 rounded-3xl border border-white/10 bg-white/5 p-5">
          <h3 className="text-xl font-semibold">Hierarchy summary</h3>
          <div className="grid gap-2 text-sm text-slate-300">
            {levelCounts.map((item) => (
              <div key={item.kind} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-900/50 px-3 py-2">
                <span className="capitalize">{item.kind}</span>
                <span>{item.count}</span>
              </div>
            ))}
            <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-cyan-100">
              The graph is seeded as a mindmap: central root, state branches, local constituency leaves, and voter nodes.
            </div>
          </div>
        </aside>
      </div>
    </section>
  )
}
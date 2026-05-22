"use client"

import React, { useEffect, useMemo, useState } from 'react'
import { apiFetch } from '../../lib/auth'

type GraphNode = { id: string; label: string; kind: string }
type GraphEdge = { source: string; target: string; relation: string }

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
    const radius = Math.min(width, height) * 0.34
    const centerX = width / 2
    const centerY = height / 2
    return nodes.map((node, index) => {
      const angle = nodes.length ? (Math.PI * 2 * index) / nodes.length : 0
      return {
        ...node,
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius,
      }
    })
  }, [nodes])

  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900 to-slate-950 p-6 shadow-2xl shadow-cyan-950/20">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-300/80">Network graph</p>
        <h2 className="mt-2 text-3xl font-semibold">Visible voter and constituency links</h2>
        <p className="mt-3 max-w-3xl text-slate-300">
          This view draws the seeded graph network directly from the backend. After seeding data, you should see the voter network fill out immediately.
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
              const source = positioned.find((node) => node.id === edge.source)
              const target = positioned.find((node) => node.id === edge.target)
              if (!source || !target) return null
              return (
                <line
                  key={`${edge.source}-${edge.target}-${index}`}
                  x1={source.x}
                  y1={source.y}
                  x2={target.x}
                  y2={target.y}
                  stroke="rgba(103,232,249,0.28)"
                  strokeWidth="2"
                />
              )
            })}
            {positioned.map((node) => (
              <g key={node.id}>
                <circle cx={node.x} cy={node.y} r={20} fill={node.kind === 'voter' ? '#22d3ee' : '#f59e0b'} opacity="0.95" />
                <text x={node.x} y={node.y + 38} textAnchor="middle" fill="#e2e8f0" fontSize="11">
                  {node.label}
                </text>
              </g>
            ))}
          </svg>
        </div>

        <aside className="space-y-4 rounded-3xl border border-white/10 bg-white/5 p-5">
          <h3 className="text-xl font-semibold">Node summary</h3>
          <div className="space-y-2 text-sm text-slate-300">
            {nodes.slice(0, 12).map((node) => (
              <div key={node.id} className="rounded-xl border border-white/10 bg-slate-900/50 px-3 py-2">
                <div className="font-medium text-slate-100">{node.label}</div>
                <div>{node.kind}</div>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </section>
  )
}
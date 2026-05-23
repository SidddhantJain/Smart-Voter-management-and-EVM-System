"use client"

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiFetch, getToken } from '../../lib/auth'

export default function ConstituenciesPage() {
  const router = useRouter()
  const [items, setItems] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState({ constituency_id: '', name: '', state: '', district: '' })

  async function loadItems() {
    try {
      const res = await apiFetch('/api/v1/constituencies')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setItems(await res.json())
    } catch (e: any) {
      setError(e?.message || String(e))
    }
  }

  useEffect(() => {
    const token = getToken()
    if (!token) {
      router.push('/login')
      return
    }
    loadItems()
  }, [])

  async function createConstituency(e: React.FormEvent) {
    e.preventDefault()
    if (!form.constituency_id || !form.name) {
      setError('Constituency id and name are required')
      return
    }
    const res = await apiFetch('/api/v1/constituencies', {
      method: 'POST',
      body: JSON.stringify(form),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      setError(data.detail || `HTTP ${res.status}`)
      return
    }
    setForm({ constituency_id: '', name: '', state: '', district: '' })
    setError(null)
    await loadItems()
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-semibold">Constituencies</h2>
      {error && <div style={{color:'crimson'}}>{error}</div>}
      <form onSubmit={createConstituency} className="grid gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 md:grid-cols-5">
        <input className="rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2" placeholder="ID" value={form.constituency_id} onChange={(e)=>setForm({...form,constituency_id:e.target.value})} />
        <input className="rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2" placeholder="Name" value={form.name} onChange={(e)=>setForm({...form,name:e.target.value})} />
        <input className="rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2" placeholder="State" value={form.state} onChange={(e)=>setForm({...form,state:e.target.value})} />
        <input className="rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2" placeholder="District" value={form.district} onChange={(e)=>setForm({...form,district:e.target.value})} />
        <button className="rounded-xl bg-amber-400 px-4 py-2 font-semibold text-slate-950" type="submit">Add constituency</button>
      </form>
      <ul className="grid gap-3 md:grid-cols-2">
        {items.map((c:any)=> (
          <li className="rounded-xl border border-white/10 bg-slate-900/50 px-4 py-3" key={c.constituency_id}>
            <div className="font-semibold text-slate-100">{c.name}</div>
            <div className="text-sm text-slate-300">{c.constituency_id} • {c.state ?? 'NA'} • {c.district ?? 'NA'}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}

"use client"

import React, { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiFetch, getToken } from '../../lib/auth'

export default function VotersPage() {
  const router = useRouter()
  const [voters, setVoters] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState({ voter_id: '', first_name: '', last_name: '', constituency: 'CONS-001' })

  async function loadVoters() {
    try {
      const res = await apiFetch('/api/v1/voters')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setVoters(await res.json())
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
    loadVoters()
  }, [])

  async function createVoter(e: React.FormEvent) {
    e.preventDefault()
    if (!form.voter_id || !form.first_name || !form.last_name) {
      setError('Fill voter id, first name, and last name')
      return
    }
    const res = await apiFetch('/api/v1/voters', {
      method: 'POST',
      body: JSON.stringify(form),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      setError(data.detail || `HTTP ${res.status}`)
      return
    }
    setForm({ voter_id: '', first_name: '', last_name: '', constituency: 'CONS-001' })
    setError(null)
    await loadVoters()
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-semibold">Voters</h2>
      {error && <div style={{color:'crimson'}}>{error}</div>}
      <form onSubmit={createVoter} className="grid gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 md:grid-cols-5">
        <input className="rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2" placeholder="Voter ID" value={form.voter_id} onChange={(e)=>setForm({...form,voter_id:e.target.value})} />
        <input className="rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2" placeholder="First name" value={form.first_name} onChange={(e)=>setForm({...form,first_name:e.target.value})} />
        <input className="rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2" placeholder="Last name" value={form.last_name} onChange={(e)=>setForm({...form,last_name:e.target.value})} />
        <input className="rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2" placeholder="Constituency" value={form.constituency} onChange={(e)=>setForm({...form,constituency:e.target.value})} />
        <button className="rounded-xl bg-cyan-400 px-4 py-2 font-semibold text-slate-950" type="submit">Add voter</button>
      </form>
      <ul className="grid gap-3 md:grid-cols-2">
        {voters.map((v:any)=> (
          <li className="rounded-xl border border-white/10 bg-slate-900/50 px-4 py-3" key={v.voter_id}>
            <div className="font-semibold text-slate-100">{v.first_name} {v.last_name}</div>
            <div className="text-sm text-slate-300">{v.voter_id} • {v.constituency ?? 'No constituency'}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}

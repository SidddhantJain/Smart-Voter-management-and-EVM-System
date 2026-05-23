"use client"

import React, { useEffect, useState } from 'react'
import { getToken, apiFetch } from '../../lib/auth'

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      const token = getToken()
      if (!token) {
        setError('Not authenticated — please login')
        return
      }
      try {
        const res = await apiFetch('/api/v1/analytics/summary')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setSummary(data)
      } catch (e: any) {
        setError(e?.message || String(e))
      }
    }
    load()
  }, [])

  return (
    <div>
      <h2>Dashboard</h2>
      {error && <div style={{color:'crimson'}}>{error}</div>}
      {summary ? (
        <pre style={{background:'#0b1220',color:'#d1fae5',padding:12,borderRadius:6}}>{JSON.stringify(summary,null,2)}</pre>
      ) : (
        <div>Loading summary…</div>
      )}
    </div>
  )
}

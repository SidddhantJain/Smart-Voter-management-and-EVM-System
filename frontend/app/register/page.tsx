"use client"

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { register, setToken } from '../../lib/auth'

export default function RegisterPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(false)

  const doRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.includes('@')) {
      setMsg('Enter a valid email address')
      return
    }
    if (password.length < 6) {
      setMsg('Password must be at least 6 characters')
      return
    }
    setLoading(true)
    const result = await register(email, password)
    if (result.access_token) {
      setToken(result.access_token)
      setMsg('Registered and logged in. Redirecting...')
      router.push('/dashboard')
    } else {
      setMsg(result.detail || result.message || JSON.stringify(result))
    }
    setLoading(false)
  }

  return (
    <main className="mx-auto max-w-md rounded-3xl border border-white/10 bg-white/5 p-6">
      <h2 className="mb-4 text-2xl font-semibold">Register</h2>
      <form onSubmit={doRegister} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm text-slate-300">Email</label>
          <input className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2" value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div>
          <label className="mb-1 block text-sm text-slate-300">Password</label>
          <input className="w-full rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <button disabled={loading} className="w-full rounded-xl bg-amber-400 px-4 py-2 font-semibold text-slate-950 disabled:opacity-60" type="submit">{loading ? 'Registering...' : 'Register'}</button>
      </form>
      <div className="mt-4 text-sm text-amber-300">{msg}</div>
    </main>
  )
}

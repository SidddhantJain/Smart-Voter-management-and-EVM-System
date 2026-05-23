import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'VoteGuard Nexus',
  description: 'VoteGuard Nexus management console',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen text-slate-100">
          <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
              <div>
                <p className="text-xs uppercase tracking-[0.35em] text-cyan-300/80">VoteGuard Nexus</p>
                <h1 className="text-lg font-semibold">Management Console</h1>
              </div>
              <nav className="flex flex-wrap gap-3 text-sm text-slate-200">
                <a className="rounded-full border border-white/10 px-4 py-2 hover:bg-white/5" href="/">Home</a>
                <a className="rounded-full border border-white/10 px-4 py-2 hover:bg-white/5" href="/dashboard">Dashboard</a>
                <a className="rounded-full border border-white/10 px-4 py-2 hover:bg-white/5" href="/voters">Voters</a>
                <a className="rounded-full border border-white/10 px-4 py-2 hover:bg-white/5" href="/constituencies">Constituencies</a>
                <a className="rounded-full border border-white/10 px-4 py-2 hover:bg-white/5" href="/graph">Graph</a>
                <a className="rounded-full border border-white/10 px-4 py-2 hover:bg-white/5" href="/login">Login</a>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  )
}
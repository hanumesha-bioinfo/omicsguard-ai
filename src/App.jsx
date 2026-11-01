import { useEffect, useState } from 'react'
import {
  Activity, ShieldCheck, AlertTriangle, BrainCircuit,
  FlaskConical, History, LayoutDashboard, Upload,
  RefreshCw, CheckCircle2, CircleDot, Database,
  Dna, Menu, Sun, Moon, ArrowUpRight, FileSearch,
} from 'lucide-react'

const API = 'http://127.0.0.1:8001'

const modules = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'integrity', label: 'Integrity Audit', icon: ShieldCheck },
  { id: 'anomaly', label: 'Anomaly Analysis', icon: Activity },
  { id: 'benchmark', label: 'Fault-Injection Benchmark', icon: FlaskConical },
  { id: 'leakage', label: 'ML Leakage Audit', icon: BrainCircuit },
  { id: 'history', label: 'Audit History', icon: History },
]

const descriptions = {
  overview: 'Monitor dataset quality and analysis activity.',
  integrity: 'Check expression data and metadata for integrity issues.',
  anomaly: 'Explore unusual samples and expression patterns.',
  benchmark: 'Evaluate detection performance using controlled data corruption.',
  leakage: 'Inspect machine-learning workflows for data leakage risks.',
  history: 'Review previously executed audits and their reports.',
}

function App() {
  const [activeTab, setActiveTab] = useState('overview')
  const [backend, setBackend] = useState('checking')
  const [dark, setDark] = useState(true)
  const [mobileMenu, setMobileMenu] = useState(false)

  async function checkBackend() {
    setBackend('checking')
    try {
      const response = await fetch(`${API}/api/health`)
      if (!response.ok) throw new Error('Backend unavailable')
      const data = await response.json()
      setBackend(data.status === 'healthy' ? 'online' : 'offline')
    } catch {
      setBackend('offline')
    }
  }

  useEffect(() => {
    checkBackend()
  }, [])

  const currentModule = modules.find((item) => item.id === activeTab)
  const theme = dark
    ? 'bg-[#07111f] text-slate-100'
    : 'bg-slate-100 text-slate-900'
  const panel = dark
    ? 'bg-[#101d2d] border-slate-800'
    : 'bg-white border-slate-200'
  const muted = dark ? 'text-slate-400' : 'text-slate-500'

  return (
    <div className={`min-h-screen ${theme}`}>
      <header className={`sticky top-0 z-30 border-b ${panel} backdrop-blur`}>
        <div className="mx-auto flex max-w-[1500px] items-center justify-between px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-teal-400/10 p-2.5 text-teal-400">
              <Dna size={25} />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">OmicsGuard <span className="text-teal-400">AI</span></h1>
              <p className={`text-xs ${muted}`}>Bioinformatics reliability auditor</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className={`hidden items-center gap-2 rounded-full border px-3 py-2 text-xs sm:flex ${panel}`}>
              <span className={`h-2 w-2 rounded-full ${
                backend === 'online' ? 'bg-emerald-400' :
                backend === 'offline' ? 'bg-red-400' : 'bg-amber-400'
              }`} />
              API {backend === 'checking' ? 'Checking' : backend}
            </div>
            <button
              onClick={checkBackend}
              className={`rounded-lg border p-2 ${panel} ${muted}`}
              title="Check backend connection"
            >
              <RefreshCw size={17} />
            </button>
            <button
              onClick={() => setDark(!dark)}
              className={`rounded-lg border p-2 ${panel}`}
              title="Toggle theme"
            >
              {dark ? <Sun size={17} /> : <Moon size={17} />}
            </button>
            <button
              onClick={() => setMobileMenu(!mobileMenu)}
              className={`rounded-lg border p-2 md:hidden ${panel}`}
            >
              <Menu size={18} />
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1500px] md:grid-cols-[245px_1fr]">
        <aside className={`border-r ${panel} ${mobileMenu ? 'block' : 'hidden'} md:block`}>
          <div className="sticky top-[73px] p-4">
            <p className={`mb-3 px-3 text-[10px] font-bold uppercase tracking-[.2em] ${muted}`}>
              Workspace
            </p>
            <nav className="space-y-1">
              {modules.map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => {
                    setActiveTab(id)
                    setMobileMenu(false)
                  }}
                  className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm transition ${
                    activeTab === id
                      ? 'bg-teal-400/10 font-semibold text-teal-400'
                      : `${muted} hover:bg-slate-500/10`
                  }`}
                >
                  <Icon size={18} />
                  {label}
                  {activeTab === id && <ArrowUpRight className="ml-auto" size={15} />}
                </button>
              ))}
            </nav>

            <div className={`mt-8 rounded-xl border p-4 ${panel}`}>
              <div className="mb-2 flex items-center gap-2 text-teal-400">
                <Database size={17} />
                <span className="text-xs font-semibold">Project workspace</span>
              </div>
              <p className={`text-xs leading-5 ${muted}`}>
                Dataset analysis and reliability checks will be managed here.
              </p>
            </div>
          </div>
        </aside>

        <main className="min-w-0 p-5 md:p-8">
          <div className="mb-7 flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className={`mb-2 flex items-center gap-2 text-xs ${muted}`}>
                <span>OmicsGuard AI</span>
                <span>/</span>
                <span className="text-teal-400">{currentModule?.label}</span>
              </div>
              <h2 className="text-2xl font-bold md:text-3xl">{currentModule?.label}</h2>
              <p className={`mt-2 text-sm ${muted}`}>{descriptions[activeTab]}</p>
            </div>
            <div className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-xs ${panel}`}>
              <CircleDot size={15} className="text-teal-400" />
              Research workspace
            </div>
          </div>

          {activeTab === 'overview' ? (
            <>
              <section className="relative mb-6 overflow-hidden rounded-2xl border border-teal-400/20 bg-gradient-to-br from-[#103b46] via-[#102b3c] to-[#14233b] p-6 md:p-8">
                <div className="relative z-10 max-w-2xl">
                  <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-teal-300/20 bg-teal-300/10 px-3 py-1 text-xs text-teal-200">
                    <ShieldCheck size={14} /> Dataset reliability platform
                  </div>
                  <h3 className="text-2xl font-bold leading-tight md:text-3xl">
                    Make your omics data <span className="text-teal-300">research-ready.</span>
                  </h3>
                  <p className="mt-3 max-w-xl text-sm leading-6 text-slate-300">
                    Inspect dataset integrity, detect anomalous samples, benchmark
                    detection methods, and assess machine-learning leakage risks.
                  </p>
                  <button
                    onClick={() => setActiveTab('integrity')}
                    className="mt-5 inline-flex items-center gap-2 rounded-lg bg-teal-400 px-4 py-2.5 text-sm font-semibold text-slate-950 hover:bg-teal-300"
                  >
                    Explore integrity audit <ArrowUpRight size={16} />
                  </button>
                </div>
                <Dna className="absolute -right-4 -top-5 h-64 w-64 rotate-12 text-teal-200/10" strokeWidth={1} />
              </section>

              <section className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {[
                  { label: 'Dataset status', value: 'Not loaded', icon: Database, note: 'Awaiting dataset upload' },
                  { label: 'Integrity checks', value: 'Not run', icon: ShieldCheck, note: 'No audit results yet' },
                  { label: 'Anomalies', value: 'Not assessed', icon: AlertTriangle, note: 'Awaiting analysis' },
                  { label: 'Benchmark', value: 'Not run', icon: BrainCircuit, note: 'No benchmark results yet' },
                ].map((item) => (
                  <div key={item.label} className={`rounded-xl border p-5 ${panel}`}>
                    <div className="mb-4 flex items-center justify-between">
                      <span className={`text-sm ${muted}`}>{item.label}</span>
                      <item.icon className="text-teal-400" size={19} />
                    </div>
                    <p className="text-xl font-bold">{item.value}</p>
                    <p className={`mt-2 text-xs ${muted}`}>{item.note}</p>
                  </div>
                ))}
              </section>

              <section className="grid gap-4 lg:grid-cols-2">
                <div className={`rounded-xl border p-5 ${panel}`}>
                  <div className="mb-3 flex items-center gap-2">
                    <FileSearch size={18} className="text-teal-400" />
                    <h3 className="font-semibold">Analysis workflow</h3>
                  </div>
                  <div className="space-y-4">
                    {[
                      ['01', 'Dataset ingestion', 'Load expression data and sample metadata.'],
                      ['02', 'Integrity validation', 'Check missing values, duplicates and consistency.'],
                      ['03', 'Anomaly detection', 'Explore unusual samples and expression patterns.'],
                      ['04', 'Reliability assessment', 'Benchmark and inspect ML leakage risks.'],
                    ].map(([number, title, description]) => (
                      <div key={number} className="flex gap-3">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-teal-400/10 text-xs font-bold text-teal-400">{number}</span>
                        <div>
                          <p className="text-sm font-medium">{title}</p>
                          <p className={`mt-1 text-xs ${muted}`}>{description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className={`rounded-xl border p-5 ${panel}`}>
                  <div className="mb-3 flex items-center gap-2">
                    <Activity size={18} className="text-teal-400" />
                    <h3 className="font-semibold">Analysis results</h3>
                  </div>
                  <div className={`flex min-h-52 flex-col items-center justify-center text-center ${muted}`}>
                    <Database size={32} className="mb-3 opacity-50" />
                    <p className="text-sm font-medium">No analysis results available</p>
                    <p className="mt-1 max-w-xs text-xs leading-5">
                      Charts and metrics will appear here after the dataset is loaded
                      and the corresponding analysis has been executed.
                    </p>
                  </div>
                </div>
              </section>
            </>
          ) : (
            <section className={`rounded-2xl border p-6 md:p-8 ${panel}`}>
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-teal-400/10 text-teal-400">
                {(() => {
                  const Icon = currentModule?.icon || Activity
                  return <Icon size={24} />
                })()}
              </div>
              <h3 className="text-xl font-bold">{currentModule?.label}</h3>
              <p className={`mt-2 max-w-2xl text-sm leading-6 ${muted}`}>
                {descriptions[activeTab]}
              </p>
              <div className={`mt-6 rounded-xl border border-dashed p-8 text-center ${dark ? 'border-slate-700' : 'border-slate-300'}`}>
                <Database size={28} className={`mx-auto mb-3 ${muted}`} />
                <p className="font-medium">Analysis module awaiting API integration</p>
                <p className={`mx-auto mt-2 max-w-lg text-xs leading-5 ${muted}`}>
                  This section will display results from the existing OmicsGuard
                  Python scientific modules. No simulated results are shown.
                </p>
              </div>
            </section>
          )}

          <footer className={`mt-8 flex flex-wrap items-center justify-between gap-2 border-t pt-5 text-xs ${dark ? 'border-slate-800 text-slate-500' : 'border-slate-200 text-slate-500'}`}>
            <span>OmicsGuard AI · Bioinformatics reliability auditor</span>
            <span className="flex items-center gap-2">
              <CheckCircle2 size={14} className="text-teal-400" />
              React interface
            </span>
          </footer>
        </main>
      </div>
    </div>
  )
}

export default App
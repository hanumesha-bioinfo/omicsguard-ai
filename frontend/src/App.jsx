import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity, ShieldCheck, AlertTriangle, BrainCircuit, FlaskConical,
  History, LayoutDashboard, RefreshCw, CheckCircle2, Database, Dna,
  Menu, Sun, Moon, ArrowUpRight, FileSearch, Microscope, Play,
} from 'lucide-react'
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  ScatterChart, Scatter, ZAxis,
} from 'recharts'

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

const endpoints = {
  integrity: '/api/audit/integrity',
  anomaly: '/api/audit/anomaly',
  benchmark: '/api/audit/benchmark',
  leakage: '/api/audit/leakage',
}

const colors = ['#2dd4bf', '#fbbf24', '#fb7185', '#94a3b8']

function Card({ children, dark }) {
  return (
    <section className={`rounded-2xl border p-5 ${dark ? 'border-slate-800 bg-[#101d2d]' : 'border-slate-200 bg-white'}`}>
      {children}
    </section>
  )
}

function Metric({ label, value, note, icon: Icon, dark }) {
  return (
    <Card dark={dark}>
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-400">{label}</span>
        <Icon size={19} className="text-teal-400" />
      </div>
      <div className="mt-3 text-2xl font-bold">{value ?? '—'}</div>
      <p className="mt-1 text-xs text-slate-400">{note}</p>
    </Card>
  )
}

function JsonDetails({ data }) {
  return (
    <details className="mt-4">
      <summary className="cursor-pointer text-xs font-medium text-teal-400">
        View complete API response
      </summary>
      <pre className="mt-3 max-h-96 overflow-auto rounded-xl bg-black/20 p-4 text-xs leading-5 text-slate-300">
        {JSON.stringify(data, null, 2)}
      </pre>
    </details>
  )
}

function StatusPill({ status }) {
  const value = String(status || 'UNKNOWN').toUpperCase()
  const style = value === 'PASS' || value === 'HEALTHY'
    ? 'bg-emerald-400/10 text-emerald-400'
    : value === 'WARNING' || value === 'SKIPPED'
      ? 'bg-amber-400/10 text-amber-400'
      : 'bg-rose-400/10 text-rose-400'
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${style}`}>{value}</span>
}

function App() {
  const [activeTab, setActiveTab] = useState('overview')
  const [backend, setBackend] = useState('checking')
  const [dark, setDark] = useState(true)
  const [mobileMenu, setMobileMenu] = useState(false)
  const [dataset, setDataset] = useState(null)
  const [results, setResults] = useState({})
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState('')
  const [error, setError] = useState('')

  const currentModule = modules.find((item) => item.id === activeTab)
  const panel = dark ? 'border-slate-800 bg-[#101d2d]' : 'border-slate-200 bg-white'
  const muted = dark ? 'text-slate-400' : 'text-slate-500'
  const page = dark ? 'bg-[#07111f] text-slate-100' : 'bg-slate-100 text-slate-900'

  const request = useCallback(async (path, options = {}) => {
    const response = await fetch(`${API}${path}`, options)
    const data = await response.json().catch(() => ({}))
    if (!response.ok) {
      throw new Error(data.detail || `Request failed (${response.status})`)
    }
    return data
  }, [])

  const checkBackend = useCallback(async () => {
    try {
      await request('/api/health')
      setBackend('online')
      return true
    } catch {
      setBackend('offline')
      return false
    }
  }, [request])

  const loadDataset = useCallback(async () => {
    try {
      const data = await request('/api/dataset/summary')
      setDataset(data)
    } catch (err) {
      setError(err.message)
    }
  }, [request])

  const loadHistory = useCallback(async () => {
    try {
      const data = await request('/api/audit/history')
      setHistory(data.records || [])
    } catch (err) {
      setError(err.message)
    }
  }, [request])

  useEffect(() => {
    checkBackend().then((online) => {
      if (online) {
        loadDataset()
        loadHistory()
      }
    })
  }, [checkBackend, loadDataset, loadHistory])

  async function runAudit(type) {
    setLoading(type)
    setError('')
    try {
      const data = await request(endpoints[type], { method: 'POST' })
      setResults((previous) => ({ ...previous, [type]: data }))
      await loadHistory()
      setActiveTab(type)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading('')
    }
  }

  async function refreshAll() {
    setError('')
    const online = await checkBackend()
    if (online) {
      await loadDataset()
      await loadHistory()
    }
  }

  const integrity = results.integrity
  const anomaly = results.anomaly
  const benchmark = results.benchmark
  const leakage = results.leakage
  const anomalySummary = anomaly?.summary
  const integritySummary = integrity?.summary
  const benchmarkSummary = benchmark?.summary

  const pcaData = useMemo(() => {
    const rows = anomaly?.pca || []
    if (!rows.length) return []
    const keys = Object.keys(rows[0])
    const xKey = keys.find((key) => /^pc1$/i.test(key)) || keys.find((key) => key.toLowerCase().includes('pc1'))
    const yKey = keys.find((key) => /^pc2$/i.test(key)) || keys.find((key) => key.toLowerCase().includes('pc2'))
    if (!xKey || !yKey) return []
    return rows.map((row) => ({
      x: Number(row[xKey]),
      y: Number(row[yKey]),
      sample: String(row.sample_id ?? row.index ?? row[keys[0]] ?? ''),
    })).filter((row) => Number.isFinite(row.x) && Number.isFinite(row.y))
  }, [anomaly])

  const benchmarkBars = useMemo(() => {
    const metrics = benchmark?.metrics || benchmarkSummary?.per_check_metrics
    if (!metrics) return []
    if (Array.isArray(metrics)) {
      return metrics.map((item, index) => ({
        name: item.check_name || item.check || `Check ${index + 1}`,
        precision: Number(item.precision ?? 0),
        recall: Number(item.recall ?? 0),
        f1: Number(item.f1 ?? item.f1_score ?? 0),
      }))
    }
    return Object.entries(metrics).map(([name, item]) => ({
      name: name.replaceAll('_', ' '),
      precision: Number(item?.precision ?? 0),
      recall: Number(item?.recall ?? 0),
      f1: Number(item?.f1 ?? item?.f1_score ?? 0),
    }))
  }, [benchmark, benchmarkSummary])

  const anomalyPie = anomalySummary ? [
    { name: 'Typical profiles', value: anomalySummary.typical_profiles || 0 },
    { name: 'Potential anomalies', value: anomalySummary.potential_anomalies || 0 },
  ] : []

  const actions = [
    { id: 'integrity', label: 'Run integrity audit', icon: ShieldCheck },
    { id: 'anomaly', label: 'Run anomaly analysis', icon: Activity },
    { id: 'benchmark', label: 'Run fault-injection benchmark', icon: FlaskConical },
  ]

  function runButton(type, label) {
    const Icon = actions.find((item) => item.id === type)?.icon || Play
    return (
      <button
        onClick={() => runAudit(type)}
        disabled={Boolean(loading) || backend !== 'online'}
        className="inline-flex items-center gap-2 rounded-lg bg-teal-400 px-4 py-2.5 text-sm font-semibold text-slate-950 hover:bg-teal-300 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading === type ? <RefreshCw size={16} className="animate-spin" /> : <Icon size={16} />}
        {loading === type ? 'Running...' : label}
      </button>
    )
  }

  function renderIntegrity() {
    if (!integrity) return <Empty text="Run the integrity audit to see the five scientific checks." />
    return (
      <>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Metric dark={dark} label="Total checks" value={integritySummary?.total_checks} note="Scientific validation checks" icon={FileSearch} />
          <Metric dark={dark} label="Passed" value={integritySummary?.passed} note="Checks passed" icon={CheckCircle2} />
          <Metric dark={dark} label="Warnings" value={integritySummary?.warnings} note="Require review" icon={AlertTriangle} />
          <Metric dark={dark} label="Failed" value={integritySummary?.failed} note="Detected failures" icon={ShieldCheck} />
        </div>
        <Card dark={dark}>
          <h3 className="mb-4 font-semibold">Integrity check results</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className={muted}><tr><th className="p-3">Check</th><th className="p-3">Status</th><th className="p-3">Details</th></tr></thead>
              <tbody>
                {(integrity.results || []).map((item, index) => (
                  <tr key={index} className="border-t border-slate-700/40">
                    <td className="p-3 font-medium">{String(item.check || item.name || `Check ${index + 1}`).replaceAll('_', ' ')}</td>
                    <td className="p-3"><StatusPill status={item.status} /></td>
                    <td className={`max-w-lg p-3 text-xs ${muted}`}>{item.message || item.details || item.description || 'See full response'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <JsonDetails data={integrity} />
        </Card>
      </>
    )
  }

  function renderAnomaly() {
    if (!anomaly) return <Empty text="Run anomaly analysis to inspect PCA coordinates and potential outlier samples." />
    return (
      <>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Metric dark={dark} label="Samples analysed" value={anomalySummary?.total_samples} note="Expression profiles" icon={Database} />
          <Metric dark={dark} label="Potential anomalies" value={anomalySummary?.potential_anomalies} note="Flagged by Isolation Forest" icon={AlertTriangle} />
          <Metric dark={dark} label="Typical profiles" value={anomalySummary?.typical_profiles} note="Not flagged by the model" icon={CheckCircle2} />
          <Metric dark={dark} label="Flagged percentage" value={`${anomalySummary?.flagged_percentage ?? '—'}%`} note={anomalySummary?.method || 'Detection method'} icon={Activity} />
        </div>
        <div className="mt-4 grid gap-4 xl:grid-cols-2">
          <Card dark={dark}>
            <h3 className="mb-3 font-semibold">PCA sample projection</h3>
            {pcaData.length ? (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 10, right: 15, bottom: 10, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                    <XAxis type="number" dataKey="x" name="PC1" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <YAxis type="number" dataKey="y" name="PC2" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <ZAxis range={[45, 45]} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter data={pcaData} fill="#2dd4bf" />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            ) : <Empty text="PCA coordinates were returned, but their axis columns could not be identified." />}
            <p className={`text-xs ${muted}`}>Explained variance: {(anomalySummary?.pca_explained_variance || []).map((v) => `${(v * 100).toFixed(2)}%`).join(' / ') || 'Not reported'}</p>
          </Card>
          <Card dark={dark}>
            <h3 className="mb-3 font-semibold">Sample classification</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={anomalyPie} dataKey="value" nameKey="name" outerRadius={90} label>
                    {anomalyPie.map((item, index) => <Cell key={item.name} fill={colors[index]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <p className={`text-xs leading-5 ${muted}`}>{anomalySummary?.interpretation}</p>
          </Card>
        </div>
        <Card dark={dark}>
          <h3 className="mb-3 font-semibold">Potentially anomalous samples</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className={muted}><tr><th className="p-3">Sample</th><th className="p-3">Flag</th></tr></thead>
              <tbody>
                {(anomaly.anomalies || []).filter((row) => row.is_anomaly).map((row, index) => (
                  <tr key={index} className="border-t border-slate-700/40">
                    <td className="p-3">{row.sample_id || row.index || `Sample ${index + 1}`}</td>
                    <td className="p-3"><StatusPill status="WARNING" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <JsonDetails data={anomaly} />
        </Card>
      </>
    )
  }

  function renderBenchmark() {
    if (!benchmark) return <Empty text="Run the controlled fault-injection benchmark to view detection results." />
    return (
      <>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Metric dark={dark} label="Experiments" value={benchmarkSummary?.total_experiments ?? benchmark.experiments?.length} note="Clean baseline plus injected defects" icon={FlaskConical} />
          <Metric dark={dark} label="Detected" value={benchmarkSummary?.detected ?? benchmarkSummary?.total_detected ?? '—'} note="Defects detected" icon={CheckCircle2} />
          <Metric dark={dark} label="Missed" value={benchmarkSummary?.missed ?? benchmarkSummary?.total_missed ?? '—'} note="Defects not detected" icon={AlertTriangle} />
          <Metric dark={dark} label="Detection rate" value={benchmarkSummary?.detection_rate != null ? `${(benchmarkSummary.detection_rate * 100).toFixed(1)}%` : '—'} note="Controlled benchmark result" icon={Activity} />
        </div>
        <Card dark={dark}>
          <h3 className="mb-4 font-semibold">Per-check benchmark metrics</h3>
          {benchmarkBars.length ? (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={benchmarkBars} margin={{ top: 10, right: 10, left: 0, bottom: 45 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis dataKey="name" angle={-25} textAnchor="end" interval={0} tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <YAxis domain={[0, 1]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="precision" fill="#2dd4bf" />
                  <Bar dataKey="recall" fill="#60a5fa" />
                  <Bar dataKey="f1" fill="#fbbf24" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : <p className={`text-sm ${muted}`}>No per-check chart metrics were returned. Inspect the complete response below.</p>}
          <p className={`text-xs leading-5 ${muted}`}>This is a controlled fault-injection experiment. Its results should not be interpreted as a general estimate of real-world detection performance.</p>
          <JsonDetails data={benchmark} />
        </Card>
      </>
    )
  }

  function renderLeakage() {
    if (!leakage) {
      return (
        <Empty text="Run the ML leakage audit to inspect sample overlap, duplicate expression profiles, and target-feature associations." />
      )
    }

    const summary = leakage.summary || {}
    const checks = leakage.results || []

    return (
      <>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Metric dark={dark} label="Total samples" value={summary.total_samples ?? '—'} note="Verified labeled samples" icon={Database} />
          <Metric dark={dark} label="Training samples" value={summary.training_samples ?? '—'} note="80% stratified training split" icon={Activity} />
          <Metric dark={dark} label="Testing samples" value={summary.testing_samples ?? '—'} note="20% stratified testing split" icon={BrainCircuit} />
          <Metric dark={dark} label="Checks passed" value={`${summary.passed ?? 0}/${summary.total_checks ?? checks.length}`} note={`${summary.warnings ?? 0} warnings · ${summary.failed ?? 0} failures`} icon={CheckCircle2} />
        </div>

        <Card dark={dark}>
          <h3 className="mb-4 font-semibold">Train/test class distribution</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-slate-700/40 p-4">
              <p className={`mb-2 text-sm ${muted}`}>Training set · {summary.training_samples ?? 0} samples</p>
              <p className="text-sm">Tumor: <strong>{summary.training_class_counts?.tumor ?? 0}</strong></p>
              <p className="text-sm">Normal: <strong>{summary.training_class_counts?.normal ?? 0}</strong></p>
            </div>
            <div className="rounded-xl border border-slate-700/40 p-4">
              <p className={`mb-2 text-sm ${muted}`}>Testing set · {summary.testing_samples ?? 0} samples</p>
              <p className="text-sm">Tumor: <strong>{summary.testing_class_counts?.tumor ?? 0}</strong></p>
              <p className="text-sm">Normal: <strong>{summary.testing_class_counts?.normal ?? 0}</strong></p>
            </div>
          </div>
          <p className={`mt-4 text-xs ${muted}`}>
            {summary.split || 'Stratified 80/20 split'} · Random state: {summary.random_state ?? '—'}
          </p>
        </Card>

        <Card dark={dark}>
          <h3 className="mb-4 font-semibold">Leakage screening results</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className={`border-b ${dark ? 'border-slate-700' : 'border-slate-200'}`}>
                  <th className="px-3 py-3">Check</th>
                  <th className="px-3 py-3">Status</th>
                  <th className="px-3 py-3">Details</th>
                </tr>
              </thead>
              <tbody>
                {checks.map((check, index) => (
                  <tr key={`${check.check}-${index}`} className={`border-b ${dark ? 'border-slate-800' : 'border-slate-100'}`}>
                    <td className="px-3 py-3 font-medium">{check.check}</td>
                    <td className="px-3 py-3">
                      <span className={`rounded-full px-2 py-1 text-xs font-semibold ${
                        check.status === 'PASS'
                          ? 'bg-teal-400/10 text-teal-400'
                          : check.status === 'FAIL'
                            ? 'bg-rose-400/10 text-rose-400'
                            : 'bg-amber-400/10 text-amber-400'
                      }`}>{check.status}</span>
                    </td>
                    <td className={`px-3 py-3 text-xs ${muted}`}>
                      {check.message ||
                        (check.overlap_count !== undefined
                          ? `${check.overlap_count} overlapping samples`
                          : check.duplicate_profile_count !== undefined
                            ? `${check.duplicate_profile_count} duplicate profiles`
                            : check.flagged_feature_count !== undefined
                              ? `${check.flagged_feature_count} flagged features`
                              : 'See details')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {checks.some((check) => check.flagged_features?.length) && (
            <div className="mt-5">
              <h4 className="mb-2 text-sm font-semibold">Flagged target-associated features</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead><tr><th className="p-2">Feature</th><th className="p-2">Absolute correlation</th></tr></thead>
                  <tbody>
                    {checks.flatMap((check) => check.flagged_features || []).map((feature) => (
                      <tr key={feature.feature}>
                        <td className="p-2">{feature.feature}</td>
                        <td className="p-2">{Number(feature.absolute_correlation).toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <p className={`mt-4 text-xs leading-5 ${muted}`}>
            {leakage.interpretation || 'Leakage screening results require scientific interpretation.'}
          </p>
          <JsonDetails data={leakage} />
        </Card>
      </>
    )
  }

  function renderHistory() {
    return (
      <Card dark={dark}>
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold">Previous audit records</h3>
          <button onClick={loadHistory} className="text-xs text-teal-400">Refresh history</button>
        </div>
        {history.length ? (
          <div className="space-y-3">
            {history.map((record, index) => (
              <div key={record.timestamp || index} className="rounded-xl border border-slate-700/40 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-medium capitalize">{String(record.analysis_type || record.analysis || 'Audit').replaceAll('_', ' ')}</span>
                  <span className={`text-xs ${muted}`}>{record.timestamp || ''}</span>
                </div>
                <pre className={`mt-2 whitespace-pre-wrap text-xs ${muted}`}>{JSON.stringify(record.summary || record, null, 2)}</pre>
              </div>
            ))}
          </div>
        ) : <Empty text="No audit history has been returned yet. Run an audit to create a record." />}
      </Card>
    )
  }

  function Empty({ text }) {
    return (
      <div className={`flex min-h-40 flex-col items-center justify-center rounded-xl border border-dashed p-8 text-center ${dark ? 'border-slate-700' : 'border-slate-300'}`}>
        <Database size={27} className={`mb-3 ${muted}`} />
        <p className={`max-w-lg text-sm ${muted}`}>{text}</p>
      </div>
    )
  }

  function renderOverview() {
    const expression = dataset?.expression
    return (
      <>
        <section className="relative mb-6 overflow-hidden rounded-2xl border border-teal-400/20 bg-gradient-to-br from-[#103b46] via-[#102b3c] to-[#14233b] p-6 md:p-8">
          <div className="relative z-10 max-w-2xl">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-teal-300/20 bg-teal-300/10 px-3 py-1 text-xs text-teal-200">
              <ShieldCheck size={14} /> Dataset reliability platform
            </div>
            <h3 className="text-2xl font-bold md:text-3xl">Make your omics data <span className="text-teal-300">research-ready.</span></h3>
            <p className="mt-3 text-sm leading-6 text-slate-300">Inspect dataset integrity, detect anomalous samples, and benchmark detection methods using the existing scientific pipeline.</p>
            <div className="mt-5 flex flex-wrap gap-2">
              {runButton('integrity', 'Run integrity audit')}
              {runButton('anomaly', 'Run anomaly analysis')}
              {runButton('benchmark', 'Run benchmark')}
            </div>
          </div>
          <Dna className="absolute -right-4 -top-5 h-64 w-64 rotate-12 text-teal-200/10" strokeWidth={1} />
        </section>
        <section className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <Metric dark={dark} label="Dataset" value={dataset?.dataset || 'Loading'} note="Current processed dataset" icon={Database} />
          <Metric dark={dark} label="Samples" value={expression?.samples} note="Expression profiles" icon={Activity} />
          <Metric dark={dark} label="Probes" value={expression?.probes?.toLocaleString()} note="Expression features" icon={Dna} />
          <Metric dark={dark} label="Missing values" value={expression?.missing_values} note="In expression matrix" icon={AlertTriangle} />
        </section>
        <div className="grid gap-4 lg:grid-cols-2">
          <Card dark={dark}>
            <h3 className="mb-4 font-semibold">Analysis workflow</h3>
            {actions.map((item, index) => (
              <div key={item.id} className="flex items-center justify-between gap-3 border-t border-slate-700/40 py-4 first:border-0">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-teal-400">0{index + 1}</span>
                  <div><p className="text-sm font-medium">{item.label}</p><p className={`text-xs ${muted}`}>Execute using the Python API</p></div>
                </div>
                <button onClick={() => runAudit(item.id)} disabled={Boolean(loading) || backend !== 'online'} className="rounded-lg border border-slate-600 p-2 text-teal-400 disabled:opacity-40" title={item.label}>
                  {loading === item.id ? <RefreshCw size={16} className="animate-spin" /> : <Play size={16} />}
                </button>
              </div>
            ))}
          </Card>
          <Card dark={dark}>
            <h3 className="mb-4 font-semibold">Latest results</h3>
            {integritySummary || anomalySummary || benchmarkSummary ? (
              <div className="space-y-3 text-sm">
                {integritySummary && <p>Integrity: <strong>{integritySummary.passed}/{integritySummary.total_checks}</strong> checks passed</p>}
                {anomalySummary && <p>Anomaly analysis: <strong>{anomalySummary.potential_anomalies}</strong> potential anomalies flagged</p>}
                {benchmarkSummary && <p>Benchmark: <strong>{benchmarkSummary.detection_rate != null ? `${(benchmarkSummary.detection_rate * 100).toFixed(1)}%` : 'Completed'}</strong> detection rate</p>}
              </div>
            ) : <Empty text="Run an analysis to display its results here." />}
          </Card>
        </div>
        {dataset && <Card dark={dark}><h3 className="mb-3 font-semibold">Dataset metadata</h3><p className={`text-sm ${muted}`}>{dataset.metadata?.samples} metadata records · {dataset.metadata?.columns} metadata fields</p><div className="mt-3 flex flex-wrap gap-2">{Object.entries(dataset.metadata?.tissue_descriptions || {}).map(([name, count]) => <span key={name} className="rounded-full bg-teal-400/10 px-3 py-1 text-xs text-teal-300">{name}: {count}</span>)}</div></Card>}
      </>
    )
  }

  return (
    <div className={`min-h-screen ${page}`}>
      <header className={`sticky top-0 z-30 border-b backdrop-blur ${panel}`}>
        <div className="mx-auto flex max-w-[1500px] items-center justify-between px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-teal-400/10 p-2.5 text-teal-400"><Dna size={25} /></div>
            <div><h1 className="text-lg font-bold">OmicsGuard <span className="text-teal-400">AI</span></h1><p className={`text-xs ${muted}`}>Bioinformatics reliability auditor</p></div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`hidden items-center gap-2 rounded-full border px-3 py-2 text-xs sm:flex ${panel}`}><span className={`h-2 w-2 rounded-full ${backend === 'online' ? 'bg-emerald-400' : backend === 'offline' ? 'bg-rose-400' : 'bg-amber-400'}`} />API {backend}</span>
            <button onClick={refreshAll} className={`rounded-lg border p-2 ${panel}`} title="Refresh API and dataset"><RefreshCw size={17} /></button>
            <button onClick={() => setDark(!dark)} className={`rounded-lg border p-2 ${panel}`} title="Toggle theme">{dark ? <Sun size={17} /> : <Moon size={17} />}</button>
            <button onClick={() => setMobileMenu(!mobileMenu)} className={`rounded-lg border p-2 md:hidden ${panel}`}><Menu size={18} /></button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1500px] md:grid-cols-[245px_1fr]">
        <aside className={`border-r ${panel} ${mobileMenu ? 'block' : 'hidden'} md:block`}>
          <nav className="sticky top-[73px] space-y-1 p-4">
            <p className={`mb-3 px-3 text-[10px] font-bold uppercase tracking-[.2em] ${muted}`}>Workspace</p>
            {modules.map(({ id, label, icon: Icon }) => (
              <button key={id} onClick={() => { setActiveTab(id); setMobileMenu(false) }} className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm ${activeTab === id ? 'bg-teal-400/10 font-semibold text-teal-400' : `${muted} hover:bg-slate-500/10`}`}>
                <Icon size={18} />{label}{activeTab === id && <ArrowUpRight className="ml-auto" size={15} />}
              </button>
            ))}
            <div className={`mt-8 rounded-xl border p-4 ${panel}`}><div className="mb-2 flex items-center gap-2 text-teal-400"><Database size={17} /><span className="text-xs font-semibold">Project workspace</span></div><p className={`text-xs leading-5 ${muted}`}>GSE10072 processed expression data and metadata.</p></div>
          </nav>
        </aside>

        <main className="min-w-0 space-y-5 p-5 md:p-8">
          <div>
            <div className={`mb-2 flex items-center gap-2 text-xs ${muted}`}><span>OmicsGuard AI</span><span>/</span><span className="text-teal-400">{currentModule?.label}</span></div>
            <h2 className="text-2xl font-bold md:text-3xl">{currentModule?.label}</h2>
            <p className={`mt-2 text-sm ${muted}`}>{descriptions[activeTab]}</p>
          </div>

          {error && <div className="flex items-start justify-between gap-3 rounded-xl border border-rose-400/30 bg-rose-400/10 p-4 text-sm text-rose-300"><span>{error}</span><button onClick={() => setError('')} aria-label="Dismiss error">×</button></div>}

          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'integrity' && <><div className="flex flex-wrap gap-2">{runButton('integrity', 'Run integrity audit')}</div>{renderIntegrity()}</>}
          {activeTab === 'anomaly' && <><div className="flex flex-wrap gap-2">{runButton('anomaly', 'Run anomaly analysis')}</div>{renderAnomaly()}</>}
          {activeTab === 'benchmark' && <><div className="flex flex-wrap gap-2">{runButton('benchmark', 'Run fault-injection benchmark')}</div>{renderBenchmark()}</>}
          {activeTab === 'history' && renderHistory()}
          {activeTab === 'leakage' && <><div className="flex flex-wrap gap-2">{runButton('leakage', 'Run ML leakage audit')}</div>{renderLeakage()}</>}

          <footer className={`flex flex-wrap items-center justify-between gap-2 border-t pt-5 text-xs ${dark ? 'border-slate-800 text-slate-500' : 'border-slate-200 text-slate-500'}`}>
            <span>OmicsGuard AI · Bioinformatics reliability auditor</span>
            <span className="flex items-center gap-2"><CheckCircle2 size={14} className="text-teal-400" />Connected React interface</span>
          </footer>
        </main>
      </div>
    </div>
  )
}

export default App

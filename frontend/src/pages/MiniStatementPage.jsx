import { useEffect, useState } from 'react'
import { miniStatementApi } from '../api/bankApi'

const fallbackRows = [
  { id: 1, type: 'TRANSFER', amount: 80.0, timestamp: '2026-05-17 10:00' },
  { id: 2, type: 'DEPOSIT', amount: 600.0, timestamp: '2026-05-17 09:00' },
  { id: 3, type: 'WITHDRAW', amount: 120.0, timestamp: '2026-05-16 20:15' },
  { id: 4, type: 'TRANSFER', amount: 45.5, timestamp: '2026-05-16 16:03' },
  { id: 5, type: 'DEPOSIT', amount: 1500.0, timestamp: '2026-05-16 11:40' },
]

function MiniStatementPage() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await miniStatementApi()
        setRows(data.transactions || data || [])
      } catch (err) {
        setRows(fallbackRows)
        setError(err?.response?.data?.message || 'Using fallback mini statement. Connect backend endpoint /transactions/mini-statement.')
      }
    }
    fetchData()
  }, [])

  return (
    <div className="glass-card max-w-3xl p-6">
      <h2 className="font-display text-2xl font-semibold text-slate-800 dark:text-slate-100">Mini Statement</h2>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Last 5 transactions snapshot.</p>

      {error ? <p className="mt-3 rounded-lg bg-amber-100 p-2 text-sm text-amber-700">{error}</p> : null}

      <ul className="mt-5 space-y-3">
        {rows.slice(0, 5).map((tx) => (
          <li
            key={tx.id || tx.transaction_id}
            className="flex items-center justify-between rounded-xl border border-slate-200/70 bg-white/60 px-4 py-3 dark:border-slate-700 dark:bg-slate-800/40"
          >
            <div>
              <p className="font-semibold text-slate-800 dark:text-slate-100">{tx.type || tx.transaction_type}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">{tx.timestamp || tx.created_at}</p>
            </div>
            <p className="font-display text-lg font-bold text-slate-800 dark:text-slate-100">${Number(tx.amount || 0).toFixed(2)}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default MiniStatementPage

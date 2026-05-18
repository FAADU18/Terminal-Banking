import { useEffect, useState } from 'react'
import { transactionsApi } from '../api/bankApi'

const fallbackRows = [
  { id: 1, type: 'DEPOSIT', amount: 1200, status: 'SUCCESS', timestamp: '2026-05-16 10:20' },
  { id: 2, type: 'TRANSFER', amount: 300, status: 'SUCCESS', timestamp: '2026-05-16 12:00' },
  { id: 3, type: 'WITHDRAW', amount: 200, status: 'SUCCESS', timestamp: '2026-05-17 09:45' },
]

function HistoryPage() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await transactionsApi()
        setRows(data.transactions || data || [])
      } catch (err) {
        setRows(fallbackRows)
        setError(err?.response?.data?.message || 'Using fallback history. Connect backend endpoint /transactions/history.')
      }
    }
    fetchData()
  }, [])

  return (
    <div className="glass-card overflow-hidden p-6">
      <h2 className="font-display text-2xl font-semibold text-slate-800 dark:text-slate-100">Transaction History</h2>
      {error ? <p className="mt-2 rounded-lg bg-amber-100 p-2 text-sm text-amber-700">{error}</p> : null}

      <div className="mt-5 overflow-x-auto">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-700">
              <th className="py-3">Type</th>
              <th className="py-3">Amount</th>
              <th className="py-3">Status</th>
              <th className="py-3">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((tx) => (
              <tr key={tx.id || tx.transaction_id} className="border-b border-slate-100 dark:border-slate-800">
                <td className="py-3 font-medium text-slate-700 dark:text-slate-100">{tx.type || tx.transaction_type}</td>
                <td className="py-3">${Number(tx.amount || 0).toFixed(2)}</td>
                <td className="py-3">{tx.status || tx.transaction_status || 'SUCCESS'}</td>
                <td className="py-3 text-slate-500 dark:text-slate-400">{tx.timestamp || tx.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default HistoryPage

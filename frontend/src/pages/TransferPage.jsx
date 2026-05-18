import { useState } from 'react'
import { transferApi } from '../api/bankApi'

function TransferPage() {
  const [form, setForm] = useState({ toAccount: '', amount: '', remarks: '' })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')

    try {
      const data = await transferApi({
        to_account: form.toAccount,
        amount: Number(form.amount),
        remarks: form.remarks,
      })
      setMessage(data.message || 'Transfer successful.')
      setForm({ toAccount: '', amount: '', remarks: '' })
    } catch (err) {
      setError(err?.response?.data?.message || 'Transfer failed.')
    }
  }

  return (
    <div className="glass-card max-w-2xl p-6">
      <h2 className="font-display text-2xl font-semibold text-slate-800 dark:text-slate-100">Transfer Money</h2>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">NEFT/IMPS-style transfer flow with remarks.</p>

      <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
        <input
          className="field-input"
          placeholder="Beneficiary Account Number"
          value={form.toAccount}
          onChange={(e) => setForm((p) => ({ ...p, toAccount: e.target.value }))}
          required
        />
        <input
          type="number"
          min="1"
          step="0.01"
          className="field-input"
          placeholder="Amount"
          value={form.amount}
          onChange={(e) => setForm((p) => ({ ...p, amount: e.target.value }))}
          required
        />
        <input
          className="field-input"
          placeholder="Remarks"
          value={form.remarks}
          onChange={(e) => setForm((p) => ({ ...p, remarks: e.target.value }))}
        />

        {message ? <p className="text-sm text-emerald-600">{message}</p> : null}
        {error ? <p className="text-sm text-rose-600">{error}</p> : null}

        <button className="btn-primary" type="submit">
          Transfer
        </button>
      </form>
    </div>
  )
}

export default TransferPage

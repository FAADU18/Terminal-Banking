import { useState } from 'react'
import { withdrawApi } from '../api/bankApi'

function WithdrawPage() {
  const [amount, setAmount] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')

    try {
      const data = await withdrawApi({ amount: Number(amount) })
      setMessage(data.message || 'Withdrawal successful.')
      setAmount('')
    } catch (err) {
      setError(err?.response?.data?.message || 'Withdrawal failed.')
    }
  }

  return (
    <div className="glass-card max-w-xl p-6">
      <h2 className="font-display text-2xl font-semibold text-slate-800 dark:text-slate-100">Withdraw Money</h2>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Transfer funds out securely.</p>

      <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
        <input
          type="number"
          min="1"
          step="0.01"
          className="field-input"
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />

        {message ? <p className="text-sm text-emerald-600">{message}</p> : null}
        {error ? <p className="text-sm text-rose-600">{error}</p> : null}

        <button className="btn-primary" type="submit">
          Withdraw
        </button>
      </form>
    </div>
  )
}

export default WithdrawPage

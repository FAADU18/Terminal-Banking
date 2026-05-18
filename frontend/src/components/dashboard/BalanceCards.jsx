import { ArrowDownCircle, ArrowUpCircle, Wallet } from 'lucide-react'

const cardClasses = 'glass-card p-5'

function BalanceCards({ stats }) {
  return (
    <section className="grid gap-4 md:grid-cols-3">
      <article className={cardClasses}>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-600 dark:text-slate-300">Available Balance</h3>
          <Wallet className="h-5 w-5 text-brand-700" />
        </div>
        <p className="font-display text-3xl font-bold text-slate-800 dark:text-slate-100">${stats.balance.toFixed(2)}</p>
      </article>

      <article className={cardClasses}>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-600 dark:text-slate-300">Total Credits</h3>
          <ArrowDownCircle className="h-5 w-5 text-emerald-500" />
        </div>
        <p className="font-display text-3xl font-bold text-emerald-600">${stats.credits.toFixed(2)}</p>
      </article>

      <article className={cardClasses}>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-600 dark:text-slate-300">Total Debits</h3>
          <ArrowUpCircle className="h-5 w-5 text-rose-500" />
        </div>
        <p className="font-display text-3xl font-bold text-rose-600">${stats.debits.toFixed(2)}</p>
      </article>
    </section>
  )
}

export default BalanceCards

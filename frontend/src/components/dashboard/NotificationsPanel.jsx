import { BellRing } from 'lucide-react'

function NotificationsPanel({ items }) {
  return (
    <div className="glass-card p-5">
      <div className="mb-4 flex items-center gap-2">
        <BellRing className="h-5 w-5 text-brand-700" />
        <h3 className="font-display text-lg font-semibold text-slate-800 dark:text-slate-100">Notifications</h3>
      </div>
      <ul className="space-y-3">
        {items.map((item) => (
          <li key={item.id} className="rounded-xl border border-slate-200/70 bg-white/60 p-3 dark:border-slate-700 dark:bg-slate-800/40">
            <p className="text-sm font-medium text-slate-700 dark:text-slate-100">{item.message}</p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{item.time}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default NotificationsPanel

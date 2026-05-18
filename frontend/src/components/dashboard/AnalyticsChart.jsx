import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

function AnalyticsChart({ data }) {
  return (
    <div className="glass-card p-5">
      <div className="mb-4">
        <h3 className="font-display text-lg font-semibold text-slate-800 dark:text-slate-100">Cashflow Analytics</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400">Last 7 days inflow vs outflow</p>
      </div>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="creditColor" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#16a34a" stopOpacity={0.7} />
                <stop offset="95%" stopColor="#16a34a" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="debitColor" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.7} />
                <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="credit" stroke="#16a34a" fill="url(#creditColor)" strokeWidth={2} />
            <Area type="monotone" dataKey="debit" stroke="#f43f5e" fill="url(#debitColor)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default AnalyticsChart
